import hearthstone, os, time
from hearthstone import cardxml
from hearthstone.enums import GameTag, Zone, CardType

from hslog.parser import LogParser
from hslog.export import EntityTreeExporter, BaseExporter, FriendlyPlayerExporter

directory = "C:\Program Files (x86)\Hearthstone\Logs"
logs_path = [x[0] for x in os.walk(directory)][-1] + "\\Power.log"
cards_db, _ = hearthstone.cardxml.load(locale="frFR")


def get_current_minions(player):
    minions = []
    for e in player.entities:
        if e.tags[GameTag.CONTROLLER] == player.tags[GameTag.CONTROLLER] and e.zone == Zone.PLAY:
            if GameTag.CARDTYPE in e.tags.keys() and e.tags[GameTag.CARDTYPE] == CardType.MINION:
                minions.append(e)
    return minions


i = 0
saved_minions1, saved_minions2 = [], []
while i != 1:
    parser = LogParser()
    with open(logs_path) as f:
        parser.read(f)
    packet_tree = parser.games[-1]
    exporter = EntityTreeExporter(packet_tree)
    export = exporter.export()
    game = export.game
    player1 = game.players[0]
    player2 = game.players[1]
    minions1 = [cards_db[x.card_id].name for x in get_current_minions(player1)]
    minions2 = [cards_db[x.card_id].name for x in get_current_minions(player2)]
    if (minions1 != saved_minions1) or (minions2 != saved_minions2):
        print("Joueur 1 : ", minions1)
        print("Joueur 2 : ", minions2)
        print('----------------------------------')
    saved_minions1 = minions1.copy()
    saved_minions2 = minions2.copy()

