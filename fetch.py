import requests
import json
from bs4 import BeautifulSoup


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


def get_cardstat_from_page(url: str) -> dict:
    """ Return the card stats from the correct url """
    if url[:33] != "https://www.hearthstone-decks.com":
        url = "https://www.hearthstone-decks.com"+url
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        card = {"name": None, "classe": None, "type": None, "genre": None,
                "cost": None, "attack": None, "health": None, "description": None}
        tbody = soup.find_all("td")
        for i, elt in enumerate(tbody):
            elt = elt.getText()
            if elt == "Nom":
                card["name"] = tbody[i + 1].getText()
            if elt == "Coût en mana":
                card["cost"] = int(tbody[i + 1].getText())
            if elt == "École" or elt == "Race":
                card["genre"] = tbody[i + 1].getText()
            if elt == "Description":
                card["description"] = tbody[i + 1].getText()
            if elt == "Attaque":
                sugar = tbody[i + 1].getText()
                if sugar is not None:
                    sugar = int(sugar)
                card["attack"] = sugar
            if elt == "Vie":
                sugar = tbody[i + 1].getText()
                if sugar is not None:
                    sugar = int(sugar)
                card["health"] = sugar
            if elt == "Classe":
                card["classe"] = tbody[i + 1].getText()[1:]  # Pour enlever le vide laissé par le logo
            if elt == "Type":
                card["type"] = tbody[i + 1].getText()

        return card
    else:
        raise ValueError(f"{url} est inaccessible")


def fetch_all():
    """ Va chercher les cartes de base et les enregistre dans un json """
    cards_file = "cards.json"

    card_list = []

    page = requests.get("https://www.hearthstone-decks.com/carte/set-de-base", allow_redirects=True)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        div = soup.find_all("div", {"class": "carte_galerie_container"})
        for page in div:
            card = get_cardstat_from_page(page.a.get("href"))
            card_list.append(card)

    with open(cards_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(card_list, jsonfile, indent=4, ensure_ascii=False)


def add_card(card, file):
    with open(file, 'r', encoding='utf-8') as jsonfile:
        cardls = json.load(jsonfile)
    exist = False
    for carddict in cardls:
        if carddict['name'] == card['name']:
            exist = True
            break
    if exist:
        print(f"La carte {card['name']} est déjà connue.")
    else:
        cardls.sort(key=lambda c: c['id'])
        new_card = {'id': cardls[-1]['id'] + 1}
        for key, value in card.items():
            new_card[key] = value
        print(new_card)
        if len(cardls) > 1:
            cardls.append(new_card)
        with open(file, 'w', encoding='utf-8') as jsonfile:
            json.dump(cardls, jsonfile, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    """ Mettez l'url de la carte que vous voulez rajouter et lancez le script """
    url = "https://www.hearthstone-decks.com/carte/voir/malefice-classic"
    card = get_cardstat_from_page(url)
    #add_card(card, "cards.json")
    add_card(card, "cards.json")




