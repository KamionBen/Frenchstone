import numpy as np
import random
import gym
from gym import spaces
from preprocessing import *

dict_actions = {
  0: "passer_tour",
  1: "jouer_carte",
  2: "attaquer"
}
class FrenchstoneEnvironment(gym.Env):
  """ Notre environnement pour le projet d'AI Hearthstone : Frenchstone """
  def __init__(self, data):

    self.data = data
    """ Actions possibles : passer_tour, jouer_carte, attaquer """
    self.action_space = spaces.Discrete(3)

    """ Vecteur d'état : les différents attributs du plateau sont compris entre 0 et 100 """
    self.observation_space = spaces.Box(low = 0, high = 100, shape = (1, self.data.shape[1]))
    self.state = data.loc[random.randint(0, self.data.shape[1])].values

    """ Nombre de pas à réaliser"""
    self.nb_steps = 50

  def step(self, action):
    """ Calcul de l'état choisi aléatoirement """
    obs = random.randint(0, self.data.shape[1])
    self.state = self.data.loc[obs].values

    """ Un pas en moins """
    self.nb_steps -= 1

    """ Calcul de la récompense """
    if dict_actions[action] != df_action.loc[obs].values[0]:
      reward = 0
    else:
      reward = df_reward.loc[obs].values[0]

    """ On regarde si on a terminé """
    if self.nb_steps <= 0 :
      done = True
    else:
      done = False

    return self.state, reward, done

  def reset(self):
    """ Revient à un état aléatoire """
    self.state = self.data.loc[random.randint(0, self.data.shape[1])].values

    """ Réinitialise le nombre de pas à réaliser"""
    self.nb_steps = 50
    return self.state

env = FrenchstoneEnvironment(df_state)


episodes = 10
for episode in range(1, episodes + 1):
  state = env.reset()
  done = False
  score = 0

  while not done:
    action = env.action_space.sample()
    n_state, reward, done = env.step(action)
    score += reward
  print('Episode:{} Score:{}'.format(episode, score))