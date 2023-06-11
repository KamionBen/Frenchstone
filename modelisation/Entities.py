import csv
import json
from os import path
from random import shuffle, choice
from typing import Union
import random
import pickle

""" CONSTANTS """
dict_actions = {
            0: "passer_tour",
            1: "jouer_carte",
            2: "attaquer"
        }

classes_heros_old = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                 "Chevalier de la mort"]
classes_heros = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                 "Chevalier de la mort"]

def get_cards_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)


cardsfile = "cards.json"
all_cards = get_cards_data('cards.json')
all_servants = [x for x in all_cards if x['type'] == "Serviteur"]
heroes = {"Chasseur": ["Rexxar", "Alleria Coursevent", "Sylvanas Coursevent", "Rexxar chanteguerre"],
          "Mage": ["Jaina Portvaillant", "Medivh", "Khadgar", "Jaina mage Feu"],
          "Paladin": ["Uther"],
          "Démoniste": ["Gul'dan"],
          "Chasseur de démons": ["Ilidan"],
          "Druide" : ["Malfurion"],
          "Voleur" : ["Valeera"],
          "Guerrier": ["Garrosh"],
          "Chevalier de la mort": ["Le Roi-Liche"],
          "Prêtre": ["Anduin"]
          }  # Devra être dans un fichier à part


empty_action_line = {"carte_jouee": "",
   "attaquant": "", "attaquant_atq": "", "attaquant_pv": "",
   "cible": "", "cible_atq": "", "cible_pv": "",
   "classe_j": -99, "classe_adv": -99,
   "mana_dispo_j": -99, "mana_max_j": -99,
   "mana_max_adv": -99,
   "pv_j": -99, "pv_adv": -99,
   "armor_j": -99, "armor_adv": -99,
   "surcharge_j": -99, "surcharge_adv": -99,
   "pv_max_j": -99, "pv_max_adv": -99,
   "nbre_cartes_j": -99,
   "nbre_cartes_adv": -99,
   "dispo_ph_j": -99,
   "cout_ph_j": -99,
   "arme_j": -99,
   "arme_adv": -99,
   "attaque_j": -99,
   "remaining_atk_j": -99,
   "attaque_adv": -99,
   "attack_arme_j": -99,
   "attack_arme_adv": -99,
   "durabilite_arme_j": -99,
   "durabilite_arme_adv": -99,
   "pseudo_j": -99,
   "pseudo_adv": -99
}
for classe_heros in classes_heros:
    empty_action_line[f"is_{classe_heros}"] = -99
for i in range(10):
    empty_action_line[f"carte_en_main{i + 1}"] = -99
    empty_action_line[f"carte_en_main{i + 1}_cost"] = -99
    empty_action_line[f"carte_en_main{i + 1}_atk"] = -99
    empty_action_line[f"carte_en_main{i + 1}_pv"] = -99
    for j in range(len(all_cards)):
        empty_action_line[f"is_carte{i + 1}_{all_cards[j]['name']}"] = -99
for i in range(7):
    empty_action_line[f"serv{i + 1}_j"] = -99
    empty_action_line[f"atq_serv{i + 1}_j"] = -99
    empty_action_line[f"pv_serv{i + 1}_j"] = -99
    empty_action_line[f"atq_remain_serv{i + 1}_j"] = -99
    empty_action_line[f"divineshield_serv{i + 1}_j"] = -99
    empty_action_line[f"provocation_serv{i + 1}_j"] = -99
    empty_action_line[f"cant_attack_serv{i + 1}_j"] = -99
    empty_action_line[f"ruee_serv{i + 1}_j"] = -99
    empty_action_line[f"charge_serv{i + 1}_j"] = -99
    empty_action_line[f"camouflage_serv{i + 1}_j"] = -99
    empty_action_line[f"reincarnation_serv{i + 1}_j"] = -99
    empty_action_line[f"en_sommeil_serv{i + 1}_j"] = -99
    empty_action_line[f"gel_serv{i + 1}_j"] = -99
    empty_action_line[f"serv{i + 1}_adv"] = -99
    empty_action_line[f"atq_serv{i + 1}_adv"] = -99
    empty_action_line[f"pv_serv{i + 1}_adv"] = -99
    empty_action_line[f"divineshield_serv{i + 1}_adv"] = -99
    empty_action_line[f"provocation_serv{i + 1}_adv"] = -99
    empty_action_line[f"cant_attack_serv{i + 1}_adv"] = -99
    empty_action_line[f"ruee_serv{i + 1}_adv"] = -99
    empty_action_line[f"charge_serv{i + 1}_adv"] = -99
    empty_action_line[f"camouflage_serv{i + 1}_adv"] = -99
    empty_action_line[f"reincarnation_serv{i + 1}_adv"] = -99
    empty_action_line[f"en_sommeil_serv{i + 1}_adv"] = -99
    empty_action_line[f"gel_serv{i + 1}_adv"] = -99
    for j in range(len(all_servants)):
        empty_action_line[f"is_servant{i + 1}_{all_servants[j]['name']}_j"] = -99
        empty_action_line[f"is_servant{i + 1}_{all_servants[j]['name']}_adv"] = -99


""" CLASSES """
class Plateau:
    def __init__(self, players=()):
        """ Décrit exhaustivement le plateau de jeu """
        class_files = {'Chasseur': 'test_deck.csv',
                       'Mage': 'test_deck.csv',
                       'Paladin': 'test_deck.csv',
                       'Démoniste': 'test_deck.csv',
                       'Chasseur de démons': 'test_deck.csv',
                       'Druide': 'test_deck.csv',
                       'Voleur': 'test_deck.csv',
                       'Guerrier': 'test_deck.csv',
                       'Chevalier de la mort': 'test_deck.csv',
                       'Prêtre': 'test_deck.csv'
                       }
        if players == ():
            self.players = [Player("Smaguy", 'Chasseur'), Player("Rupert", 'Mage')]

        else:
            self.players = list(players)
        Card.created = []

        for player in self.players:
            player.set_deck(class_files[player.classe])

        # shuffle(self.players)  ## Il ne faut probablement pas shuffle les joueurs, mais plutôt les faire alterner dans le main

        """ Mélange des decks et tirage de la main de départ """
        for player in self.players:
            player.start_game()
        """ Le joueur 2 reçoit une carte en plus et la pièce """
        self.players[1].pick()
        self.players[1].hand.add(get_card("La piece", get_cards_data("cards.json")))

        """ Gestion du mana """
        """ Le premier joueur démarre son tour à l'initialisation """
        self.players[0].start_turn()

        """ Tour de jeu """
        self.game_turn = 0  # Décompte des tours
        self.game_on = True
        self.winner = None

    def tour_suivant(self):
        """ Met à jour le plateau à la fin du tour d'un joueur """
        self.game_turn += 1
        self.players.reverse()

        self.players[1].end_turn()
        self.players[0].start_turn()

    def update(self):
        """ Vérifie les serviteurs morts et les pdv des joueurs """
        dead_servants = []
        for player in self.players:
            if player.hero.is_dead():
                self.game_on = False
                for winner in self.players:
                    if winner != player:
                        self.winner = winner
            for servant in player.servants:
                if servant.is_dead():
                    player.servants.remove(servant)
                    if "rale d'agonie" in servant.effects and "allié" in servant.effects["rale d'agonie"][1] and player == self.players[1]:
                        servant.effects["rale d'agonie"][1] = ["ennemi" if x == "allié" else x for x in servant.effects["rale d'agonie"][1]]
                    if "réincarnation" in servant.effects and player == self.players[0]:
                        servant.effects["réincarnation"] = 0
                    dead_servants.append(servant)
        return dead_servants


    def targets_hp(self):
        """ Retourne les cibles possibles du pouvoir héroïque """
        player = self.players[0]
        adv = self.players[1]
        targets = []
        if player.classe in ["Mage", "Prêtre"]:
            targets = [player.hero] + [adv.hero] + player.servants.cards + adv.servants.cards
        elif player.classe == "Chasseur":
            targets.append(adv.hero)
        elif player.classe in ["Paladin", "Chevalier de la mort"]:
            if len(player.servants) < 7:
                targets.append(player.hero)
        else:
            targets.append(player.hero)
        return targets

    def get_gamestate(self) -> dict:
        player = self.players[0]
        adv = self.players[1]

        # On assigne les actions de base avant les actions spécifiques au choix
        """ BOARD """
        action_line = empty_action_line.copy()
        action_line["classe_j"], action_line["classe_adv"] = player.classe, adv.classe
        action_line["mana_dispo_j"], action_line["mana_max_j"] = player.mana, player.mana_max
        action_line["mana_max_adv"] = adv.mana_max
        action_line["pv_j"], action_line["pv_adv"] = player.hero.health, adv.hero.health
        action_line["armor_j"], action_line["armor_adv"] = player.hero.armor, adv.hero.armor
        action_line["surcharge_j"], action_line["surcharge_adv"] = player.surcharge, adv.surcharge
        action_line["pv_max_j"], action_line["pv_max_adv"] = player.hero.base_health, adv.hero.base_health
        action_line["nbre_cartes_j"], action_line["nbre_cartes_adv"] = len(player.hand), len(adv.hand)
        action_line["dispo_ph_j"], action_line["cout_ph_j"] = player.hero.dispo_pouvoir, player.hero.cout_pouvoir
        action_line["arme_j"], action_line["arme_adv"] = player.hero.weapon, adv.hero.weapon
        action_line["attaque_j"], action_line["attaque_adv"] = player.hero.attack, adv.hero.attack
        action_line["remaining_atk_j"] = player.hero.remaining_atk
        action_line["attack_arme_j"] = player.hero.weapon.attack if player.hero.weapon is not None else 0
        action_line["attack_arme_adv"] = adv.hero.weapon.attack if adv.hero.weapon is not None else 0
        action_line["durabilite_arme_j"] = player.hero.weapon.durability if player.hero.weapon is not None else 0
        action_line["durabilite_arme_adv"] = adv.hero.weapon.durability if adv.hero.weapon is not None else 0
        action_line["pseudo_j"], action_line["pseudo_adv"] = player.name, adv.name

        """ HERO """
        action_line[f"is_{player.classe}"] = 1

        """ HAND """
        for i in range(len(player.hand)):
            action_line[f"carte_en_main{i + 1}"] = player.hand[i].id
            action_line[f"carte_en_main{i + 1}_cost"] = player.hand[i].cost
            action_line[f"carte_en_main{i + 1}_atk"] = player.hand[i].attack
            action_line[f"carte_en_main{i + 1}_pv"] = player.hand[i].health
            action_line[f"is_carte{i + 1}_{player.hand[i].name}"] = 1

        """ SERVANTS """
        for i in range(len(player.servants)):
            action_line[f"serv{i + 1}_j"] = player.servants[i].id
            action_line[f"atq_serv{i + 1}_j"] = player.servants[i].attack
            action_line[f"pv_serv{i + 1}_j"] = player.servants[i].health
            action_line[f"atq_remain_serv{i + 1}_j"] = player.servants[i].remaining_atk
            if "bouclier divin" in player.servants[i].effects:
                action_line[f"divineshield_serv{i + 1}_j"] = player.servants[i].effects["bouclier divin"]
            if "provocation" in player.servants[i].effects:
                action_line[f"provocation_serv{i + 1}_j"] = player.servants[i].effects["provocation"]
            if "ne peut pas attaquer" in player.servants[i].effects:
                action_line[f"cant_attack_serv{i + 1}_j"] = player.servants[i].effects["ne peut pas attaquer"]
            if "ruée" in player.servants[i].effects:
                action_line[f"ruee_serv{i + 1}_j"] = player.servants[i].effects["ruée"]
            if "charge" in player.servants[i].effects:
                action_line[f"charge_serv{i + 1}_j"] = player.servants[i].effects["charge"]
            if "camouflage" in player.servants[i].effects:
                action_line[f"camouflage_serv{i + 1}_j"] = player.servants[i].effects["camouflage"]
            if "réincarnation" in player.servants[i].effects:
                action_line[f"reincarnation_serv{i + 1}_j"] = player.servants[i].effects["réincarnation"]
            if "en sommeil" in player.servants[i].effects:
                action_line[f"en_sommeil_serv{i + 1}_j"] = player.servants[i].effects["en sommeil"]
            if "gel" in player.servants[i].effects:
                action_line[f"gel_serv{i + 1}_j"] = player.servants[i].effects["gel"]
            action_line[f"is_servant{i + 1}_{player.servants[i].name}_j"] = 1
        for i in range(len(adv.servants)):
            action_line[f"serv{i + 1}_adv"] = adv.servants[i].id
            action_line[f"atq_serv{i + 1}_adv"] = adv.servants[i].attack
            action_line[f"pv_serv{i + 1}_adv"] = adv.servants[i].health
            if "bouclier divin" in adv.servants[i].effects:
                action_line[f"divineshield_serv{i + 1}_adv"] = adv.servants[i].effects["bouclier divin"]
            if "provocation" in adv.servants[i].effects:
                action_line[f"provocation_serv{i + 1}_adv"] = adv.servants[i].effects["provocation"]
            if "ne peut pas attaquer" in adv.servants[i].effects:
                action_line[f"cant_attack_serv{i + 1}_adv"] = adv.servants[i].effects["ne peut pas attaquer"]
            if "ruée" in adv.servants[i].effects:
                action_line[f"ruee_serv{i + 1}_adv"] = adv.servants[i].effects["ruée"]
            if "charge" in adv.servants[i].effects:
                action_line[f"charge_serv{i + 1}_adv"] = adv.servants[i].effects["charge"]
            if "camouflage" in adv.servants[i].effects:
                action_line[f"camouflage_serv{i + 1}_adv"] = adv.servants[i].effects["camouflage"]
            if "réincarnation" in adv.servants[i].effects:
                action_line[f"reincarnation_serv{i + 1}_adv"] = adv.servants[i].effects["réincarnation"]
            if "en sommeil" in adv.servants[i].effects:
                action_line[f"en_sommeil_serv{i + 1}_adv"] = adv.servants[i].effects["en sommeil"]
            if "gel" in adv.servants[i].effects:
                action_line[f"gel_serv{i + 1}_adv"] = adv.servants[i].effects["gel"]
            action_line[f"is_servant{i + 1}_{adv.servants[i].name}_adv"] = 1

        return action_line


class Player:
    def __init__(self, name, classe, ia=True):
        """ Profil de l'utilisateur ou de l'IA"""
        self.name = name
        self.classe = classe
        self.ia = ia
        self.hero = Hero(heroes[self.classe][0])  # Premier héros par défaut

        # Cartes
        self.deck = CardGroup()  # Le tas de cartes à l'envers
        self.hand = CardGroup()  # La main du joueur
        self.servants = CardGroup()  # Les cartes sur le "terrain"

        self.mana, self.mana_max = 0, 0
        self.surcharge = 0
        self.discount_next = []

    def start_game(self):
        self.deck.shuffle()
        self.pick_multi(3)
        self.hero.reset_complete()
        if self.classe == "Chasseur de démons":
            self.hero.cout_pouvoir = 1
            self.hero.cout_pouvoir_temp = 1

    def start_turn(self):
        """ Remise à zéro de début de tour """
        if len(self.deck) > 0:
            self.pick()
        else:
            self.hero.fatigue += 1
        self.hero.damage(self.hero.fatigue)
        self.hero.reset()
        self.mana_grow()
        self.mana_reset()
        self.power_reset()
        self.servants.reset()

    def end_turn(self):
        """ Mise à jour de fin de tour """
        self.hero.attack = 0
        if self.hero.remaining_atk == 0 and self.hero.gel == 1:
            self.hero.gel = 0
        for servant in self.servants:
            if servant.name == "Goule fragile":
                self.servants.remove(servant)
            if "temp_turn" in servant.effects:
                servant.attack -= servant.effects["temp_turn"][0]
                servant.health -= servant.effects["temp_turn"][1]
                servant.base_health -= servant.effects["temp_turn"][1]
            if "gel" in servant.effects and servant.remaining_atk == 0:
                servant.effects.pop("gel")
            if "aura" in servant.effects and "end_turn" in servant.effects["aura"][1]:
                if "self" in servant.effects["aura"][1]:
                    servant.attack += servant.effects["aura"][2][0]
                    servant.health += servant.effects["aura"][2][1]
                    servant.base_health += servant.effects["aura"][2][1]

    def apply_discount(self):
        if self.discount_next:
            for card in self.hand:
                card.cost = card.base_cost
                for discount in self.discount_next:
                    if card.type.lower() == discount[0]:
                        if discount[1] != "" and discount[1] in card.genre:
                            card.cost = max(0, card.base_cost - discount[2])


    def mana_spend(self, nb):
        self.mana -= nb

    def mana_grow(self):
        self.mana_max = min(self.mana_max + 1, 10)

    def mana_reset(self):
        self.mana = self.mana_max - self.surcharge
        self.surcharge = 0

    def power_reset(self):
        self.hero.dispo_pouvoir = True

    def pick(self):
        """ Prendre la première carte du deck et l'ajouter à sa main """
        if len(self.hand) < 10:
            self.hand.add(self.deck.pick_one())
        else:
            self.deck.pick_one()
            # raise PermissionError("Il a plus de cartes en main que de place prévue dans le log")

    def pick_multi(self, nb):
        for _ in range(nb):
            self.pick()

    def set_hero(self, name):
        self.hero = Hero(name)

    def set_deck(self, file):
        self.deck = import_deck(file)

    def __repr__(self) -> str:
        return self.name


class Hero:
    def __init__(self, name):
        """ Héros choisi par le joueur """
        self.name = name
        self.power = None

        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.cout_pouvoir_temp = 2
        self.effet_pouvoir = None

        self.attack = 0
        self.remaining_atk = 1
        self.armor = 0
        self.gel = 0
        self.health, self.base_health = 30, 30
        self.weapon = None

        self.fatigue = 0

    def __repr__(self):
        return self.name

    def damage(self, nb):
        nb_armor = nb * (self.armor >= nb) + self.armor * (self.armor < nb)
        self.armor -= nb_armor
        self.health -= (nb - nb_armor)

    def reset(self):
        """ Le reset de début de tour """
        self.dispo_pouvoir = True
        if self.gel == 0:
            self.remaining_atk = 1
        else:
            self.remaining_atk = 0
        self.attack = self.weapon.attack if self.weapon is not None else 0

    def reset_complete(self):
        """ Le reset de début de partie """
        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.effet_pouvoir = None

        self.attack = 0
        self.armor = 0
        self.gel = 0
        self.health, self.base_health = 30, 30
        self.weapon = None

        self.fatigue = 0

    def heal(self, nb):
        self.health += nb
        if self.health > self.base_health:
            self.health = self.base_health

    def is_dead(self) -> bool:
        return self.health <= 0


class CardGroup:
    def __init__(self, cards=()):
        """ Permet de faire des opérations sur un groupe de cartes """
        self.cards = list(cards)
        self.carddict = {c.id: c for c in self.cards}

    def reset(self):
        for card in self.cards:
            card.reset()

    def add(self, new_card):
        if type(new_card) == Card:
            self.cards.append(new_card)


    def remove(self, card):
        if type(card) == Card:
            self.cards.remove(card)

    def shuffle(self):
        shuffle(self.cards)

    def pick_one(self):
        """ Renvoie la première carte de la liste et l'enlève du deck """
        if len(self.cards) > 0:
            picked = self.cards[0]
            self.cards = self.cards[1:]
            return picked
        else:
            raise IndexError("Le groupe de cartes est vide")

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __add__(self, other):
        if type(other) is Card:
            ls = self.cards.copy()
            ls.append(other)
            return CardGroup(ls)
        elif type(other) is list:
            ls = self.cards.copy()
            for l in other:
                ls.append(l)
            return ls
        else:
            raise TypeError(f"Impossible d'additionner {other} (type:{type(other)}) avec le type CardGroup")

    def __getitem__(self, x):
        """ Renvoie la xième carte du groupe"""
        if type(x) is int:
            return self.cards[x]
        else:
            raise TypeError

    def get(self, cid):
        """ Renvoie une carte en particulier """
        if is_card_id(cid):
            if cid in self.carddict:
                return self.carddict[cid]
            else:
                return KeyError
        else:
            raise TypeError

    def choice(self):
        """ Retire une carte au hasard """
        if len(self.cards) == 0:
            return None
        else:
            my_choice = choice(self.cards)
            self.cards.remove(my_choice)
            return my_choice

    def __repr__(self):
        return str(self.cards)


class Card:
    created = []

    def __init__(self, cid=None, **kw):
        """ Classe généraliste pour les cartes à jouer """
        if cid is None:
            # Génération d'un id de carte
            self.id = self.generate_id(kw['id'])
        else:
            self.id = cid
        Card.created.append(self.id)

        """ Description """
        self.name = kw["name"]
        self.effects = kw["effects"].copy()
        self.genre = kw["genre"]

        """ Category """
        self.classe = kw["classe"]
        self.type = kw["type"]

        """ Stats """
        self.cost, self.base_cost = kw["cost"], kw["cost"]
        self.attack, self.base_attack = kw["attack"], kw["attack"]
        self.health, self.base_health = kw["health"], kw["health"]
        
        """ Combat """
        self.remaining_atk = 0

    def generate_id(self, base_id):
        x = 0
        while f"{base_id}-{x}" in Card.created:
            x += 1
        return f"{base_id}-{x}"

    def get_effects(self):
        return list(self.effects.values())

    def reset(self):
        """ Reset de début de tour """
        if "ne peut pas attaquer" in self.effects:
            self.remaining_atk = 0
        else:
            self.remaining_atk = 1
        if "ruée" in self.effects and not "en sommeil" in self.effects:
            self.effects["ruée"] = 0
        if "aura" in self.effects and "temp_fullturn" in self.effects["aura"][1]:
            self.attack = self.base_attack
        if "gel" in self.effects:
            self.remaining_atk = 0
        if "en sommeil" in self.effects:
            self.effects["en sommeil"] -= 1
            if self.effects["en sommeil"] == 0:
                self.effects.pop("en sommeil")

    def reset_complete(self):
        self.cost = self.base_cost
        self.attack = self.base_attack
        self.health = self.base_health


    def damage(self, nb):
        """ Removes nb from the card health """
        if self.name == "Bulleur" and nb == 1:
            self.health = 0
        if "bouclier divin" in self.effects:
            self.effects.pop("bouclier divin")
        else:
            self.health -= nb

    def heal(self, nb):
        """ Heal nb health to a given creatures """
        self.health += nb
        if self.health > self.base_health:
            self.health = self.base_health



    def is_dead(self):
        """ Return True if the card health <= 0"""
        return self.health <= 0

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if type(other) == Card:
            return other.id == self.id
        elif type(other) == str:
            return other == self.id or other.lower() == self.name.lower()
        else:
            return False

    def data(self) -> str:
        return f"id:{self.id} - {self.name} - Classe : {self.classe} - Type : {self.type} - Genre : {self.genre} - " \
               f"Coût = {self.cost} - Attaque = {self.attack} - Santé = {self.health}"


class Weapon:
    def __init__(self, name):
        self.name = name

        self.attack = 0
        self.durability = 0

""" FUNCTIONS """

def import_deck(file: str, data='cards.json') -> CardGroup:
    """
    :param file: A csv file with the card's name and the number of this card in the deck
    :param data : The .json file
    :return: A CardGroup
    """
    jsoncards = get_cards_data(data)
    deck = CardGroup()
    with open(path.join('../decks', file), 'r') as csvdeck:
        reader = csv.reader(csvdeck, delimiter=";")
        for line in reader:
            name = line[0]
            number = int(line[1])
            found = False
            for jsoncard in jsoncards:
                if jsoncard['name'] == name:
                    found = True
                    for _ in range(number):
                        card = Card(**jsoncard)
                        deck.add(card)
                    break
            if found is False:
                print(f"\033[91mERREUR : La carte {name} n'a pas été trouvée dans le fichier cards.json\033[0m")
    if len(deck) == 0:
        raise ImportError("Le deck est vide")
    else:
        return deck


def get_card(key: Union[int, str], cardpool: list) -> Card:
    """ Renvoie l'objet Card en fonction de 'key', qui peut être l'id où le nom de la carte """
    found = False
    if type(key) is int:
        # Recherche par id fixe
        for elt in cardpool:
            if elt['id'] == key:
                return Card(**elt)
    elif type(key) is str:
        if len(key.split('-')) == 2:
            # Recherche par id temporaire
            key, ext = key.split('-')
            for elt in cardpool:
                if str(elt['id']) == key:
                    return Card(cid=f"{key}-{ext}", **elt)
        else:
            for elt in cardpool:
                if elt['name'].lower() == key.lower():
                    return Card(**elt)
    else:
        raise TypeError

    if found is False:
        raise KeyError(f"Impossible de trouver {key}")


def int_to_id(baseid: int, nb: int) -> str:
    if type(baseid) is int and type(nb) is int:
        if baseid < 10:
            return f"000{baseid}-{nb}"
        elif baseid < 100:
            return f"00{baseid}-{nb}"
        elif baseid < 1000:
            return f"0{baseid}-{nb}"
        else:
            return f"{baseid}-{nb}"
    else:
        raise TypeError


def is_card_id(elt) -> bool:
    """ Renvoie vrai si elt est au format int-int """
    try:
        parse = elt.split('-')
        cid = int(parse[0])
        number = int(parse[1])
        return True
    except ValueError:
        return False
    except IndexError:
        return False
    except AttributeError:
        return False



if __name__ == '__main__':
    pass








