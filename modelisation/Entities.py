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
all_genre_servants = ["Méca", "Murloc", "Élémentaire", "Bête", "Mort-vivant", "Totem", "Naga", "Pirate", "Dragon", "Huran", "Démon"]

def get_cards_data(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)


cardsfile = "cards.json"
all_cards = get_cards_data('cards.json')
all_servants = [x for x in all_cards if x['type'] == "Serviteur"]
all_spells = [x for x in all_cards if x['type'] == "Sort"]
all_weapons = [x for x in all_cards if x['type'] == "Arme"]
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
    empty_action_line[f"titan_serv{i + 1}_j"] = -99
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
    empty_action_line[f"titan_serv{i + 1}_adv"] = -99
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
        class_files = {'Chasseur': 'dk_sang.csv',
                       'Mage': 'dk_sang.csv',
                       'Paladin': 'dk_sang.csv',
                       'Démoniste': 'dk_sang.csv',
                       'Chasseur de démons': 'dh_marginal.csv',
                       'Druide': 'big_druid.csv',
                       'Voleur': 'dk_sang.csv',
                       'Guerrier': 'dk_sang.csv',
                       'Chevalier de la mort': 'dk_sang.csv',
                       'Prêtre': 'dk_sang.csv'
                       }
        self.cards_chosen, self.cards_dragage, self.cards_entrave, self.cards_hands_to_deck, self.choix_des_armes = [], [], [], [], None
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
        player = self.players[0]
        """ Fin du tour"""
        player.end_turn()
        self.players.reverse()
        player = self.players[0]
        adv = self.players[1]

        """ Debut du tour """
        if [x for x in player.hand if "eclosion" in x.effects]:
            for card in [x for x in player.hand if "eclosion" in x.effects]:
                card.effects["eclosion"][1] -= 1
                if card.effects["eclosion"][1] <= 0:
                    player.hand.remove(card)
                    player.hand.add(get_card(card.effects["eclosion"][0], all_cards))
        """ Effets de début de tour """
        for servant in player.servants:
            if "aura" in servant.effects and "start_turn" in servant.effects["aura"][1]:
                if "serviteur" in servant.effects["aura"][1] and "destroy" in servant.effects["aura"]:
                    if "tous" in servant.effects["aura"][1]:
                        for serv in player.servants.cards + adv.servants.cards:
                            serv.blessure = 1000
                if "boost" in servant.effects["aura"]:
                    if "self" in servant.effects["aura"][1] and "random_lose" in servant.effects["aura"][1]:
                        if random.randint(0, 1) == 0:
                            servant.attack -= 1
                            servant.base_attack -= 1
                        else:
                            servant.health -= 1
                            servant.base_health -= 1
                        self.update()
                    elif "Pedoncule oculaire de xhilag" and [x for x in player.servants if
                                                             x.name == "Pedoncule oculaire de xhilag"]:
                        for pedoncule in [x for x in player.servants if x.name == "Pedoncule oculaire de xhilag"]:
                            try:
                                pedoncule.effects["damage"][2] += 1
                            except:
                                pass
                if "suicide" in servant.effects["aura"]:
                    servant.blessure = 1000
                if "Thaddius" in servant.effects["aura"]:
                    servant.effects["aura"][2] = 1 if servant.effects["aura"][2] == 0 else 0
        if [x for x in player.hand if "start_turn" in x.effects]:
            for card in [x for x in player.hand if "start_turn" in x.effects]:
                """ Transformation des serviteurs concernés """
                if "transformation" in card.effects["start_turn"]:
                    potential_transform = [get_card(x, all_cards) for x in card.effects["start_turn"][1]]
                    player.hand.remove(card)
                    new_cost = card.cost
                    new_card = random.choice(potential_transform)
                    new_card.cost = new_cost
                    player.hand.add(new_card)
        player.start_turn()

        """ Le Geolier """
        if player.geolier:
            for servant in player.servants:
                servant.effects["bouclier divin"] = 2
                servant.effects["camouflage"] = 1
        if adv.geolier:
            for servant in adv.servants:
                servant.effects["bouclier divin"] = 2
                servant.effects["camouflage"] = 1
        player.apply_discount()

    def update(self):
        """ Vérifie les serviteurs morts et les pdv des joueurs """
        dead_servants = []
        for player in self.players:
            """ Geant des mers """
            if [x for x in player.hand if x.name == "Geant des mers"]:
                for geant in [x for x in player.hand if x.name == "Geant des mers"]:
                    if player == self.players[0]:
                        geant.cost = geant.base_cost - len(player.servants) - len(self.players[1].servants)
                    else:
                        geant.cost = geant.base_cost - len(player.servants) - len(self.players[0].servants)
            dead_servants_player = []
            if not "gardien de l'au dela" in [x.effects["aura"] for x in player.servants if "aura" in x.effects]:
                cards_impregnation = [x for x in player.hand if "impregnation" in x.effects]
            else:
                cards_impregnation = [x for x in player.hand if "impregnation" in x.effects] + [x for x in player.deck if "impregnation" in x.effects]
            if player.is_dead():
                self.game_on = False
                for winner in self.players:
                    if winner != player:
                        self.winner = winner
            for servant in player.servants:
                if servant.is_dead():
                    if "Mort-vivant" in servant.genre:
                        player.dead_undeads.append(servant)
                    if "Démon" in servant.genre:
                        player.dead_demons.append(servant)
                    if "rale d'agonie" in servant.effects:
                        player.dead_rale.append(servant)
                    player.all_dead_servants.append(servant)
                    player.dead_this_turn.append(servant)
                    if len(player.all_dead_servants) > 3:
                        player.all_dead_servants = player.all_dead_servants[-3:]
                    dead_servants.append(servant)
                    dead_servants_player.append(servant)
                    if "ressuscite" not in servant.name:
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
                    if "impregnation_demon" in card.effects["impregnation"]:
                        card.effects["impregnation"][1] -= len([x for x in dead_servants_player if "Démon" in x.genre])
                    else:
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
            """ Répartition cadavres """
            if player.cadavres_spent > sum(player.cadavres_repartis):
                a_repartir = player.cadavres_spent - sum(player.cadavres_repartis)
                bins = [0, 0, 0, 0]
                for _ in range(a_repartir):
                    bins[random.randrange(4)] += 1
                player.cadavres_repartis = [player.cadavres_repartis[i] + bins[i] for i in range(4)]
                if player.cadavres_repartis[3] > 5:
                    a_repartir = player.cadavres_repartis[3] - 5
                    player.cadavres_repartis[3] = 5
                    bins = [0, 0, 0]
                    for _ in range(a_repartir):
                        bins[random.randrange(3)] += 1
                    player.cadavres_repartis = [player.cadavres_repartis[i] + bins[i] for i in range(3)] + [player.cadavres_repartis[3]]
        return dead_servants, dead_servants_player

    def targets_hp(self):
        """ Retourne les cibles possibles du pouvoir héroïque """
        player = self.players[0]
        adv = self.players[1]
        targets = []
        if player.power is None:
            if player.classe in ["Mage", "Prêtre"]:
                targets = [player] + [adv] + player.servants.cards + adv.servants.cards
            elif player.classe == "Chasseur":
                targets.append(adv)
            elif player.classe in ["Paladin", "Chevalier de la mort"]:
                if len(player.servants) + len(player.lieux) < 7:
                    targets.append(player)
            else:
                targets.append(player)
        elif player.power[0] == "Explosion demoniaque":
            targets = [player] + [adv] + player.servants.cards + adv.servants.cards
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
        action_line["pv_j"], action_line["pv_adv"] = player.health, adv.health
        action_line["armor_j"], action_line["armor_adv"] = player.armor, adv.armor
        action_line["surcharge_j"], action_line["surcharge_adv"] = player.surcharge, adv.surcharge
        action_line["pv_max_j"], action_line["pv_max_adv"] = player.base_health, adv.base_health
        action_line["cadavres_j"], action_line["cadavres_adv"] = player.cadavres, adv.cadavres
        action_line["nbre_cartes_j"], action_line["nbre_cartes_adv"] = len(player.hand), len(adv.hand)
        action_line["dispo_ph_j"], action_line["cout_ph_j"] = player.dispo_pouvoir, player.cout_pouvoir
        action_line["arme_j"] = player.weapon.name if player.weapon is not None else ""
        action_line["arme_adv"] = adv.weapon.name if adv.weapon is not None else ""
        action_line["attaque_j"], action_line["attaque_adv"] = player.attack, adv.attack
        action_line["remaining_atk_j"] = player.remaining_atk
        action_line["attack_arme_j"] = player.weapon.attack if player.weapon is not None else 0
        action_line["attack_arme_adv"] = adv.weapon.attack if adv.weapon is not None else 0
        action_line["durabilite_arme_j"] = player.weapon.health if player.weapon is not None else 0
        action_line["durabilite_arme_adv"] = adv.weapon.health if adv.weapon is not None else 0
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
            if "titan" in player.servants[i].effects:
                action_line[f"titan_serv{i + 1}_j"] = player.servants[i].effects["titan"][-1]
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
            if "titan" in adv.servants[i].effects:
                action_line[f"titan_serv{i + 1}_adv"] = adv.servants[i].effects["titan"][-1]
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

        # Cartes
        self.deck, self.initial_deck = CardGroup(), CardGroup()  # Le tas de cartes à l'envers
        self.hand = CardGroup()  # La main du joueur
        self.servants, self.lieux, self.secrets = CardGroup(), CardGroup(), CardGroup()
        self.serv_this_turn, self.drawn_this_turn = CardGroup(), 0
        self.last_card, self.first_spell = "", None # la dernière carte jouée par le joueur

        self.mana, self.mana_max, self.mana_final, self.mana_spend_spells = 0, 0, 10, 0
        self.surcharge = 0
        self.cadavres, self.cadavres_spent, self.cadavres_repartis = 0, 0, [0, 0, 0, 0]
        self.discount_next, self.augment, self.next_turn = [], [], []
        self.all_dead_servants, self.dead_this_turn = [], []
        self.dead_undeads, self.dead_rale, self.cavalier_apocalypse, self.genre_joues, self.ames_liees, self.dead_demons = [], [], [], [], [], []
        self.oiseaux_libres, self.geolier, self.reliques, self.double_relique, = 0, 0, 0, 0
        self.weapons_played, self.marginal_played = 0, 0
        self.copies_to_deck = 0

        """ Héros choisi par le joueur """
        self.power = None
        self.hp_boost = {}
        self.dispo_pouvoir = True
        self.cout_pouvoir = 2
        self.cout_pouvoir_temp = 2

        self.attack, self.inter_attack = 0, 0
        self.remaining_atk, self.has_attacked = 1, 0
        self.armor = 0
        self.gel, self.curses, self.permanent_buff = 0, [], {}
        self.health, self.base_health = 30, 30
        self.weapon = None
        self.effects = {}

        self.fatigue, self.damage_this_turn, self.heal_this_turn = 0, 0, 0
        self.my_turn = 0

    def start_game(self):
        self.deck.shuffle()
        self.reset_complete()
        if self.classe == "Chasseur de démons":
            self.cout_pouvoir = 1
            self.cout_pouvoir_temp = 1
            if "Faux de la devoreuse d'ames" in [x.name for x in self.deck if x.type == "Arme"]:
                serv_to_consume = random.sample([x for x in self.deck if x.type == "Serviteur"], min(3, len([x for x in self.deck if x.type == "Serviteur"])))
                for serviteur in serv_to_consume:
                    self.deck.remove(serviteur)
                    self.deck.add(get_card("Ame liee", all_spells))
                    self.ames_liees.append(serviteur)
                self.deck.shuffle()
        if "Prince Renathal" in [x.name for x in self.deck]:
            self.health = 35
            self.base_health = 35
        self.pick_multi(3)

    def start_turn(self):
        """ Remise à zéro de début de tour """
        self.reset()
        if self.next_turn:
            for element in self.next_turn:
                if element[0] == "add_armor":
                    self.armor += element[1]
            self.next_turn = []
        self.pick_multi(1)
        if "pioche" in self.permanent_buff:
            self.pick_multi(self.permanent_buff["pioche"])
        if "murmegivre" in self.effects:
            self.discount_next.append(["murmegivre"])
            if self.effects["murmegivre"] == 0:
                self.damage(1000)
            else:
                self.effects["murmegivre"] -= 1
        for lieu in self.lieux:
            lieu.attack = min(0.5 + lieu.attack, 1)
        self.damage(self.fatigue)
        self.mana_grow()
        self.mana_reset()
        self.power_reset()
        self.servants.reset()
        self.apply_weapon()

    def end_turn(self):
        """ Mise à jour de fin de tour """
        self.attack, self.inter_attack = 0, 0
        self.damage_this_turn, self.my_turn = 0, 0
        self.dead_undeads, self.dead_this_turn = [], []
        self.serv_this_turn = CardGroup()
        self.augment = []
        if self.remaining_atk == 0 and self.gel == 1:
            self.gel = 0
        if self.effects:
            if "inciblable" in self.effects and "temp_turn" in self.effects["inciblable"]:
                self.effects.pop("inciblable")
            if "draw" in self.effects and "temp_turn" in self.effects["draw"]:
                self.effects.pop("draw")
            if "insensible_attack" in self.effects:
                self.effects.pop("insensible_attack")
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

    def end_action(self):
        if len(self.hand) > 10:
            self.hand.cards = self.hand.cards[:10]

    def apply_discount(self):
        for card in self.hand:
            card.cost = card.base_cost
            if "reduc" in card.effects:
                if "self" in card.effects["reduc"]:
                    if "len_hand" in card.effects["reduc"]:
                        card.cost = max(0, card.base_cost - len(self.hand) + 1)
                    elif "total_mana_spend_spells" in card.effects["reduc"]:
                        card.cost = max(0, card.base_cost - self.mana_spend_spells)
                    elif "cadavres_spent" in card.effects["reduc"]:
                        card.cost = max(0, card.base_cost - self.cadavres_spent)
                    elif "cards_drawn" in card.effects["reduc"]:
                        card.cost = max(0, card.base_cost - self.drawn_this_turn)
                    elif "weapons_played" in card.effects["reduc"]:
                        card.cost = max(0, card.base_cost - 2 * self.weapons_played)
                    elif "marginal_played" in card.effects["reduc"]:
                        card.cost = max(0, card.base_cost - self.marginal_played)
            if "marginal" in card.effects and "cost" in card.effects["marginal"] and card in [self.hand[0], self.hand[-1]]:
                card.cost = card.effects["marginal"][1]
        if "Corsaire de l'effroi" in [x.name for x in self.hand] and self.weapon is not None:
            for corsaire in [x for x in self.hand if x.name == "Corsaire de l'effroi"]:
                corsaire.cost = max(0, corsaire.base_cost - self.weapon.attack - self.attack)
        if self.discount_next:
            for discount in self.discount_next:
                for card in self.hand:
                    if card.type.lower() == discount[0] or discount[0] == "tous":
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
                        elif discount[1] == "marginal" and "marginal" in card.effects and discount[2] < 0:
                            card.cost = max(0, card.cost + discount[2])
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
        if [x for x in self.hand if "cost_pv" in x.effects]:
            for creature in [x for x in self.hand if "cost_pv" in x.effects]:
                if "if_heal_this_turn" in creature.effects["cost_pv"]:
                    if self.heal_this_turn > 0:
                        creature.cost = 0
                        creature.effects["cost_pv"][1] = 1
                    else:
                        creature.effects["cost_pv"][1] = 0
                else:
                    creature.cost = 0
                    creature.effects["cost_pv"][1] = 1

    def apply_weapon(self):
        if self.weapon is not None:
            self.attack = self.weapon.attack + self.inter_attack
            if "vol de vie" in self.weapon.effects:
                self.effects["vol de vie"] = 1
            if "cleave" in self.weapon.effects:
                self.effects["cleave"] = 1
        else:
            self.attack = self.inter_attack

    def mana_spend(self, nb):
        self.mana -= nb

    def mana_grow(self):
        self.mana_max = min(self.mana_max + 1, self.mana_final)

    def mana_reset(self):
        self.mana = self.mana_max - self.surcharge
        self.surcharge = 0

    def power_reset(self):
        self.dispo_pouvoir = True

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
                    if [x for x in self.servants.cards if "en sommeil" in x.effects and type(x.effects["en sommeil"]) == list and "pioche" in x.effects["en sommeil"]]:
                        for creature in [x for x in self.servants.cards if "en sommeil" in x.effects and type(x.effects["en sommeil"]) == list and "pioche" in x.effects["en sommeil"]]:
                            creature.effects["en sommeil"][1] -= 1
                            if creature.effects["en sommeil"][1] == 0:
                                creature.effects.pop("en sommeil")
                self.hand.add(self.deck.pick_one())
                self.drawn_this_turn += 1
                if [x for x in self.servants.cards if "en sommeil" in x.effects and type(x.effects["en sommeil"]) == list and "pioche" in x.effects["en sommeil"]]:
                    for creature in [x for x in self.servants.cards if "en sommeil" in x.effects and type(x.effects["en sommeil"]) == list and "pioche" in x.effects["en sommeil"]]:
                        creature.effects["en sommeil"][1] -= 1
                        if creature.effects["en sommeil"][1] == 0:
                            creature.effects.pop("en sommeil")
                if "draw" in self.effects:
                    self.damage(self.effects["draw"][2])
                if "if_pioche" in [x.effects["aura"][1][-1] for x in self.servants if "aura" in x.effects]:
                    for creature in [x for x in self.servants if "aura" in x.effects and x.effects["aura"][1][-1] == "if_pioche"]:
                        if "invocation" in creature.effects["aura"] and len(self.servants) + len(self.lieux) < 7:
                            self.servants.add(get_card(creature.effects["aura"][2], all_servants))
            else:
                self.fatigue += 1
                self.damage(self.fatigue)
        else:
            if self.deck.cards:
                self.deck.pick_one()
            else:
                self.fatigue += 1
                self.damage(self.fatigue)
            # raise PermissionError("Il a plus de cartes en main que de place prévue dans le log")

    def pick_multi(self, nb):
        for _ in range(nb):
            if type(nb) == str:
                print(nb)
            self.pick()

    def set_deck(self, file):
        self.deck = import_deck(file)
        
    def damage(self, nb):
        nb_armor = nb * (self.armor >= nb) + self.armor * (self.armor < nb)
        self.armor -= nb_armor
        self.health -= (nb - nb_armor)
        self.damage_this_turn += nb
        if nb - nb_armor and self.weapon is not None and self.weapon.name == "Eventreur en arcanite" and self.my_turn == 1:
            self.weapon.effects["stack"] += 1

    def reset(self):
        """ Le reset de début de tour """
        self.dispo_pouvoir = True
        self.first_spell = None
        if "jotun" in self.permanent_buff:
            self.permanent_buff["jotun"] = 1
        self.dead_this_turn, self.drawn_this_turn, self.curses = [], 0, []
        if self.gel == 0:
            self.remaining_atk = 1
        else:
            self.remaining_atk = 0
        if "vol de vie" in self.effects:
            self.effects.pop("vol de vie")
        if "cleave" in self.effects:
            self.effects.pop("cleave")
        self.damage_this_turn, self.heal_this_turn = 0, 0
        self.inter_attack, self.has_attacked = 0, 0
        self.my_turn = 1

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
        if nb_heal and self.weapon is not None and self.weapon.name == "Eventreur en arcanite" and self.my_turn == 1:
            self.weapon.effects["stack"] += 1
        if nb_heal > 0 and [x for x in self.servants if "aura" in x.effects and "Banshee hurlante" in x.effects["aura"]] and len(self.servants) + len(self.lieux) < 7:
            invoked_servant = get_card("Fanshee", all_servants)
            invoked_servant.attack = nb_heal
            invoked_servant.base_attack = nb_heal
            invoked_servant.health = nb_heal
            invoked_servant.base_health = nb_heal
            self.servants.add(invoked_servant)

    def is_dead(self) -> bool:
        return self.health <= 0

    def __repr__(self) -> str:
        return self.name


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
        self.remaining_atk = -1
        self.damage_taken, self.blessure, self.surplus = False, 0, 0
        self.total_temp_boost = [0, 0]
        self.cursed_player = None

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
        if "titan" in self.effects:
            if len(self.effects["titan"]) == 1:
                self.effects.pop("titan")
                self.effects.pop("ne peut pas attaquer")
            elif self.effects["titan"][-1] == 0:
                self.effects["titan"][-1] = 1
        if "ne peut pas attaquer" in self.effects:
            self.remaining_atk = -1
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
                self.total_temp_boost = [0, 0]
                self.attack = max(0, self.base_attack + self.total_temp_boost[0])
                self.health = max(0, self.base_health + self.total_temp_boost[1] - self.blessure)
        if "gel" in self.effects:
            self.remaining_atk = -1
        if "en sommeil" in self.effects:
            if type(self.effects["en sommeil"]) == int:
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
            if nb > 0:
                self.damage_taken = True
                if "curse_link" in self.effects:
                    self.cursed_player.damage(self.effects["curse_link"])
            else:
                self.damage_taken = False
            self.blessure += nb

    def heal(self, nb):
        """ Heal nb health to a given creatures """
        self.health += nb
        self.blessure = max(0, self.blessure - nb)
        if self.health > self.base_health:
            self.surplus = self.health - self.base_health
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


def generate_targets(state):
    """ Gestion des actions légales """
    legal_actions = [False] * 250
    player = state.players[0]
    adv = state.players[1]

    """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
    for i in range(len(player.hand)):
        if player.hand[i].type.lower() == "sort":
            if "ciblage" in player.hand[i].effects:
                if "serviteur" in player.hand[i].effects["ciblage"]:
                    if "ennemi" in player.hand[i].effects["ciblage"]:
                        for j in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                legal_actions[17 * i + j + 10] = True
                    elif "tous" in player.hand[i].effects["ciblage"]:
                        if "if_rale_agonie" in player.hand[i].effects["ciblage"]:
                            for j in range(len(player.servants)):
                                if "rale d'agonie" in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                    legal_actions[17 * i + j + 2] = True
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                    if "rale d'agonie" in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 10] = True
                        elif "Mort-vivant" in player.hand[i].effects["ciblage"]:
                            for j in range(len(player.servants)):
                                if "Mort-vivant" in player.servants[j].genre and "inciblable" not in player.servants[j].effects:
                                    legal_actions[17 * i + j + 2] = True
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                    if "Mort-vivant" in adv.servants[j].genre:
                                        legal_actions[17 * i + j + 10] = True
                        else:
                            for j in range(len(player.servants)):
                                if "inciblable" not in player.servants[j].effects:
                                    legal_actions[17 * i + j + 2] = True
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                    legal_actions[17 * i + j + 10] = True
                elif "tous" in player.hand[i].effects["ciblage"]:
                    if "ennemi" in player.hand[i].effects["ciblage"]:
                        legal_actions[17 * i + 9] = True
                        for j in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                legal_actions[17 * i + j + 10] = True
                    else:
                        legal_actions[17 * i + 1] = True
                        legal_actions[17 * i + 9] = True
                        for j in range(len(player.servants)):
                            if "inciblable" not in player.servants[j].effects:
                                legal_actions[17 * i + j + 2] = True
                        for j in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                legal_actions[17 * i + j + 10] = True
            else:
                legal_actions[17 * i] = True
    return legal_actions


def jouer_sort(self, carte, target=None):
        """ Action de poser une carte depuis la main du joueur dont c'est le tour.
        Le plateau est mis à jour en conséquence """
        player = self.plt.players[0]
        adv = self.plt.players[1]
        if carte.cost <= player.mana:
            if carte.type.lower() == "sort":
                if "marginal" in carte.effects:
                    if carte in [player.hand[0], player.hand[-1]]:
                        carte.effects[carte.effects["marginal"][0]] = carte.effects["marginal"][1]
                        print(carte.effects)
                player.hand.remove(carte)
                player.mana_spend(carte.cost)
                if "counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "sort" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]:
                    print("Sort contré")
                    [x for x in adv.servants if "counter" in x.effects["aura"][0]][0].effects.pop("counter")
                else:
                    player.mana_spend_spells += carte.cost
                    if "relique" in carte.effects:
                        player.reliques += 1
                        if player.double_relique == 1:
                            self.apply_effects(carte, target)
                            player.reliques += 1
                            player.double_relique = 0
                    self.apply_effects(carte, target)
                    if [x for x in player.hand if "cri de guerre" in x.effects and "if_spell" in x.effects["cri de guerre"][1]]:
                        for serv in [x for x in player.hand if "cri de guerre" in x.effects and "if_spell" in x.effects["cri de guerre"][1]]:
                            serv.effects["cri de guerre"][1][-1] -= 1
                            if serv.effects["cri de guerre"][1][-1] <= 0:
                                serv.effects["cri de guerre"][2] = serv.effects["cri de guerre"][3]
        else:
            raise PermissionError("Carte plus chère que la mana du joueur")

if __name__ == '__main__':
    pass








