import hearthstone, os, time
from hearthstone import cardxml, dbf
from hearthstone.enums import GameTag, Zone, CardType
from best_output import *
from hslog.parser import LogParser
from hslog.export import EntityTreeExporter, BaseExporter, FriendlyPlayerExporter
from unidecode import unidecode
from collections import Counter

directory = "C:\Program Files (x86)\Hearthstone\Logs"
logs_path = [x[0] for x in os.walk(directory)][-1] + "\\Power.log"
cards_db, _ = hearthstone.cardxml.load(locale="frFR")


def standardize_name(name):
    name = unidecode(name)
    name = name.replace("'", "\'").replace("’", "\'").replace("-", " ").replace("Œ", "Oe").replace("œ", "oe").lower()
    name = name.replace("é", "e").replace("â", "a").replace("à", "a").replace("î", "i").replace("è", "e").replace("ê", "e").replace("ë", "e")
    name = name.replace(",", "").replace(".", "").replace(" !", "").replace("ç", "c")
    name = name.capitalize()
    return name


def guess_player(game):
    tester = [(x.card_id, x.tags[GameTag.CONTROLLER]) for x in game.entities if GameTag.CONTROLLER in x.tags.keys() and x.zone == Zone.HAND]
    for test in tester:
        if test[0] is None:
            return 2 if test[1] == 1 else 1


def mulligan_help(cards_mulligan, deck):
    deck_wr = {"Protectrice vertueuse": 65.2,
                "Soldate sanguine": 66.5,
                "Sous cheffe immorale": 66.7,
                "En avant aile argent": 67,
                "Liadrin matriarche de sang": 60.8,
                "Main d'a'dal": 61.7,
                "Pour quel'thalas": 60.8,
                "Boogie sans fin": 67.8,
                "Regiment de bataille": 64.6,
                "Sceau de sang": 61.9,
                "Groga vorace": 66.2,
                "Aura des croises": 61.9,
                "Force de la gardienne": 62.4,
                "Le purificateur": 52,
                "Cor du seigneur des vents": 57,
                "La comtesse": 60.1,
                "Leviathan": 58.3,
                "Raie de lumiere": 52.1}

    remaining_deck = list((Counter(deck) - Counter(cards_mulligan)).elements())

    for card in cards_mulligan:
        if card != "La piece":
            actual_value = deck_wr[card]
            potential_value = sum([deck_wr[x] for x in remaining_deck])/len(remaining_deck)
            if actual_value > potential_value:
                print(card, "Keep")
            else:
                print(card, "Discard")


def guess_deck_adv(game, player_number, class_deck):
    adv_cards, num_common, best_guess = [], 0, []
    for e in [x for x in game.entities if GameTag.CONTROLLER in x.tags.keys()]:
        if e.tags[GameTag.CONTROLLER] != player_number:
            if e.zone == Zone.GRAVEYARD:
                card_name = standardize_name(cards_db[e.card_id].name)
                adv_cards.append(card_name)
            elif e.zone == Zone.PLAY:
                if e.type == CardType.MINION or e.type == CardType.WEAPON:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    adv_cards.append(card_name)
    for deck in class_files[class_deck]:
        deck_names = [x.name for x in import_deck(deck[0])]
        common_cards = list((Counter(deck_names) & Counter(adv_cards)).elements())
        if len(common_cards) > num_common:
            num_common = len(common_cards)
            best_guess = deck_names
    if best_guess:
        return best_guess
    else:
        return deck_names


def get_current_inputs(game, player_number):
    player_hand, adv_hand, player_left_deck, adv_left_deck, player_secrets, player_attached = [None] * 11, [], [], [], [], []
    player_servants, adv_servants = [], []
    discovery = [[]]
    hero = {"weapon": None, "all_dead_servants": [], "cards_played": [], "mulligan_state": False}
    hero_adv = {"weapon": None, "all_dead_servants": [], "cards_played": []}
    for e in [x for x in game.entities if (GameTag.CONTROLLER in x.tags.keys() or x.type == CardType.GAME)]:
        if e.type == CardType.GAME:
            if GameTag.TURN in e.tags.keys() and e.tags[GameTag.TURN] == 1:
                hero["mulligan_state"] = True
        elif e.tags[GameTag.CONTROLLER] == player_number:
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
                hero["dispo_hp"] = 1 if ((GameTag.EXHAUSTED in e.tags.keys() and not e.tags[GameTag.EXHAUSTED]) or (not GameTag.EXHAUSTED in e.tags.keys())) else 0
            elif e.type == CardType.PLAYER:
                used_resources = e.tags[GameTag.RESOURCES_USED] if GameTag.RESOURCES_USED in e.tags.keys() else 0
                resources = e.tags[GameTag.RESOURCES] if GameTag.RESOURCES in e.tags.keys() else 0
                hero["mana"] = resources - used_resources
                hero["mana_max"] = resources
                hero["cadavres"] = e.tags[GameTag.CORPSES] if GameTag.CORPSES in e.tags.keys() else 0
                hero["played_this_turn"] = e.tags[GameTag.NUM_CARDS_PLAYED_THIS_TURN] if GameTag.NUM_CARDS_PLAYED_THIS_TURN in e.tags.keys() else 0
                hero["drawn_this_turn"] = e.tags[GameTag.NUM_CARDS_DRAWN_THIS_TURN] if GameTag.NUM_CARDS_DRAWN_THIS_TURN in e.tags.keys() else 0
            elif e.zone == Zone.HAND:
                card_name = standardize_name(cards_db[e.card_id].name)
                position = e.tags[GameTag.ZONE_POSITION] - 1
                card = get_card(card_name, name_index)
                if GameTag.INFUSE in e.tags.keys():
                    if e.tags[GameTag.INFUSE] == 1:
                        card.effects["impregnation"][1] = e.tags[GameTag.TAG_SCRIPT_DATA_NUM_1]
                    else:
                        if e.tags[GameTag.INFUSED] == 1:
                            card = get_card(card.effects["impregnation"][0], name_index)
                card.cost = e.tags[GameTag.COST] if GameTag.COST in e.tags.keys() else 0
                if card.type == "Serviteur":
                    card.boost(e.tags[GameTag.ATK] if GameTag.ATK in e.tags.keys() else 0, e.tags[GameTag.HEALTH], fixed_stats=True)
                player_hand[position] = card
                player_left_deck.append(card_name)
            elif e.zone == Zone.GRAVEYARD:
                card_name = standardize_name(cards_db[e.card_id].name)
                player_left_deck.append(card_name)
                if e.type == CardType.MINION:
                    hero["all_dead_servants"].append(card_name)
                if GameTag.JUST_PLAYED in e.tags.keys():
                    hero["cards_played"].append(card_name)
            elif e.zone == Zone.PLAY:
                if e.type == CardType.MINION:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_servants)
                    if GameTag.INFUSE in e.tags.keys():
                        if e.tags[GameTag.INFUSE] == 1:
                            card.effects["impregnation"][1] = e.tags[GameTag.TAG_SCRIPT_DATA_NUM_1]
                        else:
                            if e.tags[GameTag.INFUSED] == 1:
                                card = get_card(card.effects["impregnation"][0], name_index)
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
                    if GameTag.RUSH in e.tags.keys():
                        if e.tags[GameTag.RUSH] == 1:
                            card.effects["ruée"] = 1
                        else:
                            if "ruée" in card.effects:
                                card.effects.pop("ruée")
                    if GameTag.CHARGE in e.tags.keys():
                        if e.tags[GameTag.CHARGE] == 1:
                            card.effects["charge"] = 1
                        else:
                            if "charge" in card.effects:
                                card.effects.pop("charge")
                    if GameTag.EXHAUSTED in e.tags.keys():
                        card.remaining_atk = 1 if not e.tags[GameTag.EXHAUSTED] else 0
                        if GameTag.JUST_PLAYED in e.tags.keys() and e.tags[GameTag.JUST_PLAYED] and not GameTag.RUSH in e.tags.keys():
                            card.remaining_atk = 0
                    else:
                        card.remaining_atk = 1
                    player_servants.insert(0, card)
                    player_left_deck.append(card_name)
                elif e.type == CardType.WEAPON:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_weapons)
                    card.health = e.tags[GameTag.DURABILITY]
                    hero["weapon"] = card
                if GameTag.JUST_PLAYED in e.tags.keys():
                    card_name = standardize_name(cards_db[e.card_id].name)
                    hero["cards_played"].append(card_name)
            elif e.zone == Zone.SETASIDE:
                if 2509 in e.tags.keys():
                    card_name = standardize_name(cards_db[e.card_id].name)
                    if card_name != "Jeune naga":
                        card = get_card(card_name, name_index)
                        discovery[0].append(card)
            elif e.zone == Zone.SECRET:
                card_name = standardize_name(cards_db[e.card_id].name)
                card = get_card(card_name, name_index_spells)
                if "secret" in card.effects:
                    player_secrets.append(card)
                else:
                    for element in card.effects["attach_hero"]:
                        player_attached.append(element)
        else:
            if e.type == CardType.HERO:
                damage_hero = e.tags[GameTag.DAMAGE] if GameTag.DAMAGE in e.tags.keys() else 0
                hero_adv["health"] = e.tags[GameTag.HEALTH] - damage_hero
                hero_adv["base_health"] = e.tags[GameTag.HEALTH]
                hero_adv["armor"] = e.tags[GameTag.ARMOR] if GameTag.ARMOR in e.tags.keys() else 0
            elif e.type == CardType.HERO_POWER:
                hero_adv["cost_hp"] = e.tags[GameTag.COST]
                hero_adv["dispo_hp"] = 1 if ((GameTag.EXHAUSTED in e.tags.keys() and not e.tags[GameTag.EXHAUSTED]) or (not GameTag.EXHAUSTED in e.tags.keys())) else 0
            elif e.type == CardType.PLAYER:
                used_resources = e.tags[GameTag.RESOURCES_USED] if GameTag.RESOURCES_USED in e.tags.keys() else 0
                resources = e.tags[GameTag.RESOURCES] if GameTag.RESOURCES in e.tags.keys() else 0
                cadavres = e.tags[GameTag.CORPSES] if GameTag.CORPSES in e.tags.keys() else 0
                hero_adv["mana"] = resources - used_resources
                hero_adv["mana_max"] = resources
                hero_adv["cadavres"] = cadavres
                hero_adv["played_this_turn"] = e.tags[GameTag.NUM_CARDS_PLAYED_THIS_TURN] if GameTag.NUM_CARDS_PLAYED_THIS_TURN in e.tags.keys() else 0
                hero_adv["drawn_this_turn"] = e.tags[GameTag.NUM_CARDS_DRAWN_THIS_TURN] if GameTag.NUM_CARDS_DRAWN_THIS_TURN in e.tags.keys() else 0
            elif e.zone == Zone.HAND:
                adv_hand.append(get_card("", name_index))
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
                    if GameTag.RUSH in e.tags.keys():
                        if e.tags[GameTag.RUSH] == 1:
                            card.effects["ruée"] = 1
                        else:
                            if "ruée" in card.effects:
                                card.effects.pop("ruée")
                    if GameTag.CHARGE in e.tags.keys():
                        if e.tags[GameTag.CHARGE] == 1:
                            card.effects["charge"] = 1
                        else:
                            if "charge" in card.effects:
                                card.effects.pop("charge")
                    adv_servants.insert(0, card)
                    adv_left_deck.append(card_name)
                elif e.type == CardType.WEAPON:
                    card_name = standardize_name(cards_db[e.card_id].name)
                    card = get_card(card_name, name_index_weapons)
                    card.health = e.tags[GameTag.DURABILITY]
                    hero_adv["weapon"] = card
                if GameTag.JUST_PLAYED in e.tags.keys():
                    card_name = standardize_name(cards_db[e.card_id].name)
                    hero_adv["cards_played"].append(card_name)
            elif e.zone == Zone.GRAVEYARD:
                card_name = standardize_name(cards_db[e.card_id].name)
                if e.type == CardType.MINION:
                    hero_adv["all_dead_servants"].append(card_name)
                if GameTag.JUST_PLAYED in e.tags.keys():
                    hero_adv["cards_played"].append(card_name)
                adv_left_deck.append(card_name)
    return {"hero": hero, "hero_adv": hero_adv, "player_hand": player_hand, "adv_hand": adv_hand, "player_servants": player_servants, "player_left_deck": player_left_deck,
            "player_secrets": player_secrets, "player_attached": player_attached, "adv_servants": adv_servants, "discovery": discovery, "adv_left_deck": adv_left_deck}


def modify_plateau(plateau, game, player_number=None):
    player = plateau.players[0]
    adv = plateau.players[1]
    actual_state = get_current_inputs(game, player_number=player_number)
    left_deck = actual_state["player_left_deck"]
    initial_deck = [x.name for x in player.deck.cards + player.hand.cards]
    remaining_deck = list((Counter(initial_deck)-Counter(left_deck)).elements())
    left_deck_adv = actual_state["adv_left_deck"]
    initial_deck_adv = guess_deck_adv(game, player_number, adv.classe)
    remaining_deck_adv = list((Counter(initial_deck_adv) - Counter(left_deck_adv)).elements())
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
    player.cadavres = actual_state["hero"]["cadavres"]
    player.cards_this_turn = actual_state["hero"]["played_this_turn"] * [""]
    player.drawn_this_turn = actual_state["hero"]["drawn_this_turn"]
    player.deck.cards = [get_card(x, name_index) for x in remaining_deck]
    player.all_dead_servants = actual_state["hero"]["all_dead_servants"]
    player.cards_played = actual_state["hero"]["cards_played"]
    player.hand.cards = [x for x in actual_state["player_hand"] if x is not None]
    player.servants.cards = actual_state["player_servants"]
    player.attached = actual_state["player_attached"]
    player.secrets.cards = actual_state["player_secrets"]

    ########## ADVERSAIRE ############

    adv.health = actual_state["hero_adv"]["health"]
    adv.base_health = actual_state["hero_adv"]["base_health"]
    adv.armor = actual_state["hero_adv"]["armor"]
    adv.mana = actual_state["hero_adv"]["mana"]
    adv.mana_max = actual_state["hero_adv"]["mana_max"]
    adv.dispo_pouvoir = True if actual_state["hero_adv"]["dispo_hp"] else False
    adv.cout_pouvoir_temp = actual_state["hero_adv"]["cost_hp"]
    adv.weapon = actual_state["hero_adv"]["weapon"]
    adv.attack, adv.inter_attack = 0, 0
    adv.cadavres = actual_state["hero_adv"]["cadavres"]
    adv.cards_this_turn = actual_state["hero_adv"]["played_this_turn"] * [""]
    adv.drawn_this_turn = actual_state["hero_adv"]["drawn_this_turn"]
    if actual_state["adv_hand"]:
        hand_names = random.choices(remaining_deck_adv, k=len(actual_state["adv_hand"]))
    else:
        hand_names = []
    deck_names = list((Counter(remaining_deck_adv) - Counter(hand_names)).elements())
    adv.hand.cards = [get_card(x, name_index) for x in hand_names]
    adv.deck.cards = [get_card(x, name_index) for x in deck_names]
    adv.all_dead_servants = actual_state["hero_adv"]["all_dead_servants"]
    adv.cards_played = actual_state["hero_adv"]["cards_played"]
    adv.servants.cards = actual_state["adv_servants"]

    ##################################
    ########## DECOUVERTES ###########

    if actual_state["discovery"] != [[]]:
        plateau.cards_chosen = actual_state["discovery"]
    elif actual_state["hero"]["mulligan_state"]:
        mulligan_help([x.name for x in player.hand], initial_deck)

    ##################################
    ############ AUTRES ##############

    player.deck.shuffle()
    adv.deck.shuffle()

    return plateau


class_j = "Paladin"
class_adv = "Chasseur"
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
        if 0 < best_action < 171:
            plateau_depart.players[0].last_card = plateau_reel.players[0].hand[(best_action - 1) // 17]
        game_prec = running_game.tags

# parser = LogParser()
# with open(logs_path) as f:
#     parser.read(f)
# packet_tree = parser.games[-1]
# exporter = EntityTreeExporter(packet_tree)
# export = exporter.export()
# running_game = export.game
# for e in running_game.entities:
#     if e.zone == Zone.HAND and e.tags[GameTag.CONTROLLER] == 2:
#         print(e.tags)
#         print('----------------------------------')

