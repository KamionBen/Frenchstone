## Lanceur de la simulation Hearthstone

# Import & Utils
from classes import *
from tabulate import tabulate
import pickle

""" Générateur de parties aléatoires """
RandomOrchestrator().generate_game(1, "Mage", "Smaguy", "Chasseur", "KamionBen")

""" Affichage des résultats """
print(tabulate(logs_hs, headers='keys'))

""" Sauvegarde des logs """
# with open('logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs, f)