from modelisation.Entities import *


CLASS_BY_TYPE = {
    "Sort": SpellCard,
    "Arme": WeaponCard,
    "Serviteur": ServitorCard,
}


def get_card_data_by_id(file, cid):
    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)
    
    for card in data:
        if card["id"] != cid:
            continue
        
        return card
    
    return None


class Card(object):
    
    @classmethod
    def from_ids(cls, list_cid):
        
        for cid in list_cid:
            _data = get_card_data_by_id("card.json", cid)
        
            if not _data:
                continue
                
            class_type = CLASS_BY_TYPE[_data["type"]]
            yield class_type(data)

    @classmethod
    def from_id(cls, cid):
        _data = get_card_data_by_id("card.json", cid)
        
        if not _data:
            raise ValueError("Card not found.")

        class_type = CLASS_BY_TYPE[_data["type"]]
        return class_type(data)
    
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


class ServantCard(Card):
    _type = "Serviteur"
    _have_fury = False
    _have_shield = False
    _have_provoc = False
    
    def __init__(self, _data):
        super(ServantCard, self).__init__(_data)
    
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

    def __init__(self, _data):
        super(SpellCard, self).__init__(_data)


class WeaponCard(Card):
    
    def __init__(self, _data):
        super(WeaponCard, self).__init__(_data)
    
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
    def __init__(self, name, state=None, **kwargs):
        self.name = name
        self.state = state

        self.invocation = kwargs['invocation'] if 'invocation' in kwargs.keys() else None

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
    data = get_cards_data("cards.json")
    spell_type = []
    for elt in data:
        convert = {'card_id': elt['id'],
                   'name': elt['name'],
                   'description': elt['description'],
                   'genre': elt['genre'],
                   'cost': elt['cost'],
                   'classe': elt['classe']}
        if elt['type'] == "Serviteur":
            convert['attack'] = elt['attack']
            convert['health'] = elt['health']

            carte = ServantCard(**convert)
            effect = [e.cd() for e in carte.effects]
            if len(effect) == 0:
                effect = ''
            else:
                effect = f"({effect[0]})"
            print(carte, f"[{carte.stats()[0]}/{carte.stats()[1]}]", effect, carte.description)


