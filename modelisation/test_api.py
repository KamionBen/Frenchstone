import hearthstone, os, time
from hearthstone import cardxml, dbf
from hearthstone.enums import GameTag, Zone, CardType
from best_output import *
from hslog.parser import LogParser
from hslog.export import EntityTreeExporter, BaseExporter, FriendlyPlayerExporter
from unidecode import unidecode

directory = "C:\Program Files (x86)\Hearthstone\Logs"
logs_path = [x[0] for x in os.walk(directory)][-1] + "\\Power.log"
cards_db, _ = hearthstone.cardxml.load(locale="frFR")


def standardize_name(name):
    name = unidecode(name)
    name = name.replace("'", "\'").replace("’", "\'").replace("-", " ").replace("Œ", "Oe").replace("œ", "oe").lower()
    name = name.replace("é", "e").replace("â", "a").replace("à", "a").replace("î", "i").replace("è", "e").replace("ê", "e").replace("ë", "e")
    name = name.replace(",", "").replace(" !", "").replace("ç", "c")
    name = name.capitalize()
    return name


def guess_player(game):
    tester = [(x.card_id, x.tags[GameTag.CONTROLLER]) for x in game.entities if GameTag.CONTROLLER in x.tags.keys() and x.zone == Zone.HAND][0]
    if tester[0] is not None:
        player_number = tester[1]
    else:
        player_number = 2 if tester[1] == 1 else 1
    return player_number


def get_current_inputs(game, player_number):
    player_hand, player_deck = [], []
    player_servants, adv_servants = [], []
    discovery = [[]]
    hero, hero_adv = {"weapon": None}, {"weapon": None}
    for e in [x for x in game.entities if GameTag.CONTROLLER in x.tags.keys()]:
        if e.tags[GameTag.CONTROLLER] == player_number:
            """ Héros """
            if e.type == CardType.HERO:
                damage_hero = e.tags[GameTag.DAMAGE] if GameTag.DAMAGE in e.tags.keys() else 0
                hero["health"] = e.tags[GameTag.HEALTH] - damage_hero
                hero["base_health"] = e.tags[GameTag.HEALTH]
                hero["attack"] = e.tags[GameTag.ATK] if GameTag.ATK in e.tags.keys() else 0
                hero["armor"] = e.tags[GameTag.ARMOR] if GameTag.ARMOR in e.tags.keys() else 0
                if GameTag.EXHAUSTED in e.tags.keys():
                    hero["remaining_atk"] = 1 if not e.tags[GameTag.EXHAUSTED] else 0
                else:
                    hero["remaining_atk"] = 1
            elif e.type == CardType.HERO_POWER:
                hero["cost_hp"] = e.tags[GameTag.COST]
                hero["dispo_hp"] = 1 if (GameTag.EXHAUSTED in e.tags.keys() and not e.tags[GameTag.EXHAUSTED]) else 0
            elif e.type == CardType.PLAYER:
                used_resources = e.tags[GameTag.RESOURCES_USED] if GameTag.RESOURCES_USED in e.tags.keys() else 0
                resources = e.tags[GameTag.RESOURCES] if GameTag.RESOURCES in e.tags.keys() else 0
                hero["mana"] = resources - used_resources
                hero["mana_max"] = resources
            elif e.zone == Zone.HAND:
                card_name = standardize_name(cards_db[e.card_id].name)
                card = get_card(card_name, name_index)
                card.cost = e.tags[GameTag.COST] if GameTag.COST in e.tags.keys() else 0
                if card.type == "Serviteur":
                    card.boost(e.tags[GameTag.ATK] if GameTag.ATK in e.tags.keys() else 0, e.tags[GameTag.HEALTH], fixed_stats=True)
                player_hand.insert(0, card)
            elif e.zone == Zone.PLAY:
                if e.type == CardType.MINION:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_servants)
                    card.cost = e.tags[GameTag.COST] if GameTag.COST in e.tags.keys() else 0
                    card.boost(e.tags[GameTag.ATK] if GameTag.ATK in e.tags.keys() else 0, e.tags[GameTag.HEALTH], fixed_stats=True)
                    card.blessure = e.tags[GameTag.DAMAGE] if GameTag.DAMAGE in e.tags.keys() else 0
                    card.health = e.tags[GameTag.HEALTH] - card.blessure
                    if GameTag.DIVINE_SHIELD in e.tags.keys():
                        if e.tags[GameTag.DIVINE_SHIELD] == 1:
                            card.effects["bouclier divin"] = 1
                        else:
                            if "bouclier divin" in card.effects:
                                card.effects.pop("bouclier divin")
                    if GameTag.TAUNT in e.tags.keys():
                        if e.tags[GameTag.TAUNT] == 1:
                            card.effects["provocation"] = 1
                        else:
                            if "provocation" in card.effects:
                                card.effects.pop("provocation")
                    if GameTag.WINDFURY in e.tags.keys():
                        if e.tags[GameTag.WINDFURY] == 1:
                            card.effects["furie des vents"] = 1
                        else:
                            if "furie des vents" in card.effects:
                                card.effects.pop("furie des vents")
                    if GameTag.STEALTH in e.tags.keys():
                        if e.tags[GameTag.STEALTH] == 1:
                            card.effects["camouflage"] = 1
                        else:
                            if "camouflage" in card.effects:
                                card.effects.pop("camouflage")
                    if GameTag.FREEZE in e.tags.keys():
                        if e.tags[GameTag.FREEZE] == 1:
                            card.effects["gel"] = 1
                        else:
                            if "gel" in card.effects:
                                card.effects.pop("gel")
                    if GameTag.REBORN in e.tags.keys():
                        if e.tags[GameTag.REBORN] == 1:
                            card.effects["reincarnation"] = 1
                        else:
                            if "reincarnation" in card.effects:
                                card.effects.pop("reincarnation")
                    if GameTag.EXHAUSTED in e.tags.keys():
                        card.remaining_atk = 1 if not e.tags[GameTag.EXHAUSTED] else 0
                        if GameTag.JUST_PLAYED in e.tags.keys() and e.tags[GameTag.JUST_PLAYED]:
                            card.remaining_atk = 0
                    else:
                        card.remaining_atk = 1
                    player_servants.insert(0, card)
                elif e.type == CardType.WEAPON:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_weapons)
                    card.health = e.tags[GameTag.DURABILITY]
                    hero["weapon"] = card
            elif e.zone == Zone.SETASIDE:
                if 2509 in e.tags.keys():
                    card_name = standardize_name(cards_db[e.card_id].name)
                    if card_name != "Jeune naga":
                        card = get_card(card_name, name_index)
                        discovery[0].append(card)
        else:
            if e.type == CardType.HERO:
                damage_hero = e.tags[GameTag.DAMAGE] if GameTag.DAMAGE in e.tags.keys() else 0
                hero_adv["health"] = e.tags[GameTag.HEALTH] - damage_hero
                hero_adv["base_health"] = e.tags[GameTag.HEALTH]
                hero_adv["armor"] = e.tags[GameTag.ARMOR] if GameTag.ARMOR in e.tags.keys() else 0
            elif e.type == CardType.PLAYER:
                resources = e.tags[GameTag.RESOURCES] if GameTag.RESOURCES in e.tags.keys() else 0
                hero_adv["mana_max"] = resources
            elif e.zone == Zone.PLAY:
                if e.type == CardType.MINION:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_servants)
                    card.cost = e.tags[GameTag.COST] if GameTag.COST in e.tags.keys() else 0
                    card.boost(e.tags[GameTag.ATK] if GameTag.ATK in e.tags.keys() else 0, e.tags[GameTag.HEALTH],
                               fixed_stats=True)
                    card.blessure = e.tags[GameTag.DAMAGE] if GameTag.DAMAGE in e.tags.keys() else 0
                    card.health = e.tags[GameTag.HEALTH] - card.blessure
                    if GameTag.DIVINE_SHIELD in e.tags.keys():
                        if e.tags[GameTag.DIVINE_SHIELD] == 1:
                            card.effects["bouclier divin"] = 1
                        else:
                            if "bouclier divin" in card.effects:
                                card.effects.pop("bouclier divin")
                    if GameTag.TAUNT in e.tags.keys():
                        if e.tags[GameTag.TAUNT] == 1:
                            card.effects["provocation"] = 1
                        else:
                            if "provocation" in card.effects:
                                card.effects.pop("provocation")
                    if GameTag.WINDFURY in e.tags.keys():
                        if e.tags[GameTag.WINDFURY] == 1:
                            card.effects["furie des vents"] = 1
                        else:
                            if "furie des vents" in card.effects:
                                card.effects.pop("furie des vents")
                    if GameTag.STEALTH in e.tags.keys():
                        if e.tags[GameTag.STEALTH] == 1:
                            card.effects["camouflage"] = 1
                        else:
                            if "camouflage" in card.effects:
                                card.effects.pop("camouflage")
                    if GameTag.FREEZE in e.tags.keys():
                        if e.tags[GameTag.FREEZE] == 1:
                            card.effects["gel"] = 1
                        else:
                            if "gel" in card.effects:
                                card.effects.pop("gel")
                    if GameTag.REBORN in e.tags.keys():
                        if e.tags[GameTag.REBORN] == 1:
                            card.effects["reincarnation"] = 1
                        else:
                            if "reincarnation" in card.effects:
                                card.effects.pop("reincarnation")
                    adv_servants.insert(0, card)
                elif e.type == CardType.WEAPON:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_weapons)
                    card.health = e.tags[GameTag.DURABILITY]
                    hero_adv["weapon"] = card
    return {"hero": hero, "hero_adv": hero_adv, "player_hand": player_hand, "player_servants": player_servants, "adv_servants": adv_servants, "discovery": discovery}


def modify_plateau(plateau, game, player_number=None):
    player = plateau.players[0]
    adv = plateau.players[1]
    actual_state = get_current_inputs(game, player_number=player_number)
    player.health = actual_state["hero"]["health"]
    player.base_health = actual_state["hero"]["base_health"]
    player.armor = actual_state["hero"]["armor"]
    player.attack = actual_state["hero"]["attack"]
    player.inter_attack = actual_state["hero"]["attack"]
    player.remaining_atk = actual_state["hero"]["remaining_atk"]
    player.mana = actual_state["hero"]["mana"]
    player.mana_max = actual_state["hero"]["mana_max"]
    player.dispo_pouvoir = True if actual_state["hero"]["dispo_hp"] else False
    player.cout_pouvoir_temp = actual_state["hero"]["cost_hp"]
    player.weapon = actual_state["hero"]["weapon"]
    adv.health = actual_state["hero_adv"]["health"]
    adv.base_health = actual_state["hero_adv"]["base_health"]
    adv.armor = actual_state["hero_adv"]["armor"]
    adv.mana_max = actual_state["hero_adv"]["mana_max"]
    adv.weapon = actual_state["hero_adv"]["weapon"]
    player.hand.cards = actual_state["player_hand"]
    player.servants.cards = actual_state["player_servants"]
    adv.servants.cards = actual_state["adv_servants"]
    if actual_state["discovery"] != [[]]:
        plateau.cards_chosen = actual_state["discovery"]
    return plateau


class_j = "Paladin"
class_adv = "Druide"
deck_j = ["pala_aggro.csv", "aggro"]
deck_adv = random.choice(class_files[class_adv])
players = [Player("Smaguy", class_j, import_deck(deck_j[0]), style_deck=deck_j[1]), Player("Adversaire", class_adv, import_deck(deck_adv[0]), style_deck=deck_adv[1])].copy()
plateau_depart = Plateau(pickle.loads(pickle.dumps(players, -1)))
game_prec, player_number, last_discovery = None, None, 1

while True:
    parser = LogParser()
    with open(logs_path) as f:
        parser.read(f)
    packet_tree = parser.games[-1]
    exporter = EntityTreeExporter(packet_tree)
    export = exporter.export()
    running_game = export.game
    if player_number is None:
        player_number = guess_player(running_game)
    potential_discovery = [x for x in running_game.entities if x.zone == Zone.SETASIDE and 2509 in x.tags.keys()]

    if (game_prec != running_game.tags) or (potential_discovery and last_discovery == 1):
        if potential_discovery:
            last_discovery = 0
        else:
            last_discovery = 1
        print('                            ')
        print('%%%%%%%%% RUNNING %%%%%%%%%%')
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        plateau_reel = modify_plateau(pickle.loads(pickle.dumps(plateau_depart, -1)), running_game, player_number=player_number)
        max_reward, best_action = return_best_action(plateau_reel)
        game_prec = running_game.tags

# parser = LogParser()
# with open(logs_path) as f:
#     parser.read(f)
# packet_tree = parser.games[-1]
# exporter = EntityTreeExporter(packet_tree)
# export = exporter.export()
# running_game = export.game
# for e in running_game.entities:
#     print(e.tags)
#     print('----------------------------------')

