from Entities import *


def fancy_c(fancy_card: Card, active=False) -> str:
    """ Return a str representing a single card """
    if active:
        a, e = '\033[92m', '\033[0m'  # GREEN, ENDC
    else:
        a, e = '', ''

    length = 25
    f_card = f"{a}┌"+"─"*(length-2)+f"┐{e}\n"
    f_card += f"{a}│{e} C={fancy_card.cost}  \033[1m{fancy_card.name}\033[0m" + " " * ((length - 9) - len(fancy_card.name)) + f" {a}│{e}\n"
    f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    f_card += f"{a}│{e} A={fancy_card.attack}" + " " * (length - 10) + f"H={fancy_card.health} {a}│{e}\n"

    type = f"Type={fancy_card.type.capitalize()}"

    f_card += f"{a}└"+"─"*(int((length-2)/2-len(type)/2))+f"{e}{type}{a}"+"─"*(int((length-2)/2-len(type)/2)+1)+f"┘{e}"
    return f_card


def fancy_l(cartes: list[Card], selection=False) -> str:
    """ Return a str representing a card hand """
    cards_l = [fancy_c(c).split('\n') for c in cartes]
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


if __name__ == '__main__':
    player = Player("KamionBen")
    player.set_deck("Chasseur", "basic_chasseur.csv")
    for card in player.deck:
        print(fancy_c(card))
