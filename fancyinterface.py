import pandas.core.frame

from Entities import *
from random import choice
import pickle

def center_text(text: str, length: int, filler=' ', bold=False) -> str:
    left = (length - len(text)) // 2
    right = length - left - len(text)
    if bold:
        text = f"\033[1m{text}\033[0m"
    centered_text = filler * left + text + filler * right
    return centered_text


def fancy_c(fancy_card: Card, active=False) -> str:
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


def fancy_l(cartes: list[Card], selection=False, mana=0) -> str:
    """ Return a str representing a card hand """
    card_ls = []
    for card in cartes:
        card_ls.append(fancy_c(card, card.cost <= mana))
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


def fancy_j(hero) -> str:
    """ Besoin d'une classe "Joueur" ou Héros """
    j_str = f"┌───────{hero.name}───────┐"

    return j_str


def import_log(file: str) -> pandas.core.frame.DataFrame:
    with open(file, 'rb') as f:
        return pickle.load(f)


if __name__ == '__main__':
    player = Player("KamionBen")
    player.set_deck("Chasseur", "basic_chasseur.csv")
    player.start_game()
    player.start_turn()
    print(fancy_l(player.hand, mana=player.mana))
    log = import_log("modelisation/logs_games.pickle")
    for elt in log.values:
        player = elt[71]
        action = elt[0]

        print([f"{i} : {a}" for i, a in enumerate(elt)])
        if action == "passer_tour":
            print(f"{player} passe son tour.")
        elif action == "jouer_carte":
            card = elt[1] if elt[1] != "" else elt[2]
            print(f"{player} joue {card}")


