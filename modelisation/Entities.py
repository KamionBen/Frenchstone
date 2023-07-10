import csv
import json
from os import path
from random import shuffle, choice
from typing import Union
import random
from copy import deepcopy
import pickle

""" CONSTANTS """
dict_actions = {
            0: "passer_tour",
            1: "jouer_carte",
            2: "attaquer"
        }

classes_heros_old = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                 "Chevalier de la mort"]
classes_heros = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                 "Chevalier de la mort"]
all_genre_servants = ["Méca", "Murloc", "Élémentaire", "Bête", "Mort-vivant", "Totem", "Naga", "Pirate", "Dragon", "Huran"]

def get_cards_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)


cardsfile = "cards.json"
all_cards = get_cards_data('cards.json')
all_servants = [x for x in all_cards if x['type'] == "Serviteur"]
all_spells = [x for x in all_cards if x['type'] == "Sort"]
heroes = {"Chasseur": ["Rexxar", "Alleria Coursevent", "Sylvanas Coursevent", "Rexxar chanteguerre"],
          "Mage": ["Jaina Portvaillant", "Medivh", "Khadgar", "Jaina mage Feu"],
          "Paladin": ["Uther"],
          "Démoniste": ["Gul'dan"],
          "Chasseur de démons": ["Ilidan"],
          "Druide" : ["Malfurion"],
          "Voleur" : ["Valeera"],
          "Guerrier": ["Garrosh"],
          "Chevalier de la mort": ["Le Roi-Liche"],
          "Prêtre": ["Anduin"]
          }  # Devra être dans un fichier à part


empty_action_line = {"carte_jouee": "",
   "attaquant": "", "attaquant_atq": "", "attaquant_pv": "",
   "cible": "", "cible_atq": "", "cible_pv": "",
   "classe_j": -99, "classe_adv": -99,
   "mana_dispo_j": -99, "mana_max_j": -99,
   "mana_max_adv": -99,
   "pv_j": -99, "pv_adv": -99,
   "armor_j": -99, "armor_adv": -99,
   "surcharge_j": -99, "surcharge_adv": -99,
   "pv_max_j": -99, "pv_max_adv": -99,
   "nbre_cartes_j": -99,
   "nbre_cartes_adv": -99,
   "cadavres_j": -99, "cadavres_adv": -99,
   "dispo_ph_j": -99,
   "cout_ph_j": -99,
   "arme_j": -99,
   "arme_adv": -99,
   "attaque_j": -99,
   "remaining_atk_j": -99,
   "attaque_adv": -99,
   "attack_arme_j": -99,
   "attack_arme_adv": -99,
   "durabilite_arme_j": -99,
   "durabilite_arme_adv": -99,
   "pseudo_j": -99,
   "pseudo_adv": -99
}
for classe_heros in set(classes_heros):
    empty_action_line[f"is_{classe_heros}"] = -99
for i in range(10):
    empty_action_line[f"carte_en_main{i + 1}_j"] = -99
    empty_action_line[f"cost_carte_en_main{i + 1}_j"] = -99
    empty_action_line[f"atq_carte_en_main{i + 1}_j"] = -99
    empty_action_line[f"pv_carte_en_main{i + 1}_j"] = -99
    empty_action_line[f"impregnation_carte_en_main{i + 1}_j"] = -99
    for j in range(len(all_cards)):
        empty_action_line[f"is_carte{i + 1}_{all_cards[j]['name']}"] = -99
for i in range(7):
    empty_action_line[f"serv{i + 1}_j"] = -99
    empty_action_line[f"atq_serv{i + 1}_j"] = -99
    empty_action_line[f"pv_serv{i + 1}_j"] = -99
    empty_action_line[f"atq_remain_serv{i + 1}_j"] = -99
    empty_action_line[f"divineshield_serv{i + 1}_j"] = -99
    empty_action_line[f"provocation_serv{i + 1}_j"] = -99
    empty_action_line[f"cant_attack_serv{i + 1}_j"] = -99
    empty_action_line[f"ruee_serv{i + 1}_j"] = -99
    empty_action_line[f"charge_serv{i + 1}_j"] = -99
    empty_action_line[f"camouflage_serv{i + 1}_j"] = -99
    empty_action_line[f"reincarnation_serv{i + 1}_j"] = -99
    empty_action_line[f"en_sommeil_serv{i + 1}_j"] = -99
    empty_action_line[f"gel_serv{i + 1}_j"] = -99
    empty_action_line[f"inciblable_serv{i + 1}_j"] = -99
    empty_action_line[f"voldevie_serv{i + 1}_j"] = -99
    empty_action_line[f"toxicite_serv{i + 1}_j"] = -99
    empty_action_line[f"furiedesvents_serv{i + 1}_j"] = -99
    empty_action_line[f"lieu{i + 1}_j"] = -99
    empty_action_line[f"atq_lieu{i + 1}_j"] = -99
    empty_action_line[f"pv_lieu{i + 1}_j"] = -99
    empty_action_line[f"serv{i + 1}_adv"] = -99
    empty_action_line[f"atq_serv{i + 1}_adv"] = -99
    empty_action_line[f"pv_serv{i + 1}_adv"] = -99
    empty_action_line[f"divineshield_serv{i + 1}_adv"] = -99
    empty_action_line[f"provocation_serv{i + 1}_adv"] = -99
    empty_action_line[f"cant_attack_serv{i + 1}_adv"] = -99
    empty_action_line[f"ruee_serv{i + 1}_adv"] = -99
    empty_action_line[f"charge_serv{i + 1}_adv"] = -99
    empty_action_line[f"camouflage_serv{i + 1}_adv"] = -99
    empty_action_line[f"reincarnation_serv{i + 1}_adv"] = -99
    empty_action_line[f"en_sommeil_serv{i + 1}_adv"] = -99
    empty_action_line[f"gel_serv{i + 1}_adv"] = -99
    empty_action_line[f"inciblable_serv{i + 1}_adv"] = -99
    empty_action_line[f"voldevie_serv{i + 1}_adv"] = -99
    empty_action_line[f"toxicite_serv{i + 1}_adv"] = -99
    empty_action_line[f"furiedesvents_serv{i + 1}_adv"] = -99
    empty_action_line[f"lieu{i + 1}_adv"] = -99
    empty_action_line[f"atq_lieu{i + 1}_adv"] = -99
    empty_action_line[f"pv_lieu{i + 1}_adv"] = -99
    for j in range(len(all_servants)):
        empty_action_line[f"is_servant{i + 1}_{all_servants[j]['name']}_j"] = -99
        empty_action_line[f"is_servant{i + 1}_{all_servants[j]['name']}_adv"] = -99


""" CLASSES """
class Plateau:
    def __init__(self, players=()):
        """ Décrit exhaustivement le plateau de jeu """
        class_files = {'Chasseur': 'test_deck.csv',
                       'Mage': 'test_deck.csv',
                       'Paladin': 'test_deck.csv',
                       'Démoniste': 'test_deck.csv',
                       'Chasseur de démons': 'test_deck.csv',
                       'Druide': 'test_deck.csv',
                       'Voleur': 'test_deck.csv',
                       'Guerrier': 'test_deck.csv',
                       'Chevalier de la mort': 'test_dk.csv',
                       'Prêtre': 'test_deck.csv'
                       }
        self.cards_chosen = []
        self.cards_dragage = []
        self.cards_entrave = []
        if players == ():
            self.players = [Player("Smaguy", 'Chasseur'), Player("Rupert", 'Mage')]

        else:
            self.players = list(players)
        Card.created = {}

        for player in self.players:
            player.set_deck(class_files[player.classe])
            player.initial_deck = player.deck

        """ Mélange des decks et tirage de la main de départ """
        for player in self.players:
            player.start_game()
        """ Le joueur 2 reçoit une carte en plus et la pièce """
        self.players[1].pick()
        self.players[1].hand.add(get_card("La piece", get_cards_data("cards.json")))

        """ Gestion du mana """
        """ Le premier joueur démarre son tour à l'initialisation """
        self.players[0].start_turn()

        """ Tour de jeu """
        self.game_turn = 0  # Décompte des tours
        self.game_on = True
        self.winner = None

    def tour_suivant(self):
        """ Met à jour le plateau à la fin du tour d'un joueur """
        self.game_turn += 1
        self.players.reverse()
        player = self.players[0]
        adv = self.players[1]

        adv.end_turn()
        """ Effets de fin de tour """
        for servant in adv.servants:
            if "aura" in servant.effects and "end_turn" in servant.effects["aura"][1]:
                if servant.name == "Cuisinier toque" and player.hero.damage_this_turn >= 3:
                    adv.pick()
                elif "add_deck" in servant.effects["aura"] and "random_spell_top" in servant.effects["aura"][1]:
                    try:
                        player.deck.cards.insert(0, Card(**random.choice([x for x in all_spells if x["decouvrable"] == 1])))
                    except:
                        player.deck.cards.insert(0, Card(**random.choice([x for x in all_servants if x["decouvrable"] == 1])))
                elif "damage" in servant.effects["aura"]:
                    if "tous" in servant.effects["aura"][1]:
                        if not "aléatoire" in servant.effects["aura"][1]:
                            for entity in [player.hero] + [adv.hero] + player.servants.cards + adv.servants.cards:
                                if entity != servant:
                                    entity.damage(servant.effects["aura"][2])
                        elif "ennemi" in servant.effects["aura"][1]:
                            target = random.choice([player.hero] + player.servants.cards)
                            target.damage(servant.effects["aura"][2])
                elif "invocation" in servant.effects["aura"]:
                    if "until_full" in servant.effects["aura"][1]:
                        while len(adv.servants) + len(adv.lieux) < 7:
                            adv.servants.add(get_card(servant.effects["aura"][2], all_servants))
        for servant in player.servants:
            if "aura" in servant.effects and "each_turn" in servant.effects["aura"][1]:
                if "invocation" in servant.effects["aura"]:
                    if "until_full" in servant.effects["aura"][1]:
                        while len(player.servants) + len(player.lieux) < 7:
                            player.servants.add(get_card(servant.effects["aura"][2], all_servants))
        if "Rock en fusion" in [x.name for x in adv.hand]:
            rock_en_fusion = [x for x in adv.hand if x.name == "Rock en fusion"][0]
            adv.hand.remove(rock_en_fusion)
            if adv.mana > 0:
                adv.hero.damage(rock_en_fusion.effects["rock_en_fusion"])
            else:
                rock_en_fusion.effects["rock_en_fusion"] += 2
                if len(player.hand) < 10:
                    player.hand.add(rock_en_fusion)
                
        player.start_turn()
        """ Effets de début de tour """
        for servant in player.servants:
            if "aura" in servant.effects and "start_turn" in servant.effects["aura"][1]:
                if "serviteur" in servant.effects["aura"][1] and "destroy" in servant.effects["aura"]:
                    if "tous" in servant.effects["aura"][1]:
                        for serv in player.servants.cards + adv.servants.cards:
                            serv.blessure = 1000
                if "boost" in servant.effects["aura"] and "self" in servant.effects["aura"][1] and "random_lose" in servant.effects["aura"][1]:
                    if random.randint(0, 1) == 0:
                        servant.attack -= 1
                        servant.base_attack -= 1
                    else:
                        servant.health -= 1
                        servant.base_health -= 1
                    self.update()
                if "suicide" in servant.effects["aura"]:
                    servant.blessure = 1000
                if "Thaddius" in servant.effects["aura"]:
                    servant.effects["aura"][2] = 1 if servant.effects["aura"][2] == 0 else 0
        if [x for x in player.hand if "start_turn" in x.effects]:
            for card in [x for x in player.hand if "start_turn" in x.effects]:
                if "start_turn" in card.effects:
                    """ Transformation des serviteurs concernés """
                    if "transformation" in card.effects["start_turn"]:
                        potential_transform = [get_card(x, all_cards) for x in card.effects["start_turn"][1]]
                        player.hand.remove(card)
                        new_cost = card.cost
                        new_card = random.choice(potential_transform)
                        new_card.cost = new_cost
                        player.hand.add(new_card)
        player.apply_discount()

    def update(self):
        """ Vérifie les serviteurs morts et les pdv des joueurs """
        dead_servants = []
        for player in self.players:
            dead_servants_player = []
            if not "gardien de l'au dela" in [x.effects["aura"] for x in player.servants if "aura" in x.effects]:
                cards_impregnation = [x for x in player.hand if "impregnation" in x.effects]
            else:
                cards_impregnation = [x for x in player.hand if "impregnation" in x.effects] + [x for x in player.deck if "impregnation" in x.effects]
            if player.hero.is_dead():
                self.game_on = False
                for winner in self.players:
                    if winner != player:
                        self.winner = winner
            for servant in player.servants:
                if servant.is_dead():
                    if "Mort-vivant" in servant.genre:
                        player.dead_undeads.append(servant)
                    player.all_dead_servants.append(servant)
                    if len(player.all_dead_servants) > 3:
                        player.all_dead_servants = player.all_dead_servants[-3:]
                    dead_servants.append(servant)
                    dead_servants_player.append(servant)
                    if servant.name != "Fantassin ressuscite":
                        player.cadavres += 1
                    if servant.name in ["Vaillefendre cavalier de la guerre", "Blaumeux cavaliere de la famine", "Korth'azz cavalier de la mort", "Zeliek cavalier de la conquete"]:
                        player.cavalier_apocalypse.append(servant.name)
                        player.cavalier_apocalypse = list(set(player.cavalier_apocalypse))
                        if len(player.cavalier_apocalypse) == 4:
                            if player == self.players[0]:
                                self.players[1].damage(1000)
                            else:
                                self.players[0].damage(1000)
            if cards_impregnation and dead_servants_player:
                for card in cards_impregnation:
                    card.effects["impregnation"][1] -= len(dead_servants_player)
                    if card.effects["impregnation"][1] <= 0:
                        if card.name == "Sire Denathrius":
                            card.effects["impregnation"][1] = 2
                            card.effects["cri de guerre"][1][3] += 1
                        else:
                            player.hand.remove(card)
                            new_card = get_card(card.effects["impregnation"][0], all_cards)
                            player.hand.add(new_card)
                            if new_card.name == "Golem pecheur impregne":
                                new_card.effects["cri de guerre"][2] = [sum([x.base_attack for x in player.all_dead_servants]), sum([x.base_health for x in player.all_dead_servants])]
        return dead_servants, dead_servants_player

    def targets_hp(self):
        """ Retourne les cibles possibles du pouvoir héroïque """
        player = self.players[0]
        adv = self.players[1]
        targets = []
        if player.classe in ["Mage", "Prêtre"]:
            targets = [player.hero] + [adv.hero] + player.servants.cards + adv.servants.cards
        elif player.classe == "Chasseur":
            targets.append(adv.hero)
        elif player.classe in ["Paladin", "Chevalier de la mort"]:
            if len(player.servants) + len(player.lieux) < 7:
                targets.append(player.hero)
        else:
            targets.append(player.hero)
        return targets

    def get_gamestate(self) -> dict:
        player = self.players[0]
        adv = self.players[1]

        # On assigne les actions de base avant les actions spécifiques au choix
        """ BOARD """
        action_line = empty_action_line.copy()
        action_line["classe_j"], action_line["classe_adv"] = player.classe, adv.classe
        action_line["mana_dispo_j"], action_line["mana_max_j"] = player.mana, player.mana_max
        action_line["mana_max_adv"] = adv.mana_max
        action_line["pv_j"], action_line["pv_adv"] = player.hero.health, adv.hero.health
        action_line["armor_j"], action_line["armor_adv"] = player.hero.armor, adv.hero.armor
        action_line["surcharge_j"], action_line["surcharge_adv"] = player.surcharge, adv.surcharge
        action_line["pv_max_j"], action_line["pv_max_adv"] = player.hero.base_health, adv.hero.base_health
        action_line["cadavres_j"], action_line["cadavres_adv"] = player.cadavres, adv.cadavres
        action_line["nbre_cartes_j"], action_line["nbre_cartes_adv"] = len(player.hand), len(adv.hand)
        action_line["dispo_ph_j"], action_line["cout_ph_j"] = player.hero.dispo_pouvoir, player.hero.cout_pouvoir
        action_line["arme_j"] = player.hero.weapon.name if player.hero.weapon is not None else ""
        action_line["arme_adv"] = adv.hero.weapon.name if adv.hero.weapon is not None else ""
        action_line["attaque_j"], action_line["attaque_adv"] = player.hero.attack, adv.hero.attack
        action_line["remaining_atk_j"] = player.hero.remaining_atk
        action_line["attack_arme_j"] = player.hero.weapon.attack if player.hero.weapon is not None else 0
        action_line["attack_arme_adv"] = adv.hero.weapon.attack if adv.hero.weapon is not None else 0
        action_line["durabilite_arme_j"] = player.hero.weapon.health if player.hero.weapon is not None else 0
        action_line["durabilite_arme_adv"] = adv.hero.weapon.health if adv.hero.weapon is not None else 0
        action_line["pseudo_j"], action_line["pseudo_adv"] = player.name, adv.name

        """ HERO """
        action_line[f"is_{player.classe}"] = 1

        """ HAND """
        for i in range(len(player.hand)):
            action_line[f"carte_en_main{i + 1}_j"] = player.hand[i].id
            action_line[f"cost_carte_en_main{i + 1}_j"] = player.hand[i].cost
            action_line[f"atq_carte_en_main{i + 1}_j"] = player.hand[i].attack
            action_line[f"pv_carte_en_main{i + 1}_j"] = player.hand[i].health
            action_line[f"impregnation_carte_en_main{i + 1}_j"] = player.hand[i].effects["impregnation"][1] if "impregnation" in player.hand[i].effects else -99
            action_line[f"is_carte{i + 1}_{player.hand[i].name}_j"] = 1

        """ SERVANTS """
        for i in range(len(player.servants)):
            action_line[f"serv{i + 1}_j"] = player.servants[i].id
            action_line[f"atq_serv{i + 1}_j"] = player.servants[i].attack
            action_line[f"pv_serv{i + 1}_j"] = player.servants[i].health
            action_line[f"atq_remain_serv{i + 1}_j"] = player.servants[i].remaining_atk
            if "bouclier divin" in player.servants[i].effects:
                action_line[f"divineshield_serv{i + 1}_j"] = player.servants[i].effects["bouclier divin"]
            if "provocation" in player.servants[i].effects:
                action_line[f"provocation_serv{i + 1}_j"] = player.servants[i].effects["provocation"]
            if "ne peut pas attaquer" in player.servants[i].effects:
                action_line[f"cant_attack_serv{i + 1}_j"] = player.servants[i].effects["ne peut pas attaquer"]
            if "ruée" in player.servants[i].effects:
                action_line[f"ruee_serv{i + 1}_j"] = player.servants[i].effects["ruée"]
            if "charge" in player.servants[i].effects:
                action_line[f"charge_serv{i + 1}_j"] = player.servants[i].effects["charge"]
            if "camouflage" in player.servants[i].effects:
                action_line[f"camouflage_serv{i + 1}_j"] = player.servants[i].effects["camouflage"]
            if "reincarnation" in player.servants[i].effects:
                action_line[f"reincarnation_serv{i + 1}_j"] = player.servants[i].effects["reincarnation"]
            if "en sommeil" in player.servants[i].effects:
                action_line[f"en_sommeil_serv{i + 1}_j"] = player.servants[i].effects["en sommeil"]
            if "gel" in player.servants[i].effects:
                action_line[f"gel_serv{i + 1}_j"] = player.servants[i].effects["gel"]
            if "inciblable" in player.servants[i].effects:
                action_line[f"inciblable_serv{i + 1}_j"] = player.servants[i].effects["inciblable"]
            if "vol de vie" in player.servants[i].effects:
                action_line[f"voldevie_serv{i + 1}_j"] = player.servants[i].effects["vol de vie"]
            if "toxicite" in player.servants[i].effects:
                action_line[f"toxicite_serv{i + 1}_j"] = player.servants[i].effects["toxicite"]
            if "furie des vents" in player.servants[i].effects:
                action_line[f"furiedesvents_serv{i + 1}_j"] = player.servants[i].effects["furie des vents"]
            action_line[f"is_servant{i + 1}_{player.servants[i].name}_j"] = 1
        for i in range(len(adv.servants)):
            action_line[f"serv{i + 1}_adv"] = adv.servants[i].id
            action_line[f"atq_serv{i + 1}_adv"] = adv.servants[i].attack
            action_line[f"pv_serv{i + 1}_adv"] = adv.servants[i].health
            if "bouclier divin" in adv.servants[i].effects:
                action_line[f"divineshield_serv{i + 1}_adv"] = adv.servants[i].effects["bouclier divin"]
            if "provocation" in adv.servants[i].effects:
                action_line[f"provocation_serv{i + 1}_adv"] = adv.servants[i].effects["provocation"]
            if "ne peut pas attaquer" in adv.servants[i].effects:
                action_line[f"cant_attack_serv{i + 1}_adv"] = adv.servants[i].effects["ne peut pas attaquer"]
            if "ruée" in adv.servants[i].effects:
                action_line[f"ruee_serv{i + 1}_adv"] = adv.servants[i].effects["ruée"]
            if "charge" in adv.servants[i].effects:
                action_line[f"charge_serv{i + 1}_adv"] = adv.servants[i].effects["charge"]
            if "camouflage" in adv.servants[i].effects:
                action_line[f"camouflage_serv{i + 1}_adv"] = adv.servants[i].effects["camouflage"]
            if "reincarnation" in adv.servants[i].effects:
                action_line[f"reincarnation_serv{i + 1}_adv"] = adv.servants[i].effects["reincarnation"]
            if "en sommeil" in adv.servants[i].effects:
                action_line[f"en_sommeil_serv{i + 1}_adv"] = adv.servants[i].effects["en sommeil"]
            if "gel" in adv.servants[i].effects:
                action_line[f"gel_serv{i + 1}_adv"] = adv.servants[i].effects["gel"]
            if "inciblable" in adv.servants[i].effects:
                action_line[f"inciblable_serv{i + 1}_adv"] = adv.servants[i].effects["inciblable"]
            if "vol de vie" in adv.servants[i].effects:
                action_line[f"voldevie_serv{i + 1}_adv"] = adv.servants[i].effects["vol de vie"]
            if "toxicite" in adv.servants[i].effects:
                action_line[f"toxicite_serv{i + 1}_adv"] = adv.servants[i].effects["toxicite"]
            if "furie des vents" in adv.servants[i].effects:
                action_line[f"furiedesvents_serv{i + 1}_adv"] = adv.servants[i].effects["furie des vents"]
            action_line[f"is_servant{i + 1}_{adv.servants[i].name}_adv"] = 1

        for i in range(len(player.lieux)):
            action_line[f"lieu{i + 1}_j"] = player.lieux[i].id
            action_line[f"atq_lieu{i + 1}_j"] = player.lieux[i].attack
            action_line[f"pv_lieu{i + 1}_j"] = player.lieux[i].health
        for i in range(len(adv.lieux)):
            action_line[f"lieu{i + 1}_adv"] = adv.lieux[i].id
            action_line[f"atq_lieu{i + 1}_adv"] = adv.lieux[i].attack
            action_line[f"pv_lieu{i + 1}_adv"] = adv.lieux[i].health

        return action_line


class Player:
    def __init__(self, name, classe, ia=True):
        """ Profil de l'utilisateur ou de l'IA"""
        self.name = name
        self.classe = classe
        self.ia = ia
        self.hero = Hero(heroes[self.classe][0])  # Premier héros par défaut

        # Cartes
        self.deck, self.initial_deck = CardGroup(), CardGroup()  # Le tas de cartes à l'envers
        self.hand = CardGroup()  # La main du joueur
        self.servants, self.lieux, self.secrets = CardGroup(), CardGroup(), CardGroup()
        self.serv_this_turn = CardGroup()
        self.last_card = "" # la dernière carte jouée par le joueur

        self.mana, self.mana_max, self.mana_final, self.mana_spend_spells = 0, 0, 10, 0
        self.surcharge = 0
        self.cadavres = 0
        self.discount_next, self.augment = [], []
        self.all_dead_servants = []
        self.dead_undeads, self.cavalier_apocalypse, self.genre_joues = [], [], []
        self.oiseaux_libres, self.geolier = 0, 0

    def start_game(self):
        self.deck.shuffle()
        self.hero.reset_complete()
        if self.classe == "Chasseur de démons":
            self.hero.cout_pouvoir = 1
            self.hero.cout_pouvoir_temp = 1
        if "Prince Renathal" in [x.name for x in self.deck]:
            self.hero.health = 35
            self.hero.base_health = 35
        self.pick_multi(3)

    def start_turn(self):
        """ Remise à zéro de début de tour """
        if len(self.deck) > 0:
            self.pick()
        else:
            self.hero.fatigue += 1
        if "murmegivre" in self.hero.effects:
            self.discount_next.append(["murmegivre"])
            if self.hero.effects["murmegivre"] == 0:
                self.hero.damage(1000)
            else:
                self.hero.effects["murmegivre"] -= 1
        for lieu in self.lieux:
            lieu.attack = min(0.5 + lieu.attack, 1)
        self.hero.damage(self.hero.fatigue)
        self.hero.reset()
        self.mana_grow()
        self.mana_reset()
        self.power_reset()
        self.servants.reset()
        self.apply_weapon()

    def end_turn(self):
        """ Mise à jour de fin de tour """
        self.hero.attack, self.hero.inter_attack = 0, 0
        self.hero.damage_this_turn = 0
        self.dead_undeads = []
        self.serv_this_turn = CardGroup()
        self.augment = []
        if self.hero.remaining_atk == 0 and self.hero.gel == 1:
            self.hero.gel = 0
        if self.hero.effects:
            if "inciblable" in self.hero.effects and "temp_turn" in self.hero.effects["inciblable"]:
                self.hero.effects.pop("inciblable")
            if "draw" in self.hero.effects and "temp_turn" in self.hero.effects["draw"]:
                self.hero.effects.pop("draw")

        if self.discount_next:
            for discount in self.discount_next:
                if "end_turn" in discount:
                    self.discount_next.remove(discount)
                    for servant in self.servants:
                        if discount in servant.discount:
                            servant.discount.remove(discount)
                    for card in self.hand:
                        if discount in card.discount:
                            card.discount.remove(discount)
        if self.augment:
            for augment in self.augment:
                if "temp_fullturn" in augment:
                    self.augment.remove(augment)
        for servant in self.servants:
            servant.damage_taken = False
            if servant.name == "Goule fragile":
                servant.blessure = 1000
            if "temp_turn" in servant.effects:
                servant.attack -= servant.effects["temp_turn"][0]
                servant.health -= servant.effects["temp_turn"][1]
                servant.base_health -= servant.effects["temp_turn"][1]
            if "gel" in servant.effects and servant.remaining_atk == 0:
                servant.effects.pop("gel")
            if "aura" in servant.effects and "end_turn" in servant.effects["aura"][1]:
                if "boost" in servant.effects["aura"] and "self" in servant.effects["aura"][1]:
                    if "random_lose" in servant.effects["aura"][1]:
                        if random.randint(0, 1) == 0:
                            servant.attack -= 1
                            servant.base_attack -= 1
                        else:
                            servant.health -= 1
                            servant.base_health -= 1
                    else:
                        servant.attack += servant.effects["aura"][2][0]
                        servant.base_attack += servant.effects["aura"][2][0]
                        servant.health += servant.effects["aura"][2][1]
                        servant.base_health += servant.effects["aura"][2][1]
                elif "damage" in servant.effects["aura"]:
                    if "heros" in servant.effects["aura"][1] and "allié" in servant.effects["aura"][1]:
                        self.hero.damage(servant.effects["aura"][2])
                elif "main" in servant.effects["aura"][1]:
                    if "allié" in servant.effects["aura"][1] and "serviteur" in servant.effects["aura"][1]:
                        if [x for x in self.hand if x.type == "Serviteur"]:
                            target = random.choice([x for x in self.hand if x.type == "Serviteur"])
                            target.attack += servant.effects["aura"][2][0]
                            target.base_attack += servant.effects["aura"][2][0]
                            target.health += servant.effects["aura"][2][1]
                            target.base_health += servant.effects["aura"][2][1]
                elif "invocation" in servant.effects["aura"]:
                    if "if_cadavre" in servant.effects["aura"][1] and self.cadavres >= servant.effects["aura"][1][-1] and len(self.servants) + len(self.lieux) < 7:
                        self.cadavres -= servant.effects["aura"][1][-1]
                        self.servants.add(get_card(servant.effects["aura"][2], all_servants))

    def apply_discount(self):
        for card in self.hand:
            card.cost = card.base_cost
            if "reduc" in card.effects:
                if "self" in card.effects["reduc"] :
                    if "len_hand" in card.effects["reduc"]:
                        card.cost = card.base_cost - len(self.hand) + 1
                    elif "total_mana_spend_spells" in card.effects["reduc"]:
                        card.cost = card.base_cost - self.mana_spend_spells
        if "Corsaire de l'effroi" in [x.name for x in self.hand] and self.hero.weapon is not None:
            for corsaire in [x for x in self.hand if x.name == "Corsaire de l'effroi"]:
                corsaire.cost = max(0, corsaire.base_cost - self.hero.weapon.attack - self.hero.attack)
        if self.discount_next:
            for discount in self.discount_next:
                for card in self.hand:
                    if card.type.lower() == discount[0]:
                        if discount[1] != "" and discount[1] in card.genre and discount[2] < 0:
                            card.cost = max(0, card.cost + discount[2])
                            if discount not in card.discount:
                                card.discount.append(discount)
                        elif discount[2] >= 0:
                            card.cost = max(0, discount[2])
                            if discount not in card.discount:
                                card.discount.append(discount)
                        elif discount[1] == "secret" and "secret" in card.effects and discount[2] >= 0:
                            card.cost = discount[2]
                            if discount not in card.discount:
                                card.discount.append(discount)
                        elif "tous" in discount[1]:
                            card.cost = max(0, card.cost + discount[2])
                            if discount not in card.discount:
                                card.discount.append(discount)
                    elif discount[0] == "murmegivre":
                        card.cost = 0
                        if discount not in card.discount:
                            card.discount.append(discount)
        if self.augment:
            for card in self.hand:
                for augment in self.augment:
                    if card.type.lower() == augment[0]:
                        if augment[2] > 0:
                            card.cost = card.base_cost + augment[2]
        if [x for x in self.servants if "aura" in x.effects and "Thaddius" in x.effects["aura"]]:
            reduction = [x for x in self.servants if "aura" in x.effects and "Thaddius" in x.effects["aura"]][0].effects["aura"][2]
            for card in self.hand:
                if reduction == card.cost % 2:
                    card.cost = 1
        if [x for x in self.servants if "cost_pv" in x.effects]:
            if self.hero.heal_this_turn > 0:
                for creature in [x for x in self.servants if "cost_pv" in x.effects]:
                    creature.cost = 0
                    creature.effects["cost_pv"][1] = 1
            else:
                for creature in [x for x in self.servants if "cost_pv" in x.effects]:
                    creature.effects["cost_pv"][1] = 0
    def apply_weapon(self):
        if self.hero.weapon is not None:
            self.hero.attack = self.hero.weapon.attack + self.hero.inter_attack
        else:
            self.hero.attack = self.hero.inter_attack

    def mana_spend(self, nb):
        self.mana -= nb

    def mana_grow(self):
        self.mana_max = min(self.mana_max + 1, self.mana_final)

    def mana_reset(self):
        self.mana = self.mana_max - self.surcharge
        self.surcharge = 0

    def power_reset(self):
        self.hero.dispo_pouvoir = True

    def pick(self):
        """ Prendre la première carte du deck et l'ajouter à sa main """
        if len(self.hand) < 10:
            if self.deck.cards:
                while "invoked_drawn" in self.deck.cards[0].effects and len(self.servants) + len(self.lieux) < 7:
                    if self.deck.cards[0].type == "Serviteur":
                        self.servants.add(self.deck.pick_one())
                    else:
                        self.servants.add(get_card(self.deck.cards[0].effects["invoked_drawn"], all_servants))
                        self.deck.remove(self.deck.cards[0])
                self.hand.add(self.deck.pick_one())
                if "draw" in self.hero.effects:
                    self.hero.damage(self.hero.effects["draw"][2])
            else:
                self.hero.fatigue += 1
                self.hero.damage(self.hero.fatigue)
        else:
            if self.deck.cards:
                self.deck.pick_one()
            else:
                self.hero.fatigue += 1
                self.hero.damage(self.hero.fatigue)
            # raise PermissionError("Il a plus de cartes en main que de place prévue dans le log")

    def pick_multi(self, nb):
        for _ in range(nb):
            self.pick()

    def set_hero(self, name):
        self.hero = Hero(name)

    def set_deck(self, file):
        self.deck = import_deck(file)

    def __repr__(self) -> str:
        return self.name


class Hero:
    def __init__(self, name):
        """ Héros choisi par le joueur """
        self.name = name
        self.power = None

        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.cout_pouvoir_temp = 2
        self.effet_pouvoir = None

        self.attack, self.inter_attack = 0, 0
        self.remaining_atk, self.has_attacked = 1, 0
        self.armor = 0
        self.gel = 0
        self.health, self.base_health = 30, 30
        self.weapon = None
        self.effects = {}

        self.fatigue, self.damage_this_turn, self.heal_this_turn = 0, 0, 0

    def __repr__(self):
        return self.name

    def damage(self, nb):
        nb_armor = nb * (self.armor >= nb) + self.armor * (self.armor < nb)
        self.armor -= nb_armor
        self.health -= (nb - nb_armor)
        self.damage_this_turn += nb

    def reset(self):
        """ Le reset de début de tour """
        self.dispo_pouvoir = True
        if self.gel == 0:
            self.remaining_atk = 1
        else:
            self.remaining_atk = 0
        self.damage_this_turn = 0
        self.heal_this_turn = 0
        self.inter_attack = 0

    def reset_complete(self):
        """ Le reset de début de partie """
        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.effet_pouvoir = None

        self.attack = 0
        self.armor = 0
        self.gel = 0
        self.health, self.base_health = 30, 30
        self.weapon = None

        self.fatigue, self.damage_this_turn = 0, 0

    def heal(self, nb):
        nb_heal = min(nb, self.base_health - self.health)
        self.health += nb_heal
        self.heal_this_turn += nb_heal

    def is_dead(self) -> bool:
        return self.health <= 0


class CardGroup:
    def __init__(self, cards=()):
        """ Permet de faire des opérations sur un groupe de cartes """
        self.cards = list(cards)
        self.carddict = {c.id: c for c in self.cards}

    def reset(self):
        for card in self.cards:
            card.reset()

    def add(self, new_card):
        if type(new_card) == Card:
            self.cards.append(new_card)


    def remove(self, card):
        if type(card) == Card:
            self.cards.remove(card)

    def shuffle(self):
        shuffle(self.cards)

    def pick_one(self):
        """ Renvoie la première carte de la liste et l'enlève du deck """
        if len(self.cards) > 0:
            picked = self.cards[0]
            self.cards = self.cards[1:]
            return picked
        else:
            raise IndexError("Le groupe de cartes est vide")

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __add__(self, other):
        if type(other) is Card:
            ls = self.cards.copy()
            ls.append(other)
            return CardGroup(ls)
        elif type(other) is list:
            ls = self.cards.copy()
            for l in other:
                ls.append(l)
            return ls
        else:
            raise TypeError(f"Impossible d'additionner {other} (type:{type(other)}) avec le type CardGroup")

    def __getitem__(self, x):
        """ Renvoie la xième carte du groupe"""
        if type(x) is int:
            return self.cards[x]
        else:
            raise TypeError

    def get(self, cid):
        """ Renvoie une carte en particulier """
        if is_card_id(cid):
            if cid in self.carddict:
                return self.carddict[cid]
            else:
                return KeyError
        else:
            raise TypeError

    def choice(self):
        """ Retire une carte au hasard """
        if len(self.cards) == 0:
            return None
        else:
            my_choice = choice(self.cards)
            self.cards.remove(my_choice)
            return my_choice

    def __repr__(self):
        return str(self.cards)


class Card:
    created = {}

    def __init__(self, cid=None, **kw):
        """ Classe généraliste pour les cartes à jouer """
        """ Description """
        self.name = kw["name"]
        self.effects = deepcopy(kw["effects"])
        self.genre = kw["genre"]
        if cid is None:
            # Génération d'un id de carte
            self.id = f"{kw['id']}-{self.generate_id()}"
            Card.created[self.name] = self.generate_id()
        else:
            self.id = cid

        """ Category """
        self.classe = kw["classe"]
        self.type = kw["type"]

        """ Stats """
        self.cost, self.base_cost, self.discount = kw["cost"], kw["cost"], []
        self.attack, self.base_attack = kw["attack"], kw["attack"]
        self.health, self.base_health = kw["health"], kw["health"]
        
        """ Combat """
        self.remaining_atk = 0
        self.damage_taken, self.blessure = False, 0
        self.total_temp_boost = [0, 0]

    def generate_id(self):
        try:
            x = Card.created[self.name]
            x += 1
        except:
            x = 0
        return x

    def get_effects(self):
        return list(self.effects.values())

    def reset(self):
        """ Reset de début de tour """
        if "ne peut pas attaquer" in self.effects:
            self.remaining_atk = 0
        else:
            self.remaining_atk = 1
        if "furie des vents" in self.effects:
            self.effects["furie des vents"] = 1
        if "entrave" in self.effects:
            self.effects.pop("entrave")
        if "ruée" in self.effects and not "en sommeil" in self.effects:
            self.effects["ruée"] = 0
        if "aura" in self.effects:
            if "temp_fullturn" in self.effects["aura"][1]:
                self.attack = self.base_attack
        if "gel" in self.effects:
            self.remaining_atk = 0
        if "en sommeil" in self.effects:
            self.effects["en sommeil"] -= 1
            if self.effects["en sommeil"] == 0:
                self.effects.pop("en sommeil")

    def reset_complete(self):
        self.cost = self.base_cost
        self.attack = self.base_attack
        self.health = self.base_health


    def damage(self, nb):
        """ Removes nb from the card health """
        if self.name == "Bulleur" and nb == 1:
            self.health = 0
        if "bouclier divin" in self.effects and nb != 0:
            if self.effects["bouclier divin"] != 2:
                self.effects.pop("bouclier divin")
        else:
            self.health -= nb
            self.damage_taken = True if nb > 0 else False
            self.blessure += nb


    def heal(self, nb):
        """ Heal nb health to a given creatures """
        self.health += nb
        self.blessure = max(0, self.blessure - nb)
        if self.health > self.base_health:
            self.health = self.base_health



    def is_dead(self):
        """ Return True if the card health <= 0"""
        return self.health <= 0

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if type(other) == Card:
            return other.id == self.id
        elif type(other) == str:
            return other == self.id or other.lower() == self.name.lower()
        else:
            return False

    def data(self) -> str:
        return f"id:{self.id} - {self.name} - Classe : {self.classe} - Type : {self.type} - Genre : {self.genre} - " \
               f"Coût = {self.cost} - Attaque = {self.attack} - Santé = {self.health}"


class Weapon:
    def __init__(self, name):
        self.name = name

        self.attack = 0
        self.health = 0

""" FUNCTIONS """

def import_deck(file: str, data='cards.json') -> CardGroup:
    """
    :param file: A csv file with the card's name and the number of this card in the deck
    :param data : The .json file
    :return: A CardGroup
    """
    jsoncards = get_cards_data(data)
    deck = CardGroup()
    with open(path.join('../decks', file), 'r') as csvdeck:
        reader = csv.reader(csvdeck, delimiter=";")
        for line in reader:
            name = line[0]
            number = int(line[1])
            found = False
            for jsoncard in jsoncards:
                if jsoncard['name'] == name:
                    found = True
                    for _ in range(number):
                        card = Card(**jsoncard)
                        deck.add(card)
                    break
            if found is False:
                print(f"\033[91mERREUR : La carte {name} n'a pas été trouvée dans le fichier cards.json\033[0m")
    if len(deck) == 0:
        raise ImportError("Le deck est vide")
    else:
        return deck


def get_card(key: Union[int, str], cardpool: list) -> Card:
    """ Renvoie l'objet Card en fonction de 'key', qui peut être l'id où le nom de la carte """
    found = False
    if type(key) is int:
        # Recherche par id fixe
        for elt in cardpool:
            if elt['id'] == key:
                return Card(**elt)
    elif type(key) is str:
        if len(key.split('-')) == 2:
            # Recherche par id temporaire
            key, ext = key.split('-')
            for elt in cardpool:
                if str(elt['id']) == key:
                    return Card(cid=f"{key}-{ext}", **elt)
        else:
            for elt in cardpool:
                if elt['name'].lower() == key.lower():
                    return Card(**elt)
    else:
        raise TypeError

    if found is False:
        raise KeyError(f"Impossible de trouver {key}")


def int_to_id(baseid: int, nb: int) -> str:
    if type(baseid) is int and type(nb) is int:
        if baseid < 10:
            return f"000{baseid}-{nb}"
        elif baseid < 100:
            return f"00{baseid}-{nb}"
        elif baseid < 1000:
            return f"0{baseid}-{nb}"
        else:
            return f"{baseid}-{nb}"
    else:
        raise TypeError


def is_card_id(elt) -> bool:
    """ Renvoie vrai si elt est au format int-int """
    try:
        parse = elt.split('-')
        cid = int(parse[0])
        number = int(parse[1])
        return True
    except ValueError:
        return False
    except IndexError:
        return False
    except AttributeError:
        return False



if __name__ == '__main__':
    pass








