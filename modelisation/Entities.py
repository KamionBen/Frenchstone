import csv
import json
from os import path
from random import shuffle, choice
from typing import Union

""" CONSTANTS """


def get_cards_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)


cardsfile = "cards.json"
all_cards = get_cards_data('cards.json')
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
        # self.players[1].hand.add(get_card(0, get_cards_data("cards.json")))

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
        for player in self.players:
            if player.hero.is_dead():
                self.game_on = False
                for winner in self.players:
                    if winner != player:
                        self.winner = winner
            for servant in player.servants:
                if servant.is_dead():
                    player.servants.remove(servant)

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
        elif player.classe in ["Chasseur de démons", "Druide",
                               "Voleur", "Chaman", "Démoniste", "Guerrier"]:
            targets.append(player.hero)
        return targets


    def get_targets(self, serviteur):
        if serviteur not in self.players[0].servants:
            raise KeyError("Le serviteur choisi n'est pas sur le plateau du joueur actif")
        else:
            adv = self.players[1]
            targets = []
            if "Ruée" in serviteur.get_effects():
                if serviteur.effects["Ruée"].active is False:
                    targets.append(adv.hero)
            else:
                targets.append(adv.hero)
            for carte in adv.servants:
                targets.append(carte)
        return targets

    def get_gamestate(self) -> dict:
        player = self.players[0]
        adv = self.players[1]

        # On assigne les actions de base avant les actions spécifiques au choix
        """ BOARD """
        action_line = {"action": 0,
                       "carte_jouee": "",
                       "attaquant": "", "attaquant_atq": "", "attaquant_pv": "",
                       "cible": "", "cible_atq": "", "cible_pv": "",
                       "classe_j": player.classe, "classe_adv": adv.classe,
                       "mana_dispo_j": player.mana, "mana_max_j": player.mana_max,
                       "mana_max_adv": adv.mana_max,
                       "pv_j": player.hero.health, "pv_adv": adv.hero.health,
                       "armor_j": player.hero.armor, "armor_adv": adv.hero.armor,
                       "surcharge_j": player.surcharge, "surcharge_adv": adv.surcharge,
                       "pv_max_j": player.hero.base_health, "pv_max_adv": adv.hero.base_health,
                       "nbre_cartes_j": len(player.hand),
                       "nbre_cartes_adv": len(adv.hand),
                       "dispo_ph_j": player.hero.dispo_pouvoir,
                       "cout_ph_j": player.hero.cout_pouvoir,
                       "arme_j": player.hero.weapon,
                       "arme_adv": adv.hero.weapon,
                       "attaque_j": player.hero.attack,
                       "remaining_atk_j": player.hero.remaining_atk,
                       "attaque_adv": adv.hero.attack,
                       "attack_arme_j": player.hero.weapon.attack if player.hero.weapon is not None else 0,
                       "attack_arme_adv": adv.hero.weapon.attack if adv.hero.weapon is not None else 0,
                       "durabilite_arme_j": player.hero.weapon.durability if player.hero.weapon is not None else 0,
                       "durabilite_arme_adv": adv.hero.weapon.durability if adv.hero.weapon is not None else 0,
                       "pseudo_j": player.name,
                       "pseudo_adv": adv.name,
                       "victoire": 0}
        """ HERO """
        for classe_heros in ["Mage", "Chasseur", "Paladin", "Démoniste", "Chasseur de démons", "Druide", "Voleur",
                             "Guerrier", "Chevalier de la mort", "Prêtre"]:
            if player.classe == classe_heros:
                action_line[f"is_{classe_heros}"] = 1
            else:
                action_line[f"is_{classe_heros}"] = -99

        """ HAND """
        cartes_en_main = {i: carte for i, carte in enumerate(player.hand)}
        for i in range(10):
            if i in cartes_en_main.keys():
                action_line[f"carte_en_main{i + 1}"] = cartes_en_main[i].id
                action_line[f"carte_en_main{i + 1}_cost"] = cartes_en_main[i].cost
                action_line[f"carte_en_main{i + 1}_atk"] = cartes_en_main[i].attack
                action_line[f"carte_en_main{i + 1}_pv"] = cartes_en_main[i].health
            else:
                action_line[f"carte_en_main{i + 1}"] = -99
                action_line[f"carte_en_main{i + 1}_cost"] = -99
                action_line[f"carte_en_main{i + 1}_atk"] = -99
                action_line[f"carte_en_main{i + 1}_pv"] = -99

        for i in range(10):
            for j in range(len(all_cards)):
                action_line[f"is_carte{i + 1}_{all_cards[j]['name']}"] = 0

        for i in range(10):
            for j in range(len(all_cards)):
                if i in cartes_en_main.keys():
                    if cartes_en_main[i].name == all_cards[j]['name']:
                        action_line[f"is_carte{i + 1}_{all_cards[j]['name']}"] += 1
                    else:
                        action_line[f"is_carte{i + 1}_{all_cards[j]['name']}"] = -99
                else:
                    action_line[f"is_carte{i + 1}_{all_cards[j]['name']}"] = -99


        """ SERVANTS """
        player_servants = {i: carte.id for i, carte in enumerate(player.servants)}
        player_servants_atk = {i: carte.attack for i, carte in enumerate(player.servants)}
        player_servants_pv = {i: carte.health for i, carte in enumerate(player.servants)}
        player_servants_atk_remain = {i: carte.remaining_atk for i, carte in enumerate(player.servants)}
        for i in range(7):
            if i in player_servants.keys():
                action_line[f"serv{i + 1}_j"] = player_servants[i]
                action_line[f"atq_serv{i + 1}_j"] = player_servants_atk[i]
                action_line[f"pv_serv{i + 1}_j"] = player_servants_pv[i]
                action_line[f"atq_remain_serv{i + 1}_j"] = player_servants_atk_remain[i]
            else:
                action_line[f"serv{i + 1}_j"] = -99
                action_line[f"atq_serv{i + 1}_j"] = -99
                action_line[f"pv_serv{i + 1}_j"] = -99
                action_line[f"atq_remain_serv{i + 1}_j"] = -99

        adv_servants = {i: carte.id for i, carte in enumerate(adv.servants)}
        adv_servants_atk = {i: carte.attack for i, carte in enumerate(adv.servants)}
        adv_servants_pv = {i: carte.health for i, carte in enumerate(adv.servants)}
        for i in range(7):
            if i in adv_servants.keys():
                action_line[f"serv{i + 1}_adv"] = adv_servants[i]
                action_line[f"atq_serv{i + 1}_adv"] = adv_servants_atk[i]
                action_line[f"pv_serv{i + 1}_adv"] = adv_servants_pv[i]
            else:
                action_line[f"serv{i + 1}_adv"] = -99
                action_line[f"atq_serv{i + 1}_adv"] = -99
                action_line[f"pv_serv{i + 1}_adv"] = -99

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

    def start_game(self):
        self.deck.shuffle()
        self.pick_multi(3)
        self.hero.reset_complete()
        if self.classe == "Chasseur de démons":
            self.hero.cout_pouvoir = 1

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
        if self.classe == "Chevalier de la mort":
            for servant in self.servants:
                if servant.name == "Goule fragile":
                    self.servants.remove(servant)

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
        self.effet_pouvoir = None

        self.attack = 0
        self.remaining_atk = 1
        self.armor = 0
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
        self.remaining_atk = 1
        self.attack = self.weapon.attack if self.weapon is not None else 0

    def reset_complete(self):
        """ Le reset de début de partie """
        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.effet_pouvoir = None

        self.attack = 0
        self.armor = 0
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
        self.effects = kw["effects"]
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
        self.remaining_atk = 1
        # if "Ruée" in self.effects:
        #     self.effects["Ruée"].active = False

    def reset_complete(self):
        self.cost = self.base_cost
        self.attack = self.base_attack
        self.health = self.base_health


    def damage(self, nb):
        """ Removes nb from the card health """
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








