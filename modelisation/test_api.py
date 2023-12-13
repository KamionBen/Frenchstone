import hearthstone, os, time
from hearthstone import cardxml, dbf
from hearthstone.enums import GameTag, Zone, CardType
from Entities import *

from hslog.parser import LogParser
from hslog.export import EntityTreeExporter, BaseExporter, FriendlyPlayerExporter

directory = "C:\Program Files (x86)\Hearthstone\Logs"
logs_path = [x[0] for x in os.walk(directory)][-1] + "\\Power.log"
cards_db, _ = hearthstone.cardxml.load(locale="frFR")


def get_current_inputs(player):
    player_hand, player_deck = [], []
    minions = []
    hero = {}
    for e in player.entities:
        """ Héros """
        if GameTag.CARDTYPE in e.tags.keys() and e.tags[GameTag.CARDTYPE] == CardType.HERO:
            hero["health"] = e.tags[GameTag.HEALTH]
        """ Main """
        if GameTag.ZONE in e.tags.keys() and e.tags[GameTag.ZONE] == Zone.HAND:
            card_name = cards_db[e.card_id].name
            card_name = card_name.replace("'", "\'").replace("’", "\'").replace("-", " ").replace("Œ", "Oe").lower().capitalize()
            card = get_card(card_name, name_index)
            card.cost = e.tags[GameTag.COST] if GameTag.COST in e.tags.keys() else 0
            if card.type == "Serviteur":
                card.boost(e.tags[GameTag.ATK] if GameTag.ATK in e.tags.keys() else 0, e.tags[GameTag.HEALTH], fixed_stats=True)
            player_hand.insert(0, card)
        """ Deck """

        """ Plateau """
        if e.tags[GameTag.CONTROLLER] == player.tags[GameTag.CONTROLLER] and e.zone == Zone.PLAY:
            if GameTag.CARDTYPE in e.tags.keys() and e.tags[GameTag.CARDTYPE] == CardType.MINION:
                minions.append(e)
    return {"hero": hero, "player_hand": player_hand, "player_deck": player_deck}


parser = LogParser()
with open(logs_path) as f:
    parser.read(f)
packet_tree = parser.games[-1]
exporter = EntityTreeExporter(packet_tree)
export = exporter.export()
game = export.game
player1 = game.players[0]
player2 = game.players[1]
# print(get_current_inputs(player2)["player_hand"])
# print(get_current_inputs(player2)["player_deck"])
# minions1 = [cards_db[x.card_id].name for x in get_current_minions(player1)]
# minions2 = [cards_db[x.card_id].name for x in get_current_minions(player2)]
for e in player2.entities:
    if GameTag.ZONE in e.tags.keys() and e.tags[GameTag.ZONE] == Zone.DECK:
        print(e.tags)
        print('----------------------------------')

