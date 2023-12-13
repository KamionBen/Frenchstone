import time
from engine import *
import gc
import math
import functools


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
            serv_effects = player.hand[i].effects
            if "reduc" in player.hand[i].effects and "self" in player.hand[i].effects["reduc"]:
                if "total_serv" in player.hand[i].effects["reduc"]:
                    player.hand[i].cost = max(0, player.hand[i].cost - len(player.servants) + len(adv.servants))
                elif "adv_servants" in player.hand[i].effects["reduc"]:
                    player.hand[i].cost -= len(adv.servants)
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
                                    if "if_attack_greater" in player.hand[i].effects["cri de guerre"][1] and [x for x in player.servants.cards + adv.servants.cards if x.attack >= player.hand[i].effects["cri de guerre"][1][5]]\
                                            or "if_death_undead" in player.hand[i].effects["cri de guerre"][1] and player.dead_undeads:
                                        for j in range(len(player.servants)):
                                            if player.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5] and player.servants[j] != player.hand[i]:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if adv.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5]:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        player.hand[i].effects.pop("cri de guerre")
                                        legal_actions[17 * i + 1] = True
                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in player.hand[i].effects["cri de guerre"][1]:
                            if "ennemi" in player.hand[i].effects["cri de guerre"][1]:
                                legal_actions[17 * i + 10] = True
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
                                        player.hand[i].effects.pop("cri de guerre")
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
                    if "ciblage" in serv_effects:
                        if "serviteur" in serv_effects["ciblage"]:
                            if "ennemi" in serv_effects["ciblage"]:
                                if "if_2adv" in serv_effects["ciblage"]:
                                    if len([x for x in adv.servants if
                                            "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 2:
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects and "inciblable" not in adv.servants[
                                                j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_blessure" in serv_effects["ciblage"]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects\
                                                and adv.servants[j].blessure != 0:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                            elif "allié" in serv_effects["ciblage"]:
                                if "conditional" in serv_effects["ciblage"]:
                                    if "if_bouclier_divin" in serv_effects["ciblage"] and [x for x in player.servants if
                                                                                           "bouclier divin" in x.effects]:
                                        for j in range(len(player.servants)):
                                            if "inciblable" not in player.servants[j].effects and "en sommeil" not in \
                                                    player.servants[j].effects and "bouclier divin" in player.servants[
                                                j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                    elif "if_adv" in serv_effects["ciblage"] and len([x for x in adv.servants if
                                                                                      "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 1:
                                        for j in range(len(player.servants)):
                                            if "en sommeil" not in player.servants[j].effects and "inciblable" not in \
                                                    player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                    elif "if_rale_agonie" in serv_effects["ciblage"]:
                                        for j in range(len(player.servants)):
                                            if "rale d'agonie" in player.servants[j].effects and "inciblable" not in \
                                                    player.servants[j].effects and "en sommeil" not in player.servants[
                                                j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects and "en sommeil" not in \
                                                player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                            elif "tous" in serv_effects["ciblage"]:
                                if "if_rale_agonie" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects and "inciblable" not in \
                                                player.servants[j].effects and "en sommeil" not in player.servants[
                                            j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "rale d'agonie" in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "Mort-vivant" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre and "inciblable" not in \
                                                player.servants[j].effects and "en sommeil" not in player.servants[
                                            j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "Mort-vivant" in adv.servants[j].genre:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_recrue" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[
                                            j].name == "Recrue de la main d'argent" and "inciblable" not in \
                                                player.servants[j].effects \
                                                and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].name == "Recrue de la main d'argent":
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_atk_sup5" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].attack >= 5 and "inciblable" not in player.servants[
                                            j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].attack >= 5:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_indemne" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].blessure == 0 and "inciblable" not in player.servants[
                                            j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].blessure == 0:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_2serv" in serv_effects["ciblage"] \
                                        and len([x for x in adv.servants if
                                                 "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) + len(
                                    [x for x in player.servants if
                                     "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 2:
                                    for j in range(len(player.servants)):
                                        if "en sommeil" not in player.servants[j].effects and "inciblable" not in \
                                                player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                elif "if_not_titan" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects and "titan" not in \
                                                player.servants[j].effects and "en sommeil" not in player.servants[
                                            j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[
                                            j].effects and "titan" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects and "en sommeil" not in \
                                                player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                        elif "tous" in serv_effects["ciblage"]:
                            if "ennemi" in serv_effects["ciblage"]:
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
        if len([x for x in legal_actions if x]) == 1:
            for card in [x for x in player.hand if "mandatory" in x.effects]:
                player.hand.remove(card)
        return legal_actions
    else:
        for i in range(len(player.hand)):
            serv_effects = player.hand[i].effects
            if "reduc" in player.hand[i].effects and "self" in player.hand[i].effects["reduc"]:
                if "total_serv" in player.hand[i].effects["reduc"]:
                    player.hand[i].cost = max(0, player.hand[i].cost - len(player.servants) + len(adv.servants))
                elif "adv_servants" in player.hand[i].effects["reduc"]:
                    player.hand[i].cost -= len(adv.servants)
            if ((player.hand[i].type == "Serviteur" and (player.hand[i].cost <= player.mana if "cost_armor" not in player.effects else player.hand[i].cost <= player.armor))\
                    or (player.hand[i].type != "Serviteur" and player.hand[i].cost <= player.mana)) and "entrave" not in serv_effects:
                if player.hand[i].type == "Serviteur" and ((len(player.servants) + len(player.lieux) < 7 and "reno_ranger" not in player.permanent_buff) or\
                        (len(player.servants) + len(player.lieux) == 0 and "reno_ranger" in player.permanent_buff)):
                    """ Serviteurs avec cris de guerre ciblés """
                    if "cri de guerre" in serv_effects and "choisi" in serv_effects["cri de guerre"][1]:
                        if "serviteur" in serv_effects["cri de guerre"][1]:
                            if "allié" in serv_effects["cri de guerre"][1] and player.servants.cards:
                                if "genre" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Bête" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Bête" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Mort-vivant" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "Méca" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "Méca" in player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                elif "if_rale_agonie" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                elif "if_treant" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].name == "Treant":
                                            legal_actions[17 * i + j + 3] = True
                                elif "if_diablotin" in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        if "diablotin" in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                            elif "ennemi" in serv_effects["cri de guerre"][1] and adv.servants.cards:
                                if "conditional" not in serv_effects["cri de guerre"][1]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_provocation" in serv_effects["cri de guerre"][1]:
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects and "provocation" in adv.servants[
                                                j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    if "if_dragon_inhand" in serv_effects["cri de guerre"][1] and [x for x in player.hand if "Dragon" in x.genre]:
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        legal_actions[17 * i + 1] = True
                            elif "tous" in serv_effects["cri de guerre"][1] and (
                                    player.servants.cards or adv.servants.cards):
                                if "conditional" not in serv_effects["cri de guerre"][1]:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if ("if_attack_greater" in serv_effects["cri de guerre"][1]\
                                            and [x for x in player.servants.cards + adv.servants.cards if x.attack >= serv_effects["cri de guerre"][1][5]]):
                                        for j in range(len(player.servants)):
                                            if player.servants[j].attack >= serv_effects["cri de guerre"][1][
                                                5] and player.servants[j] != player.hand[i]:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if adv.servants[j].attack >= serv_effects["cri de guerre"][1][5]:
                                                legal_actions[17 * i + j + 11] = True
                                    elif ("if_pur" in serv_effects["cri de guerre"][1] and not [x for x in player.deck if x.classe == "Neutre"])\
                                           or ("if_death_undead" in serv_effects["cri de guerre"][1] and player.dead_undeads):
                                        for j in range(len(player.servants)):
                                            if "en sommeil" not in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                    elif "if_hurt" in serv_effects["cri de guerre"][1] and [x for x in player.servants.cards + adv.servants.cards if x.blessure > 0]:
                                        for j in range(len(player.servants)):
                                            if player.servants[j].blessure > 0 and "en sommeil" not in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                    adv.servants[j].effects and adv.servants[j].blessure > 0:
                                                legal_actions[17 * i + j + 11] = True
                                    else:
                                        serv_effects.pop("cri de guerre")
                                        legal_actions[17 * i + 1] = True
                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in serv_effects["cri de guerre"][1]:
                            if "ennemi" in serv_effects["cri de guerre"][1]:
                                legal_actions[17 * i + 10] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                if "conditional" not in serv_effects["cri de guerre"][1]:
                                    legal_actions[17 * i + 2] = True
                                    legal_actions[17 * i + 10] = True
                                    for j in range(len(player.servants)):
                                        if "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    if "if_weapon" in serv_effects["cri de guerre"][
                                        1] and player.weapon is not None \
                                            or "if_death_undead" in serv_effects["cri de guerre"][
                                        1] and player.dead_undeads \
                                            or "if_dragon_hand" in serv_effects["cri de guerre"][1] and [x for
                                                                                                                   x in
                                                                                                                   player.hand
                                                                                                                   if
                                                                                                                   "Dragon" in x.genre and x !=
                                                                                                                   player.hand[
                                                                                                                       i]] \
                                            or "if_alone" in serv_effects["cri de guerre"][1] and len(
                                        player.servants) == 0 \
                                            or "if_spell" in serv_effects["cri de guerre"][1] and serv_effects["cri de guerre"][2] != 0 \
                                            or "if_cadavre" in serv_effects["cri de guerre"][1] and player.cadavres >= serv_effects["cri de guerre"][2]\
                                            or "if_méca_inhand" in serv_effects["cri de guerre"][1] and [x for x in player.hand if "Méca" in x.genre and x != player.hand[i]]\
                                            or "if_hand_cost4" in serv_effects["cri de guerre"][1] and [x for x in player.hand if x.cost == 4]:
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
                        elif "lieu" in serv_effects["cri de guerre"][1]:
                            if "ennemi" in serv_effects["cri de guerre"][1]:
                                for j in range(len(adv.lieux)):
                                    legal_actions[17 * i + j + 11] = True
                    elif "final" in serv_effects and "choisi" in serv_effects["final"][1]:
                        if "serviteur" in serv_effects["final"][1]:
                            if "allié" in serv_effects["final"][1] and player.servants.cards:
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                            else:
                                legal_actions[17 * i + 1] = True
                    # Serviteurs avec soif de mana ciblée
                    elif "soif de mana" in serv_effects and "choisi" in \
                            serv_effects["soif de mana"][1]:
                        if "serviteur" in serv_effects["soif de mana"][1]:
                            if "allié" in serv_effects["soif de mana"][1] and gamestate[f"serv1_j"] != -99:
                                if "genre" in serv_effects["soif de mana"][1]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].genre:
                                            legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        legal_actions[17 * i + j + 3] = True
                            elif "ennemi" in serv_effects["cri de guerre"][1] and adv.servants.cards:
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            elif "tous" in serv_effects["soif de mana"][1] and (
                                    gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
                                for j in range(len(player.servants)):
                                    legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                legal_actions[17 * i + 1] = True
                        elif "tous" in serv_effects["soif de mana"][1]:
                            if "ennemi" in serv_effects["soif de mana"][1]:
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
                    if "magnetisme" in serv_effects:
                        for j in range(len(player.servants)):
                            if ("Méca" in player.servants[j].genre) or ("Méca" in player.servants[j].genre and player.hand[i].name == "Parasite degoulinant"):
                                legal_actions[17 * i + j + 3] = True
                elif player.hand[i].type.lower() == "sort" and "unplayable" not in serv_effects:
                    if "ciblage" in serv_effects:
                        if "serviteur" in serv_effects["ciblage"]:
                            if "ennemi" in serv_effects["ciblage"]:
                                if "if_2adv" in serv_effects["ciblage"]:
                                    if len([x for x in adv.servants if "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 2:
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_blessure" in serv_effects["ciblage"]:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects\
                                                and adv.servants[j].blessure != 0:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                            elif "allié" in serv_effects["ciblage"]:
                                if "conditional" in serv_effects["ciblage"]:
                                    if "if_bouclier_divin" in serv_effects["ciblage"] and [x for x in player.servants if "bouclier divin" in x.effects]:
                                        for j in range(len(player.servants)):
                                            if "inciblable" not in player.servants[j].effects and "en sommeil" not in player.servants[j].effects and "bouclier divin" in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                    elif "if_adv" in serv_effects["ciblage"] and len([x for x in adv.servants if
                                                                                     "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 1:
                                        for j in range(len(player.servants)):
                                            if "en sommeil" not in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                    elif "if_rale_agonie" in serv_effects["ciblage"]:
                                        for j in range(len(player.servants)):
                                            if "rale d'agonie" in player.servants[j].effects and "inciblable" not in \
                                                    player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                    elif "if_undead" in serv_effects["ciblage"]:
                                        for j in range(len(player.servants)):
                                            if "Mort_vivant" in player.servants[j].genre and "inciblable" not in \
                                                    player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                                legal_actions[17 * i + j + 3] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                            elif "tous" in serv_effects["ciblage"]:
                                if "if_rale_agonie" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "rale d'agonie" in player.servants[j].effects and "inciblable" not in \
                                                player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "rale d'agonie" in adv.servants[j].effects:
                                                legal_actions[17 * i + j + 11] = True
                                elif "Mort-vivant" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "Mort-vivant" in player.servants[j].genre and "inciblable" not in \
                                                player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if "Mort-vivant" in adv.servants[j].genre:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_recrue" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].name == "Recrue de la main d'argent" and "inciblable" not in player.servants[j].effects\
                                                and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].name == "Recrue de la main d'argent":
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_atk_sup5" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].attack >= 5 and "inciblable" not in player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].attack >= 5:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_indemne" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].blessure == 0 and "inciblable" not in player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            if adv.servants[j].blessure == 0:
                                                legal_actions[17 * i + j + 11] = True
                                elif "if_2serv" in serv_effects["ciblage"] \
                                        and len([x for x in adv.servants if "camouflage" not in x.effects and "en sommeil" not in x.effects and "inciblable" not in x.effects]) + len([x for x in player.servants if "en sommeil" not in x.effects and "inciblable" not in x.effects]) >= 2:
                                    for j in range(len(player.servants)):
                                        if "en sommeil" not in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                elif "if_not_titan" in serv_effects["ciblage"]:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects and "titan" not in player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects and "titan" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    for j in range(len(player.servants)):
                                        if "inciblable" not in player.servants[j].effects and "en sommeil" not in player.servants[j].effects:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                                adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                        elif "tous" in serv_effects["ciblage"]:
                            if "ennemi" in serv_effects["ciblage"]:
                                legal_actions[17 * i + 10] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[
                                        j].effects and "inciblable" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                            else:
                                if "conditional" in serv_effects["ciblage"]:
                                    if "if_hurt" in serv_effects["ciblage"]:
                                        if player.health < player.base_health:
                                            legal_actions[17 * i + 2] = True
                                        if adv.health < adv.base_health:
                                            legal_actions[17 * i + 10] = True
                                        for j in range(len(player.servants)):
                                            if "inciblable" not in player.servants[j].effects and player.servants[j].blessure > 0:
                                                legal_actions[17 * i + j + 3] = True
                                        for j in range(len(adv.servants)):
                                            if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects and adv.servants[j].blessure > 0:
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
                elif player.hand[i].type.lower() == "lieu" and ((len(player.servants) + len(player.lieux) < 7 and "reno_ranger" not in player.permanent_buff) or\
                        (len(player.servants) + len(player.lieux) == 0 and "reno_ranger" in player.permanent_buff)):
                    legal_actions[17 * i + 1] = True
                elif player.hand[i].type.lower() == "heros":
                    legal_actions[17 * i + 1] = True
                elif player.hand[i].type.lower() == "arme":
                    if "cri de guerre" in serv_effects and "choisi" in serv_effects["cri de guerre"][1]:
                        if "tous" in serv_effects["cri de guerre"][1]:
                            legal_actions[17 * i + 2] = True
                            legal_actions[17 * i + 10] = True
                            for j in range(len(player.servants)):
                                if "en sommeil" not in player.servants[j].effects:
                                    legal_actions[17 * i + j + 3] = True
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in \
                                        adv.servants[j].effects:
                                    legal_actions[17 * i + j + 11] = True
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

    if [x for x in legal_actions if x and x >= 171 + 8 * (len(player.servants) + 1)]:
        print(player.servants, adv.servants, [x for x in legal_actions if x and x >= 171 + 8 * (len(player.servants) + 1)])

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
                    if "en sommeil" not in player.servants[i].effects:
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
                        if "en sommeil" not in player.servants[m].effects:
                            legal_actions[265 + 16 * i + m + 1] = True
                    for n in range(len(adv.servants)):
                        if "camouflage" not in adv.servants[n].effects and "en sommeil" not in adv.servants[n].effects:
                            legal_actions[265 + 16 * i + n + 9] = True
                elif player.lieux[i].effects["use"][1][0] == "serviteur":
                    if player.lieux[i].effects["use"][1][1] == "allié":
                        if "conditional" in player.lieux[i].effects["use"][1]:
                            if "if_cadavre" in player.lieux[i].effects["use"][1] and player.cadavres >= player.lieux[i].effects["use"][1][-1]:
                                for m in range(len(player.servants)):
                                    if "en sommeil" not in player.servants[m].effects:
                                        legal_actions[265 + 16 * i + m + 1] = True
                            if "if_rale" in player.lieux[i].effects["use"][1]:
                                for m in range(len(player.servants)):
                                    if "rale d'agonie" in player.servants[m].effects and "en sommeil" not in player.servants[m].effects:
                                        legal_actions[265 + 16 * i + m + 1] = True
                        else:
                            for m in range(len(player.servants)):
                                if "en sommeil" not in player.servants[m].effects:
                                    legal_actions[265 + 16 * i + m + 1] = True
                    elif player.lieux[i].effects["use"][1][1] == "tous":
                        for m in range(len(player.servants)):
                            if "en sommeil" not in player.servants[m].effects:
                                legal_actions[265 + 16 * i + m + 1] = True
                        for n in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[n].effects and "en sommeil" not in adv.servants[n].effects:
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
    if "aura" in servant.effects:
        serv_advantage *= 1.5
    if "toxicite" in servant.effects:
        serv_advantage *= 1.25
    if "provocation" in servant.effects:
        serv_advantage += servant.health / player.health
    if "reincarnation" in servant.effects:
        serv_advantage += 1.25 * servant.attack
    if "gel" in servant.effects:
        serv_advantage -= 1.25 * servant.attack
    if "fragile" in servant.effects:
        serv_advantage /= 3
    if "frail" in servant.effects:
        serv_advantage /= 3
    if "en sommeil" in servant.effects:
        remaining_turns = servant.effects["en sommeil"] if type(servant.effects["en sommeil"]) == int else servant.effects["en sommeil"][-1]
        serv_advantage -= (remaining_turns / (remaining_turns + 1)) * (1.25 * servant.attack + 1.25 * servant.health)
    if not servant.attack:
        serv_advantage /= 1.5

    if not serv_adv:
        """ Potentiel value trade adverse """
        value_trade = [calc_advantage_serv(x, adv, player, serv_adv=True) for x in adv.servants if (calc_advantage_serv(x, adv, player, serv_adv=True) < calc_advantage_serv(servant, player, adv, serv_adv=True)) and deadly_attack(x, servant)]
        if value_trade:
            serv_advantage = min(serv_advantage, min(value_trade))
        """ Potentiel d'être tué par le HP adverse """
        if servant.health == 1 and "bouclier divin" not in servant.effects and "camouflage" not in servant.effects and adv.classe in ["Chasseur de démons", "Mage", "Druide", "Chevalier de la mort", "Voleur"]:
            serv_advantage = min(serv_advantage, 2)
    return serv_advantage


def calc_advantage_card_hand(card, player):
    if card.cost <= player.mana_max:
        card_advantage = 1.5 + (0.1 * card.intrinsec_cost)
    else:
        card_advantage = 2 + (0.12 * card.intrinsec_cost)
    if not card.discount:
        card_advantage = card_advantage + min(0.75 * (card.intrinsec_cost - card.cost), 5)
    if card.type == "Serviteur":
        card_advantage = card_advantage * min(max(0.5, card.base_attack) / max(0.5, card.intrinsec_attack), 1.5)
        card_advantage = card_advantage * min(max(0.5, card.base_health) / max(0.5, card.intrinsec_health), 1.5)
    elif card.type == "Sort":
        if "decouverte" in card.effects or "add_hand" in card.effects or "add_deck" in card.effects or "pioche" in card.effects or "dragage" in card.effects:
            card_advantage /= 2
    if "forged" in card.effects:
        card_advantage += 3
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
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1, 0.25, 0.6, 2.5, 1, 1, 3, 0.25, 1.5
        elif adv.style == "tempo":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1.2, 1, 0.7, 2, 1, 1.5, 2, 0.75, 1.5
        elif adv.style == "controle":
            coef_hand, coef_deck, coef_board_j, coef_board_adv, coef_weapon, coef_mana, coef_health_j, coef_health_adv, coef_other = 1.7, 2, 0.8, 0.85, 1, 3, 1, 0.5, 2

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

    """ Deck """
    deck_advantage = 0.1 * (len(player.deck) - len(adv.deck))
    if player.deck:
        deck_advantage += sum([(x.intrinsec_cost - x.cost) for x in player.deck])
        deck_advantage += 0.5 * sum([(x.base_attack - x.intrinsec_attack) for x in player.deck if x.type in ["Serviteur", "Arme"]])
        deck_advantage += 0.5 * sum([(x.base_health - x.intrinsec_health) for x in player.deck if x.type in ["Serviteur", "Arme"]])
    if player.forge and [x for x in player.deck.cards + player.hand.cards if x.name == "Ignis la flamme eternelle"]:
        deck_advantage += 1
    deck_advantage *= coef_deck

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
    mana_advantage += 4.5 * (player.mana_max - adv.mana_max)
    mana_advantage += 1.5 * (sum(adv.surcharge) - sum(player.surcharge))
    mana_advantage *= coef_mana

    """ Health """
    health_advantage = 6 * coef_health_adv * (-math.sqrt(adv.health + adv.armor) + math.sqrt(adv.base_health + adv.armor))
    health_advantage -= 6 * coef_health_j * (-math.sqrt(player.health + player.armor) + math.sqrt(player.base_health + player.armor))
    health_advantage += 0.5 * (player.armor - adv.armor)
    """ Others """
    other_advantage = 0
    # Secrets
    other_advantage += 2.5 * (sum([x.intrinsec_cost for x in player.secrets]) - sum([x.intrinsec_cost for x in adv.secrets]))
    # Lieux
    other_advantage += 2.5 * (sum([(x.attack * x.intrinsec_cost/x.intrinsec_attack) for x in player.lieux]) - sum([(x.attack * x.intrinsec_cost/x.intrinsec_attack) for x in adv.lieux]))
    # Autres
    other_advantage += 4 * len(player.permanent_buff)
    other_advantage += 4 * len(player.next_turn)
    other_advantage += 0.01 * player.cadavres
    if player.power is not None:
        other_advantage += 5
    other_advantage *= coef_other

    advantage = hand_advantage + deck_advantage + board_advantage_j + board_advantage_adv + weapon_advantage + mana_advantage + health_advantage + other_advantage

    """ Lethal on board adverse """
    if adv.servants and sum([x.attack for x in adv.servants]) >= player.health and not [x for x in player.servants if "provocation" in x.effects]:
        advantage -= 300

    return round(advantage, 2)


total_actions = 0
# avg_time = [[0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1]]

def minimax(state, alpha=-1000, depth=0, best_action=-99, max_depth=3, exploration_toll=2.75):
    t0 = time.perf_counter()
    gc.disable()
    global total_actions
    base_advantage = calc_advantage_minmax(state)
    t1 = time.perf_counter()
    legal_actions = np.array(generate_legal_vector_test(state), dtype=bool)
    legal_actions = [i for i in range(len(legal_actions)) if legal_actions[i]]
    if len(legal_actions) == 0:
        player = state.players[0]
        adv = state.players[1]
        print(player.health, adv.health)
        print(player.servants, adv.servants)
        print(player.mana)
        print(player.hand)
    t2_byaction = (time.perf_counter() - t1) / len(legal_actions)
    t2 = time.perf_counter()

    state_saved = pickle.dumps(state, -1)
    t3 = time.perf_counter()

    possible_new_states = np.array([
         (action, Orchestrator().tour_ia_minmax(pickle.loads(state_saved), [], action, False)[0]) for action in legal_actions
    ])

    t4_byaction = (time.perf_counter() - t3)/len(legal_actions)
    t4 = time.perf_counter()

    first_estimate = [calc_advantage_minmax(possible_new_states[i][1]) for i in range(len(possible_new_states))]
    t5_byaction = (time.perf_counter() - t4) / len(possible_new_states)
    t5 = time.perf_counter()
    if len(possible_new_states) != 0 and possible_new_states[0][0] == 0:
        first_estimate[0] = base_advantage
    first_estimate_sorted = np.array(first_estimate).argsort()
    to_simulate = -max(round(min(30, len(possible_new_states)) / (pow(exploration_toll, depth))), 1)
    first_estimate_duplicates = [idx for idx, item in enumerate(first_estimate) if item in first_estimate[:idx]]
    first_estimate_sorted1 = first_estimate_sorted[~np.in1d(first_estimate_sorted, first_estimate_duplicates)]
    t6 = time.perf_counter()

    # avg_time[0][0] += 1000 * (t1 - t0)
    # avg_time[0][1] += 1
    # avg_time[1][0] += 1000 * t2_byaction
    # avg_time[1][1] += 1
    # avg_time[2][0] += 1000 * (t3 - t2)
    # avg_time[2][1] += 1
    # avg_time[3][0] += 1000 * t4_byaction
    # avg_time[3][1] += 1
    # avg_time[4][0] += 1000 * t5_byaction
    # avg_time[4][1] += 1
    # avg_time[5][0] += 1000 * (t6 - t5)
    # avg_time[5][1] += 1

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
class_to_chose = ["Chevalier de la mort", "Chasseur de démons", "Paladin", "Voleur", "Prêtre", "Chasseur", "Druide", "Mage", "Chaman", "Démoniste", "Guerrier"]
for i in range(3):
    class_j1 = "Paladin"
    class_j2 = random.choice(class_to_chose)
    players = [Player("NewIA", class_j1), Player("OldIA", class_j2)].copy()
    plateau_depart = Plateau(pickle.loads(pickle.dumps(players, -1)))
    print(i)
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    copy_best_action = 0
    while plateau_depart.game_on:
        max_reward, best_action = minimax(plateau_depart)
        copy_best_action = best_action
        if type(best_action) == list:
            for action in best_action:
                plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], action, generate_logs=True)
        else:
            plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], best_action, generate_logs=True)
        # print(round(avg_time[0][0]/avg_time[0][1], 3), round(avg_time[1][0]/avg_time[1][1], 3), round(avg_time[2][0]/avg_time[2][1], 3), round(avg_time[3][0]/avg_time[3][1], 3), round(avg_time[4][0]/avg_time[4][1], 3), round(avg_time[5][0]/avg_time[5][1], 3))
        # print(f"Meilleure action : {best_action}   ---   Avantage estimé : {max_reward}")
        # print('----------------------------------------------')
        logs.append(pd.DataFrame(logs_inter))

end = time.perf_counter()
logs_hs = pd.concat(logs).reset_index().drop("index", axis=1)
print(f"Temps total : {round(end - beginning, 1)}s")

""" Sauvegarde des logs"""
os.remove('logs_games.pickle')
with open('logs_games.pickle', 'wb') as f:
    pickle.dump(logs_hs, f)

