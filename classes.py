""" Les différentes classes utilisées pour la simulation """

""" Imports """
import random
from init_variables import *
from random import shuffle
from Entities import *
from copy import deepcopy

""" Décrit exhaustivement le plateau de jeu """
class Plateau:
    def __init__(self, classe_joueur1, pseudo_joueur1, classe_joueur2, pseudo_joueur2):
        """ Initialisation du plateau au tour 0"""
        """ Caractéristiques joueurs """
        class_files = {'Chasseur': 'test_deck.csv',
                       'Mage': 'test_deck.csv'}

        """ Choix au hasard du joueur qui commence"""
        self.player1 = random.choice([Player(pseudo_joueur1, classe_joueur1), Player(pseudo_joueur2, classe_joueur2)])
        self.player2 = Player(pseudo_joueur2, classe_joueur2) if self.player1.name == Player(pseudo_joueur1, classe_joueur1).name else Player(pseudo_joueur1, classe_joueur1)

        """ Importation des decks de chaque joueur """
        self.player1.set_deck(class_files[self.player1.classe])
        self.player2.set_deck(class_files[self.player2.classe])

        """ Gestion du mana """
        self.mana_max_joueur1 = 1
        self.mana_max_joueur2 = 0
        self.mana_dispo_joueur1 = 1
        self.mana_dispo_joueur2 = 0
        self.surcharge_joueur1 = 0
        self.surcharge_joueur2 = 0

        """ Points de vie """
        self.pv_max_joueur1 = 30
        self.pv_max_joueur2 = 30
        self.pv_actuels_joueur1 = 30
        self.pv_actuels_joueur2 = 30

        """ Cartes en main """
        self.cartes_joueur1 = 0
        self.cartes_joueur2 = 0

        """ Pouvoir héroïque """
        self.dispo_pouvoir_hero_joueur1 = True
        self.dispo_pouvoir_hero_joueur2 = True
        self.cout_pouvoir_hero_joueur1 = 2
        self.cout_pouvoir_hero_joueur2 = 2
        self.effet_pouvoir_hero_joueur1 = None
        self.effet_pouvoir_hero_joueur2 = None

        """ Serviteurs posés """
        self.serviteurs_joueur1 = []
        self.serviteurs_joueur2 = []

        """ Attaque et arme des héros """
        self.arme_joueur1 = False
        self.arme_joueur2 = False
        self.attaque_joueur1 = 0
        self.attaque_joueur2 = 0
        self.durabilite_joueur1 = 0
        self.durabilite_joueur2 = 0

        """ Tour de jeu """
        self.tour_de_jeu = 1

    """ Met à jour le plateau à la fin du tour d'un joueur """
    def tour_suivant(self):
        self.tour_de_jeu = 3 - self.tour_de_jeu  # alterne entre 1 et 2

        if self.tour_de_jeu == 1:

            # Réinitialisation du mana et du pouvoir héroïque
            self.player1.start_turn()

            self.mana_max_joueur1 = min(self.mana_max_joueur1 + 1, 10)
            self.mana_dispo_joueur1 = self.mana_max_joueur1 - self.surcharge_joueur1
            self.surcharge_joueur1 = 0
            self.dispo_pouvoir_hero_joueur1 = True
            self.cartes_joueur1 += 1

            # Réinitialisation de l'attaque des seviteurs présents sur le plateau
            for serviteur in self.serviteurs_joueur1:
                serviteur.remaining_atk = 1

        else:
            # Réinitialisation du mana et du pouvoir héroïque
            self.mana_max_joueur2 = min(self.mana_max_joueur2 + 1, 10)
            self.mana_dispo_joueur2 = self.mana_max_joueur2 - self.surcharge_joueur2
            self.surcharge_joueur1 = 0
            self.dispo_pouvoir_hero_joueur2 = True
            self.cartes_joueur2 += 1

            # Réinitialisation de l'attaque des seviteurs présents sur le plateau
            for serviteur in self.serviteurs_joueur2:
                serviteur.remaining_atk = 1


### Classe prenant en entrée un plateau de jeu et permettant d'effectuer toutes les actions possibles dessus.
class TourEnCours:
    def __init__(self, plateau):
        self.plateau = plateau

    ## Action de poser une carte depuis la main du joueur dont c'est le tour.
    ## Le plateau est mis à jour en conséquence
    def jouer_carte(self, carte):
        if self.plateau.tour_de_jeu == 1:
            if carte.cost <= self.plateau.mana_dispo_joueur1:
                if carte.type == "sort":
                    self.plateau.cartes_joueur1 -= 1
                    self.plateau.mana_dispo_joueur1 -= carte.cost
                elif carte.type == "Serviteur":
                    if len(self.plateau.serviteurs_joueur1) < 7:
                        self.plateau.cartes_joueur1 -= 1
                        self.plateau.mana_dispo_joueur1 -= carte.cost
                        self.plateau.serviteurs_joueur1.append(carte)
        else:
            if carte.cost <= self.plateau.mana_dispo_joueur2:
                if carte.type == "sort":
                    self.plateau.cartes_joueur2 -= 1
                    self.plateau.mana_dispo_joueur2 -= carte.cost
                elif carte.type == "Serviteur":
                    if len(self.plateau.serviteurs_joueur2) < 7:
                        self.plateau.cartes_joueur2 -= 1
                        self.plateau.mana_dispo_joueur2 -= carte.cost
                        self.plateau.serviteurs_joueur2.append(carte)

    ## Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi)
    def attaquer(self, attaquant, cible):
        if self.plateau.tour_de_jeu == 1:
            if (attaquant == "heros" and self.plateau.arme_joueur1 == True) and cible == "heros":
                self.plateau.pv_actuels_joueur2 -= self.plateau.attaque_joueur1
            elif (attaquant == "heros" and self.plateau.arme_joueur1 == True) and cible != "heros":
                self.plateau.pv_actuels_joueur1 -= cible.attack
                cible.health -= self.plateau.attaque_joueur1
                ## Mort de la cible ou de notre propre héros
                if cible.health <= 0:
                    #MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur2 = [serviteur for serviteur in self.plateau.serviteurs_joueur2 if serviteur.PV > 0]
            elif attaquant != "heros" and cible == "heros":
                # Conséquences de l'attaque
                self.plateau.pv_actuels_joueur2 -= attaquant.attack
                attaquant.remaining_atk -= 1
            else:
                # Conséquences de l'attaque
                attaquant.health -= cible.attack
                cible.health -= attaquant.attack
                attaquant.remaining_atk -= 1

                ## Mort de l'attaquant ou/et de la cible
                if cible.health <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur2 = [serviteur for serviteur in self.plateau.serviteurs_joueur2 if
                                                       serviteur.health > 0]
                if attaquant.health <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur1 = [serviteur for serviteur in self.plateau.serviteurs_joueur1 if
                                                       serviteur.health > 0]
        else:
            if (attaquant == "heros" and self.plateau.arme_joueur2 == True) and cible == "heros":
                self.plateau.pv_actuels_joueur1 -= self.plateau.attaque_joueur2
            elif (attaquant == "heros" and self.plateau.arme_joueur2 == True) and cible != "heros":
                self.plateau.pv_actuels_joueur2 -= cible.attack
                cible.health -= self.plateau.attaque_joueur2

                ## Mort de la cible ou de notre propre héros
                if cible.health <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur1 = [serviteur for serviteur in self.plateau.serviteurs_joueur1 if
                                                       serviteur.health > 0]
            elif attaquant != "heros" and cible == "heros":
                # Conséquences de l'attaque
                self.plateau.pv_actuels_joueur1 -= attaquant.attack
                attaquant.remaining_atk -= 1
            else:

                # Conséquences de l'attaque
                attaquant.health -= cible.attack
                cible.health -= attaquant.attack
                attaquant.remaining_atk -= 1

                ## Mort de l'attaquant ou/et de la cible
                if cible.health <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur1 = [serviteur for serviteur in self.plateau.serviteurs_joueur1 if
                                                       serviteur.health > 0]
                if attaquant.health <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur2 = [serviteur for serviteur in self.plateau.serviteurs_joueur2 if
                                                       serviteur.health > 0]

    def fin_du_tour(self):
        self.plateau.tour_suivant()

## L'orchestrateur, qui appelle la classe tourencours pour lui faire effectuer une action aléatoire sur le plateau
class RandomOrchestrator:

    ## On génère une action aléatoire et on la fait jouer par la classe Tourencours
    def tour_au_hasard(self, carte, attaquant, cible, plateau, logs):
        tour_en_cours = TourEnCours(plateau)
        ## On liste les différentes actions possibles pendant un tour
        action_possible = ["Passer_tour", "Jouer_carte", "Attaquer"]
        ## Choix des actions possibles en fonction du plateau
        if carte == -99 : # aucune carte jouable
            action_possible.remove("Jouer_carte")
        if attaquant == -99 :
            action_possible.remove("Attaquer")
        ## On choisit aléatoirement parmi les actions possibles
        action = random.choice(action_possible)
        if action == "Passer_tour":
            ## Génération des logs associés à l'action
            action_line = {
                "action" : "passer_tour",
                "carte_jouee" : "",
                "attaquant": "",
                "attaquant_atq": "",
                "attaquant_pv": "",
                "cible": "",
                "cible_atq": "",
                "cible_pv": "",
                "classe_j" : plateau.player1.classe if plateau.tour_de_jeu == 1 else plateau.player2.classe,
                "classe_adv" : plateau.player2.classe if plateau.tour_de_jeu == 1 else plateau.player1.classe,
                "mana_dispo_j" : plateau.mana_dispo_joueur1 if plateau.tour_de_jeu == 1 else plateau.mana_dispo_joueur2,
                "mana_max_j" : plateau.mana_max_joueur1 if plateau.tour_de_jeu == 1 else plateau.mana_max_joueur2,
                "mana_max_adv" : plateau.mana_max_joueur2 if plateau.tour_de_jeu == 1 else plateau.mana_max_joueur1,
                "surcharge_j" : plateau.surcharge_joueur1 if plateau.tour_de_jeu == 1 else plateau.surcharge_joueur2,
                "surcharge_adv" : plateau.surcharge_joueur2 if plateau.tour_de_jeu == 1 else plateau.surcharge_joueur1,
                "pv_j" : plateau.pv_actuels_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur2,
                "pv_adv" : plateau.pv_actuels_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur1,
                "pv_max_j" : plateau.pv_max_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_max_joueur2,
                "pv_max_adv" : plateau.pv_max_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_max_joueur1,
                "nbre_cartes_j" : plateau.cartes_joueur1 if plateau.tour_de_jeu == 1 else plateau.cartes_joueur2,
                "nbre_cartes_adv" : plateau.cartes_joueur2 if plateau.tour_de_jeu == 1 else plateau.cartes_joueur1,
                "dispo_ph_j" : plateau.dispo_pouvoir_hero_joueur1 if plateau.tour_de_jeu == 1 else plateau.dispo_pouvoir_hero_joueur2,
                "cout_ph_j" : plateau.cout_pouvoir_hero_joueur1 if plateau.tour_de_jeu == 1 else plateau.cout_pouvoir_hero_joueur2,
                "serv1_j" : plateau.serviteurs_joueur1[0].name if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "atq_serv1_j" : plateau.serviteurs_joueur1[0].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "pv_serv1_j" : plateau.serviteurs_joueur1[0].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "serv2_j" : plateau.serviteurs_joueur1[1].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "atq_serv2_j" : plateau.serviteurs_joueur1[1].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "pv_serv2_j" : plateau.serviteurs_joueur1[1].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "serv3_j" : plateau.serviteurs_joueur1[2].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "atq_serv3_j" : plateau.serviteurs_joueur1[2].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "pv_serv3_j" : plateau.serviteurs_joueur1[2].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "serv4_j" : plateau.serviteurs_joueur1[3].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "atq_serv4_j" : plateau.serviteurs_joueur1[3].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "pv_serv4_j" : plateau.serviteurs_joueur1[3].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "serv5_j" : plateau.serviteurs_joueur1[4].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "atq_serv5_j" : plateau.serviteurs_joueur1[4].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "pv_serv5_j" : plateau.serviteurs_joueur1[4].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "serv6_j" : plateau.serviteurs_joueur1[5].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "atq_serv6_j" : plateau.serviteurs_joueur1[5].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "pv_serv6_j" : plateau.serviteurs_joueur1[5].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "serv7_j" : plateau.serviteurs_joueur1[6].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "atq_serv7_j" : plateau.serviteurs_joueur1[6].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "pv_serv7_j" : plateau.serviteurs_joueur1[6].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "serv1_adv" : plateau.serviteurs_joueur2[0].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].name if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "atq_serv1_adv" : plateau.serviteurs_joueur2[0].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "pv_serv1_adv" : plateau.serviteurs_joueur2[0].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "serv2_adv" : plateau.serviteurs_joueur2[1].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "atq_serv2_adv" : plateau.serviteurs_joueur2[1].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "pv_serv2_adv" : plateau.serviteurs_joueur2[1].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "serv3_adv" : plateau.serviteurs_joueur2[2].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "atq_serv3_adv" : plateau.serviteurs_joueur2[2].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "pv_serv3_adv" : plateau.serviteurs_joueur2[2].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "serv4_adv" : plateau.serviteurs_joueur2[3].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "atq_serv4_adv" : plateau.serviteurs_joueur2[3].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "pv_serv4_adv" : plateau.serviteurs_joueur2[3].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "serv5_adv" : plateau.serviteurs_joueur2[4].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "atq_serv5_adv" : plateau.serviteurs_joueur2[4].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "pv_serv5_adv" : plateau.serviteurs_joueur2[4].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "serv6_adv" : plateau.serviteurs_joueur2[5].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "atq_serv6_adv" : plateau.serviteurs_joueur2[5].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "pv_serv6_adv" : plateau.serviteurs_joueur2[5].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "serv7_adv" : plateau.serviteurs_joueur2[6].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "atq_serv7_adv" : plateau.serviteurs_joueur2[6].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "pv_serv7_adv" : plateau.serviteurs_joueur2[6].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "arme_j" : plateau.arme_joueur1 if plateau.tour_de_jeu == 1 else plateau.arme_joueur2,
                "arme_adv" : plateau.arme_joueur2 if plateau.tour_de_jeu == 1 else plateau.arme_joueur1,
                "attaque_j" : plateau.attaque_joueur1 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur2,
                "attaque_adv" : plateau.attaque_joueur2 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur1,
                "durabilite_arme_j" : plateau.durabilite_joueur1 if plateau.tour_de_jeu == 1 else plateau.durabilite_joueur2,
                "durabilite_arme_adv" : plateau.durabilite_joueur2 if plateau.tour_de_jeu == 1 else plateau.durabilite_joueur1,
                "pseudo_j" : plateau.player1.name if plateau.tour_de_jeu == 1 else plateau.player2.name,
                "pseudo_adv": plateau.player2.name if plateau.tour_de_jeu == 1 else plateau.player1.name,
                "victoire" : 0
            }
            logs.loc[len(logs)] = action_line

            ## Action
            tour_en_cours.fin_du_tour()

        elif action == "Jouer_carte":
            ## Génération des logs associés à l'action
            action_line = {
                "action": "jouer_carte",
                "carte_jouee": carte.name,
                "attaquant": "",
                "attaquant_atq": "",
                "attaquant_pv": "",
                "cible": "",
                "cible_atq": "",
                "cible_pv": "",
                "classe_j" : plateau.player1.classe if plateau.tour_de_jeu == 1 else plateau.player2.classe,
                "classe_adv" : plateau.player2.classe if plateau.tour_de_jeu == 1 else plateau.player1.classe,
                "mana_dispo_j" : plateau.mana_dispo_joueur1 if plateau.tour_de_jeu == 1 else plateau.mana_dispo_joueur2,
                "mana_max_j" : plateau.mana_max_joueur1 if plateau.tour_de_jeu == 1 else plateau.mana_max_joueur2,
                "mana_max_adv" : plateau.mana_max_joueur2 if plateau.tour_de_jeu == 1 else plateau.mana_max_joueur1,
                "surcharge_j" : plateau.surcharge_joueur1 if plateau.tour_de_jeu == 1 else plateau.surcharge_joueur2,
                "surcharge_adv" : plateau.surcharge_joueur2 if plateau.tour_de_jeu == 1 else plateau.surcharge_joueur1,
                "pv_j" : plateau.pv_actuels_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur2,
                "pv_adv" : plateau.pv_actuels_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur1,
                "pv_max_j" : plateau.pv_max_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_max_joueur2,
                "pv_max_adv" : plateau.pv_max_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_max_joueur1,
                "nbre_cartes_j" : plateau.cartes_joueur1 if plateau.tour_de_jeu == 1 else plateau.cartes_joueur2,
                "nbre_cartes_adv" : plateau.cartes_joueur2 if plateau.tour_de_jeu == 1 else plateau.cartes_joueur1,
                "dispo_ph_j" : plateau.dispo_pouvoir_hero_joueur1 if plateau.tour_de_jeu == 1 else plateau.dispo_pouvoir_hero_joueur2,
                "cout_ph_j" : plateau.cout_pouvoir_hero_joueur1 if plateau.tour_de_jeu == 1 else plateau.cout_pouvoir_hero_joueur2,
                "serv1_j" : plateau.serviteurs_joueur1[0].name if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "atq_serv1_j" : plateau.serviteurs_joueur1[0].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "pv_serv1_j" : plateau.serviteurs_joueur1[0].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "serv2_j" : plateau.serviteurs_joueur1[1].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "atq_serv2_j" : plateau.serviteurs_joueur1[1].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "pv_serv2_j" : plateau.serviteurs_joueur1[1].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "serv3_j" : plateau.serviteurs_joueur1[2].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "atq_serv3_j" : plateau.serviteurs_joueur1[2].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "pv_serv3_j" : plateau.serviteurs_joueur1[2].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "serv4_j" : plateau.serviteurs_joueur1[3].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "atq_serv4_j" : plateau.serviteurs_joueur1[3].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "pv_serv4_j" : plateau.serviteurs_joueur1[3].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "serv5_j" : plateau.serviteurs_joueur1[4].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "atq_serv5_j" : plateau.serviteurs_joueur1[4].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "pv_serv5_j" : plateau.serviteurs_joueur1[4].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "serv6_j" : plateau.serviteurs_joueur1[5].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "atq_serv6_j" : plateau.serviteurs_joueur1[5].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "pv_serv6_j" : plateau.serviteurs_joueur1[5].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "serv7_j" : plateau.serviteurs_joueur1[6].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "atq_serv7_j" : plateau.serviteurs_joueur1[6].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "pv_serv7_j" : plateau.serviteurs_joueur1[6].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "serv1_adv" : plateau.serviteurs_joueur2[0].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].name if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "atq_serv1_adv" : plateau.serviteurs_joueur2[0].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "pv_serv1_adv" : plateau.serviteurs_joueur2[0].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "serv2_adv" : plateau.serviteurs_joueur2[1].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "atq_serv2_adv" : plateau.serviteurs_joueur2[1].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "pv_serv2_adv" : plateau.serviteurs_joueur2[1].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "serv3_adv" : plateau.serviteurs_joueur2[2].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "atq_serv3_adv" : plateau.serviteurs_joueur2[2].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "pv_serv3_adv" : plateau.serviteurs_joueur2[2].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "serv4_adv" : plateau.serviteurs_joueur2[3].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "atq_serv4_adv" : plateau.serviteurs_joueur2[3].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "pv_serv4_adv" : plateau.serviteurs_joueur2[3].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "serv5_adv" : plateau.serviteurs_joueur2[4].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "atq_serv5_adv" : plateau.serviteurs_joueur2[4].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "pv_serv5_adv" : plateau.serviteurs_joueur2[4].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "serv6_adv" : plateau.serviteurs_joueur2[5].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "atq_serv6_adv" : plateau.serviteurs_joueur2[5].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "pv_serv6_adv" : plateau.serviteurs_joueur2[5].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "serv7_adv" : plateau.serviteurs_joueur2[6].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "atq_serv7_adv" : plateau.serviteurs_joueur2[6].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "pv_serv7_adv" : plateau.serviteurs_joueur2[6].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "arme_j" : plateau.arme_joueur1 if plateau.tour_de_jeu == 1 else plateau.arme_joueur2,
                "arme_adv" : plateau.arme_joueur2 if plateau.tour_de_jeu == 1 else plateau.arme_joueur1,
                "attaque_j" : plateau.attaque_joueur1 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur2,
                "attaque_adv" : plateau.attaque_joueur2 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur1,
                "durabilite_arme_j" : plateau.durabilite_joueur1 if plateau.tour_de_jeu == 1 else plateau.durabilite_joueur2,
                "durabilite_arme_adv" : plateau.durabilite_joueur2 if plateau.tour_de_jeu == 1 else plateau.durabilite_joueur1,
                "pseudo_j": plateau.player1.name if plateau.tour_de_jeu == 1 else plateau.player2.name,
                "pseudo_adv": plateau.player2.name if plateau.tour_de_jeu == 1 else plateau.player1.name,
                "victoire": 0
            }
            logs.loc[len(logs)] = action_line

            ## Action
            tour_en_cours.jouer_carte(carte)

        # On filtre pour n'attaquer que quand c'est légal
        elif action == "Attaquer" and attaquant != "":
            ## Génération des logs associés à l'action
            action_line = {
                "action": "attaquer",
                "carte_jouee": "",
                "attaquant": attaquant.name if attaquant != "heros" else "heros",
                "attaquant_atq": attaquant.attack if attaquant != "heros" else plateau.attaque_joueur1 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur2 if plateau.tour_de_jeu == 2 else -99,
                "attaquant_pv": attaquant.health if attaquant != "heros" else plateau.pv_actuels_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur2 if plateau.tour_de_jeu == 2 else -99,
                "cible": cible.name if cible != "heros" else "heros",
                "cible_atq": cible.attack if cible != "heros" else 0,
                "cible_pv": cible.health if cible != "heros" else plateau.pv_actuels_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur1 if plateau.tour_de_jeu == 2 else -99,
                "classe_j" : plateau.player1.classe if plateau.tour_de_jeu == 1 else plateau.player2.classe,
                "classe_adv" : plateau.player2.classe if plateau.tour_de_jeu == 1 else plateau.player1.classe,
                "mana_dispo_j" : plateau.mana_dispo_joueur1 if plateau.tour_de_jeu == 1 else plateau.mana_dispo_joueur2,
                "mana_max_j" : plateau.mana_max_joueur1 if plateau.tour_de_jeu == 1 else plateau.mana_max_joueur2,
                "mana_max_adv" : plateau.mana_max_joueur2 if plateau.tour_de_jeu == 1 else plateau.mana_max_joueur1,
                "surcharge_j" : plateau.surcharge_joueur1 if plateau.tour_de_jeu == 1 else plateau.surcharge_joueur2,
                "surcharge_adv" : plateau.surcharge_joueur2 if plateau.tour_de_jeu == 1 else plateau.surcharge_joueur1,
                "pv_j" : plateau.pv_actuels_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur2,
                "pv_adv" : plateau.pv_actuels_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_actuels_joueur1,
                "pv_max_j" : plateau.pv_max_joueur1 if plateau.tour_de_jeu == 1 else plateau.pv_max_joueur2,
                "pv_max_adv" : plateau.pv_max_joueur2 if plateau.tour_de_jeu == 1 else plateau.pv_max_joueur1,
                "nbre_cartes_j" : plateau.cartes_joueur1 if plateau.tour_de_jeu == 1 else plateau.cartes_joueur2,
                "nbre_cartes_adv" : plateau.cartes_joueur2 if plateau.tour_de_jeu == 1 else plateau.cartes_joueur1,
                "dispo_ph_j" : plateau.dispo_pouvoir_hero_joueur1 if plateau.tour_de_jeu == 1 else plateau.dispo_pouvoir_hero_joueur2,
                "cout_ph_j" : plateau.cout_pouvoir_hero_joueur1 if plateau.tour_de_jeu == 1 else plateau.cout_pouvoir_hero_joueur2,
                "serv1_j" : plateau.serviteurs_joueur1[0].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "atq_serv1_j" : plateau.serviteurs_joueur1[0].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "pv_serv1_j" : plateau.serviteurs_joueur1[0].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 0 else plateau.serviteurs_joueur2[0].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 0 else -99,
                "serv2_j" : plateau.serviteurs_joueur1[1].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "atq_serv2_j" : plateau.serviteurs_joueur1[1].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "pv_serv2_j" : plateau.serviteurs_joueur1[1].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 1 else plateau.serviteurs_joueur2[1].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 1 else -99,
                "serv3_j" : plateau.serviteurs_joueur1[2].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "atq_serv3_j" : plateau.serviteurs_joueur1[2].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "pv_serv3_j" : plateau.serviteurs_joueur1[2].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 2 else plateau.serviteurs_joueur2[2].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 2 else -99,
                "serv4_j" : plateau.serviteurs_joueur1[3].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "atq_serv4_j" : plateau.serviteurs_joueur1[3].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "pv_serv4_j" : plateau.serviteurs_joueur1[3].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 3 else plateau.serviteurs_joueur2[3].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 3 else -99,
                "serv5_j" : plateau.serviteurs_joueur1[4].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "atq_serv5_j" : plateau.serviteurs_joueur1[4].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "pv_serv5_j" : plateau.serviteurs_joueur1[4].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 4 else plateau.serviteurs_joueur2[4].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 4 else -99,
                "serv6_j" : plateau.serviteurs_joueur1[5].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "atq_serv6_j" : plateau.serviteurs_joueur1[5].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "pv_serv6_j" : plateau.serviteurs_joueur1[5].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 5 else plateau.serviteurs_joueur2[5].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 5 else -99,
                "serv7_j" : plateau.serviteurs_joueur1[6].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "atq_serv7_j" : plateau.serviteurs_joueur1[6].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "pv_serv7_j" : plateau.serviteurs_joueur1[6].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur1) > 6 else plateau.serviteurs_joueur2[6].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur2) > 6 else -99,
                "serv1_adv" : plateau.serviteurs_joueur2[0].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].name if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "atq_serv1_adv" : plateau.serviteurs_joueur2[0].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "pv_serv1_adv" : plateau.serviteurs_joueur2[0].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 0 else plateau.serviteurs_joueur1[0].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 0 else -99,
                "serv2_adv" : plateau.serviteurs_joueur2[1].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "atq_serv2_adv" : plateau.serviteurs_joueur2[1].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "pv_serv2_adv" : plateau.serviteurs_joueur2[1].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 1 else plateau.serviteurs_joueur1[1].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 1 else -99,
                "serv3_adv" : plateau.serviteurs_joueur2[2].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "atq_serv3_adv" : plateau.serviteurs_joueur2[2].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "pv_serv3_adv" : plateau.serviteurs_joueur2[2].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 2 else plateau.serviteurs_joueur1[2].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 2 else -99,
                "serv4_adv" : plateau.serviteurs_joueur2[3].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "atq_serv4_adv" : plateau.serviteurs_joueur2[3].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "pv_serv4_adv" : plateau.serviteurs_joueur2[3].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 3 else plateau.serviteurs_joueur1[3].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 3 else -99,
                "serv5_adv" : plateau.serviteurs_joueur2[4].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "atq_serv5_adv" : plateau.serviteurs_joueur2[4].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "pv_serv5_adv" : plateau.serviteurs_joueur2[4].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 4 else plateau.serviteurs_joueur1[4].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 4 else -99,
                "serv6_adv" : plateau.serviteurs_joueur2[5].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "atq_serv6_adv" : plateau.serviteurs_joueur2[5].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "pv_serv6_adv" : plateau.serviteurs_joueur2[5].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 5 else plateau.serviteurs_joueur1[5].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 5 else -99,
                "serv7_adv" : plateau.serviteurs_joueur2[6].id if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].id if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "atq_serv7_adv" : plateau.serviteurs_joueur2[6].attack if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].attack if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "pv_serv7_adv" : plateau.serviteurs_joueur2[6].health if plateau.tour_de_jeu == 1 and len(plateau.serviteurs_joueur2) > 6 else plateau.serviteurs_joueur1[6].health if plateau.tour_de_jeu == 2 and len(plateau.serviteurs_joueur1) > 6 else -99,
                "arme_j" : plateau.arme_joueur1 if plateau.tour_de_jeu == 1 else plateau.arme_joueur2,
                "arme_adv" : plateau.arme_joueur2 if plateau.tour_de_jeu == 1 else plateau.arme_joueur1,
                "attaque_j" : plateau.attaque_joueur1 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur2,
                "attaque_adv" : plateau.attaque_joueur2 if plateau.tour_de_jeu == 1 else plateau.attaque_joueur1,
                "durabilite_arme_j" : plateau.durabilite_joueur1 if plateau.tour_de_jeu == 1 else plateau.durabilite_joueur2,
                "durabilite_arme_adv" : plateau.durabilite_joueur2 if plateau.tour_de_jeu == 1 else plateau.durabilite_joueur1,
                "pseudo_j": plateau.player1.name if plateau.tour_de_jeu == 1 else plateau.player2.name,
                "pseudo_adv": plateau.player2.name if plateau.tour_de_jeu == 1 else plateau.player1.name,
                "victoire": 0
            }
            logs.loc[len(logs)] = action_line

            ## Action
            if attaquant != "heros": # attaque seulement si le serviteur le peut
                tour_en_cours.attaquer(attaquant, cible)
            elif attaquant == "heros":
                if (plateau.tour_de_jeu == 1 and plateau.attaque_joueur1 != 0) or \
                    (plateau.tour_de_jeu == 2 and plateau.attaque_joueur2 != 0): # n'attaque que si le héros a de l'attaque
                    tour_en_cours.attaquer(attaquant, cible)
        return plateau

    """ Génère un nombre donné de parties et créé les logs associés"""
    def generate_game(self, nb_games, classe_j1, pseudo_j1, classe_j2, pseudo_j2):
        logs_hs = pd.DataFrame(columns=columns_logs)
        i = 0
        victoires_j1 = 0
        victoires_j2 = 0
        """ On simule n parties """
        while i < nb_games:
            logs_inter = pd.DataFrame(columns=columns_logs)
            mon_plateau = Plateau(classe_j1, pseudo_j1, classe_j2, pseudo_j2)
            while not (mon_plateau.pv_actuels_joueur1 <= 0 or mon_plateau.pv_actuels_joueur2 <= 0):
                if mon_plateau.tour_de_jeu == 1:
                    ## On choisit une carte au hasard à jouer si on a le mana pour
                    cartes_jouables = [x for x in mon_plateau.player1.deck if x.cost <= mon_plateau.mana_dispo_joueur1]
                    carte_a_jouer = deepcopy(random.choice(cartes_jouables)) if len(cartes_jouables) != 0 else -99

                    # On ne peut attaquer que si notre héros a de l'attaque ou qu'un serviteur pouvant attaquer est présent sur le plateau
                    serv_pvnt_attaquer = [x for x in mon_plateau.serviteurs_joueur1 if x.remaining_atk != 0]
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
                    cartes_jouables = [x for x in mon_plateau.player2.deck if x.cost <= mon_plateau.mana_dispo_joueur2]
                    carte_a_jouer = deepcopy(random.choice(cartes_jouables)) if len(cartes_jouables) != 0 else -99

                    # On ne peut attaquer que si notre héros a de l'attaque ou qu'un serviteur pouvant attaquer est présent sur le plateau
                    serv_pvnt_attaquer = [x for x in mon_plateau.serviteurs_joueur2 if x.remaining_atk != 0]
                    if mon_plateau.attaque_joueur2 != 0:
                        attaquant = random.choice(["heros"] + serv_pvnt_attaquer)
                    else:
                        try:
                            attaquant = random.choice(serv_pvnt_attaquer)
                        except:
                            attaquant = ""
                    cible = random.choice(["heros"] + mon_plateau.serviteurs_joueur1)
                mon_plateau = RandomOrchestrator().tour_au_hasard(carte_a_jouer, attaquant, cible, mon_plateau, logs_inter)
                if mon_plateau.pv_actuels_joueur1 <= 0:
                    logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == mon_plateau.player2.name, 1, -1)
                    logs_hs = pd.concat([logs_hs, logs_inter]).reset_index().drop('index', axis = 1)
                    victoires_j2 += 1
                if mon_plateau.pv_actuels_joueur2 <= 0:
                    logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == mon_plateau.player1.name, 1, -1)
                    logs_hs = pd.concat([logs_hs, logs_inter]).reset_index().drop('index', axis = 1)
                    victoires_j1 += 1
            i += 1
            print(i)
        return logs_hs, (victoires_j1, victoires_j2)
