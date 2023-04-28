## Lanceur de la simulation Hearthstone

# Import & Utils
from classes import *
import pickle

""" Générateur de parties aléatoires """
logs_hs = RandomOrchestrator().generate_game(1, "Mage", "Smaguy", "Chasseur", "KamionBen")[0]

""" Affichage des résultats """
# print(logs_hs.to_string())

""" Sauvegarde des logs """
#with open('modelisation/logs_games.pickle', 'wb') as f:
    #pickle.dump(logs_hs, f)