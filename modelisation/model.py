import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Flatten
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from keras.optimizers import Adam
from environment import *

states = env.observation_space.shape
actions = env.action_space.n

def build_model(states, actions):
    model = Sequential()
    model.add(Dense(200, activation='relu', input_shape=states))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    model.add(Flatten())
    return model

def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy, nb_actions=actions, nb_steps_warmup=150, target_model_update=1e-2)
    return dqn

model = build_model(states, actions)

dqn = build_agent(model, actions)
dqn.compile(Adam(lr=5e-4), metrics=['mae'])
dqn.fit(env, nb_steps=150000, visualize=False, verbose=1)