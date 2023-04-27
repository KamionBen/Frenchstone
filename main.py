## Lanceur de la simulation Hearthstone

# Import & Utils
from classes import *
from cartes import *
from copy import deepcopy
from tabulate import tabulate

""" Générateur de parties aléatoires """
nbre_parties_simul = 1  # combien de partie jouer
i = 0
victoires_j1 = 0
victoires_j2 = 0
while i < nbre_parties_simul:

    """ Choix des classes et des pseudos des joueurs """
    mon_plateau = Plateau("Mage", "Smaguy", "Chasseur", "KamionBen")
    while not(mon_plateau.pv_actuels_joueur1 <= 0 or mon_plateau.pv_actuels_joueur2 <= 0):
        if mon_plateau.tour_de_jeu == 1:
            ## On choisit une carte au hasard à jouer si on a le mana pour
            cartes_jouables = [x for x in all_cartes if x.cout <= mon_plateau.mana_dispo_joueur1]
            carte_a_jouer = deepcopy(random.choice(cartes_jouables)) if len(cartes_jouables) != 0 else ""

            # On ne peut attaquer que si notre héros a de l'attaque ou qu'un serviteur pouvant attaquer est présent sur le plateau
            serv_pvnt_attaquer = [x for x in mon_plateau.serviteurs_joueur1 if x.atq_restante != 0]
            if mon_plateau.attaque_joueur1 != 0:
                attaquant = random.choice(["heros"] + serv_pvnt_attaquer)
            else:
                try:
                    attaquant = random.choice(serv_pvnt_attaquer)
                except:
                    attaquant = ""
            cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur2)
        else:
            ## On choisit une carte au hasard à jouer si on a le mana pour
            cartes_jouables = [x for x in all_cartes if x.cout <= mon_plateau.mana_dispo_joueur2]
            carte_a_jouer = deepcopy(random.choice(cartes_jouables)) if len(cartes_jouables) != 0 else ""

            # On ne peut attaquer que si notre héros a de l'attaque ou qu'un serviteur pouvant attaquer est présent sur le plateau
            serv_pvnt_attaquer = [x for x in mon_plateau.serviteurs_joueur2 if x.atq_restante != 0]
            if mon_plateau.attaque_joueur2 != 0:
                attaquant = random.choice(["heros"] + serv_pvnt_attaquer)
            else:
                try:
                    attaquant = random.choice(serv_pvnt_attaquer)
                except:
                    attaquant = ""
            cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur1)
        mon_plateau = RandomOrchestrator(mon_plateau).tour_au_hasard(carte_a_jouer, attaquant, cible)
        if mon_plateau.pv_actuels_joueur1 <= 0:
            victoires_j2 += 1
        if mon_plateau.pv_actuels_joueur2 <= 0:
            victoires_j1 += 1
    print(i)
    i += 1

""" Affichage des résultats """
print(tabulate(logs_hs, headers='keys'))
# print(f"Victoires J1 : {victoires_j1}")
# print(f"Victoires J2 : {victoires_j2}")