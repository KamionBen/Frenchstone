from Entities import *


def get_card_data_by_id(file, cid):
    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)
    for card in data:
        if card["id"] == cid:
            return card
    return None


class Spell(Card):
    def __init__(self, name, **kw):
        """ Réprésente les cartes 'Sort' """
        Card.__init__(self, kw['id'])
        # TODO : qlb comment on va faire ça ? aaaaaaaah


class Servant(Card):
    def __init__(self, name, attack, health, **kw):
        """ Représente les cartes 'Serviteur' """
        Card.__init__(self, kw['id'])

        self.attack, self.base_attack = attack, attack
        self.health, self.base_health = health, health

        self.effects = EffectGroup()

        self.remaining_atq = 0

        self.parse_descr()  # Recherche les effets dans la description

    def damage(self, nb):
        """ Remove nb to the servant health """
        self.health -= nb

        # Exceptions
        if "Bouclier divin" in self.effects:
            if self.effects["Bouclier divin"].state:
                self.effects["Bouclier divin"].switch_state()
                self.health += nb

        if self.is_dead() and "Réincarnation" in self.effects:
            if self.effects["Réincarnation"].state:
                self.effects["Réincarnation"].switch_state()
                self.health = 1

    def is_dead(self):
        return self.health <= 0

    def stats(self):
        """ Un condensé des stats """
        return self.attack, self.health

    def parse_descr(self):
        first_word = self.description.split(' ')[0]
        if first_word == 'Provocation':
            self.effects.add(Effect('Provocation'))
        if first_word == 'Ruée':
            self.effects.add(Effect('Ruée', True))
            self.remaining_atq += 1
        if first_word == 'Charge':
            self.effects.add(Effect('Charge'))
            self.remaining_atq += 1
        if first_word == 'Réincarnation':
            self.effects.add(Effect('Réincarnation', True))


class CardGroup:
    created = []

    def __init__(self, *args, **kwargs):
        """ Permet de faire des opérations sur un groupe de cartes """
        if len(args) > 0:
            self.cards = list(args)
            self.carddict = {self.generate_id(c.cid): c for c in self.cards}
        elif len(kwargs) > 0:
            self.cards = list(kwargs.values())
            self.carddict = kwargs
        else:
            self.cards = []
            self.carddict = {}

    def get_id(self, card_item):
        if type(card_item) is Card:
            found = False
            for cid, card in self.carddict.items():
                if card_item == card:
                    found = True
                    return cid
            if found is False:
                raise FileNotFoundError(f"{card_item} n'est pas dans le groupe")
        else:
            raise TypeError

    def generate_id(self, base_id):
        """ Créer un identifiant unique temporaire au format 123-0
        123 étant l'identifiant général de la carte, et 0 l'identifiant unique
        Les invocations ont 0 comme identifiant général """
        x = -1
        while f"{base_id}-{x}" in CardGroup.created:
            x += 1
        return f"{base_id}-{x}"

    def reset(self):
        for card in self.cards:
            card.reset()

    def add(self, new_card):
        if type(new_card) == Card:
            self.cards.append(new_card)

    def remove(self, card):
        if type(card) == Card:
            self.cards.remove(card)
            self.carddict.pop(self.get_id(card))
        else:
            raise TypeError

    def shuffle(self):
        shuffle(self.cards)

    def pick_one(self):
        """ Renvoie la première carte de la liste et l'enlève du deck """
        if len(self.cards) > 0:
            picked = self.cards[0]
            self.remove(picked)
            return picked
        else:
            raise IndexError("Le groupe de cartes est vide")

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, x):
        """ Renvoie la xième carte du groupe"""
        if type(x) is int:
            return self.cards[x]
        else:
            raise TypeError

    def get(self, cid):
        """ Renvoie une carte en particulier """
        return self.carddict[cid]

    def choice(self):
        """ Retire une carte au hasard """
        if len(self.cards) == 0:
            return None
        else:
            my_choice = choice(self.cards)
            self.remove(my_choice)
            return my_choice

    def __repr__(self):
        return str(self.cards)


CLASS_BY_TYPE = {
    "Sort": Spell,
    "Arme": Weapon,
    "Serviteur": Servant,
}


class Card(object):

    @classmethod
    def from_ids(cls, list_cid):

        for cid in list_cid:
            _data = get_card_data_by_id("cards.json", cid)

            if not _data:
                continue

            class_type = CLASS_BY_TYPE[_data["type"]]
            yield class_type(_data)

    @classmethod
    def from_id(cls, cid):
        _data = get_card_data_by_id("cards.json", cid)

        if not _data:
            raise ValueError("Card not found.")

        class_type = CLASS_BY_TYPE[_data["type"]]
        return class_type(_data)

    def __init__(self, _data):

        self._id = _data["id"]
        self._data = _data
        self.type = _data["type"]

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


class EffectGroup:
    def __init__(self):
        self.effect = []
        self.effdict = {}

    def add(self, new_effect):
        if type(new_effect) is Effect:
            self.effect.append(new_effect)
            self.effdict[new_effect.name] = new_effect

    def __iter__(self):
        return iter(self.effect)

    def __getitem__(self, item: str) -> Effect:
        return self.effdict[item]


class Effect:
    def __init__(self, name, state=None):
        self.name = name
        self.state = state

    def switch_state(self):
        self.state = self.state is False

    def __repr__(self):
        return self.name

    def cd(self):
        """ Condensé """
        return self.name[:1]

    def __eq__(self, other: str) -> bool:
        return other == self.name


if __name__ == '__main__':
    print(Card.from_id(1))



