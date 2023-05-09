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

# Define the Deep Q-Learning agent
class DQNAgent:
    def __init__(self, state_size=52, action_size=50, learning_rate=0.001, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.999, batch_size=32):
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
        self.exploration_rate *= self.exploration_decay

env=CreateClusEnv()
agent=DQNAgent()
batch_size=32
num_of_episodes=6
timesteps_per_episode=100
#agent.q_network.summary()
ep_reward=[0]*600
success_rate=[0]*600
rewards=[]
count=0
success_count=0
total_reward=0
for e in range(0, num_of_episodes):

    #reset the environment
    state=env.reset()
    state=np.reshape(state,[1,52])
    
    #Initialize variable
    terminated=False
    
    success_count=0
    for timestep in range(timesteps_per_episode):
        #Run Action
        action=agent.act(state)

        next_state, reward, terminated, info= env.step(action)
        total_reward+=reward
        ep_reward[count]=total_reward
        if(reward==2 or reward==3):
            success_count+=1

        print("Success Count,rewards:::",success_count,reward,len(rewards))
        #success rate
        #success_rate[count]=((100*success_count)/(count+1))
        #print("Success rate:::",success_rate[count],count)

        #next state
        next_state=np.reshape(next_state,[1,52])
        agent.store(state,action, reward, next_state, terminated)
        state=next_state

        print("Next State::",state)

        if terminated:
            agent.alighn_target_model()
            break
        
        if len(agent.memory) > agent.batch_size:
            agent.retrain()
        
        count+=1
       
    rewards.append((100*success_count)/(timesteps_per_episode))

    
    
    #while not terminated_q:
    count+=1

    #reset the environment
    state=env.reset()
    
print("Rewards::::::::::::",rewards)

env.render(rewards,num_of_episodes,"Success Rate(%)")
#env.render(success_rate,1000,"Success Rate(%)")

