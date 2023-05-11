import numpy as np
import random
from IPython.display import clear_output
from collections import deque
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from environment import CreateClusEnv
from env_without_prediction import CreateClusEnv_Without_Pred
import matplotlib.pyplot as plt
import pyautogui


# Define the Deep Q-Learning agent
class DQNAgent:
    def __init__(self, state_size=52, action_size=50, learning_rate=0.001, discount_factor=0.99, exploration_rate=0.1, exploration_decay=0.999, batch_size=32):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.batch_size = batch_size
        self.memory = []
        self.model = self._build_model()
        self.target_network=self._build_model()

    def _build_model(self):
        model = Sequential([
            Dense(64, input_dim=self.state_size, activation='relu'),
            Dense(64, activation='relu'),
            Dense(64, activation='relu'),
            Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def alighn_target_model(self):
        self.target_network.set_weights(self.model.get_weights())

    def store(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size)
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])

    def retrain(self):
        if len(self.memory) < self.batch_size:
            return
        samples = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in samples:
            target = self.model.predict(state)
            if done:
                target[0][action] = reward
            else:
                q_next = np.max(self.target_network.predict(next_state)[0])
                target[0][action] = reward + self.discount_factor * q_next
            self.model.fit(state, target, epochs=1, verbose=0)

env_pred=CreateClusEnv()
agent_pred=DQNAgent()

env_without_pred=CreateClusEnv_Without_Pred()
agent_without_pred=DQNAgent(state_size=50)

chs_cpu_util=[]
for x in range(len(env_pred.fog_gateway.get_clus_heads())):
    chs_cpu_util.append(env_pred.fog_gateway.get_clus_heads()[x].get_fog_cpu_util())

env_without_pred.chs_cpu_reset=chs_cpu_util
env_without_pred.reset_cluster_heads_cpu_util()

batch_size=32
num_of_episodes=6
timesteps_per_episode=100

count=0
success_count_pred=0
success_count_without_pred=0

success_rate_pred=[]
success_rate_without_pred=[]


for e in range(0, num_of_episodes):

    #reset the environment
    state_pred=env_pred.reset()
    state_pred=np.reshape(state_pred,[1,52])

    state_without_pred=env_without_pred.reset()
    state_without_pred=np.reshape(state_without_pred,[1,50])
    
    #Initialize variable
    terminated=False
    
    success_count_pred=0
    success_count_without_pred=0
    for timestep in range(timesteps_per_episode):
        #Run Action
        action_pred=agent_pred.act(state_pred)
        next_state_pred, reward_pred, terminated, info_pred= env_pred.step(action_pred)

        action_without_pred=agent_without_pred.act(state_without_pred)
        next_state_without_pred, reward_without_pred, terminated, info_without_pred= env_without_pred.step(action_without_pred)

        if(reward_pred==2 or reward_pred==3):
            success_count_pred+=1

        if(reward_without_pred==2 or reward_without_pred==3):
            success_count_without_pred+=1
            
        print(e,"With Pred::::",success_count_pred,"::::Without Pred::::",success_count_without_pred)

        #next state
        next_state_pred=np.reshape(next_state_pred,[1,52])
        agent_pred.store(state_pred,action_pred, reward_pred, next_state_pred, terminated)
        state_pred=next_state_pred

        next_state_without_pred=np.reshape(next_state_without_pred,[1,50])
        agent_without_pred.store(state_without_pred,action_without_pred,reward_without_pred,next_state_without_pred,terminated)
        state_without_pred=next_state_without_pred

        if terminated:
            agent_pred.alighn_target_model()
            agent_without_pred.alighn_target_model()
            break
        
        if len(agent_pred.memory) > agent_pred.batch_size:
            agent_pred.retrain()

        if len(agent_without_pred.memory) > agent_without_pred.batch_size:
            agent_without_pred.retrain()
        
        #clear_output(wait=True)
        #os.system('cls') 
        pyautogui.hotkey('ctrl', 'k')
      
    success_rate_pred.append((100*success_count_pred)/(timesteps_per_episode))
    success_rate_without_pred.append((100*success_count_without_pred)/(timesteps_per_episode))
    #reset the environment
    state_pred=env_pred.reset()
    state_without_pred=env_without_pred.reset()
    

x_axis=[]
for x in range(0,num_of_episodes):
    x_axis.append((x+1))

#plotting the points
plt.ylim(0,100)
plt.plot(x_axis,success_rate_pred,label="Deep Q Network prediction")
plt.plot(x_axis,success_rate_without_pred,label="Deep Q Network without prediction")
#naming the x axis
plt.xlabel('No. of Tasks')
#naming the y axis
plt.ylabel("Success Rate")
#giving a title
plt.title("Testing")

#function to show the plot
plt.show()