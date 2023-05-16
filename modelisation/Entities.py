import csv
import json
from os import path
from random import shuffle, choice
from typing import Union

""" CONSTANTS """
cardsfile = "cards.json"
heroes = {"Chasseur": ["Rexxar", "Alleria Coursevent", "Sylvanas Coursevent", "Rexxar chanteguerre"],
          "Mage": ["Jaina Portvaillant", "Medivh", "Khadgar", "Jaina mage Feu"]}  # Devra être dans un fichier à part


""" CLASSES """


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

    def mana_spend(self, nb):
        self.mana -= nb

    def mana_grow(self):
        self.mana_max = min(self.mana_max + 1, 10)

    def mana_reset(self):
        self.mana = self.mana_max - self.surcharge
        self.surcharge = 0

    def power_reset(self):
        pass

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
        self.defense = 0
        self.health, self.base_health = 30, 30
        self.weapon = None

        self.fatigue = 0

    def __repr__(self):
        return self.name

    def damage(self, nb):
        self.health -= nb

    def reset(self):
        """ Le reset de début de tour """
        self.dispo_pouvoir = True

    def reset_complete(self):
        """ Le reset de début de partie """
        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.effet_pouvoir = None

        self.attack = 0
        self.defense = 0
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
        self.description = kw["description"]
        self.genre = kw["genre"]

        """ Category """
        self.classe = kw["classe"]
        self.type = kw["type"]

        """ Stats """
        self.cost, self.base_cost = kw["cost"], kw["cost"]
        self.attack, self.base_attack = kw["attack"], kw["attack"]
        self.health, self.base_health = kw["health"], kw["health"]
        
        """ Combat """
        self.effects = {}
        self.remaining_atk = 0

        self.parse_description()

    def generate_id(self, base_id):
        x = 0
        while f"{base_id}-{x}" in Card.created:
            x += 1
        return f"{base_id}-{x}"

    def get_effects(self):
        return list(self.effects.values())

    def parse_description(self):
        if self.description == "Provocation":
            self.effects["Provocation"] = Effect("Provocation")
        if self.description == "Ruée":
            self.effects["Ruée"] = Effect("Ruée", active=True)
            self.remaining_atk = 1
        if self.description == "Charge":
            self.effects["Charge"] = Effect("Charge")
            self.remaining_atk = 1

    def reset(self):
        """ Reset de début de tour """
        self.remaining_atk = 1
        if "Ruée" in self.effects:
            self.effects["Ruée"].active = False

    def reset_complete(self):
        self.cost = self.base_cost
        self.attack = self.base_attack
        self.health = self.base_health


    def damage(self, nb):
        """ Removes nb from the card health """
        self.health -= nb

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
            raise TypeError

    def data(self) -> str:
        return f"id:{self.id} - {self.name} - Classe : {self.classe} - Type : {self.type} - Genre : {self.genre} - " \
               f"Coût = {self.cost} - Attaque = {self.attack} - Santé = {self.health}"




class Weapon:
    def __init__(self, name):
        self.name = name

        self.attack = 0
        self.durability = 0


class Effect:
    def __init__(self, name, active=None):
        self.name = name
        self.active = active

    def __eq__(self, other):
        return other.lower() == self.name.lower()

    def __repr__(self):
        return self.name


""" FUNCTIONS """

def get_cards_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)


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








