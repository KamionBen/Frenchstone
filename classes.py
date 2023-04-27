## Les différentes classes utilisées pour la simulation

### Imports
import random
from init_variables import *
from random import shuffle

### La classe plateau permet de décrire l'ensemble des caractéristiques du plateau à un moment donnée de la partie
class Plateau:
    def __init__(self, classe_joueur1, pseudo_joueur1, classe_joueur2, pseudo_joueur2):
        self.classe_joueur1 = classe_joueur1
        self.classe_joueur2 = classe_joueur2
        self.pseudo_joueur1 = pseudo_joueur1
        self.pseudo_joueur2 = pseudo_joueur2
        self.mana_max_joueur1 = 0
        self.mana_max_joueur2 = 0
        self.mana_dispo_joueur1 = 0
        self.mana_dispo_joueur2 = 0
        self.surcharge_joueur1 = 0
        self.surcharge_joueur2 = 0
        self.pv_max_joueur1 = 30
        self.pv_max_joueur2 = 30
        self.pv_actuels_joueur1 = 30
        self.pv_actuels_joueur2 = 30
        self.cartes_joueur1 = 0
        self.cartes_joueur2 = 0
        self.dispo_pouvoir_hero_joueur1 = True
        self.dispo_pouvoir_hero_joueur2 = True
        self.cout_pouvoir_hero_joueur1 = 2
        self.cout_pouvoir_hero_joueur2 = 2
        self.effet_pouvoir_hero_joueur1 = None
        self.effet_pouvoir_hero_joueur2 = None
        self.serviteurs_joueur1 = []
        self.serviteurs_joueur2 = []
        self.arme_joueur1 = False
        self.arme_joueur2 = False
        self.attaque_joueur1 = 0
        self.attaque_joueur2 = 0
        self.durabilite_joueur1 = 0
        self.durabilite_joueur2 = 0
        self.tour_de_jeu = 2

    # méthode tour_suivant, permettant de passer au tour de l'adversaire en mettant à jour le plateau
    def tour_suivant(self):
        self.tour_de_jeu = 3 - self.tour_de_jeu  # alterne entre 1 et 2
        if self.tour_de_jeu == 1:

            # Réinitialisation du mana et du pouvoir héroïque
            self.mana_max_joueur1 = min(self.mana_max_joueur1 + 1, 10)
            self.mana_dispo_joueur1 = self.mana_max_joueur1 - self.surcharge_joueur1
            self.surcharge_joueur1 = 0
            self.dispo_pouvoir_hero_joueur1 = True
            self.cartes_joueur1 += 1

            # Réinitialisation de l'attaque des seviteurs présents sur le plateau
            for serviteur in self.serviteurs_joueur1:
                serviteur.atq_restante = 1
        else:

            # Réinitialisation du mana et du pouvoir héroïque
            self.mana_max_joueur2 = min(self.mana_max_joueur2 + 1, 10)
            self.mana_dispo_joueur2 = self.mana_max_joueur2 - self.surcharge_joueur2
            self.surcharge_joueur1 = 0
            self.dispo_pouvoir_hero_joueur2 = True
            self.cartes_joueur2 += 1

            # Réinitialisation de l'attaque des seviteurs présents sur le plateau
            for serviteur in self.serviteurs_joueur2:
                serviteur.atq_restante = 1



### Classe permettant de décrire exhaustivement une carte
class Carte:
    id = 0
    def __init__(self, nom, type_carte, attaque, PV, cout, atq_restante = 0, ecole="", description=""):
        """ Represent a playing card """
        """ Name & id """
        self.id = Carte.id
        Carte.id += 1
        self.nom = nom

        """ Category """
        self.type = type_carte
        self.ecole = ecole

        """ Stats """
        self.attaque = attaque
        self.PV = PV
        self.cout = cout
        self.atq_restante = atq_restante

        """ Infos """
        self.description = description


    def __eq__(self, other):
        """ Compare la carte avec l'id ou la carte donnée """
        if type(other) == Carte:
            return other.id == self.id
        elif type(other) == int:
            return other == self.id
        elif type(other) == str:
            return False
        else:
            raise ValueError(f"Impossible de comparer la carte avec {other} (type:{type(other)}")

    def __repr__(self):
        return self.nom

class CardGroup:
    def __init__(self, cards=()):
        self.cards = list(cards)
        self.c_dict = {card.id: card for card in cards}

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, item):
        for card in self:
            if card == item:
                return card

    def shuffle(self):
        """ Mélange le groupe de cartes """
        shuffle(self.cards)

    def pick_one(self):
        """ Renvoie la première carte du paquet et la retire du groupe """
        selected = self.cards[0]
        self.cards = self.cards[1:]
        self.reconstruct()
        return selected

    def pick(self, nb):
        """ Renvoie un groupe de 'nb' cartes et les retire du groupe actuel """
        ls = CardGroup()
        while nb > 0:
            ls.add_one(self.pick_one())
            nb -= 1

        return ls

    def add_one(self, card):
        """ Ajoute une carte au groupe """
        self.cards.append(card)
        self.reconstruct()

    def merge(self, other_group):
        """ Fusionne un groupe de cartes avec le groupe actuel """
        for card in other_group:
            self.add_one(card)
        self.reconstruct()

    def reconstruct(self):
        """ Reconstruit le dictionnaire de cartes """
        self.c_dict = {card.id: card for card in self.cards}

    def remove(self, card):
        """ Retire une carte particulière du groupe """
        self.cards.pop(card)
        self.reconstruct()

    def __repr__(self):
        return f"Groupe de {len(self.cards)} cartes"



### Classe prenant en entrée un plateau de jeu et permettant d'effectuer toutes les actions possibles dessus.
class TourEnCours:
    def __init__(self, plateau):
        self.plateau = plateau

    ## Action de poser une carte depuis la main du joueur dont c'est le tour.
    ## Le plateau est mis à jour en conséquence
    def jouer_carte(self, carte):
        if self.plateau.tour_de_jeu == 1:
            if carte.cout <= self.plateau.mana_dispo_joueur1:
                if carte.type == "sort":
                    self.plateau.cartes_joueur1 -= 1
                    self.plateau.mana_dispo_joueur1 -= carte.cout
                elif carte.type == "serviteur":
                    if len(self.plateau.serviteurs_joueur1) < 7:
                        self.plateau.cartes_joueur1 -= 1
                        self.plateau.mana_dispo_joueur1 -= carte.cout
                        self.plateau.serviteurs_joueur1.append(carte)
        else:
            if carte.cout <= self.plateau.mana_dispo_joueur2:
                if carte.type == "sort":
                    self.plateau.cartes_joueur2 -= 1
                    self.plateau.mana_dispo_joueur2 -= carte.cout
                elif carte.type == "serviteur":
                    if len(self.plateau.serviteurs_joueur2) < 7:
                        self.plateau.cartes_joueur2 -= 1
                        self.plateau.mana_dispo_joueur2 -= carte.cout
                        self.plateau.serviteurs_joueur2.append(carte)

    ## Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi)
    def attaquer(self, attaquant, cible):
        if self.plateau.tour_de_jeu == 1:
            if (attaquant == "heros" and self.plateau.arme_joueur1 == True) and cible == "heros":
                self.plateau.pv_actuels_joueur2 -= self.plateau.attaque_joueur1
                ## Mort du héros adverse
                if self.plateau.pv_actuels_joueur2 <= 0:
                    print(f"Victoire de {self.plateau.pseudo_joueur1} ! Félicitations.")
            elif (attaquant == "heros" and self.plateau.arme_joueur1 == True) and cible != "heros":
                self.plateau.pv_actuels_joueur1 -= cible.attaque
                cible.PV -= self.plateau.attaque_joueur1
                ## Mort de la cible ou de notre propre héros
                if cible.PV <= 0:
                    #MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur2 = [serviteur for serviteur in self.plateau.serviteurs_joueur2 if serviteur.PV > 0]
                if self.plateau.pv_actuels_joueur1 <= 0:
                    print(f"Victoire de {self.plateau.pseudo_joueur2} ! Félicitations.")
            elif attaquant != "heros" and cible == "heros":
                # Conséquences de l'attaque
                self.plateau.pv_actuels_joueur2 -= attaquant.attaque
                attaquant.atq_restante -= 1

                ## Mort du héros adverse
                if self.plateau.pv_actuels_joueur2 <= 0:
                    print(f"Victoire de {self.plateau.pseudo_joueur1} ! Félicitations.")
            else:
                # Conséquences de l'attaque
                attaquant.PV -= cible.attaque
                cible.PV -= attaquant.attaque
                attaquant.atq_restante -= 1

                ## Mort de l'attaquant ou/et de la cible
                if cible.PV <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur2 = [serviteur for serviteur in self.plateau.serviteurs_joueur2 if
                                                       serviteur.PV > 0]
                if attaquant.PV <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur1 = [serviteur for serviteur in self.plateau.serviteurs_joueur1 if
                                                       serviteur.PV > 0]
        else:
            if (attaquant == "heros" and self.plateau.arme_joueur2 == True) and cible == "heros":
                self.plateau.pv_actuels_joueur1 -= self.plateau.attaque_joueur2

                ## Mort du héros adverse
                if self.plateau.pv_actuels_joueur1 <= 0:
                    print(f"Victoire de {self.plateau.pseudo_joueur2} ! Félicitations.")
            elif (attaquant == "heros" and self.plateau.arme_joueur2 == True) and cible != "heros":
                self.plateau.pv_actuels_joueur2 -= cible.attaque
                cible.PV -= self.plateau.attaque_joueur2

                ## Mort de la cible ou de notre propre héros
                if cible.PV <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur1 = [serviteur for serviteur in self.plateau.serviteurs_joueur1 if
                                                       serviteur.PV > 0]
                if self.plateau.pv_actuels_joueur2 <= 0:
                    print(f"Victoire de {self.plateau.pseudo_joueur1} ! Félicitations.")
            elif attaquant != "heros" and cible == "heros":
                # Conséquences de l'attaque
                self.plateau.pv_actuels_joueur1 -= attaquant.attaque
                attaquant.atq_restante -= 1

                ## Mort du héros adverse
                if self.plateau.pv_actuels_joueur1 <= 0:
                    print(f"Victoire de {self.plateau.pseudo_joueur2} ! Félicitations.")
            else:

                # Conséquences de l'attaque
                attaquant.PV -= cible.attaque
                cible.PV -= attaquant.attaque
                attaquant.atq_restante -= 1

                ## Mort de l'attaquant ou/et de la cible
                if cible.PV <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur1 = [serviteur for serviteur in self.plateau.serviteurs_joueur1 if
                                                       serviteur.PV > 0]
                if attaquant.PV <= 0:
                    # MàJ du plateau si le serviteur meurt
                    self.plateau.serviteurs_joueur2 = [serviteur for serviteur in self.plateau.serviteurs_joueur2 if
                                                       serviteur.PV > 0]

    def fin_du_tour(self):
        self.plateau.tour_suivant()

## L'orchestrateur, qui appelle la classe tourencours pour lui faire effectuer une action aléatoire sur le plateau
class RandomOrchestrator:
    def __init__(self, plateau):
        self.plateau = plateau
        self.tourencours = TourEnCours(plateau)

    ## On génère une action aléatoire et on la fait jouer par la classe Tourencours
    def tour_au_hasard(self, carte, attaquant, cible):
        ## On liste les différentes actions possibles pendant un tour
        action_possible = ["Passer_tour", "Jouer_carte", "Attaquer"]
        ## Choix des actions possibles en fonction du plateau
        if carte == "": # aucune carte jouable
            action_possible.remove("Jouer_carte")
        if attaquant == "":
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
                "classe_j" : self.plateau.classe_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.classe_joueur2,
                "classe_adv" : self.plateau.classe_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.classe_joueur1,
                "mana_dispo_j" : self.plateau.mana_dispo_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_dispo_joueur2,
                "mana_max_j" : self.plateau.mana_max_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_max_joueur2,
                "mana_max_adv" : self.plateau.mana_max_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_max_joueur1,
                "surcharge_j" : self.plateau.surcharge_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.surcharge_joueur2,
                "surcharge_adv" : self.plateau.surcharge_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.surcharge_joueur1,
                "pv_j" : self.plateau.pv_actuels_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur2,
                "pv_adv" : self.plateau.pv_actuels_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur1,
                "pv_max_j" : self.plateau.pv_max_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_max_joueur2,
                "pv_max_adv" : self.plateau.pv_max_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_max_joueur1,
                "nbre_cartes_j" : self.plateau.cartes_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.cartes_joueur2,
                "nbre_cartes_adv" : self.plateau.cartes_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.cartes_joueur1,
                "dispo_ph_j" : self.plateau.dispo_pouvoir_hero_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.dispo_pouvoir_hero_joueur2,
                "cout_ph_j" : self.plateau.cout_pouvoir_hero_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.cout_pouvoir_hero_joueur2,
                "serv1_j" : self.plateau.serviteurs_joueur1[0].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "atq_serv1_j" : self.plateau.serviteurs_joueur1[0].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "pv_serv1_j" : self.plateau.serviteurs_joueur1[0].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "serv2_j" : self.plateau.serviteurs_joueur1[1].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "atq_serv2_j" : self.plateau.serviteurs_joueur1[1].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "pv_serv2_j" : self.plateau.serviteurs_joueur1[1].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "serv3_j" : self.plateau.serviteurs_joueur1[2].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "atq_serv3_j" : self.plateau.serviteurs_joueur1[2].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "pv_serv3_j" : self.plateau.serviteurs_joueur1[2].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "serv4_j" : self.plateau.serviteurs_joueur1[3].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "atq_serv4_j" : self.plateau.serviteurs_joueur1[3].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "pv_serv4_j" : self.plateau.serviteurs_joueur1[3].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "serv5_j" : self.plateau.serviteurs_joueur1[4].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "atq_serv5_j" : self.plateau.serviteurs_joueur1[4].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "pv_serv5_j" : self.plateau.serviteurs_joueur1[4].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "serv6_j" : self.plateau.serviteurs_joueur1[5].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "atq_serv6_j" : self.plateau.serviteurs_joueur1[5].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "pv_serv6_j" : self.plateau.serviteurs_joueur1[5].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "serv7_j" : self.plateau.serviteurs_joueur1[6].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "atq_serv7_j" : self.plateau.serviteurs_joueur1[6].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "pv_serv7_j" : self.plateau.serviteurs_joueur1[6].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "serv1_adv" : self.plateau.serviteurs_joueur2[0].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "atq_serv1_adv" : self.plateau.serviteurs_joueur2[0].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "pv_serv1_adv" : self.plateau.serviteurs_joueur2[0].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "serv2_adv" : self.plateau.serviteurs_joueur2[1].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "atq_serv2_adv" : self.plateau.serviteurs_joueur2[1].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "pv_serv2_adv" : self.plateau.serviteurs_joueur2[1].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "serv3_adv" : self.plateau.serviteurs_joueur2[2].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "atq_serv3_adv" : self.plateau.serviteurs_joueur2[2].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "pv_serv3_adv" : self.plateau.serviteurs_joueur2[2].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "serv4_adv" : self.plateau.serviteurs_joueur2[3].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "atq_serv4_adv" : self.plateau.serviteurs_joueur2[3].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "pv_serv4_adv" : self.plateau.serviteurs_joueur2[3].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "serv5_adv" : self.plateau.serviteurs_joueur2[4].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "atq_serv5_adv" : self.plateau.serviteurs_joueur2[4].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "pv_serv5_adv" : self.plateau.serviteurs_joueur2[4].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "serv6_adv" : self.plateau.serviteurs_joueur2[5].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "atq_serv6_adv" : self.plateau.serviteurs_joueur2[5].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "pv_serv6_adv" : self.plateau.serviteurs_joueur2[5].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "serv7_adv" : self.plateau.serviteurs_joueur2[6].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "atq_serv7_adv" : self.plateau.serviteurs_joueur2[6].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "pv_serv7_adv" : self.plateau.serviteurs_joueur2[6].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "arme_j" : self.plateau.arme_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.arme_joueur2,
                "arme_adv" : self.plateau.arme_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.arme_joueur1,
                "attaque_j" : self.plateau.attaque_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur2,
                "attaque_adv" : self.plateau.attaque_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur1,
                "durabilite_arme_j" : self.plateau.durabilite_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.durabilite_joueur2,
                "durabilite_arme_adv" : self.plateau.durabilite_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.durabilite_joueur1
            }
            logs_hs.loc[len(logs_hs)] = action_line

            ## Action
            self.tourencours.fin_du_tour()

        elif action == "Jouer_carte":
            ## Génération des logs associés à l'action
            action_line = {
                "action": "jouer_carte",
                "carte_jouee": carte.nom,
                "attaquant": "",
                "attaquant_atq": "",
                "attaquant_pv": "",
                "cible": "",
                "cible_atq": "",
                "cible_pv": "",
                "classe_j": self.plateau.classe_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.classe_joueur2,
                "classe_adv": self.plateau.classe_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.classe_joueur1,
                "mana_dispo_j": self.plateau.mana_dispo_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_dispo_joueur2,
                "mana_max_j": self.plateau.mana_max_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_max_joueur2,
                "mana_max_adv": self.plateau.mana_max_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_max_joueur1,
                "surcharge_j": self.plateau.surcharge_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.surcharge_joueur2,
                "surcharge_adv": self.plateau.surcharge_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.surcharge_joueur1,
                "pv_j": self.plateau.pv_actuels_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur2,
                "pv_adv": self.plateau.pv_actuels_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur1,
                "pv_max_j": self.plateau.pv_max_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_max_joueur2,
                "pv_max_adv": self.plateau.pv_max_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_max_joueur1,
                "nbre_cartes_j": self.plateau.cartes_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.cartes_joueur2,
                "nbre_cartes_adv": self.plateau.cartes_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.cartes_joueur1,
                "dispo_ph_j": self.plateau.dispo_pouvoir_hero_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.dispo_pouvoir_hero_joueur2,
                "cout_ph_j": self.plateau.cout_pouvoir_hero_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.cout_pouvoir_hero_joueur2,
                "serv1_j" : self.plateau.serviteurs_joueur1[0].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "atq_serv1_j" : self.plateau.serviteurs_joueur1[0].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "pv_serv1_j" : self.plateau.serviteurs_joueur1[0].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "serv2_j" : self.plateau.serviteurs_joueur1[1].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "atq_serv2_j" : self.plateau.serviteurs_joueur1[1].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "pv_serv2_j" : self.plateau.serviteurs_joueur1[1].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "serv3_j" : self.plateau.serviteurs_joueur1[2].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "atq_serv3_j" : self.plateau.serviteurs_joueur1[2].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "pv_serv3_j" : self.plateau.serviteurs_joueur1[2].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "serv4_j" : self.plateau.serviteurs_joueur1[3].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "atq_serv4_j" : self.plateau.serviteurs_joueur1[3].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "pv_serv4_j" : self.plateau.serviteurs_joueur1[3].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "serv5_j" : self.plateau.serviteurs_joueur1[4].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "atq_serv5_j" : self.plateau.serviteurs_joueur1[4].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "pv_serv5_j" : self.plateau.serviteurs_joueur1[4].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "serv6_j" : self.plateau.serviteurs_joueur1[5].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "atq_serv6_j" : self.plateau.serviteurs_joueur1[5].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "pv_serv6_j" : self.plateau.serviteurs_joueur1[5].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "serv7_j" : self.plateau.serviteurs_joueur1[6].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "atq_serv7_j" : self.plateau.serviteurs_joueur1[6].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "pv_serv7_j" : self.plateau.serviteurs_joueur1[6].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "serv1_adv" : self.plateau.serviteurs_joueur2[0].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "atq_serv1_adv" : self.plateau.serviteurs_joueur2[0].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "pv_serv1_adv" : self.plateau.serviteurs_joueur2[0].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "serv2_adv" : self.plateau.serviteurs_joueur2[1].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "atq_serv2_adv" : self.plateau.serviteurs_joueur2[1].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "pv_serv2_adv" : self.plateau.serviteurs_joueur2[1].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "serv3_adv" : self.plateau.serviteurs_joueur2[2].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "atq_serv3_adv" : self.plateau.serviteurs_joueur2[2].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "pv_serv3_adv" : self.plateau.serviteurs_joueur2[2].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "serv4_adv" : self.plateau.serviteurs_joueur2[3].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "atq_serv4_adv" : self.plateau.serviteurs_joueur2[3].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "pv_serv4_adv" : self.plateau.serviteurs_joueur2[3].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "serv5_adv" : self.plateau.serviteurs_joueur2[4].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "atq_serv5_adv" : self.plateau.serviteurs_joueur2[4].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "pv_serv5_adv" : self.plateau.serviteurs_joueur2[4].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "serv6_adv" : self.plateau.serviteurs_joueur2[5].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "atq_serv6_adv" : self.plateau.serviteurs_joueur2[5].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "pv_serv6_adv" : self.plateau.serviteurs_joueur2[5].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "serv7_adv" : self.plateau.serviteurs_joueur2[6].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "atq_serv7_adv" : self.plateau.serviteurs_joueur2[6].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "pv_serv7_adv" : self.plateau.serviteurs_joueur2[6].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "arme_j": self.plateau.arme_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.arme_joueur2,
                "arme_adv": self.plateau.arme_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.arme_joueur1,
                "attaque_j": self.plateau.attaque_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur2,
                "attaque_adv": self.plateau.attaque_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur1,
                "durabilite_arme_j": self.plateau.durabilite_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.durabilite_joueur2,
                "durabilite_arme_adv": self.plateau.durabilite_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.durabilite_joueur1
            }
            logs_hs.loc[len(logs_hs)] = action_line

            ## Action
            self.tourencours.jouer_carte(carte)

        # On filtre pour n'attaquer que quand c'est légal
        elif action == "Attaquer" and attaquant != "":
            ## Génération des logs associés à l'action
            action_line = {
                "action": "attaquer",
                "carte_jouee": "",
                "attaquant": attaquant.nom if attaquant != "heros" else "heros",
                "attaquant_atq": attaquant.attaque if attaquant != "heros" else self.plateau.attaque_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur2 if self.plateau.tour_de_jeu == 2 else "",
                "attaquant_pv": attaquant.PV if attaquant != "heros" else self.plateau.pv_actuels_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur2 if self.plateau.tour_de_jeu == 2 else "",
                "cible": cible.nom if cible != "heros" else "heros",
                "cible_atq": cible.attaque if cible != "heros" else 0,
                "cible_pv": cible.PV if cible != "heros" else self.plateau.pv_actuels_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur1 if self.plateau.tour_de_jeu == 2 else "",
                "classe_j": self.plateau.classe_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.classe_joueur2,
                "classe_adv": self.plateau.classe_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.classe_joueur1,
                "mana_dispo_j": self.plateau.mana_dispo_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_dispo_joueur2,
                "mana_max_j": self.plateau.mana_max_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_max_joueur2,
                "mana_max_adv": self.plateau.mana_max_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.mana_max_joueur1,
                "surcharge_j": self.plateau.surcharge_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.surcharge_joueur2,
                "surcharge_adv": self.plateau.surcharge_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.surcharge_joueur1,
                "pv_j": self.plateau.pv_actuels_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur2,
                "pv_adv": self.plateau.pv_actuels_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_actuels_joueur1,
                "pv_max_j": self.plateau.pv_max_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_max_joueur2,
                "pv_max_adv": self.plateau.pv_max_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.pv_max_joueur1,
                "nbre_cartes_j": self.plateau.cartes_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.cartes_joueur2,
                "nbre_cartes_adv": self.plateau.cartes_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.cartes_joueur1,
                "dispo_ph_j": self.plateau.dispo_pouvoir_hero_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.dispo_pouvoir_hero_joueur2,
                "cout_ph_j": self.plateau.cout_pouvoir_hero_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.cout_pouvoir_hero_joueur2,
                "serv1_j" : self.plateau.serviteurs_joueur1[0].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "atq_serv1_j" : self.plateau.serviteurs_joueur1[0].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "pv_serv1_j" : self.plateau.serviteurs_joueur1[0].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 0 else self.plateau.serviteurs_joueur2[0].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 0 else "",
                "serv2_j" : self.plateau.serviteurs_joueur1[1].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "atq_serv2_j" : self.plateau.serviteurs_joueur1[1].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "pv_serv2_j" : self.plateau.serviteurs_joueur1[1].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 1 else self.plateau.serviteurs_joueur2[1].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 1 else "",
                "serv3_j" : self.plateau.serviteurs_joueur1[2].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "atq_serv3_j" : self.plateau.serviteurs_joueur1[2].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "pv_serv3_j" : self.plateau.serviteurs_joueur1[2].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 2 else self.plateau.serviteurs_joueur2[2].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 2 else "",
                "serv4_j" : self.plateau.serviteurs_joueur1[3].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "atq_serv4_j" : self.plateau.serviteurs_joueur1[3].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "pv_serv4_j" : self.plateau.serviteurs_joueur1[3].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 3 else self.plateau.serviteurs_joueur2[3].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 3 else "",
                "serv5_j" : self.plateau.serviteurs_joueur1[4].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "atq_serv5_j" : self.plateau.serviteurs_joueur1[4].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "pv_serv5_j" : self.plateau.serviteurs_joueur1[4].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 4 else self.plateau.serviteurs_joueur2[4].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 4 else "",
                "serv6_j" : self.plateau.serviteurs_joueur1[5].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "atq_serv6_j" : self.plateau.serviteurs_joueur1[5].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "pv_serv6_j" : self.plateau.serviteurs_joueur1[5].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 5 else self.plateau.serviteurs_joueur2[5].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 5 else "",
                "serv7_j" : self.plateau.serviteurs_joueur1[6].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "atq_serv7_j" : self.plateau.serviteurs_joueur1[6].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "pv_serv7_j" : self.plateau.serviteurs_joueur1[6].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur1) > 6 else self.plateau.serviteurs_joueur2[6].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur2) > 6 else "",
                "serv1_adv" : self.plateau.serviteurs_joueur2[0].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "atq_serv1_adv" : self.plateau.serviteurs_joueur2[0].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "pv_serv1_adv" : self.plateau.serviteurs_joueur2[0].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 0 else self.plateau.serviteurs_joueur1[0].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 0 else "",
                "serv2_adv" : self.plateau.serviteurs_joueur2[1].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "atq_serv2_adv" : self.plateau.serviteurs_joueur2[1].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "pv_serv2_adv" : self.plateau.serviteurs_joueur2[1].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 1 else self.plateau.serviteurs_joueur1[1].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 1 else "",
                "serv3_adv" : self.plateau.serviteurs_joueur2[2].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "atq_serv3_adv" : self.plateau.serviteurs_joueur2[2].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "pv_serv3_adv" : self.plateau.serviteurs_joueur2[2].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 2 else self.plateau.serviteurs_joueur1[2].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 2 else "",
                "serv4_adv" : self.plateau.serviteurs_joueur2[3].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "atq_serv4_adv" : self.plateau.serviteurs_joueur2[3].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "pv_serv4_adv" : self.plateau.serviteurs_joueur2[3].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 3 else self.plateau.serviteurs_joueur1[3].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 3 else "",
                "serv5_adv" : self.plateau.serviteurs_joueur2[4].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "atq_serv5_adv" : self.plateau.serviteurs_joueur2[4].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "pv_serv5_adv" : self.plateau.serviteurs_joueur2[4].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 4 else self.plateau.serviteurs_joueur1[4].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 4 else "",
                "serv6_adv" : self.plateau.serviteurs_joueur2[5].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "atq_serv6_adv" : self.plateau.serviteurs_joueur2[5].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "pv_serv6_adv" : self.plateau.serviteurs_joueur2[5].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 5 else self.plateau.serviteurs_joueur1[5].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 5 else "",
                "serv7_adv" : self.plateau.serviteurs_joueur2[6].nom if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].nom if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "atq_serv7_adv" : self.plateau.serviteurs_joueur2[6].attaque if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].attaque if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "pv_serv7_adv" : self.plateau.serviteurs_joueur2[6].PV if self.plateau.tour_de_jeu == 1 and len(self.plateau.serviteurs_joueur2) > 6 else self.plateau.serviteurs_joueur1[6].PV if self.plateau.tour_de_jeu == 2 and len(self.plateau.serviteurs_joueur1) > 6 else "",
                "arme_j": self.plateau.arme_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.arme_joueur2,
                "arme_adv": self.plateau.arme_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.arme_joueur1,
                "attaque_j": self.plateau.attaque_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur2,
                "attaque_adv": self.plateau.attaque_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.attaque_joueur1,
                "durabilite_arme_j": self.plateau.durabilite_joueur1 if self.plateau.tour_de_jeu == 1 else self.plateau.durabilite_joueur2,
                "durabilite_arme_adv": self.plateau.durabilite_joueur2 if self.plateau.tour_de_jeu == 1 else self.plateau.durabilite_joueur1
            }
            logs_hs.loc[len(logs_hs)] = action_line

            ## Action
            if (attaquant != "heros" and attaquant.atq_restante != 0): # attaque seulement si le serviteur le peut
                self.tourencours.attaquer(attaquant, cible)
            elif attaquant == "heros":
                if (self.plateau.tour_de_jeu == 1 and self.plateau.attaque_joueur1 != 0) or \
                    (self.plateau.tour_de_jeu == 2 and self.plateau.attaque_joueur2 != 0): # n'attaque que si le héros a de l'attaque
                    self.tourencours.attaquer(attaquant, cible)

        return self.plateau

if __name__ == '__main__':
    deck = CardGroup((Carte("Yéti Noroit", "serviteur", 4, 5, 4),
                      Carte("Raptor", "serviteur", 3, 2, 2)))

    print(deck)
    for elt in deck:
        print(elt)

    deck.add_one(Carte("Michel", "serviteur", 1, 1, 1))
    print(deck)
    deck.shuffle()
    main = deck.pick(2)
    for elt in main:
        print(elt)