## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *

""" Générateur de parties aléatoires """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs, score = Orchestrator().generate_random_game(5000, players)
#
""" Générateur de partie random vs ia """
# players = [Player("Random", "Mage"), Player("IA", "Chasseur")]
# logs_hs_randomia, score_randomia = Orchestrator().generate_randomvsia_game(1000, players)

""" Générateur de parties avec le modèle contre son prédecesseur """
# players = [Player("OldIA", "Mage"), Player("NewIA", "Chasseur")]
# logs_hs_oldia, score_oldia = Orchestrator().generate_oldia_game(1000, players)

""" Générateur de parties avec le modèle contre lui-même """
players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
logs_hs_ia, score_ia = Orchestrator().generate_ia_game(10, players)
#
# # """ Concaténation des différentes sources """
# logs_hs = pd.concat([logs_hs_randomia, logs_hs_oldia, logs_hs_ia]).reset_index().drop('index', axis=1)

""" Affichage des résultats """
# print(logs_hs_randomia.to_string())
# print(score_randomia)
# print(score_oldia)

""" Sauvegarde des logs """
os.remove('modelisation/logs_games.pickle')
with open('modelisation/logs_games.pickle', 'wb') as f:
    pickle.dump(logs_hs_ia, f)
