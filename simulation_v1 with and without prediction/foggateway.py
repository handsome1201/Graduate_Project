from clusterhead import PublicTransportation
from vehicle import Vehicle
import random
class FogGateway:
    def __init__(self, trans_range, task_workload, task_position, dead_task, clus_heads, position):
        self.trans_range=trans_range
        self.task_workload=task_workload
        self.task_position=task_position
        self.dead_task=dead_task
        self.clus_heads=clus_heads
        self.position=position
        self.pred_pos=self.predict_pos_clus_heads()
    
    def set_position(self,position):
        self.position=position
    
    def get_position(self):
        return self.position
    
    def set_task_position(self,task_position):
        self.task_position=task_position

    def get_task_position(self):
        return self.task_position

    def set_trans_range(self,trans_range):
        self.trans_range=trans_range
    
    def get_trans_range(self):
        return self.trans_range

    def set_pred_pos(self,pred_pos):
        self.pred_pos=pred_pos
    
    def get_pred_pos(self):
        return self.pred_pos

    def set_task_workload(self,task_workload):
        self.task_workload=task_workload
    
    def get_task_workload(self):
        return self.task_workload

    def set_dead_task(self,dead_task):
        self.dead_task=dead_task
    
    def get_dead_task(self):
        return self.dead_task

    def set_clus_heads(self,clus_heads):
        self.clus_heads=clus_heads
    
    def get_clus_heads(self):
        return self.clus_heads

    def predict_pos_clus_heads(self):
        pred_pos=[]
        for veh in self.clus_heads:
            v=veh.get_veh()
            pred_pos.append(v.predict_position(self.dead_task))
        return pred_pos

    
