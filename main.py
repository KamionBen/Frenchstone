## Lanceur de la simulation Hearthstone

# Import & Utils
from classes import *
from tabulate import tabulate
import pickle

""" Générateur de parties aléatoires """
logs_hs = RandomOrchestrator().generate_game(2, "Mage", "Smaguy", "Chasseur", "KamionBen")[0]

""" Affichage des résultats """
print(tabulate(logs_hs, headers='keys'))

""" Sauvegarde des logs """
# with open('logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs, f)