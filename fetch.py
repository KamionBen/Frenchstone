import requests
import json
from bs4 import BeautifulSoup


def get_cardstat_from_page(url: str) -> dict:
    """ Return the card stats from the correct url """
    if url[:33] != "https://www.hearthstone-decks.com":
        url = "https://www.hearthstone-decks.com"+url
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        card = {"NAME": None, "CATEGORY": None, "TYPE": None, "COST": None,
                "ATK": None, "PV": None, "DESCR": None, "CLASS": None}
        tbody = soup.find_all("td")
        for i, elt in enumerate(tbody):
            elt = elt.getText()
            if elt == "Nom":
                card["NAME"] = tbody[i + 1].getText()
            if elt == "Coût en mana":
                card["COST"] = tbody[i + 1].getText()
            if elt == "École":
                card["TYPE"] = tbody[i + 1].getText()
            if elt == "Description":
                card["DESCR"] = tbody[i + 1].getText()
            if elt == "Attaque":
                card["ATK"] = tbody[i + 1].getText()
            if elt == "Vie":
                card["PV"] = tbody[i + 1].getText()
            if elt == "Classe":
                card["CLASS"] = tbody[i + 1].getText()

        return card
    else:
        raise ValueError(f"{url} est inaccessible")


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



