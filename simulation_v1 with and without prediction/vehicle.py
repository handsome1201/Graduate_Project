import numpy as np
class Vehicle:
    def __init__(self, velocity, direction, dist_ch, dist_fg, position):
        self.velocity=velocity
        self.direction=direction
        self.dist_ch=dist_ch
        self.dist_fg=dist_fg
        self.position=position
        self.future_pos=self.predict_position(0)

    def get_position(self):
        return self.position

    def set_velocity(self, position):
        self.position=position


    def get_velocity(self):
        return self.velocity

    def set_velocity(self, velocity):
        self.velocity=velocity

    def get_direction(self):
        return self.direction

    def set_direction(self, direction):
        self.direction=direction

    def get_dist_ch(self):
        return self.dist_ch

    def set_dist_ch(self, dist_ch):
        self.dist_ch=dist_ch

    def get_dist_fg(self):
        return self.dist_fg

    def set_dist_fg(self, dist_fg):
        self.dist_fg=dist_fg

    def get_future_pos(self):
        return self.future_pos

    def set_future_pos(self, time):
        self.predict_position(time)
    
    def predict_position(self, time):
        move=time*self.velocity
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




    
