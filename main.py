## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *
import pickle
import os

""" Générateur de parties aléatoires """
players1 = (Player("Pascal", "Mage"), Player("Joseph", "Chasseur"))
logs_hs1, score1 = RandomOrchestrator().generate_game(10000, players1)

players2 = (Player("Joseph", "Chasseur"), Player("Pascal", "Mage"))
logs_hs2, score2 = RandomOrchestrator().generate_game(10000, players2)

logs_hs = pd.concat([logs_hs1, logs_hs2]).reset_index().drop("index", axis = 1)
# score = [sum(x) for x in zip(score1, score2)]

""" Affichage des résultats """
# print(logs_hs.to_string())
print(score1, score2)

""" Sauvegarde des logs """
os.remove('modelisation/logs_games.pickle')
with open('modelisation/logs_games.pickle', 'wb') as f:
    pickle.dump(logs_hs, f)