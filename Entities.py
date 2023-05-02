import csv
import json

from os import path
from random import shuffle
from typing import Union

import log
from effects import effect_handler

cardsfile = "cards.json"


def int_to_id(nb: int) -> str:
    if nb < 10:
        return f"00{nb}"
    elif nb < 100:
        return f"0{nb}"
    else:
        return str(nb)


def get_cards_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)
    
    
def get_card_data_by_id(file, cid):
    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)
    
    for card in data:
        if card["id"] != cid:
            continue
            
        return card
    
    return None


class Player:
    def __init__(self, name, classe, ia=True):
        """ Profil de l'utilisateur ou de l'IA"""
        self.name = name
        self.classe = classe
        self.ia = ia

        self.hero = Hero(hero_powers[self.classe][0])  # Premier héros par défaut

        # Cartes
        self.deck = CardGroup()  # Le tas de cartes à l'envers
        self.hand = CardGroup()  # La main du joueur
        self.servants = CardGroup()  # Les cartes sur le "terrain"

        self.mana, self.mana_max = 0, 0

    def start_game(self):
        self.deck.shuffle()
        self.pick_multi(3)

    def start_turn(self):
        """ Remise à zéro de début de tour """
        self.pick()
        self.mana_grow()
        self.mana_reset()
        self.power_reset()

    def mana_spend(self, nb):
        self.mana -= nb

    def mana_grow(self):
        self.mana_max = min(self.mana_max + 1, 10)

    def mana_reset(self):
        self.mana = self.mana_max

    def power_reset(self):
        pass

    def pick(self):
        """ Prendre une carte du deck et l'ajouter à sa main """
        self.hand.add(self.deck.pick_one())

    def pick_multi(self, nb):
        for _ in range(nb):
            self.pick()

    def set_hero(self, name):
        self.hero = Hero(name)

    def set_deck(self, file):
        self.deck = import_deck(file)
        #self.deck.shuffle()

    def __repr__(self) -> str:
        return self.name


hero_powers = {"Chasseur": ["Rexxar", "Alleria Coursevent", "Sylvanas Coursevent", "Rexxar chanteguerre"],
               "Mage": ["Jaina Portvaillant", "Medivh", "Khadgar", "Jaina mage Feu"]}  # Devra être dans un fichier à part


class Hero:
    def __init__(self, name):
        """ Héros choisi par le joueur """
        self.name = name
        self.power = None

        self.attack = 0
        self.health, self.base_health = 30, 30
        self.weapon = None

    def damage(self, nb):
        self.health -= nb

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

    def add(self, new_card):
        self.cards.append(new_card)

    def remove(self, card):
        if type(card) == Card:
            self.cards.remove(card)

    def shuffle(self):
        shuffle(self.cards)

    def pick_one(self):
        """ Renvoie la première carte de la liste et l'enlève du deck """
        if len(self.cards) > 0:
            picked = self.cards.pop(0)
            return picked
        else:
            log.CARTE.debug("Le deck est vide.")
            pass

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __add__(self, other):
        self.add(other)
        return self.cards

    def __getitem__(self, item):
        return self.cards[item]
    
    
class Card(object):
    
    def __init__(self, cid):
        self._id = cid
        
        _data = get_card_data_by_id("card.json", cid)
        
        if not _data:
            raise ValueError("Card not found.")
        
        self._data = _data
        
    @property
    def name(self):
        return self._data["name"]
    
    @property
    def cost(self):
        return self._data["cost"]
    
    @property
    def classe(self):
        return self._data["classe"]
    
    @property
    def description(self):
        return self._data["description"]
    
    @property
    def race(self):
        return self._data.get("race", None)
    
    @property
    def magic_type(self):
        return self._data.get("magic_type", None)
    
    
class ServitorCard(Card):
    
    _type = "Sertiveur"
    _have_fury = False
    _have_shield = False
    _have_provoc = False
    
    def __init__(self, cid):
        super(ServitorCard, self).__init__(cid)
        
    def damages(self, nb):
        rest = self.armor - nb
        
        if rest < 0:
            self.health -= abs(rest)
        
        self.armor -= nb
 
        
    @property
    def health(self):
        return self._data["health"]
    
    @health.setter
    def health(self, value):
        self._data["heath"] = value

    @property
    def attack(self):
        return self._data["attack"]

    @attack.setter
    def attack(self, value):
        self._data["attack"] = value
        
    @property
    def armor(self):
        return self._data.get("armor", 0)
    
    @armor.setter
    def armor(self, value):
        self._data["armor"] = value
        
        
class SpellCard(Card):
    
    _type = "Sort"
    
    def __init__(self, cid):
        super(SpellCard, self).__init__(cid)
        
    
class WeaponCard(Card):
    
    _type = "Arme"
    
    def __init__(self, cid):
        super(WeaponCard, self).__init__(cid)

    @property
    def attack(self):
        return self._data["attack"]

    @attack.setter
    def attack(self, value):
        self._data["attack"] = value
    
    @property
    def durability(self):
        return self._data["durability"]
    
    @durability.setter
    def durability(self, value):
        self._data["durability"] = value


def import_deck(file: str) -> CardGroup:
    jsoncards = get_cards_data('cards.json')
    deck = CardGroup()
    with open(path.join('decks', file), 'r') as csvdeck:
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
    return deck


def get_card(key: Union[int, str], file="cards.json") -> Card:
    """ Renvoie l'objet Card en fonction de 'key', qui peut être l'id où le nom de la carte """
    found = False
    with open(file, 'r', encoding='utf-8') as jsonfile:
        cardls = json.load(jsonfile)
    if type(key) is int:
        # Recherche par id fixe
        for elt in cardls:
            if elt['id'] == key:
                return Card(**elt)
    elif type(key) is str:
        ext = None
        if key[-2] == '-':
            # Recherche par id temporaire
            key, ext = key.split('-')
            for elt in cardls:
                if str(elt['id']) == key:
                    return Card(cid=f"{key}-{ext}", **elt)
        else:
            for elt in cardls:
                if elt['name'].lower() == key.lower():
                    return Card(**elt)

    if found is False:
        raise KeyError(f"Impossible de trouver {key}")


classes = {'CA': 'Chaman',
           'CH': 'Chasseur',
           'CD': 'Chasseur de démons',
           'CM': 'Chevalier de la mort',
           'DM': 'Démoniste',
           'DR': 'Druide',
           'GR': 'Guerrier',
           'MG': 'Mage',
           'PL': 'Paladin',
           'PR': 'Prêtre',
           'VL': 'Voleur',
           'NT': 'Neutre'}

reverse_classes = {value: key for key, value in classes.items()}

if __name__ == '__main__':
    print(get_card(1))
    print(get_card("Horion de givre"))
    print(get_card("1-2"))








