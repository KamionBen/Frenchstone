## Lanceur de la simulation Hearthstone

# Import & Utils
from classes import *
from cartes import *
from copy import deepcopy
from tabulate import tabulate

mon_plateau = Plateau("Mage", "Smaguy", "Chasseur", "KamionBen")

while not(mon_plateau.pv_actuels_joueur1 <= 0 or mon_plateau.pv_actuels_joueur2 <= 0):
    ## On choisit des cartes au hasard à jouer, ou pour attaquer
    carte_a_jouer = deepcopy(random.choice(all_cartes))
    if mon_plateau.tour_de_jeu == 1:
        # On ne peut attaquer que si notre héros a de l'attaque ou qu'un serviteur est présent sur le plateau
        if mon_plateau.attaque_joueur1 != 0:
            attaquant = random.choice(["heros"] + mon_plateau.serviteurs_joueur1)
        else:
            try:
                attaquant = random.choice(mon_plateau.serviteurs_joueur1)
            except:
                attaquant = ""
        cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur2)
    else:
        # On ne peut attaquer que si notre héros a de l'attaque ou qu'un serviteur est présent sur le plateau
        if mon_plateau.attaque_joueur2 != 0:
            attaquant = random.choice(["heros"] + mon_plateau.serviteurs_joueur2)
        else:
            try:
                attaquant = random.choice(mon_plateau.serviteurs_joueur2)
            except:
                attaquant = ""
        cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur1)
    mon_plateau = RandomOrchestrator(mon_plateau).tour_au_hasard(carte_a_jouer, attaquant, cible)

print(tabulate(logs_hs, headers='keys'))