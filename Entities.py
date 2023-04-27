import csv
import json
from os import path
from random import shuffle

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


class Player:
    def __init__(self, name, ia=True):
        """ Profil de l'utilisateur ou de l'IA"""
        self.name = name
        self.ia = ia

        self.hero = None
        self.classe = None

        # Cartes
        self.deck = CardGroup()  # Le tas de cartes à l'envers
        self.hand = CardGroup()  # La main du joueur
        self.fighters = CardGroup()  # Les cartes sur le "terrain"

        self.mana, self.mana_max = 0, 0

    def start_turn(self):
        """ Remise à zéro de début de tour """
        self.mana_grow()
        self.mana_reset()
        self.power_reset()

    def mana_spend(self, nb):
        self.mana -= nb

    def mana_grow(self):
        self.mana_max += 1

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

    def set_deck(self, classe, file):
        self.classe = classe
        self.deck = import_deck(file)
        self.deck.shuffle()

    def __repr__(self) -> str:
        return self.name


hero_powers = {"Michel": "Blagues de Totems"}  # Devra être dans un fichier à part


class Hero:
    def __init__(self, name):
        """ Héros choisi par le joueur """
        self.name = name
        self.power = hero_powers[self.name]

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
        if type(new_card) == Card:
            self.cards.append(new_card)

    def shuffle(self):
        shuffle(self.cards)

    def pick_one(self):
        """ Renvoie la première carte de la liste et l'enlève du deck """
        picked = self.cards[0]
        self.cards = self.cards[1:]
        return picked

    def pick_multi(self, nb):
        picked_ls = []
        for _ in range(nb):
            picked_ls.append(self.pick_one())
        return picked_ls

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)


class Card:
    nb = 0

    def __init__(self, **kw):
        """ Classe généraliste pour les cartes à jouer """
        self.id = reverse_classes[kw['classe']] + '-' + int_to_id(Card.nb)
        Card.nb += 1

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
        self.effects = []  # Inutile pour l'instant
        self.remaining_atk = 0

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if type(other) == Card:
            return other.id == self.id
        if type(other) == str:
            return other == self.id or other.lower() == self.name.lower()

    def data(self) -> str:
        return f"id:{self.id} - {self.name} - Classe : {self.classe} - Type : {self.type} - Genre : {self.genre} - " \
               f"Coût = {self.cost} - Attaque = {self.attack} - Santé = {self.health}"


class Weapon:
    def __init__(self, name):
        self.name = name


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
    player = Player("KamionBen")
    player.set_hero("Michel")
    print(player)
    player.set_deck("Chasseur", "basic_chasseur.csv")

    for card in player.deck:
        print(card.data())









