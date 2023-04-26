from cartes import *


def fancy_c(carte: Carte)->str:
    """ Return a str representing a single card """
    length = 25
    f_card = "┌"+"─"*(length-2)+"┐\n"
    f_card += f"│ C={carte.cout}  {carte.nom}"+" "*((length-9)-len(carte.nom))+" │\n"
    f_card += "│" + " " * (length - 2) + "│\n"
    f_card += "│" + " " * (length - 2) + "│\n"
    f_card += f"│ A={carte.attaque}" + " " * (length - 10) + f"H={carte.PV} │\n"

    type = f"Type={carte.type.capitalize()}"

    f_card += f"└"+"─"*(int((length-2)/2-len(type)/2))+type+"─"*(int((length-2)/2-len(type)/2)+1)+"┘"
    return f_card


def fancy_l(cartes: list[Carte])->str:
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
    for line in cards_dict.values():
        cards_str += line + "\n"

    return cards_str

if __name__ == '__main__':
    print("\nLa liste de cartes, présentée horizontalement")
    print(fancy_l(all_cartes))

    print(("La liste de cartes, une par une"))
    for carte in all_cartes:
        print(fancy_c(carte))