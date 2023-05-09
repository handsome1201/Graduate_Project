import numpy as np
class Vehicle:
    def __init__(self, velocity, direction, dist_ch, dist_fg, position):
        self.velocity=velocity
        self.direction=direction
        self.dist_ch=dist_ch
        self.dist_fg=dist_fg
        self.position=position
        self.future_pos=self.predict_position(0)

    def get_position(self): #현재 위치 반환
        return self.position

    def set_velocity(self, position): #속도 설정
        self.position=position

    def get_velocity(self): #속도 반환
        return self.velocity

    def set_velocity(self, velocity):
        self.velocity=velocity

    def get_direction(self): #방향 반환
        return self.direction

    def set_direction(self, direction): #방향 설정
        self.direction=direction

    def get_dist_ch(self): #자동차 사이의 거리 반환
        return self.dist_ch

    def set_dist_ch(self, dist_ch): #자동차 사이의 거리 반환
        self.dist_ch=dist_ch

    def get_dist_fg(self): #기준점과 자동차 사이의 거리 반환
        return self.dist_fg

    def set_dist_fg(self, dist_fg): #기준점과 자동차 사이의 거리 설정
        self.dist_fg=dist_fg

    def get_future_pos(self): #예측된 미래의 위치 반환
        return self.future_pos

    def set_future_pos(self, time): #예측된 미래의 위치 설정
        self.predict_position(time)
    
    def predict_position(self, time): #예측 할 시간 후의 위치 예측 및 반환
        move = time*self.velocity
        #print(move)
        if(self.direction=='N'):
            predict_pos=np.array([self.position[0],(self.position[1]+move)])
        elif(self.direction=='S'):
             predict_pos=np.array([self.position[0],(self.position[1]-move)])
        elif(self.direction=='E'):
             predict_pos=np.array([(self.position[0]+move),self.position[1]])
        elif(self.direction=='W'):
             predict_pos=np.array([(self.position[0]-move),self.position[1]])      
        self.future_pos=predict_pos




    
