## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *

# total_games = 50000

""" Générateur de parties aléatoires """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs, score = Orchestrator().generate_random_game(15000, players)
#
""" Générateur de partie random vs ia """
players = [Player("Random", "Mage"), Player("IA", "Chasseur")]
logs_hs_randomia, score_randomia = Orchestrator().generate_randomvsia_game(15000, players)

""" Générateur de parties avec le modèle """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs_ia, score_ia = Orchestrator().generate_ia_game(15000, players)

# """ Concaténation des différentes sources """
# logs_hs = pd.concat([logs_hs, logs_hs_randomia, logs_hs_ia]).reset_index().drop('index', axis=1)

""" Affichage des résultats """
# print(logs_hs_randomia.to_string())
print(score_randomia)

""" Sauvegarde des logs """
# os.remove('modelisation/logs_games.pickle')
# with open('modelisation/logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs, f)
