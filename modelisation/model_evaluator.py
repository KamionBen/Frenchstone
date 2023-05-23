## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *
from Entities import *

""" Générateur de parties aléatoires """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs, score = Orchestrator().generate_random_game(1, players)

""" Générateur de partie random vs ia """
# players = [Player("Random", "Mage"), Player("IA", "Chasseur")]
# logs_hs_randomia, score_randomia = Orchestrator().generate_randomvsia_game(1, players)
# logs_hs_randomia['id_partie'] = logs_hs_randomia['id_partie'] + 10000

# """ Générateur de parties avec le modèle contre son prédecesseur """
players = [Player("OldIA", "Mage"), Player("NewIA", "Chasseur")]
logs_hs_oldia, score_oldia = Orchestrator().generate_oldia_game(2, players)


# """ Générateur de parties avec le modèle contre lui-même """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs_ia, score_ia = Orchestrator().generate_ia_game(10000, players, random_toll=0.2)

# """ Affichage des résultats """
print(logs_hs_oldia.to_string())
# print(score_randomia)
# print(score_oldia)



