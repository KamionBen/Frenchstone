from Entities import *


class Card:
    created = []

    def __init__(self, name, card_id=0, temp_id=None, **kw):
        """ Représente n'importe quelle carte """
        if temp_id is None:
            self.id = self.generate_id(card_id)
        else:
            self.id = temp_id
        Card.created.append(self.id)

        """ INFOS """
        self.name = name
        self.description = kw['description'] if 'description' in kw.keys() else ""
        self.genre = kw['genre'] if 'genre' in kw.keys() else ""  # Nature, givre, bête etc ...
        self.cost = kw['cost'] if 'cost' in kw.keys() else 0

        """ TYPE """
        self.classe = kw['classe'] if 'classe' in kw.keys() else ""  # Chasseur, Mage, Démoniste, etc ...
        self.type = kw["type"]

    def generate_id(self, base_id):
        """ Créer un identifiant unique temporaire au format 123-0
        123 étant l'identifiant général de la carte, et 0 l'identifiant unique
        Les invocations ont 0 comme identifiant général """
        x = -1
        while f"{base_id}-{x}" in Card.created:
            x += 1
        return f"{base_id}-{x}"

    def __repr__(self):
        return self.name


class Servant(Card):
    def __init__(self, name, attack, health, **kw):
        """ Représente les cartes 'Serviteur' """
        Card.__init__(self, name, type="Serviteur", **kw)

        self.attack, self.base_attack = attack, attack
        self.health, self.base_health = health, health

        self.effects = EffectGroup()

        self.remaining_atq = 0

        self.parse_descr()  # Recherche les effets dans la description

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
        if first_word == "Cri":
            desc = self.description.split(':')
            if desc[0] == "Cri de guerre ":
                fx = desc[1]
                if fx.split(' ')[1] == 'invoque':
                    stats = fx.split(' ')[-1].replace('.', '')
                    stats = stats.split('/')
                    print(self.description, stats)
                    name = " ".join(fx.split(' ')[2:-1]).capitalize()
                    carte = Servant(name, stats[0], stats[1])
                    print(carte)
                    self.effects.add(Effect('Cri de guerre', invocation=carte))


EFFECTS = {'Provocation': Effect('Provocation'),
           'Ruée': Effect('Ruée', True),
           'Charge': Effect('Charge'),}


class Spell(Card):
    def __init__(self, name, **kw):
        """ Réprésente les cartes 'Sort' """
        Card.__init__(self, name, type="Sort", **kw)
        # TODO : qlb comment on va faire ça ? aaaaaaaah


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

            carte = Servant(**convert)
            effect = [e.cd() for e in carte.effects]
            if len(effect) == 0:
                effect = ''
            else:
                effect = f"({effect[0]})"
            print(carte, f"[{carte.stats()[0]}/{carte.stats()[1]}]", effect, carte.description)


