from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import matplotlib.pyplot as plt
from foggateway import FogGateway
from clusterhead import PublicTransportation
from vehicle import Vehicle
from clustermember import ClusterMember
class CreateClusEnv(Env):    
    def reset_cluster_heads_cpu_util(self):
        for x in range(len(self.fog_gateway.get_clus_heads())):
            self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util(self.chs_cpu_reset[x])

    def cluster_heads_cpu_util(self,fog_gateway):
        tmp_arr=[]
        for x in range(len(fog_gateway.get_clus_heads())):
            tmp_arr.append(fog_gateway.get_clus_heads()[x].get_fog_cpu_util())
        return tmp_arr

    #Initializing the spaces
    def __init__(self):
        
        #In order to reset the vehicles to init states
        self.fog_gateway=self.set_fog_gateway()
        self.chs_cpu_reset=list(self.cluster_heads_cpu_util(self.fog_gateway))
        self.normal_vehs=self.normal_vehicle_array()

        #For ClusterHeads CPU_util
        self.chs_cpu_util=[]
        for x in range(len(self.fog_gateway.get_clus_heads())):
            self.chs_cpu_util.append(self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util())

        #Actions that we can take 
        self.action_space=list(range(0, 50))

        #set start state of fog_gateway
        self.chs_cpu_util.append(0)
        self.chs_cpu_util.append(self.fog_gateway.get_task_workload())
        self.state=self.chs_cpu_util

        self.iteration=100

    #run whenever you take a step within your environment
    #With Prediciton of future position
    def step(self, action):
        #Action will be selected cluster head
        self.fog_gateway.get_clus_heads()[action]=self.create_cluster(self.fog_gateway.get_clus_heads()[action], self.fog_gateway)
        clu_mem=self.fog_gateway.get_clus_heads()[action].get_clu_mem()
        
        #Future positon of Cluster Head
        self.fog_gateway.get_clus_heads()[action].get_veh().set_future_pos(self.fog_gateway.get_dead_task())
        future_pos_ch=self.fog_gateway.get_clus_heads()[action].get_veh().get_future_pos()
        current_pos_ch=self.fog_gateway.get_clus_heads()[action].get_veh().get_position()
        
        #Calculate Reward
        if(self.euclidean(current_pos_ch, self.fog_gateway.get_position())>self.fog_gateway.get_trans_range()):
            print("The cluster head is out of range",action,self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util())
            reward= -3
        elif(self.euclidean(future_pos_ch, self.fog_gateway.get_position())>self.fog_gateway.get_trans_range()):
            print("Cluster Head will not be in a range after processing depend on predicted position")
            reward=-1
        elif(self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util()>90):
            if(clu_mem[0].get_fog_cpu_util()<=90):
                print("The cluster head is overloaded",action,self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util())
                reward = -1
            elif(clu_mem[1].get_fog_cpu_util()<=90):
                print("The cluster head is overloaded",action,self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util())
                reward = -1
            else:
                print("The whole cluster is overloaded",action,self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util())
                reward = -2
        else:
            tmp_ch_util=self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util()
            deadline_task=self.fog_gateway.get_dead_task()
            if(min(self.chs_cpu_util)==tmp_ch_util):
                reward=3
            else:
                reward=2
            self.fog_gateway.get_clus_heads()[action].set_fog_cpu_util(tmp_ch_util+deadline_task)
            print("Cluster Head is a good one and in a range of fog gateway after predicted positon::",action,"::::",self.fog_gateway.get_clus_heads()[action].get_fog_cpu_util())

        self.iteration-=1
        
        #iteration for each episode
        if self.iteration<=0:
            done=True
        else:
            done=False

        #Update all the vehicles CPU utilization (noise of cpu utilization)
        for x in range(len(self.fog_gateway.get_clus_heads())):
            tmp_cpu_util=self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util()
            if tmp_cpu_util>=99:
                self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util((tmp_cpu_util-1))
            elif tmp_cpu_util<=60:
                self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util((tmp_cpu_util+1))
            else:
                self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util((tmp_cpu_util+random.randint(-1,1)))

        #For ClusterHeads CPU_util
        self.chs_cpu_util=[]
        for x in range(len(self.fog_gateway.get_clus_heads())):
            self.chs_cpu_util.append(self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util())

        #next state of another task workload
        self.fog_gateway.set_task_workload(random.randint(11,15))
        self.fog_gateway.set_dead_task(self.fog_gateway.get_task_workload()-10)
        self.chs_cpu_util.append(self.euclidean(future_pos_ch, self.fog_gateway.get_position()))
        self.chs_cpu_util.append(self.fog_gateway.get_task_workload())
        self.state=self.chs_cpu_util

        #Set placeholder for info
        info={}
        return self.state, reward, done, info

    #going to visualize or not
    def render(self,ep_reward,total_num,label):
        x_axis=[]
        y_axis=ep_reward
        for x in range(0,total_num):
            x_axis.append((x+1))

        #plotting the points
        plt.plot(x_axis,y_axis,label="Deep Q Network without prediction")

        #naming the x axis
        plt.xlabel('No. of Tasks')
        #naming the y axis
        plt.ylabel(label)

        #giving a title
        plt.title("Testing")

        #function to show the plot
        plt.show()
    
    #rest the environment
    def reset(self):

        #reset the fog gateway
        self.reset_cluster_heads_cpu_util()

        #For ClusterHeads CPU_util
        self.chs_cpu_util=[]
        for x in range(len(self.fog_gateway.get_clus_heads())):
            self.chs_cpu_util.append(self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util())
        
        #reset state of fog_gateway
        self.chs_cpu_util.append(0)
        self.chs_cpu_util.append(self.fog_gateway.get_task_workload())
        self.state=self.chs_cpu_util
        
        self.iteration=100
        return self.state

    #Manhattan distance
    def manhattan(self, clu_head, veh):
        return sum(abs(val1-val2) for val1, val2 in zip(clu_head, veh))
    
    #Euclidean distance
    def euclidean(self, veh, fg):
        return ((((veh[0]-fg[0])**2)+((veh[1]-fg[1])**2))**0.5)

    #Create Cluster
    def create_cluster(self,clu_head,fg):
        clus_members=[] 
        for x in range(len(self.normal_vehs)):
            dist_ch=self.manhattan(clu_head.get_veh().get_position(), self.normal_vehs[x].get_vehicle().get_position())
            dist_fg=self.manhattan(fg.get_position(), self.normal_vehs[x].get_vehicle().get_position())
            self.normal_vehs[x].get_vehicle().set_dist_ch(dist_ch)
            self.normal_vehs[x].get_vehicle().set_dist_fg(dist_fg)
           
            if(len(clus_members)<2):
                clus_members.append(self.normal_vehs[x])
            else:
                if(dist_ch<=clus_members[0].get_vehicle().get_dist_ch()):
                    if(dist_ch<=clus_members[1].get_vehicle().get_dist_ch()):
                        if(clus_members[0].get_vehicle().get_dist_ch() < clus_members[1].get_vehicle().get_dist_ch()):
                            clus_members[1]=self.normal_vehs[x]
                        else:
                            clus_members[0]=self.normal_vehs[x]
                    else:
                        clus_members[0]=self.normal_vehs[x]
                elif(dist_ch<=clus_members[1].get_vehicle().get_dist_ch()):
                    clus_members[1]=self.normal_vehs[x]

        #set the cluster member in selected cluster head      
        clu_head.set_clu_mem(clus_members)
        return clu_head

    def random_position(self,pos,dir):
        if(pos[0]==0 or pos[1]==0):
            pos,dir=self.random_position(np.array([random.randint(-150,150),random.randint(-150,150)]),dir)
        elif(pos[0]<=3 and pos[0]>=-3):
            if(pos[0]>0):
                dir='N'
            else:
                dir='S'
            pos[1]=random.randint(-150,150)
        elif(pos[1]<=3 and pos[1]>=-3):
            if(pos[1]>0):
                dir='W'
            else:
                dir='E'
            pos[0]=random.randint(-150,150)
        else:
            pos,dir=self.random_position(np.array([random.randint(-150,150),random.randint(-150,150)]),dir)

        return pos,dir

    def normal_vehicle_array(self):
        cm_array=[]
        for index in range(100):
            velocity=random.randint(2,6)
            position, direction= self.random_position(np.array([random.randint(-150,150),random.randint(-150,150)]),'')
            #VEHICLE PARA (velocity, direction, dist_ch, dist_fg, position)
            vh=Vehicle(velocity,direction,1500,10, position)
            core=random.choice([4,8])
            ram=random.choice([8,16])
            cpu_util=random.randint(60,99)
            #CLUSTER Member PARA (fog_mips, fog_core, fog_ram, fog_cpu_util, veh)
            cm=ClusterMember(10,core,ram,cpu_util,vh)
            cm_array.append(cm)
        return cm_array

    def cluster_head_array(self):
        ch_array=[]
        for index in range(50):
            velocity=random.randint(2,6)
            position, direction= self.random_position(np.array([random.randint(-150,150),random.randint(-150,150)]),'')
            #VEHICLE PARA (velocity, direction, dist_ch, dist_fg, position)
            vh=Vehicle(velocity,direction,10,10, position)
            core=random.choice([4,8])
            ram=random.choice([8,16])
            cpu_util=random.randint(60,99)
            #CLUSTER HEAD PARA (fog_mips, fog_core, fog_ram, fog_cpu_util, veh, clu_mem)
            ch=PublicTransportation(10,core,ram,cpu_util,vh, [])
            ch_array.append(ch)
        return ch_array

    def set_fog_gateway(self):
        clus_heads=self.cluster_head_array()
        trans_range=random.choice([200,200])
        task_workload=random.randint(11,15)
        deadline_task=task_workload-10
        fg_pos= self.fg_position(np.array([random.randint(-50,50),random.randint(-50,50)]))
        task_pos= np.array([random.randint(-150,150),random.randint(-150,150)])
        #FOG_GATEWAY PARA (trans_range, task_workload,task_position, dead_task, clus_heads, position)
        fg=FogGateway(trans_range, task_workload, task_pos, deadline_task, clus_heads, fg_pos)
        return fg

    def fg_position(self,pos):
        if((pos[0]<=20 and pos[0]>=-20)or(pos[1]<=20 and pos[1]>=-20)):
            pos=self.fg_position(np.array([random.randint(-50,50),random.randint(-50,50)]))
        return pos
    