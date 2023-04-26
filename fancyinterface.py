from cartes import *


def fancy_c(carte: Carte, active=False)->str:
    """ Return a str representing a single card """
    if active:
        a, e = '\033[92m', '\033[0m'  # GREEN, ENDC
    else:
        a, e = '', ''

    length = 25
    f_card = f"{a}┌"+"─"*(length-2)+f"┐{e}\n"
    f_card += f"{a}│{e} C={carte.cout}  \033[1m{carte.nom}\033[0m"+" "*((length-9)-len(carte.nom))+f" {a}│{e}\n"
    f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    f_card += f"{a}│" + " " * (length - 2) + f"│{e}\n"
    f_card += f"{a}│{e} A={carte.attaque}" + " " * (length - 10) + f"H={carte.PV} {a}│{e}\n"

    type = f"Type={carte.type.capitalize()}"

    f_card += f"{a}└"+"─"*(int((length-2)/2-len(type)/2))+f"{e}{type}{a}"+"─"*(int((length-2)/2-len(type)/2)+1)+f"┘{e}"
    return f_card


def fancy_l(cartes: list[Carte], selection=False)->str:
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

def fancy_j(joueur)->str:
    """ Besoin d'une classe "Joueur" ou Héros """
    j_str = "┌───────────────────────┐"

    return j_str


if __name__ == '__main__':
    print("\nLa liste de cartes, présentée horizontalement, avec l'entete de sélection")
    print(fancy_l(all_cartes, selection=True))

    print("La liste de cartes, une par une, dont la première en vert")
    for i, carte in enumerate(all_cartes):
        if i == 0:
            print(fancy_c(carte, active=True))
        else:
            print(fancy_c(carte))