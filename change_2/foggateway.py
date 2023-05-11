from clusterhead import PublicTransportation
from vehicle import Vehicle
import random
class FogGateway:
    def __init__(self, trans_range, task_workload, task_position, dead_task, clus_heads, position):
        self.trans_range=trans_range #통신 가능한 최대 거리
        self.task_workload=task_workload #처리해야 할 작업 부하
        self.task_position=task_position
        self.dead_task=dead_task #작업이 완료된 시간
        self.clus_heads=clus_heads #통신 가능한 차량들의 목록
        self.position=position #Fog Gateway의 위치
        self.pred_pos=self.predict_pos_clus_heads() #차량들의 예측 위치
    
    def set_position(self,position): # Fog Gateway의 위치 설정
        self.position=position
    
    def get_position(self): # Fog Gateway의 위치 반환
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

    def predict_pos_clus_heads(self): #자동차 예측 위치 계산
        pred_pos=[]
        for veh in self.clus_heads: #모든 자동차 위치 불러옴
            v=veh.get_veh()
            pred_pos.append(v.predict_position(self.dead_task)) #예측한 위치 배열에 추가
        return pred_pos

    
