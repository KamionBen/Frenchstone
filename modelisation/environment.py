import numpy as np
import random
import gym
from gym import spaces
import pickle

dict_actions = {
  0: "passer_tour",
  1: "jouer_carte",
  2: "attaquer"
}
class FrenchstoneEnvironment(gym.Env):
  """ Notre environnement pour le projet d'AI Hearthstone : Frenchstone """
  def __init__(self, data):

    """ Chargement de nos bases de données """
    self.data = data
    """ Actions possibles : passer_tour, jouer_carte, attaquer """
    self.action_space = spaces.Discrete(3)

    """ Vecteur d'état : les différents attributs du plateau sont compris entre 0 et 100 """
    self.observation_space = spaces.Box(low = 0, high = 100, shape = (1, self.data.shape[1]))
    self.state = data.loc[random.randint(0, self.data.shape[0])].values

    """ Nombre de pas à réaliser"""
    self.nb_steps = 1000

  def step(self, action):
    """ Calcul de l'état choisi aléatoirement """
    obs = random.randint(0, self.data.shape[0] - 1)
    self.state = self.data.loc[obs].values
    real_state = self.data.loc[obs]
    legal_actions = [0]

    """ Un pas en moins """
    self.nb_steps -= 1

    """ Calcul de la récompense """
    """ Ici, on doit déterminer les actions légales en fonction de l'état tiré au hasard """
    """ Peut-on jouer une carte ? """
    for i in range(int(real_state["nbre_cartes_j"])):
      if real_state[f"carte_en_main{i + 1}_cost"] <= real_state["mana_dispo_j"]:
        legal_actions.append(1)
        break
    """ Peut-on attaquer ? """
    for i in range(7):
      if real_state[f"atq_remain_serv{i + 1}_j"] > 0:
        legal_actions.append(2)
        break

    if action == 0:
      reward = 0
    else:
      reward = 1

    # print(action, reward)


    """ On regarde si on a terminé """
    if self.nb_steps <= 0:
      done = True
    else:
      done = False

    info = {}

    # print(f"Ligne observée : {obs}")
    # print(f"Actions possibles : {legal_actions}")
    # print(f"Action choisie : {dict_actions[action]}")
    # print(f"Action BDD : {self.data_action.loc[obs].values[0]}")
    # print(f"Vecteur d'état : {real_state}")
    # print(f"Récompense attendue : {self.data_reward.loc[obs].values[0]}")
    # print(f"Récompense : {reward}")
    # print('---------------------------------------------------------------------')

    return self.state, reward, done, info

  def reset(self):
    """ Revient à un état aléatoire """
    self.state = self.data.loc[random.randint(0, self.data.shape[0])].values

    """ Réinitialise le nombre de pas à réaliser"""
    self.nb_steps = 1000
    return self.state



""" Test maison """
# episodes = 1
# for episode in range(1, episodes + 1):
#   state = env.reset()
#   done = False
#   score = 0
#
#   while not done:
#     action = env.action_space.sample()
#     n_state, reward, done, info = env.step(action)
#     score += reward
#   print('Episode:{} Score:{}'.format(episode, score))