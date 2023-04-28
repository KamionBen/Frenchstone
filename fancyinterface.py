import pandas.core.frame

from Entities import *
from time import sleep
import pickle
from init_variables import *

def center_text(text: str, length: int, filler=' ', bold=False, color=None) -> str:
    left = (length - len(text)) // 2
    right = length - left - len(text)
    if bold:
        text = f"\033[1m{text}\033[0m"
    if color is not None:
        text = f"{color}{text}\033[0m"
    centered_text = filler * left + text + filler * right
    return centered_text


def fancy_card(fancy_card: Card, active=False) -> str:
    """ Return a str representing a single card """
    if active:
        a, e = '\033[92m', '\033[0m'  # GREEN, ENDC
    else:
        a, e = '', ''

    length = 25
    """ COUT + Carte haut """
    f_card = f"{a}┌─{e}"+f"C={fancy_card.cost}{a}"+"─"*(length-6)+f"┐{e}\n"

    """ NOM """
    if len(fancy_card.name) <= length - 2:
        # Nom sur une ligne

        centered_name = center_text(fancy_card.name, length - 2, bold=True)
        f_card += f"{a}│{e}" + centered_name + f"{a}│{e}\n"
        f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    else:
        decomposed = fancy_card.name.split(' ')
        name_ls = []
        for word in decomposed:
            if not name_ls:
                name_ls = [word]
            else:
                if len(name_ls[-1] + " " + word) <= length - 2:
                    name_ls[-1] += " " + word
                else:
                    name_ls.append(word)

        centered_name1 = center_text(name_ls[0], length-2, bold=True)
        f_card += f"{a}│{e}" + centered_name1 + f"{a}│{e}\n"
        centered_name2 = center_text(name_ls[1], length - 2, bold=True)
        f_card += f"{a}│{e}" + centered_name2 + f"{a}│{e}\n"

    f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"

    """ STATS """
    if fancy_card.attack is None and fancy_card.health is None:
        f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    else:
        f_card += f"{a}│{e} A={fancy_card.attack}" + " " * (length - 10) + f"H={fancy_card.health} {a}│{e}\n"

    """ TYPE + Carte bas """
    centered_type = center_text(f" {fancy_card.type} ", length-2, f'{a}─{e}')

    f_card += f"{a}└{e}"+centered_type+f"{a}┘{e}"
    return f_card


def fancy_cardlist(cartes: list[Card], selection=False, mana=0) -> str:
    """ Return a str representing a card hand """
    card_ls = []
    for card in cartes:
        card_ls.append(fancy_card(card, card.cost <= mana))
    cards_l = [c.split('\n') for c in card_ls]
    cards_dict = {}
    for card in cards_l:
        for i, line in enumerate(card):
            if i in cards_dict.keys():
                cards_dict[i] += line
            else:
                cards_dict[i] = line
    cards_str = ""
    if selection:
        sel = [f"{x+1}:" for x in range(len(cards_l))]
        cards_str += "                       ".join(sel)
        cards_str += '\n'
    for line in cards_dict.values():
        cards_str += line + "\n"

    return cards_str


def fancy_hero(hero: Hero, active=False, playing=False) -> str:
    """ Besoin d'une classe "Joueur" ou Héros """
    if active:
        a, e = "", ""
    else:
        a, e = "", ""

    length = 25
    yellow = '\033[93m'
    if playing:
        j_str = f"┌{center_text(f' {hero.name} ', length-2, bold=True, filler='─', color=yellow)}┐\n"
    else:
        j_str = f"┌{center_text(f' {hero.name} ', length - 2, bold=True, filler='─')}┐\n"

    j_str += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    if hero.attack > 0:
        pass
    else:
        if hero.health < 10:
            health = f" {hero.health}"
        else:
            health = str(hero.health)
        j_str += "└" + "─" * (length - 9) + f" H={health} ─┘"

    return j_str


def fancy_mana(mana, mana_max) -> str:
    symbol_a = "♦︎"
    symbol_i = "♢"
    empty = mana_max - mana
    active = [symbol_a for _ in range(mana)]
    incative = [symbol_i for _ in range(empty)]
    return f"[{mana}/{mana_max}] "+" ".join(active) +" "+ " ".join(incative)


class FancyLog:
    def __init__(self):
        self.log = ["" for _ in range(10)]

    def add(self, action: str):
        self.log.insert(0, action)

    def __iter__(self):
        return iter(self.log)

    def get(self, nb=10):
        return self.log[:nb]

    def print(self, index, whitespace=50):
        return self.log[index] + " " * (whitespace - len(self.log[index]))



def import_log(file: str) -> pandas.core.frame.DataFrame:
    with open(file, 'rb') as f:
        return pickle.load(f)


if __name__ == '__main__':
    fancylog = FancyLog()
    log = import_log("modelisation/logs_games.pickle")
    sample = {columns_logs[i]: elt for i, elt in enumerate(log.values[0])}

    players = [Player(sample["pseudo_j"], sample["classe_j"]), Player(sample["pseudo_adv"], sample["classe_adv"])]
    players[0].set_deck("test_deck.csv")
    players[1].set_deck("test_deck.csv")

    turn = 1
    side = 0

    for line in log.values[:10]:
        event = {columns_logs[i]: elt for i, elt in enumerate(line)}
        if event["action"] == "passer_tour":
            fancylog.add(f"{players[side].name} passe son tour.")
            if side == 0:
                side = 1
            else:
                side = 0
                turn += 1
        if event["action"] == "jouer_carte":
            fancylog.add(f"{players[side].name} joue {event['carte_jouee']}")

        players[0].mana, players[0].mana_max = event["mana_dispo_j"], event["mana_max_j"]
        players[0].hero.health = event["pv_j"]

        players[1].mana, players[1].mana_max = event["mana_max_adv"], event["mana_max_adv"]
        players[1].hero.health = event["pv_adv"]

        print("\n" * 50)
        print(event)
        log_width = 50

        print(fancylog.print(0) + f"Tour {turn}")
        print(fancylog.print(1) + fancy_mana(players[1].mana, players[1].mana_max))
        adv = fancy_hero(players[1].hero, playing=side == 1).split('\n')
        print(fancylog.print(2) + adv[0])
        print(fancylog.print(3) + adv[1])
        print(fancylog.print(4) + adv[2])
        print(fancylog.print(5))
        print(fancylog.print(6))
        print(fancylog.print(7))
        print(fancylog.print(8))
        jr = fancy_hero(players[0].hero, playing=side == 0).split("\n")
        print(fancylog.print(9) + jr[0])
        print(" "*log_width + jr[1])
        print(" "*log_width + jr[2])
        print(" "*log_width + fancy_mana(players[0].mana, players[0].mana_max))
        sleep(2)


