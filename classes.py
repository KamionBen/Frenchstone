## Les différentes classes utilisées pour la simulation

### Imports
import random

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
            self.mana_max_joueur1 = min(self.mana_max_joueur1 + 1, 10)
            self.mana_dispo_joueur1 = self.mana_max_joueur1 - self.surcharge_joueur1
            self.surcharge_joueur1 = 0
            self.dispo_pouvoir_hero_joueur1 = True
        else:
            self.mana_max_joueur2 = min(self.mana_max_joueur2 + 1, 10)
            self.mana_dispo_joueur2 = self.mana_max_joueur2 - self.surcharge_joueur2
            self.surcharge_joueur1 = 0
            self.dispo_pouvoir_hero_joueur2 = True
        print('-----------------------------------------')
        if self.tour_de_jeu == 1:
            print(f'Tour de jeu : {self.pseudo_joueur1}')
        else:
            print(f'Tour de jeu : {self.pseudo_joueur2}')
        print('-----------------------------------------')



### Classe permettant de décrire exhaustivement une carte
class Carte:
    def __init__(self, nom, type_carte, attaque, PV, cout):
        self.nom = nom
        self.type = type_carte
        self.attaque = attaque
        self.PV = PV
        self.cout = cout



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
                    print(f"Carte jouée : {carte.nom}")
                elif carte.type == "serviteur":
                    if len(self.plateau.serviteurs_joueur1) < 7:
                        self.plateau.cartes_joueur1 -= 1
                        self.plateau.mana_dispo_joueur1 -= carte.cout
                        self.plateau.serviteurs_joueur1.append(carte)
                        print(f"Carte jouée : {carte.nom}")
        else:
            if carte.cout <= self.plateau.mana_dispo_joueur2:
                if carte.type == "sort":
                    self.plateau.cartes_joueur2 -= 1
                    self.plateau.mana_dispo_joueur2 -= carte.cout
                    print(f"Carte jouée : {carte.nom}")
                elif carte.type == "serviteur":
                    if len(self.plateau.serviteurs_joueur2) < 7:
                        self.plateau.cartes_joueur2 -= 1
                        self.plateau.mana_dispo_joueur2 -= carte.cout
                        self.plateau.serviteurs_joueur2.append(carte)
                        print(f"Carte jouée : {carte.nom}")

    ## Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi)
    def attaquer(self, attaquant, cible):
        if self.plateau.tour_de_jeu == 1:
            if attaquant == "heros" and cible == "heros":
                print(f'Votre héros attaque {self.plateau.pseudo_joueur2}'
                      f' ({self.plateau.pv_actuels_joueur2} --> {self.plateau.pv_actuels_joueur2 - self.plateau.attaque_joueur1})')
                self.plateau.pv_actuels_joueur2 -= self.plateau.attaque_joueur1
            elif attaquant == "heros" and cible != "heros":
                print(
                    f'Votre héros ({self.plateau.pv_actuels_joueur1} --> {self.plateau.pv_actuels_joueur1 - cible.attaque}) attaque {cible.nom}'
                    f' ({cible.attaque}, {cible.PV}) --> ({cible.attaque}, {cible.PV - self.plateau.attaque_joueur1})')
                self.plateau.pv_actuels_joueur1 -= cible.attaque
                cible.PV -= self.plateau.attaque_joueur1
            elif attaquant != "heros" and cible == "heros":
                print(f'Votre {attaquant.nom} attaque {self.plateau.pseudo_joueur2}'
                      f' ({self.plateau.pv_actuels_joueur2} --> {self.plateau.pv_actuels_joueur2 - attaquant.attaque})')
                self.plateau.pv_actuels_joueur2 -= attaquant.attaque
            else:
                print(f'Votre {attaquant.nom} ({attaquant.attaque}, {attaquant.PV}) --> ({attaquant.attaque}, {attaquant.PV - cible.attaque})'
                      f' attaque {cible.nom}'
                      f' ({cible.attaque}, {cible.PV}) --> ({cible.attaque}, {cible.PV - attaquant.attaque})')
                attaquant.PV -= cible.attaque
                cible.PV -= attaquant.attaque
        else:
            if attaquant == "heros" and cible == "heros":
                print(f'Votre héros attaque {self.plateau.pseudo_joueur1}'
                      f' ({self.plateau.pv_actuels_joueur1} --> {self.plateau.pv_actuels_joueur1 - self.plateau.attaque_joueur2})')
                self.plateau.pv_actuels_joueur1 -= self.plateau.attaque_joueur2
            elif attaquant == "heros" and cible != "heros":
                print(
                    f'Votre héros ({self.plateau.pv_actuels_joueur2} --> {self.plateau.pv_actuels_joueur2 - cible.attaque}) attaque {cible.nom}'
                    f' ({cible.attaque}, {cible.PV}) --> ({cible.attaque}, {cible.PV - self.plateau.attaque_joueur2})')
                self.plateau.pv_actuels_joueur2 -= cible.attaque
                cible.PV -= self.plateau.attaque_joueur2
            elif attaquant != "heros" and cible == "heros":
                print(f'Votre {attaquant.nom} attaque {self.plateau.pseudo_joueur1}'
                      f' ({self.plateau.pv_actuels_joueur1} --> {self.plateau.pv_actuels_joueur1 - attaquant.attaque})')
                self.plateau.pv_actuels_joueur1 -= attaquant.attaque
            else:
                print(f'Votre {attaquant.nom} ({attaquant.attaque}, {attaquant.PV}) --> ({attaquant.attaque}, {attaquant.PV - cible.attaque})'
                      f' attaque {cible.nom}'
                      f' ({cible.attaque}, {cible.PV}) --> ({cible.attaque}, {cible.PV - attaquant.attaque})')
                attaquant.PV -= cible.attaque
                cible.PV -= attaquant.attaque

    def fin_du_tour(self):
        self.plateau.tour_suivant()

## L'orchestrateur, qui appelle la classe tourencours pour lui faire effectuer une action aléatoire sur le plateau
class RandomOrchestrator:
    def __init__(self, plateau):
        self.plateau = plateau
        self.tourencours = TourEnCours(plateau)
        ## On liste les différentes actions possibles pendant un tour
        self.action_possible = ["Passer_tour", "Jouer_carte", "Attaquer"]

    ## On génère une action aléatoire et on la fait jouer par la classe Tourencours
    def tour_au_hasard(self, carte, attaquant, cible):
        action = random.choice(self.action_possible)
        if action == "Passer_tour":
            self.tourencours.fin_du_tour()

        elif action == "Jouer_carte":
            self.tourencours.jouer_carte(carte)

        elif action == "Attaquer":
            self.tourencours.attaquer(attaquant, cible)

        return self.plateau