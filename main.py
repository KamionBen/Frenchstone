## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *
import pickle
import os

""" Générateur de parties aléatoires """
players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
logs_hs, score = RandomOrchestrator().generate_game(10000, players)

""" Affichage des résultats """
# print(logs_hs.to_string())
print(score)

""" Sauvegarde des logs """
# os.remove('modelisation/logs_games.pickle')
# with open('modelisation/logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs, f)