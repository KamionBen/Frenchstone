## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *
import pickle

""" Générateur de parties aléatoires """
players = (Player("Pascal", "Mage"), Player("Joseph", "Chasseur"))
logs_hs, score = RandomOrchestrator().generate_game(10, players)

""" Affichage des résultats """
print(logs_hs.to_string())

""" Sauvegarde des logs """
#with open('modelisation/logs_games2.pickle', 'wb') as f:
    #pickle.dump(logs_hs, f)