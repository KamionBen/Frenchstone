import time
from engine import *
import gc
from statistics import mean
import math
import matplotlib.pyplot as plt

players = [Player("NewIA", "Voleur", "tempo"), Player("OldIA", "Chevalier de la mort", "controle")]
plateau_depart = Plateau(pickle.loads(pickle.dumps(players, -1)))


def deadly_attack(adv, serv):
    if "bouclier_divin" in serv.effects:
        return False
    else:
        toxic = True if "toxicite" in adv.effects else False
        if toxic and not "bouclier_divin" in serv.effects:
            return True
        else:
            if adv.attack >= serv.health:
                return True
            else:
                return False


def generate_legal_vector_test(state):
    """ Gestion des actions légales """
    legal_actions = [False] * 390
    player = state.players[0]
    adv = state.players[1]
    
    """ decouverte """
    if state.cards_chosen or state.cards_dragage:
        legal_actions[0] = False
        for i in range(251, 251 + len(state.cards_chosen[0]) if state.cards_chosen else 251 + len(state.cards_dragage[0])):
            legal_actions[i] = True
        if state.cards_chosen and len(state.cards_chosen[0]) == 4 and state.cards_chosen[0][3] == "choix mystere":
            legal_actions[254] = True
        return legal_actions
    elif state.cards_entrave:
        for i in range(251, 251 + len(state.cards_entrave[0])):
            legal_actions[i] = True
        return legal_actions
    elif state.cards_hands_to_deck:
        for i in range(251, 251 + len(state.cards_hands_to_deck[0])):
            legal_actions[i] = True
        return legal_actions
    elif state.choix_des_armes is not None:
        legal_actions[251], legal_actions[252] = True, True
        return legal_actions

    legal_actions[0] = True
    gamestate = state.get_gamestate()

    """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
    if "mandatory" in [x for l in [list(x.effects.keys()) for x in player.hand] for x in l]:
        for i in range(len(player.hand)):
            if "reduc" in player.hand[i].effects and "self" in player.hand[i].effects["reduc"]:
                if "total_serv" in player.hand[i].effects["reduc"]:
                    player.hand[i].cost -= len(player.servants) + len(adv.servants)
            if player.hand[i].cost <= player.mana and "mandatory" in player.hand[i].effects:
                if len(player.servants) + len(player.lieux) < 7 and player.hand[i].type == "Serviteur":
                    """ Serviteurs avec cris de guerre ciblés """
                    if "cri de guerre" in player.hand[i].effects and "choisi" in player.hand[i].effects["cri de guerre"][1]:
                        if "serviteur" in player.hand[i].effects["cri de guerre"][1]:
                            if "allié" in player.hand[i].effects["cri de guerre"][1] and player.servants.cards:
                                if "genre" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Bête" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Bête" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Mort-vivant" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Méca" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Méca" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "if_rale_agonie" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                            elif "ennemi" in player.hand[i].effects["cri de guerre"][1] and adv.servants.cards:
                                if "conditional" not in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_provocation" in player.hand[i].effects["cri de guerre"][1]:
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "provocation" in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True
                            elif "tous" in player.hand[i].effects["cri de guerre"][1] and (player.servants.cards or adv.servants.cards):
                                if "conditional" not in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_attack_greater" in player.hand[i].effects["cri de guerre"][1] and [x for x in player.servants.cards + adv.servants.cards if x.attack >= player.hand[i].effects["cri de guerre"][1][5]]:
                                        for j in range(len(player.servants)):
                                            if player.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5] and player.servants[j] != player.hand[i]:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if adv.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5]:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True


                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in player.hand[i].effects["cri de guerre"][1]:
                            if "ennemi" in player.hand[i].effects["cri de guerre"][1]:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                if "conditional" not in player.hand[i].effects["cri de guerre"][1]:
                                    legal_actions[17 * i + 2] = True
                                    legal_actions[17 * i + 10] = True
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_weapon" in player.hand[i].effects["cri de guerre"][1] and player.weapon is not None \
                                            or "if_death_undead" in player.hand[i].effects["cri de guerre"][1] and player.dead_undeads \
                                            or "if_dragon_hand" in player.hand[i].effects["cri de guerre"][1] and [x for x in player.hand if "Dragon" in x.genre and x != player.hand[i]] \
                                            or "if_alone" in player.hand[i].effects["cri de guerre"][1] and len(player.servants) == 0\
                                            or "if_spell" in player.hand[i].effects["cri de guerre"][1] and player.hand[i].effects["cri de guerre"][2] != 0:
                                        legal_actions[17 * i + 2] = True
                                        legal_actions[17 * i + 10] = True
                                        for j in range(len(player.servants)):
                                            legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True
                        elif "lieu" in player.hand[i].effects["cri de guerre"][1]:
                            if "ennemi" in player.hand[i].effects["cri de guerre"][1]:
                                for j in range(len(adv.lieux)):
                                    legal_actions[17 * i + j + 11] = True

                    elif "final" in player.hand[i].effects and "choisi" in player.hand[i].effects["final"][1]:
                        if "serviteur" in player.hand[i].effects["final"][1]:
                            if "allié" in player.hand[i].effects["final"][1] and player.servants.cards:
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                            else:
                                legal_actions[17 * i + 1] = True

                    # Serviteurs avec soif de mana ciblée
                    elif "soif de mana" in player.hand[i].effects and "choisi" in player.hand[i].effects["soif de mana"][1]:
                        if "serviteur" in player.hand[i].effects["soif de mana"][1]:
                            if "allié" in player.hand[i].effects["soif de mana"][1] and gamestate[f"serv1_j"] != -99:
                                if "genre" in player.hand[i].effects["soif de mana"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                            elif "ennemi" in player.hand[i].effects["cri de guerre"][1] and adv.servants.cards:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            elif "tous" in player.hand[i].effects["soif de mana"][1] and (gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in player.hand[i].effects["soif de mana"][1]:
                            if "ennemi" in player.hand[i].effects["soif de mana"][1]:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                            adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 2] = True
                                legal_actions[17 * i + 10] = True
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                    else:
                        legal_actions[17 * i + 1] = True
                    # Serviteurs avec magnétisme
                    if "magnetisme" in player.hand[i].effects:
                        for j in range(len(player.servants)):
                            if "Méca" in player.servants[j].genre:
                                legal_actions[17 * i + j + 3] = True
                elif player.hand[i].type.lower() == "sort":
                    if "ciblage" in player.hand[i].effects:
                        if "serviteur" in player.hand[i].effects["ciblage"]:
                            if "ennemi" in player.hand[i].effects["ciblage"]:
                                if "if_not_baston" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects and "baston" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                            elif "tous" in player.hand[i].effects["ciblage"]:
                                if "if_rale_agonie" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "rale d'agonie" in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "Mort-vivant" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "Mort-vivant" in adv.servants[j].genre:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_not_titan" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if not "titan" in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                            if not "titan" in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_not_swap_carac" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects and "swap_carac" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                        elif "tous" in player.hand[i].effects["ciblage"]:
                            if "ennemi" in player.hand[i].effects["ciblage"]:
                                legal_actions[17 * i + 10] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 2] = True
                                legal_actions[17 * i + 10] = True
                                for j in range(len(player.servants)):
                                    if "inciblable" not in player.servants[j].effects:
                                        legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                    else:
                        legal_actions[17 * i + 1] = True
                elif player.hand[i].type.lower() == "lieu" and len(player.servants) + len(player.lieux) < 7:
                    legal_actions[17 * i + 1] = True
                elif player.hand[i].type.lower() == "arme":
                    legal_actions[17 * i + 1] = True
        return legal_actions
    else:
        for i in range(len(player.hand)):
            if "reduc" in player.hand[i].effects and "self" in player.hand[i].effects["reduc"]:
                if "total_serv" in player.hand[i].effects["reduc"]:
                    player.hand[i].cost -= len(player.servants) + len(adv.servants)
            if ((player.hand[i].type == "Serviteur" and (player.hand[i].cost <= player.mana if "cost_armor" not in player.effects else player.hand[i].cost <= player.armor))\
                    or (player.hand[i].type != "Serviteur" and player.hand[i].cost <= player.mana)) and "entrave" not in player.hand[i].effects:
                if len(player.servants) + len(player.lieux) < 7 and player.hand[i].type == "Serviteur":
                    """ Serviteurs avec cris de guerre ciblés """
                    if "cri de guerre" in player.hand[i].effects and "choisi" in player.hand[i].effects["cri de guerre"][1]:
                        if "serviteur" in player.hand[i].effects["cri de guerre"][1]:
                            if "allié" in player.hand[i].effects["cri de guerre"][1] and player.servants.cards:
                                if "genre" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Bête" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Bête" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Mort-vivant" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Méca" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Méca" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "if_rale_agonie" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                elif "if_treant" in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].name == "Treant":
                                            legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                            elif "ennemi" in player.hand[i].effects["cri de guerre"][1] and adv.servants.cards:
                                if "conditional" not in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_provocation" in player.hand[i].effects["cri de guerre"][1]:
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects and "provocation" in adv.servants[
                                                j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True
                            elif "tous" in player.hand[i].effects["cri de guerre"][1] and (
                                    player.servants.cards or adv.servants.cards):
                                if "conditional" not in player.hand[i].effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_attack_greater" in player.hand[i].effects["cri de guerre"][1] \
                                            and [x for x in player.servants.cards + adv.servants.cards if x.attack >= player.hand[i].effects["cri de guerre"][1][5]]:
                                        for j in range(len(player.servants)):
                                            if player.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][
                                                5] and player.servants[j] != player.hand[i]:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if adv.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5]:
                                                legal_actions[17 * i + j + 11] = True
                                    elif "if_pur" in player.hand[i].effects["cri de guerre"][1] and not [x for x in player.deck if x.classe == "Neutre"]:
                                        for j in range(len(player.servants)):
                                            legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True
                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in player.hand[i].effects["cri de guerre"][1]:
                            if "ennemi" in player.hand[i].effects["cri de guerre"][1]:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                if "conditional" not in player.hand[i].effects["cri de guerre"][1]:
                                    legal_actions[17 * i + 2] = True
                                    legal_actions[17 * i + 10] = True
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_weapon" in player.hand[i].effects["cri de guerre"][
                                        1] and player.weapon is not None \
                                            or "if_death_undead" in player.hand[i].effects["cri de guerre"][
                                        1] and player.dead_undeads \
                                            or "if_dragon_hand" in player.hand[i].effects["cri de guerre"][1] and [x for
                                                                                                                   x in
                                                                                                                   player.hand
                                                                                                                   if
                                                                                                                   "Dragon" in x.genre and x !=
                                                                                                                   player.hand[
                                                                                                                       i]] \
                                            or "if_alone" in player.hand[i].effects["cri de guerre"][1] and len(
                                        player.servants) == 0 \
                                            or "if_spell" in player.hand[i].effects["cri de guerre"][1] and \
                                            player.hand[i].effects["cri de guerre"][2] != 0:
                                        legal_actions[17 * i + 2] = True
                                        legal_actions[17 * i + 10] = True
                                        for j in range(len(player.servants)):
                                            legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True
                        elif "lieu" in player.hand[i].effects["cri de guerre"][1]:
                            if "ennemi" in player.hand[i].effects["cri de guerre"][1]:
                                for j in range(len(adv.lieux)):
                                    legal_actions[17 * i + j + 11] = True
                    elif "final" in player.hand[i].effects and "choisi" in player.hand[i].effects["final"][1]:
                        if "serviteur" in player.hand[i].effects["final"][1]:
                            if "allié" in player.hand[i].effects["final"][1] and player.servants.cards:
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                            else:
                                legal_actions[17 * i + 1] = True
                    # Serviteurs avec soif de mana ciblée
                    elif "soif de mana" in player.hand[i].effects and "choisi" in \
                            player.hand[i].effects["soif de mana"][1]:
                        if "serviteur" in player.hand[i].effects["soif de mana"][1]:
                            if "allié" in player.hand[i].effects["soif de mana"][1] and gamestate[f"serv1_j"] != -99:
                                if "genre" in player.hand[i].effects["soif de mana"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                            elif "ennemi" in player.hand[i].effects["cri de guerre"][1] and adv.servants.cards:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            elif "tous" in player.hand[i].effects["soif de mana"][1] and (
                                    gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in player.hand[i].effects["soif de mana"][1]:
                            if "ennemi" in player.hand[i].effects["soif de mana"][1]:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                            adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 2] = True
                                legal_actions[17 * i + 10] = True
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                    else:
                        legal_actions[17 * i + 1] = True
                    # Serviteurs avec magnétisme
                    if "magnetisme" in player.hand[i].effects:
                        for j in range(len(player.servants)):
                            if ("Méca" in player.servants[j].genre) or ("Méca" in player.servants[j].genre and player.hand[i].name == "Parasite degoulinant"):
                                legal_actions[17 * i + j + 3] = True
                elif player.hand[i].type.lower() == "sort" and "unplayable" not in player.hand[i].effects:
                    if "ciblage" in player.hand[i].effects:
                        if "serviteur" in player.hand[i].effects["ciblage"]:
                            if "ennemi" in player.hand[i].effects["ciblage"]:
                                if "if_2adv" in player.hand[i].effects["ciblage"] and len([x for x in adv.servants if "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 2:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                            elif "allié" in player.hand[i].effects["ciblage"]:
                                if "conditional" in player.hand[i].effects["ciblage"]:
                                    if "if_bouclier_divin" in player.hand[i].effects["ciblage"] and [x for x in player.servants if "bouclier divin" in x.effects]:
                                        for j in range(len(player.servants)):
                                            if "inciblable" not in player.servants[j].effects and "bouclier divin" in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                            elif "tous" in player.hand[i].effects["ciblage"]:
                                if "if_rale_agonie" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects and "inciblable" not in \
                                                player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "rale d'agonie" in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "Mort-vivant" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre and "inciblable" not in \
                                                player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "Mort-vivant" in adv.servants[j].genre:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_recrue" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].name == "Recrue de la main d'argent" and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].name == "Recrue de la main d'argent":
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_atk_sup5" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].attack >= 5 and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].attack >= 5:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_indemne" in player.hand[i].effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].blessure == 0 and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].blessure == 0:
                                                legal_actions[17 * i + j + 11] = True
                                if "if_2serv" in player.hand[i].effects["ciblage"] \
                                        and len([x for x in adv.servants if "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) + len([x for x in player.servants if "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 2:
                                    for j in range(len(player.servants)):
                                        if "en sommeil" not in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                        elif "tous" in player.hand[i].effects["ciblage"]:
                            if "ennemi" in player.hand[i].effects["ciblage"]:
                                legal_actions[17 * i + 10] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects and "inciblable" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 2] = True
                                legal_actions[17 * i + 10] = True
                                for j in range(len(player.servants)):
                                    if "inciblable" not in player.servants[j].effects:
                                        legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects and "inciblable" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                    else:
                        legal_actions[17 * i + 1] = True
                elif player.hand[i].type.lower() == "lieu" and len(player.servants) + len(player.lieux) < 7:
                    legal_actions[17 * i + 1] = True
                elif player.hand[i].type.lower() == "arme":
                    legal_actions[17 * i + 1] = True
    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    is_provoc = False
    if not "ignore_taunt" in [x.effects["aura"][0] for x in player.servants if "aura" in x.effects]:
        for j in range(len(adv.servants)):
            if "provocation" in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                is_provoc = True
                break
    """ Notre héros peut attaquer """
    if player.remaining_atk > 0 and player.attack > 0:
        if not is_provoc and player.remaining_atk != 0.5:
            legal_actions[171] = True
        for j in range(len(adv.servants)):
            if not is_provoc:
                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                    legal_actions[171 + j + 1] = True
            else:
                if "provocation" in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                    legal_actions[171 + j + 1] = True

    """ Nos serviteurs peuvent attaquer """
    for i in range(len(player.servants)):
        if player.servants[i].remaining_atk * player.servants[i].attack > 0 and "en sommeil" not in player.servants[i].effects:
            if not is_provoc:
                legal_actions[171 + 8 * (i + 1)] = True
            if "ruée" in player.servants[i].effects:
                if player.servants[i].effects["ruée"] == 1:
                    legal_actions[171 + 8 * (i + 1)] = False
            for j in range(len(adv.servants)):
                if not is_provoc:
                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                        legal_actions[171 + 8 * (i + 1) + (j + 1)] = True
                else:
                    if "provocation" in adv.servants[j].effects:
                        legal_actions[171 + 8 * (i + 1) + (j + 1)] = True

    """ Pouvoir héroïque """
    if player.dispo_pouvoir and player.cout_pouvoir_temp <= player.mana:
        targets = state.targets_hp()
        if player in targets:
            legal_actions[235] = True
        if adv in targets:
            legal_actions[243] = True
        if len(targets) >= 2:
            for i in range(len(player.servants)):
                if player.servants[i] in targets:
                    legal_actions[236 + i] = True
            for i in range(len(adv.servants)):
                if adv.servants[i] in targets and not list({"camouflage", "en sommeil", "inciblable"} and set(adv.servants[i].effects)):
                    legal_actions[244 + i] = True

    """ Mot-clé échangeable ou forge """
    for i in range(len(player.hand)):
        if (player.mana >= 1 and "echangeable" in player.hand[i].effects and len(player.deck) != 0) or (player.mana >= 2 and "forge" in player.hand[i].effects):
            legal_actions[255 + i] = True

    """ Lieux """
    for i in range(len(player.lieux)):
        if player.lieux[i].attack == 1:
            if "choisi" in player.lieux[i].effects["use"][1]:
                if player.lieux[i].effects["use"][1][0] == "tous":
                    legal_actions[265 + 16 * i] = True
                    legal_actions[265 + 16 * i + 8] = True
                    for m in range(len(player.servants)):
                        legal_actions[265 + 16 * i + m + 1] = True
                    for n in range(len(adv.servants)):
                        if "camouflage" not in adv.servants[n].effects:
                            legal_actions[265 + 16 * i + n + 9] = True
                elif player.lieux[i].effects["use"][1][0] == "serviteur":
                    if player.lieux[i].effects["use"][1][1] == "allié":
                        if "conditional" in player.lieux[i].effects["use"][1]:
                            if "if_cadavre" in player.lieux[i].effects["use"][1] and player.cadavres >= player.lieux[i].effects["use"][1][-1]:
                                for m in range(len(player.servants)):
                                    legal_actions[265 + 16 * i + m + 1] = True
                            if "if_rale" in player.lieux[i].effects["use"][1]:
                                for m in range(len(player.servants)):
                                    if "rale d'agonie" in player.servants[m].effects:
                                        legal_actions[265 + 16 * i + m + 1] = True
                        else:
                            for m in range(len(player.servants)):
                                legal_actions[265 + 16 * i + m + 1] = True
                    elif player.lieux[i].effects["use"][1][1] == "tous":
                        for m in range(len(player.servants)):
                            legal_actions[265 + 16 * i + m + 1] = True
                        for n in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[n].effects:
                                legal_actions[265 + 16 * i + n + 9] = True
            else:
                legal_actions[265 + 16 * i] = True

    """ Titans """
    for i in range(len([x for x in player.servants if "titan" in x.effects and x.effects["titan"][-1] == 1])):
        for j in range(len([x for x in player.servants if "titan" in x.effects][i].effects["titan"]) - 1):
            legal_actions[377 + 3 * i + j] = True

    return legal_actions


def calc_advantage_serv(servant, player, adv, serv_adv=False):
    serv_advantage = 1.25 * servant.attack + 1.25 * servant.health
    if "bouclier divin" in servant.effects:
        serv_advantage += 1.25 * servant.attack
    if "rale d'agonie" in servant.effects:
        serv_advantage *= 1.25
    if "camouflage" in servant.effects:
        serv_advantage *= 1.25
    if "toxicite" in servant.effects:
        serv_advantage *= 1.25
    if "provocation" in servant.effects:
        serv_advantage += servant.health / player.health
    if "reincarnation" in servant.effects:
        serv_advantage += 1.25 * servant.attack
    if "gel" in servant.effects:
        serv_advantage -= servant.attack
    if "fragile" in servant.effects:
        serv_advantage /= 3
    if "frail" in servant.effects:
        serv_advantage /= 3
    if "en sommeil" in servant.effects:
        try:
            remaining_turns = servant.effects["en sommeil"] if type(servant.effects["en sommeil"]) == int else servant.effects["en sommeil"][-1]
            serv_advantage -= (remaining_turns / (remaining_turns + 1)) * (1.25 * servant.attack + 1.25 * servant.health)
        except:
            pass

    if not serv_adv:
        """ Potentiel value trade adverse """
        if [x for x in adv.servants if calc_advantage_serv(x, adv, player, serv_adv=True) < calc_advantage_serv(servant, player, adv, serv_adv=True)]:
            for adv_serv in [x for x in adv.servants if calc_advantage_serv(x, adv, player, serv_adv=True) < calc_advantage_serv(servant, player, adv, serv_adv=True)]:
                if deadly_attack(adv_serv, servant):
                    serv_advantage = min(serv_advantage, calc_advantage_serv(adv_serv, adv, player, serv_adv=True))
        """ Potentiel d'être tué par le HP adverse """
        if servant.health == 1 and "bouclier divin" not in servant.effects and "camouflage" not in servant.effects:
            if adv.classe in ["Chasseur de démons", "Mage", "Druide", "Chevalier de la mort", "Voleur"]:
                serv_advantage = min(serv_advantage, 2)
            t3 = time.perf_counter()

    return serv_advantage


def calc_advantage_card_hand(card, player):
    if card.cost <= player.mana_max:
        card_advantage = 1.5 + (0.1 * card.intrinsec_cost)
    else:
        card_advantage = 2 + (0.12 * card.intrinsec_cost)
    if not card.discount:
        card_advantage = card_advantage + 0.75 * (card.intrinsec_cost - card.cost)
    if card.type == "Serviteur":
        card_advantage = card_advantage * max(0.5, card.base_attack) / max(0.5, card.intrinsec_attack)
        card_advantage = card_advantage * max(0.5, card.base_health) / max(0.5, card.intrinsec_health)
    elif card.type == "Sort":
        if "decouverte" in card.effects or "add_hand" in card.effects or "add_deck" in card.effects or "pioche" in card.effects or "dragage" in card.effects:
            card_advantage /= 2
    if "forged" in card.effects:
        card_advantage += 1.5
    if "fragile" in card.effects:
        card_advantage = card_advantage / 3
    return card_advantage


def calc_advantage_minmax(state):
    player = state.players[0]
    adv = state.players[1]
    coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1, 1, 1, 1, 1, 1, 30, 30, 1

    if player.style == "aggro":
        if adv.style == "aggro":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 0.3, 0.1, 3, 3, 1, 0.2, 1, 3, 0.8
        elif adv.style == "tempo":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 0.2, 0.05, 3, 2, 1, 0.1, 0.5, 3.5, 1
        elif adv.style == "controle":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 0.75, 0, 1.75, 0.85, 1, 0.25, 0.25, 4, 1.5
    elif player.style == "tempo":
        if adv.style == "aggro":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1.75, 0.05, 1.3, 3, 1, 0.2, 2, 1.5, 1.25
        elif adv.style == "tempo":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 0.8, 0.25, 1.5, 1.5, 1, 0.25, 1.5, 1.5, 1.25
        elif adv.style == "controle":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1.2, 1, 0.85, 0.75, 1, 0.25, 0.75, 1.3, 1.5
    elif player.style == "controle":
        if adv.style == "aggro":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1, 0.25, 0.5, 3, 1, 1, 3, 0.25, 1.5
        elif adv.style == "tempo":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1.25, 1, 0.5, 2.25, 1, 1.5, 2, 0.75, 1.5
        elif adv.style == "controle":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 3, 3, 0.3, 0.5, 1, 3, 0.5, 0.5, 2

    """ End """
    if player.health <= 0:
        return -500
    elif adv.health <= 0:
        return 500


    """ Hand """
    discounts = [x.intrinsec_cost - x.cost for x in player.hand if x.discount]
    hand_advantage = sum([calc_advantage_card_hand(card, player) for card in player.hand])
    if discounts:
        hand_advantage += 0.5 * mean(discounts)
    hand_advantage -= 1.5 * len(adv.hand)
    hand_advantage *= coef_hand
    hand_advantage = round(hand_advantage, 3)

    """ Deck """
    deck_advantage = 0.1 * (len(player.deck) - len(adv.deck))
    if player.deck:
        deck_advantage += sum([(x.intrinsec_cost - x.cost) for x in player.deck])
    deck_advantage *= coef_deck
    deck_advantage = round(deck_advantage, 3)

    """ Board """
    board_advantage_j, board_advantage_adv = 0, 0
    board_advantage_j += sum([calc_advantage_serv(servant, player, adv) for servant in player.servants])
    board_advantage_j *= coef_board_j
    board_advantage_adv -= sum([calc_advantage_serv(servant, player, adv, serv_adv=True) for servant in adv.servants])
    board_advantage_adv *= coef_board_adv

    """ Weapon """
    weapon_advantage = 0
    if player.weapon is not None:
        weapon_advantage += max(1, player.weapon.attack) * player.weapon.health
    weapon_advantage *= coef_weapon

    """ Mana """
    mana_advantage = 0
    mana_advantage += 5 * (player.mana_max - adv.mana_max)
    mana_advantage *= coef_mana

    """ Health """
    health_advantage = 6 * coef_health_adv * (-math.sqrt(adv.health + adv.armor) + math.sqrt(adv.base_health + adv.armor))
    health_advantage -= 6 * coef_health_j * (-math.sqrt(player.health + player.armor) + math.sqrt(player.base_health + player.armor))
    health_advantage += 0.5 * (player.armor - adv.armor)
    health_advantage = round(health_advantage, 3)

    """ Others """
    other_advantage = 0
    # Secrets
    other_advantage += 2.5 * (sum([x.intrinsec_cost for x in player.secrets]) - sum([x.intrinsec_cost for x in adv.secrets]))
    # Lieux
    other_advantage += 2.5 * (sum([(x.attack * x.intrinsec_cost/x.intrinsec_attack) for x in player.lieux]) - sum([(x.attack * x.intrinsec_cost/x.intrinsec_attack) for x in adv.lieux]))
    # Autres
    other_advantage += 3 * (len(player.attached) - len(adv.attached))
    other_advantage += 4 * len(player.permanent_buff)
    other_advantage += 0.01 * player.cadavres
    other_advantage *= coef_other

    advantage = hand_advantage + deck_advantage + board_advantage_j + board_advantage_adv + weapon_advantage + mana_advantage + health_advantage + other_advantage

    """ Lethal on board adverse """
    if adv.servants and sum([x.attack for x in adv.servants]) >= player.health and not [x for x in player.servants if "provocation" in x.effects]:
        advantage -= 300

    return round(advantage, 2)


total_actions = 0


def minimax(state, alpha=-1000, depth=0, best_action=-99, max_depth=3, exploration_toll=2.8):
    gc.disable()
    global total_actions
    base_advantage = calc_advantage_minmax(state)
    legal_actions = np.array(generate_legal_vector_test(state), dtype=bool)
    legal_actions = [i for i in range(len(legal_actions)) if legal_actions[i]]
    state_saved = pickle.dumps(state, -1)

    possible_new_states = np.array([
        (action, Orchestrator().tour_ia_minmax(pickle.loads(state_saved), [], action, False)[0]) for action
        in legal_actions
    ])

    first_estimate = [calc_advantage_minmax(possible_new_states[i][1]) for i in range(len(possible_new_states))]
    if len(possible_new_states) != 0 and possible_new_states[0][0] == 0:
        first_estimate[0] = base_advantage
    first_estimate_sorted = np.array(first_estimate).argsort()
    to_simulate = -max(round(min(30, len(possible_new_states)) / (pow(exploration_toll, depth))), 1)
    first_estimate_duplicates = [idx for idx, item in enumerate(first_estimate) if item in first_estimate[:idx]]
    first_estimate_sorted1 = first_estimate_sorted[~np.in1d(first_estimate_sorted, first_estimate_duplicates)]


    if not (251 <= min(legal_actions) and max(legal_actions) <= 254):
        if depth != 0:
            possible_new_states = possible_new_states[first_estimate_sorted1[to_simulate:]]
        else:
            possible_new_states = possible_new_states[first_estimate_sorted1[-min(25, len(possible_new_states)):]]

    gc.enable()

    for new_state in possible_new_states:
        total_actions += 1
        previous_reward = alpha

        """ On va chercher les feuilles de l'arbre pour en récuperer la valeur """
        if new_state[0] == 0 or depth == max_depth:
            alpha = max(alpha, base_advantage)
        else:
            alpha = minimax(new_state[1], alpha, depth+1)[0]

        """ On met à jour alpha si nécessaire """
        if alpha > previous_reward and depth == 0:
            best_action = new_state[0]
            if alpha == 500:
                if type(best_action) == list:
                    best_action.append(new_state[0])
                else:
                    best_action = [new_state[0]]
                break

    if depth == 0:
        print(f"Total actions : {total_actions}")
        total_actions = 0
    return alpha, best_action


logs = []
beginning = time.perf_counter()
for i in range(3):
    print(i)
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    while plateau_depart.game_on:
        try:
            max_reward, best_action = minimax(plateau_depart)
            if type(best_action) == list:
                for action in best_action:
                    plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], action)
            else:
                plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], best_action)
        except:
            max_reward, best_action = minimax(plateau_depart)
            if type(best_action) == list:
                for action in best_action:
                    plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], action)
            else:
                plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], best_action)
        # print(f"Meilleure action : {best_action}   ---   Avantage estimé : {max_reward}")
        # print('----------------------------------------------')
        logs.append(pd.DataFrame(logs_inter))
    plateau_depart = Plateau(pickle.loads(pickle.dumps(players, -1)))

end = time.perf_counter()
logs_hs = pd.concat(logs).reset_index().drop("index", axis=1)
print(f"Temps total : {round(end - beginning, 1)}s")

""" Sauvegarde des logs"""
os.remove('logs_games.pickle')
with open('logs_games.pickle', 'wb') as f:
    pickle.dump(logs_hs, f)

