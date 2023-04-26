## Lanceur de la simulation Hearthstone

# Import & Utils
from classes import *
from cartes import *
from copy import deepcopy

mon_plateau = Plateau("Mage", "Smaguy", "Chasseur", "KamionBen")

while not(mon_plateau.pv_actuels_joueur1 <= 0 or mon_plateau.pv_actuels_joueur2 <= 0):
    ## On choisit des cartes au hasard à jouer, ou pour attaquer
    carte_a_jouer = deepcopy(random.choice(all_cartes))
    if mon_plateau.tour_de_jeu == 1:
        attaquant = random.choice(["heros"] + mon_plateau.serviteurs_joueur1)
        cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur2)
    else:
        attaquant = random.choice(["heros"] + mon_plateau.serviteurs_joueur2)
        cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur1)
    mon_plateau = RandomOrchestrator(mon_plateau).tour_au_hasard(carte_a_jouer, attaquant, cible)

