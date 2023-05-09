from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import matplotlib.pyplot as plt

import data_state

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
        self.chs_cpu_reset=list(self.cluster_heads_cpu_util(self.fog_gateway)) #w자동차 초기 CPU 사용률 list에 저장
        self.normal_vehs=self.normal_vehicle_array() #자동차 저장될 배열

        #Fog Gateway 객체의 각 자동차의 현재 CPU 사용률을 가져와서 self.chs_cpu_util 속성에 저장
        #이후의 프로세스에서 자동차의 CPU 사용률 추적
        self.chs_cpu_util=[]
        for x in range(len(self.fog_gateway.get_clus_heads())):
            self.chs_cpu_util.append(self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util()) #자동차 cpu 값들 chs_cpu_util에 저장

        #Actions that we can take 
        self.action_space=list(range(0, 50)) #자동차가 이동할 수 있는 거리

        #set start state of fog_gateway
        self.chs_cpu_util.append(0)
        self.chs_cpu_util.append(self.fog_gateway.get_task_workload())
        self.state=self.chs_cpu_util

        self.iteration=100 #시뮬레이션 반복 횟수

    #run whenever you take a step within your environment
    #With Prediciton of future position
    def step(self, action):
        #Action will be selected cluster head
        self.fog_gateway.get_clus_heads()[action]=self.create_cluster(self.fog_gateway.get_clus_heads()[action], self.fog_gateway)
        clu_mem=self.fog_gateway.get_clus_heads()[action].get_clu_mem()
        
        #자동차의 현재 위치와 미래 위치를 설정
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

            """
            선택된 클러스터 헤드의 위치가 Fog Gateway 객체의 전송 범위를 벗어나면, reward는 -3으로 설정
            선택된 자동차가 Fog Gateway 객체와 통신을 수행할 수 없으므로, 해당 선택은 부정적
            선택된 클러스터 헤드의 미래 위치가 Fog Gateway 객체의 전송 범위를 벗어나면, reward는 -1으로 설정
            선택된 자동차가가 미래에는 Fog Gateway 객체와 통신을 수행할 수 없을 가능성이 있으므로, 해당 선택은 애매한 영향
            선택된 클러스터 헤드의 메모리 사용량이 90%를 초과
            만약 클러스터의 다른 노드의 CPU 사용률이 90% 이하인 경우, reward는 -1으로 설정
            선택된 자동차는 과부하 상태이지만, 클러스터 전체의 성능은 개선될 가능성이 있음
            만약 클러스터의 다른 노드의 CPU 사용률이 90%를 초과하는 경우, reward는 -2로 설정
            선택된 자동차가 과부하 상태이며, 클러스터 전체의 성능은 개선될 가능성이 없다는 것을 의미
            """

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


        """
        self.chs_cpu_util 리스트에서 가장 작은 값을 가진 CPU 사용률과 비교하여, 
        현재 선택한 자동차의 CPU 사용률이 가장 작은 경우 reward 값을 3으로, 그렇지 않은 경우 reward 값을 2로 설정
        선택한 자동차의 CPU 사용률에 현재 작업량를 더하여 업데이트하고, 해당 자동차의 CPU 사용률을 출력
        """
        
        #iteration for each episode
        if self.iteration<=0:
            done=True
        else:
            done=False

        "현재 실행하고 있는 학습(100회 모델 반복)가 끝났는지 확인하는 데 사용"

        #Update all the vehicles CPU utilization (noise of cpu utilization)
        for x in range(len(self.fog_gateway.get_clus_heads())):
            tmp_cpu_util=self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util()
            if tmp_cpu_util>=99:
                self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util((tmp_cpu_util-1))
            elif tmp_cpu_util<=60:
                self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util((tmp_cpu_util+1))
            else:
                self.fog_gateway.get_clus_heads()[x].set_fog_cpu_util((tmp_cpu_util+random.randint(-1,1)))


        """
        클러스터 헤드들의 CPU 사용률을 업데이트
        각 자동차의 CPU 사용률을 가져오고, 
        현재 사용률이 99 이상이면 1을 뺀 값으로 설정 
        60 이하이면 1을 더한 값으로 설정
        그 외에는 무작위로 -1, 0, 1 중 하나를 더하여 값을 설정
        자동차의 CPU 사용률이 일정 범위에서 변동함으로써 더 현실적인 상황을 모델링
        """

        #For ClusterHeads CPU_util
        self.chs_cpu_util=[]
        for x in range(len(self.fog_gateway.get_clus_heads())):
            self.chs_cpu_util.append(self.fog_gateway.get_clus_heads()[x].get_fog_cpu_util())


        """
        현재 시점에서의 자동차의 CPU utilization 값을 self.chs_cpu_util 리스트에 저장
        """

        #next state of another task workload
        self.fog_gateway.set_task_workload(random.randint(11,15))
        self.fog_gateway.set_dead_task(self.fog_gateway.get_task_workload()-10)
        self.chs_cpu_util.append(self.euclidean(future_pos_ch, self.fog_gateway.get_position()))
        self.chs_cpu_util.append(self.fog_gateway.get_task_workload())
        self.state=self.chs_cpu_util


        """
        다음 상태를 계산하기 위해 현재 자동차의 CPU 이용률과 작업량 랜덤으로 설정
        자동차와 기준점 간의 거리 및 다음 자동차의 CPU 이용률을 계산
        """

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


    """
    리워드 시각화
    """


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

    """
    두 점 사이의 가로방향과 세로방향 거리
    """

    #Euclidean distance
    def euclidean(self, veh, fg):
        return ((((veh[0]-fg[0])**2)+((veh[1]-fg[1])**2))**0.5)

    """
    자동차와 기준점 사이의 거리 피타고라스 정리 사용하여 계산
    """

    #Create Cluster
    def create_cluster(self,clu_head,fg):
        clus_members=[] 
        for x in range(len(self.normal_vehs)):
            dist_ch=self.manhattan(clu_head.get_veh().get_position(), self.normal_vehs[x].get_vehicle().get_position())
            dist_fg=self.manhattan(fg.get_position(), self.normal_vehs[x].get_vehicle().get_position())
            self.normal_vehs[x].get_vehicle().set_dist_ch(dist_ch)
            self.normal_vehs[x].get_vehicle().set_dist_fg(dist_fg)

            """
            차량과 기준점과의 거리를 계산하여 저장
            """

            if(len(clus_members)<2): #clus_members 리스트에 속한 차량들 중 가장 가까운 대표 차량(clu_head)과 가까운 차량들을 clus_members 리스트 내에서 찾아내는 데 사용
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


            '''
            clus_members 리스트에 속한 차량들 중 가장 가까운 차량과 가까운 차량들을 clus_members 리스트 내에서 찾아내는 데 사용
            '''

        #set the cluster member in selected cluster head      
        clu_head.set_clu_mem(clus_members) #최적인 차량 반환
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

        return pos,dir #현재 위치(pos)와 방향(dir)을 인자로 받아 새로운 위치와 방향을 반환 자동차 위치 값 랜덤 생성

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
        return cm_array #랜덤한 자동차 100개 생성

    def cluster_head_array(self):
        ch_array=[]
        size = len(data_state.result_list)
        for index in range(size):
            velocity =2 #data_state.result_list.pop()
            position, direction = self.random_position(np.array([random.randint(-150, 150), random.randint(-150, 150)]),
                                                       '')
            # VEHICLE PARA (velocity, direction, dist_ch, dist_fg, position)
            vh = Vehicle(velocity, direction, 10, 10, position)
            core = random.choice([4, 8])
            ram = random.choice([8, 16])
            cpu_util = random.randint(60, 99)
            # CLUSTER HEAD PARA (fog_mips, fog_core, fog_ram, fog_cpu_util, veh, clu_mem)
            ch = PublicTransportation(10, core, ram, cpu_util, vh, [])
            ch_array.append(ch)
        return ch_array #랜덤한 위치와 속도를 가지는 클러스터 헤드를 50개 생성(요기를 수정해야해)

    def set_fog_gateway(self):
        clus_heads=self.cluster_head_array()
        trans_range=random.choice([200,200])
        task_workload=random.randint(11,15)
        deadline_task=task_workload-10
        fg_pos= self.fg_position(np.array([random.randint(-50,50),random.randint(-50,50)]))
        task_pos= np.array([random.randint(-150,150),random.randint(-150,150)])
        #FOG_GATEWAY PARA (trans_range, task_workload,task_position, dead_task, clus_heads, position)
        fg=FogGateway(trans_range, task_workload, task_pos, deadline_task, clus_heads, fg_pos)
        return fg #특정 범위 내의 차량들로부터 수집된 데이터를 수집, 처리, 저장

    def fg_position(self,pos):
        if((pos[0]<=20 and pos[0]>=-20)or(pos[1]<=20 and pos[1]>=-20)):
            pos=self.fg_position(np.array([random.randint(-50,50),random.randint(-50,50)]))
        return pos #기준점의 위치를 랜덤으로 지정
    