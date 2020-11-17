import numpy as np
import random
import math
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import torch.nn.functional as F
import matplotlib.pyplot as plt

class ReplayMemory:
    """
    Class for storing the reinforcement learning agent's past experience.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []

    def push(self, transition):
        self.memory.append(transition)
        if len(self.memory) > self.capacity:
            del self.memory[0]

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class Network(nn.Module):
    def __init__(self, HIDDEN_LAYER):
        nn.Module.__init__(self)
        self.l1 = nn.Linear(5, HIDDEN_LAYER)
        self.l2 = nn.Linear(HIDDEN_LAYER, 2)

    def forward(self, x):
        x = F.relu(self.l1(x))
        x = self.l2(x)
        return x


class DQN_Agent:
    def __init__(self, EPS_START=0.9, EPS_END=0.05, EPS_DECAY=200, GAMMA=0.9, LR=0.01, HIDDEN_LAYER=10, BATCH_SIZE=30, MEM_CAP=600):
        ### Hyper Parameters ###
        self.EPS_START = EPS_START  # e-greedy threshold start value
        self.EPS_END = EPS_END  # e-greedy threshold end value
        self.EPS_DECAY = EPS_DECAY  # e-greedy threshold decay
        self.GAMMA = GAMMA  # Q-learning discount factor
        self.LR = LR  # NN optimizer learning rate
        self.HIDDEN_LAYER = HIDDEN_LAYER  # NN hidden layer size
        self.BATCH_SIZE = BATCH_SIZE  # Q-learning batch size

        ### DQN Agent Component Objects ###
        self.memory = ReplayMemory(MEM_CAP)
        self.model = Network(self.HIDDEN_LAYER)
        self.optimizer = optim.Adam(self.model.parameters(), self.LR)

        ### House Keeping Variables ###
        self.steps_done = 0
        self.calmness_levels = []

        ### Temporary Variables that Enable the Storage of Past Experience ###
        self.action = None
        self.last_action = None
        self.last_state = None

    def select_action(self, state):
        """
        Function for selecting the next action.
        TAKES: `state`: A numpy array containing the power for the main 5 EEG bands.
        RETURNS: `action`: A straight python int that represents going UP or DOWN for the 
                           modulation value.
        """
        sample = random.random()

        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * \
            math.exp(-1. * self.steps_done / self.EPS_DECAY)


        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                output = self.model(torch.Tensor(state))
                output = output.detach().numpy()
                result = np.where(output == np.amax(output))
                return int(result[0][0])
                
        else: 
            return [random.randint(0,1)]

    def optimize_model(self):
        """
        """
        if len(self.memory) < self.BATCH_SIZE: 
            # Every time the experience gets bigger than BATCH SIZE, we actually 'review' it and learn from it.
            # print('Not enough data in memory to optimize model')
            return

        # random transition batch is taken from experience replay memory
        transitions = self.memory.sample(self.BATCH_SIZE)
        batch_state, batch_action, batch_next_state, batch_reward = zip(*transitions) # Unzipping the list of lists of tensor floats into...
        
        

        batch_state = torch.cat(batch_state) # List of initial states
        batch_action = torch.cat(batch_action) # List of corresponding actions
        batch_reward = torch.cat(batch_reward) # List of corrseponding rewards reaped
        batch_next_state = torch.cat(batch_next_state) # List of corresponding next states

        # current Q values are estimated by NN for all actions
        current_q_values = self.model(batch_state).gather(1, batch_action) # Getting the Q value given by the network for each of the 
                                                                           # initial states and actions

        # expected Q values are estimated from actions which gives maximum Q value
        max_next_q_values = self.model(batch_next_state).detach().max(1)[0] # Getting the maximum Q value for the NEXT state
        expected_q_values = batch_reward + (self.GAMMA * max_next_q_values) # Propagating that Q value back

        # loss is measured from error between current and newly expected Q values
        loss = F.smooth_l1_loss(current_q_values.squeeze(0), expected_q_values)

        # print(current_q_values.size())

        # backpropagation of loss to NN
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.detach().item()

    def run_data(self, in_state):
        """
        TAKES: `in_state` <type list[float]>
        PRODUCES: integer 0 or 1 for left/right
        """
        self.action = self.select_action(in_state)

        self.current_state = in_state

        reward = 0 # Note to self: Ordering of bands is alpha, low beta, high beta, gamma, and theta (5)
        
        if self.last_state != None:
            d_theta = self.current_state[4] - self.last_state[4]
            d_low_beta = self.current_state[1] - self.last_state[1]
            d_high_beta = self.current_state[2] - self.last_state[2]
            d_alpha = self.current_state[0] - self.last_state[0]

            # A 'better' brain state is characterized by higher alpha and lower beta, theta bands.
            reward = d_alpha - 0.5*(d_low_beta + d_high_beta) - d_theta
        else:
            self.last_state = self.current_state
            self.last_action = self.action

        self.memory.push((
            torch.FloatTensor([self.last_state]),
            torch.LongTensor([[self.last_action]]),
            torch.FloatTensor([self.current_state]),
            torch.FloatTensor([reward])
        ))

        self.last_state = self.current_state
        self.last_action = self.action

        loss = self.optimize_model()

        self.steps_done += 1

        if(self.steps_done % 100 == 0):
            print('Finished training step {}'.format(self.steps_done))

        return self.action, reward, loss

        