from abc import ABC

import pandas as pd
import numpy as np
from Entities import *
import random
import os
from operator import itemgetter
from tf_agents.trajectories import time_step as ts
import tensorflow as tf
from tf_agents.specs import array_spec
from tf_agents.environments import py_environment, tf_py_environment


def generate_column_state_old(classes_hero):
    columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                            "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]

    """ HERO """
    for classe in classes_hero:
        columns_actual_state.append(f"is_{classe}")

    """ HAND """
    for n in range(10):
        columns_actual_state.append(f"carte_en_main{n + 1}_cost")
        columns_actual_state.append(f"carte_en_main{n + 1}_atk")
        columns_actual_state.append(f"carte_en_main{n + 1}_pv")

    """ SERVANTS """
    for n in range(7):
        columns_actual_state.append(f"atq_serv{n + 1}_j")
        columns_actual_state.append(f"pv_serv{n + 1}_j")
        columns_actual_state.append(f"atq_remain_serv{n + 1}_j")

    for n in range(7):
        columns_actual_state.append(f"atq_serv{n + 1}_adv")
        columns_actual_state.append(f"pv_serv{n + 1}_adv")

    return columns_actual_state


def generate_column_state(classes_hero):
    columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                            "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]

    """ HERO """
    for classe in classes_hero:
        columns_actual_state.append(f"is_{classe}")

    """ HAND """
    for n in range(10):
        for m in range(len(all_cards)):
            columns_actual_state.append(f"is_carte{n + 1}_{all_cards[m]['name']}")

    """ SERVANTS """
    for n in range(7):
        columns_actual_state.append(f"atq_serv{n + 1}_j")
        columns_actual_state.append(f"pv_serv{n + 1}_j")
        columns_actual_state.append(f"atq_remain_serv{n + 1}_j")
        for m in range(len(all_servants)):
            columns_actual_state.append(f"is_servant{n + 1}_{all_servants[m]['name']}_j")
            columns_actual_state.append(f"is_servant{n + 1}_{all_servants[m]['name']}_adv")

    for n in range(7):
        columns_actual_state.append(f"atq_serv{n + 1}_adv")
        columns_actual_state.append(f"pv_serv{n + 1}_adv")

    return columns_actual_state


def generate_legal_vector_old(state):
    """ Gestion des actions légales """
    legal_actions = [True]
    gamestate = state.get_gamestate()
    for n in range(90):
        legal_actions.append(False)

    """ Quelles cartes peut-on jouer ? """
    for n in range(int(gamestate["nbre_cartes_j"])):
        for m in range(len(all_cards)):
            if gamestate[f"is_carte{n + 1}_{all_cards[m]['name']}"] != -99 \
                    and get_card(all_cards[m]['name'], all_cards).cost <= gamestate["mana_dispo_j"] \
                    and gamestate[f"pv_serv7_j"] == -99:
                legal_actions[n + 1] = True

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    """ Notre héros peut attaquer """
    if gamestate["remaining_atk_j"] > 0 and gamestate["attaque_j"] > 0:
        legal_actions[11] = True
        for m in range(1, 8):
            if gamestate[f"atq_serv{m}_adv"] != -99:
                legal_actions[11 + m] = True

    """ Nos serviteurs peuvent attaquer """
    is_provoc = False
    for m in range(1, 8):
        if gamestate[f"atq_serv{m}_adv"] != -99 and "provocation" in state.players[1].servants[m - 1].effects:
            is_provoc = True
            break
    for n in range(1, 8):
        if gamestate[f"atq_remain_serv{n}_j"] > 0:
            if not is_provoc:
                legal_actions[11 + 8 * n] = True
            if "ruée" in state.players[0].servants[n - 1].effects:
                if state.players[0].servants[n - 1].effects["ruée"] == 1:
                    legal_actions[11 + 8 * n] = False
            for m in range(1, 8):
                if not is_provoc:
                    if gamestate[f"atq_serv{m}_adv"] != -99:
                        legal_actions[11 + 8 * n + m] = True
                else:
                    if "provocation" in state.players[1].servants[m - 1].effects:
                        legal_actions[11 + 8 * n + m] = True

    if gamestate["dispo_ph_j"] and gamestate["cout_ph_j"] <= gamestate["mana_dispo_j"]:
        targets = state.targets_hp()
        if state.players[0].hero in targets:
            legal_actions[75] = True
        if state.players[1].hero in targets:
            legal_actions[83] = True
        for n in range(1, 8):
            if gamestate[f"atq_serv{n}_j"] != -99:
                if gamestate[f"serv{n}_j"] in targets:
                    legal_actions[75 + n] = True
            if gamestate[f"atq_serv{n}_adv"] != -99:
                if gamestate[f"serv{n}_adv"] in targets:
                    legal_actions[83 + n] = True

    return legal_actions


def generate_targets(state):
    """ Gestion des actions légales """
    legal_actions = [False] * 160
    gamestate = state.get_gamestate()
    player = state.players[0]
    adv = state.players[1]

    """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
    for n in range(len(player.hand)):
        if len(player.servants) != 7 and player.hand[n].type == "Serviteur":
            """ Serviteurs avec cris de guerre ciblés """
            if "cri de guerre" in player.hand[n].effects and "choisi" in player.hand[n].effects["cri de guerre"][1]:
                if "serviteur" in player.hand[n].effects["cri de guerre"][1]:
                    if "allié" in player.hand[n].effects["cri de guerre"][1] and player.servants.cards:
                        if "genre" in player.hand[n].effects["cri de guerre"][1]:
                            for m in range(len(player.servants)):
                                if player.servants[m].genre:
                                    legal_actions[16 * n + m + 2] = True
                        elif "Bête" in player.hand[n].effects["cri de guerre"][1]:
                            for m in range(len(player.servants)):
                                if "Bête" in player.servants[m].genre:
                                    legal_actions[16 * n + m + 2] = True
                        elif "Mort-vivant" in player.hand[n].effects["cri de guerre"][1]:
                            for m in range(len(player.servants)):
                                if "Mort-vivant" in player.servants[m].genre:
                                    legal_actions[16 * n + m + 2] = True
                        else:
                            for m in range(len(player.servants)):
                                legal_actions[16 * n + m + 2] = True
                    elif "ennemi" in player.hand[n].effects["cri de guerre"][1] and adv.servants.cards:
                        if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                                    legal_actions[16 * n + m + 9] = True
                        else:
                            if "if_provocation" in player.hand[n].effects["cri de guerre"][1]:
                                for m in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects and "provocation" in adv.servants[j].effects:
                                        legal_actions[16 * n + m + 9] = True
                            else:
                                legal_actions[16 * n] = True
                    elif "tous" in player.hand[n].effects["cri de guerre"][1] and (
                            player.servants.cards or adv.servants.cards):
                        if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
                            for m in range(len(player.servants)):
                                legal_actions[16 * n + m + 2] = True
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                                    legal_actions[16 * n + m + 9] = True
                        else:
                            if "if_attack_greater" in player.hand[n].effects["cri de guerre"][1] and [x for x in
                                                                                                      player.servants.cards + adv.servants.cards
                                                                                                      if x.attack >=
                                                                                                         player.hand[
                                                                                                             n].effects[
                                                                                                             "cri de guerre"][
                                                                                                             1][5]]:
                                for m in range(len(player.servants)):
                                    if player.servants[m].attack >= player.hand[n].effects["cri de guerre"][1][5] and \
                                            player.servants[m] != player.hand[n]:
                                        legal_actions[16 * n + m + 2] = True
                                for m in range(len(adv.servants)):
                                    if adv.servants[m].attack >= player.hand[n].effects["cri de guerre"][1][5]:
                                        legal_actions[16 * n + m + 9] = True
                            else:
                                legal_actions[16 * n] = True
                    else:
                        legal_actions[16 * n] = True
                elif "tous" in player.hand[n].effects["cri de guerre"][1]:
                    if "ennemi" in player.hand[n].effects["cri de guerre"][1]:
                        for m in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                                legal_actions[16 * n + m + 9] = True
                    else:
                        if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
                            legal_actions[16 * n + 1] = True
                            legal_actions[16 * n + 8] = True
                            for m in range(len(player.servants)):
                                legal_actions[16 * n + m + 2] = True
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                                    legal_actions[16 * n + m + 9] = True
                        else:
                            if "if_weapon" in player.hand[n].effects["cri de guerre"][
                                1] and player.hero.weapon is not None \
                                    or "if_death_undead" in player.hand[n].effects["cri de guerre"][
                                1] and player.dead_undeads \
                                    or "if_dragon_hand" in player.hand[n].effects["cri de guerre"][1] and [x for x
                                                                                                           in
                                                                                                           player.hand
                                                                                                           if
                                                                                                           "Dragon" in x.genre] \
                                    or "if_alone" in player.hand[n].effects["cri de guerre"][1] and len(
                                player.servants) == 0 \
                                    or "if_spell" in player.hand[n].effects["cri de guerre"][1] and \
                                    player.hand[n].effects["cri de guerre"][2] != 0:
                                legal_actions[16 * n + 1] = True
                                legal_actions[16 * n + 8] = True
                                for m in range(len(player.servants)):
                                    legal_actions[16 * n + m + 2] = True
                                for m in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[m].effects and "en sommeil" not in \
                                            adv.servants[m].effects:
                                        legal_actions[16 * n + m + 9] = True
                            else:
                                legal_actions[16 * n] = True
                elif "lieu" in player.hand[n].effects["cri de guerre"][1]:
                    if "ennemi" in player.hand[n].effects["cri de guerre"][1]:
                        for m in range(len(adv.lieux)):
                            legal_actions[16 * n + m + 9] = True

            elif "final" in player.hand[n].effects and "choisi" in player.hand[n].effects["final"][1]:
                if "serviteur" in player.hand[n].effects["final"][1]:
                    if "allié" in player.hand[n].effects["final"][1] and player.servants.cards:
                        for m in range(len(player.servants)):
                            legal_actions[16 * n + m + 3] = True
                    else:
                        legal_actions[16 * n + 1] = True
            # Serviteurs avec soif de mana ciblée
            elif "soif de mana" in player.hand[n].effects and "choisi" in player.hand[n].effects["soif de mana"][1]:
                if "serviteur" in player.hand[n].effects["soif de mana"][1]:
                    if "allié" in player.hand[n].effects["soif de mana"][1] and gamestate[f"serv1_j"] != -99:
                        if "genre" in player.hand[n].effects["soif de mana"][1]:
                            for m in range(len(player.servants)):
                                if player.servants[m].genre:
                                    legal_actions[16 * n + m + 2] = True
                        else:
                            for m in range(len(player.servants)):
                                legal_actions[16 * n + m + 2] = True
                    elif "ennemi" in player.hand[n].effects["soif de mana"][1] and adv.servants.cards:
                        for m in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                                legal_actions[16 * n + m + 9] = True
                    elif "tous" in player.hand[n].effects["soif de mana"][1] and (
                            gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
                        for m in range(len(player.servants)):
                            legal_actions[16 * n + m + 2] = True
                        for m in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                                legal_actions[16 * n + m + 9] = True
                    else:
                        legal_actions[16 * n] = True
                elif "tous" in player.hand[n].effects["soif de mana"][1]:
                    if "ennemi" in player.hand[n].effects["soif de mana"][1]:
                        for m in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[m].effects and "en sommeil" not in \
                                    adv.servants[m].effects:
                                legal_actions[16 * n + m + 9] = True
                    else:
                        legal_actions[16 * n + 1] = True
                        legal_actions[16 * n + 8] = True
                        for m in range(len(player.servants)):
                            legal_actions[16 * n + m + 2] = True
                        for m in range(len(adv.servants)):
                            if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                m].effects:
                                legal_actions[16 * n + m + 9] = True
            else:
                legal_actions[16 * n] = True
            # Serviteurs avec magnétisme
            if "magnetisme" in player.hand[n].effects:
                for m in range(len(player.servants)):
                    if "Méca" in player.servants[m].genre:
                        legal_actions[16 * n + m + 2] = True
        elif player.hand[n].type.lower() == "sort":
            legal_actions[16 * n] = True

    return legal_actions


def generate_legal_vector(state):
    """ Gestion des actions légales """
    legal_actions = [False] * 255
    player = state.players[0]
    adv = state.players[1]

    """ Découverte """
    if state.cards_chosen or state.cards_dragage:
        legal_actions[0] = False
        for n in range(241, 241 + len(state.cards_chosen) if state.cards_chosen else 241 + len(state.cards_dragage)):
            legal_actions[n] = True
        if state.cards_chosen and len(state.cards_chosen) == 4 and state.cards_chosen[3] == "choix mystere":
            legal_actions[244] = True
        return legal_actions

    if state.cards_entrave:
        for n in range(241, 241 + len(state.cards_entrave)):
            legal_actions[n] = True
        return legal_actions

    legal_actions[0] = True
    gamestate = state.get_gamestate()

    """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
    for n in range(len(player.hand)):
        if player.hand[n].cost <= player.mana and "entrave" not in player.hand[n].effects:
            if len(player.servants) != 7 and player.hand[n].type == "Serviteur":

                """ Serviteurs avec cris de guerre ciblés """
                if "cri de guerre" in player.hand[n].effects and "choisi" in player.hand[n].effects["cri de guerre"][1]:
                    if "serviteur" in player.hand[n].effects["cri de guerre"][1]:
                        if "allié" in player.hand[n].effects["cri de guerre"][1] and player.servants.cards:
                            if "genre" in player.hand[n].effects["cri de guerre"][1]:
                                for m in range(len(player.servants)):
                                    if player.servants[m].genre:
                                        legal_actions[16 * n + m + 3] = True
                            elif "Bête" in player.hand[n].effects["cri de guerre"][1]:
                                for m in range(len(player.servants)):
                                    if "Bête" in player.servants[m].genre:
                                        legal_actions[16 * n + m + 3] = True
                            elif "Mort-vivant" in player.hand[n].effects["cri de guerre"][1]:
                                for m in range(len(player.servants)):
                                    if "Mort-vivant" in player.servants[m].genre:
                                        legal_actions[16 * n + m + 3] = True
                            else:
                                for m in range(len(player.servants)):
                                    legal_actions[16 * n + m + 3] = True
                        elif "ennemi" in player.hand[n].effects["cri de guerre"][1] and adv.servants.cards:
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                    m].effects:
                                    legal_actions[16 * n + m + 10] = True
                        elif "tous" in player.hand[n].effects["cri de guerre"][1] and (
                                player.servants.cards or adv.servants.cards):
                            if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
                                for m in range(len(player.servants)):
                                    legal_actions[16 * n + m + 3] = True
                                for m in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                        m].effects:
                                        legal_actions[16 * n + m + 10] = True
                            else:
                                if "if_attack_greater" in player.hand[n].effects["cri de guerre"][1] and [x for x in
                                                                                                          player.servants.cards + adv.servants.cards
                                                                                                          if x.attack >=
                                                                                                             player.hand[
                                                                                                                 n].effects[
                                                                                                                 "cri de guerre"][
                                                                                                                 1][5]]:
                                    for m in range(len(player.servants)):
                                        if player.servants[m].attack >= player.hand[n].effects["cri de guerre"][1][
                                            5] and player.servants[m] != player.hand[n]:
                                            legal_actions[16 * n + m + 3] = True
                                    for m in range(len(adv.servants)):
                                        if adv.servants[m].attack >= player.hand[n].effects["cri de guerre"][1][5]:
                                            legal_actions[16 * n + m + 10] = True
                                else:
                                    legal_actions[16 * n + 1] = True
                        else:
                            legal_actions[16 * n + 1] = True
                    elif "tous" in player.hand[n].effects["cri de guerre"][1]:
                        if "ennemi" in player.hand[n].effects["cri de guerre"][1]:
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                    m].effects:
                                    legal_actions[16 * n + m + 10] = True
                        else:
                            if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
                                legal_actions[16 * n + 2] = True
                                legal_actions[16 * n + 9] = True
                                for m in range(len(player.servants)):
                                    legal_actions[16 * n + m + 3] = True
                                for m in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                        m].effects:
                                        legal_actions[16 * n + m + 10] = True
                            else:
                                if "if_weapon" in player.hand[n].effects["cri de guerre"][
                                    1] and player.hero.weapon is not None \
                                        or "if_death_undead" in player.hand[n].effects["cri de guerre"][
                                    1] and player.dead_undeads \
                                        or "if_dragon_hand" in player.hand[n].effects["cri de guerre"][1] and [x for x
                                                                                                               in
                                                                                                               player.hand
                                                                                                               if
                                                                                                               "Dragon" in x.genre] \
                                        or "if_alone" in player.hand[n].effects["cri de guerre"][1] and len(
                                    player.servants) == 0 \
                                        or "if_spell" in player.hand[n].effects["cri de guerre"][1] and \
                                        player.hand[n].effects["cri de guerre"][2] != 0:
                                    legal_actions[16 * n + 2] = True
                                    legal_actions[16 * n + 9] = True
                                    for m in range(len(player.servants)):
                                        legal_actions[16 * n + m + 3] = True
                                    for m in range(len(adv.servants)):
                                        if "camouflage" not in adv.servants[m].effects and "en sommeil" not in \
                                                adv.servants[m].effects:
                                            legal_actions[16 * n + m + 10] = True
                                else:
                                    legal_actions[16 * n + 1] = True

                # Serviteurs avec soif de mana ciblée
                elif "soif de mana" in player.hand[n].effects and "choisi" in player.hand[n].effects["soif de mana"][1]:
                    if "serviteur" in player.hand[n].effects["soif de mana"][1]:
                        if "allié" in player.hand[n].effects["soif de mana"][1] and gamestate[f"serv1_j"] != -99:
                            if "genre" in player.hand[n].effects["soif de mana"][1]:
                                for m in range(len(player.servants)):
                                    if player.servants[m].genre:
                                        legal_actions[16 * n + m + 3] = True
                            else:
                                for m in range(len(player.servants)):
                                    legal_actions[16 * n + m + 3] = True
                        elif "tous" in player.hand[n].effects["soif de mana"][1] and (
                                gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
                            for m in range(len(player.servants)):
                                legal_actions[16 * n + m + 3] = True
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                    m].effects:
                                    legal_actions[16 * n + m + 10] = True
                        else:
                            legal_actions[16 * n + 1] = True
                    elif "tous" in player.hand[n].effects["soif de mana"][1]:
                        if "ennemi" in player.hand[n].effects["soif de mana"][1]:
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in \
                                        adv.servants[m].effects:
                                    legal_actions[16 * n + m + 10] = True
                        else:
                            legal_actions[16 * n + 2] = True
                            legal_actions[16 * n + 9] = True
                            for m in range(len(player.servants)):
                                legal_actions[16 * n + m + 3] = True
                            for m in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
                                    m].effects:
                                    legal_actions[16 * n + m + 10] = True
                else:
                    legal_actions[16 * n + 1] = True
                # Serviteurs avec magnétisme
                if "magnetisme" in player.hand[n].effects:
                    for m in range(len(player.servants)):
                        if "Méca" in player.servants[m].genre:
                            legal_actions[16 * n + m + 3] = True
            elif player.hand[n].type.lower() == "sort":
                legal_actions[16 * n + 1] = True

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    is_provoc = False
    for m in range(len(adv.servants)):
        if "provocation" in adv.servants[m].effects:
            is_provoc = True
            break
    """ Notre héros peut attaquer """
    if player.hero.remaining_atk > 0 and player.hero.attack > 0:
        if not is_provoc:
            legal_actions[161] = True
        for m in range(len(adv.servants)):
            if not is_provoc:
                if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                    legal_actions[161 + m + 1] = True
            else:
                if "provocation" in adv.servants[m].effects:
                    legal_actions[161 + m + 1] = True

    """ Nos serviteurs peuvent attaquer """

    for n in range(len(player.servants)):
        if player.servants[n].remaining_atk * player.servants[n].attack > 0 and "en sommeil" not in player.servants[
            n].effects:
            if not is_provoc:
                legal_actions[161 + 8 * (n + 1)] = True
            if "ruée" in player.servants[n].effects:
                if player.servants[n].effects["ruée"] == 1:
                    legal_actions[161 + 8 * (n + 1)] = False
            for m in range(len(adv.servants)):
                if not is_provoc:
                    if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
                        legal_actions[161 + 8 * (n + 1) + (m + 1)] = True
                else:
                    if "provocation" in adv.servants[m].effects:
                        legal_actions[161 + 8 * (n + 1) + (m + 1)] = True

    """ Pouvoir héroïque """
    if player.hero.dispo_pouvoir and player.hero.cout_pouvoir_temp <= player.mana:
        targets = state.targets_hp()
        if player.hero in targets:
            legal_actions[225] = True
        if adv.hero in targets:
            legal_actions[233] = True
        if len(targets) >= 2:
            for n in range(len(player.servants)):
                if player.servants[n] in targets:
                    legal_actions[226 + n] = True
            for n in range(len(adv.servants)):
                if adv.servants[n] in targets and not list(
                        {"camouflage", "en sommeil", "inciblable"} and set(adv.servants[n].effects)):
                    legal_actions[234 + n] = True

    """ Mot-clé échangeable """
    for n in range(len(player.hand)):
        if player.mana >= 1 and "echangeable" in player.hand[n].effects:
            legal_actions[245 + n] = True

    return legal_actions


def estimated_advantage(action, state):
    """ Simule le plateau qu'aurait donné une certaine action pour en tirer une notion d'avantage gagné ou perdu """
    actual_state = deepcopy(state)
    next_state = deepcopy(state)
    action = int(action)

    if action == 0:
        TourEnCours(next_state).fin_du_tour()
        while next_state.get_gamestate()['pseudo_j'] == 'OldIA':
            next_state = Orchestrator().tour_oldia_training(next_state, old_policy)
            if not next_state.game_on:
                if next_state.winner.name == "NewIA":
                    return 500
                else:
                    return -500
    elif action < 11:
        TourEnCours(next_state).jouer_carte(next_state.players[0].hand[action - 1])
    elif 11 <= action < 75:
        if (action - 11) // 8 == 0:
            attacker = next_state.players[0].hero
        else:
            attacker = next_state.players[0].servants[int((action - 11) // 8 - 1)]
        if (action - 11) % 8 == 0:
            target = next_state.players[1].hero
        else:
            target = next_state.players[1].servants[int((action - 11) % 8 - 1)]
        TourEnCours(next_state).attaquer(attacker, target)
    elif action >= 75:
        if action == 75:
            target = next_state.players[0].hero
        elif action == 83:
            target = next_state.players[1].hero
        elif action < 83:
            target = next_state.players[0].servants[action - 76]
        else:
            target = next_state.players[1].servants[action - 84]
        TourEnCours(next_state).pouvoir_heroique(next_state.players[0].classe, target)

    next_state.update()

    if not next_state.game_on:
        if next_state.winner.name == "NewIA":
            return 500
        else:
            return -500

    def calc_advantage(state_game):
        advantage = (state_game["nbre_cartes_j"] - state_game["nbre_cartes_adv"]) + 0.8 * (
                state_game["nbre_cartes_j"] / max(1, state_game["nbre_cartes_adv"]))
        for n in range(1, 8):
            if state_game[f"serv{n}_j"] != -99:
                advantage += 2 * state_game[f"atq_serv{n}_j"] + 2 * state_game[f"pv_serv{n}_j"]
            if state_game[f"serv{n}_adv"] != -99:
                advantage -= 2 * state_game[f"atq_serv{n}_adv"] + 2 * state_game[f"pv_serv{n}_adv"]
        advantage += 0.22 * (pow(30 - state_game["pv_adv"], 1.3) - pow(30 - state_game["pv_j"], 1.3))
        advantage += state_game["attaque_j"]
        return advantage

    actual_advantage = calc_advantage(actual_state.get_gamestate())
    predicted_advantage = calc_advantage(next_state.get_gamestate())

    return round(predicted_advantage - actual_advantage, 2)


""" Initialisation de l'environnement et chargement du modèle """

old_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')
saved_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')


class Frenchstone_old(py_environment.PyEnvironment, ABC):
    def __init__(self):
        super().__init__()
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=90,
                                                        name='action')
        self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
        self._observation_spec = {
            'observation': array_spec.BoundedArraySpec(
                shape=(len(itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate())),),
                dtype=np.int32, minimum=-100, maximum=100, name='observation'),
            'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(91,), dtype=np.bool_)
        }
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        obs = self.observation_spec()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state)

        obs['observation'] = np.array(
            itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate()))
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.restart(obs)

    def _step(self, action):

        if self._episode_ended:
            return self.reset()

        """ Estimation de la récompense """
        reward = 0

        """ Gestion des actions légales """
        self._state = Orchestrator().tour_ia_training(self._state, action)

        while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
            self._state = Orchestrator().tour_oldia_training(self._state, old_policy)

        legal_actions = generate_legal_vector(self._state)
        obs = self.observation_spec()
        obs['observation'] = np.array(
            itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate()),
            dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        if reward in [-500, 500]:
            self._episode_ended = True
            return ts.termination(obs, reward)
        return ts.transition(obs, reward)


# old_env = Frenchstone_old()
# old_env = tf_py_environment.TFPyEnvironment(old_env)


class Frenchstone(py_environment.PyEnvironment):
    def __init__(self):
        super().__init__()
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=90,
                                                        name='action')
        self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
        self._observation_spec = {
            'observation': array_spec.BoundedArraySpec(
                shape=(len(itemgetter(*generate_column_state(classes_heros))(self._state.get_gamestate())),),
                dtype=np.int32, minimum=-100, maximum=100, name='observation'),
            'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(91,), dtype=np.bool_)
        }
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        obs = self.observation_spec()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state)

        obs['observation'] = np.array(itemgetter(*generate_column_state(classes_heros))(self._state.get_gamestate()))
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.restart(obs)

    def _step(self, action):

        if self._episode_ended:
            return self.reset()

        """ Estimation de la récompense """
        reward = 0

        """ Gestion des actions légales """
        self._state = Orchestrator().tour_ia_training(self._state, action)

        while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
            self._state = Orchestrator().tour_oldia_training(self._state, old_policy)

        legal_actions = generate_legal_vector(self._state)
        obs = self.observation_spec()
        obs['observation'] = np.array(itemgetter(*generate_column_state(classes_heros))(self._state.get_gamestate()),
                                      dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        if reward in [-500, 500]:
            self._episode_ended = True
            return ts.termination(obs, reward)
        return ts.transition(obs, reward)


new_env = Frenchstone()
new_env = tf_py_environment.TFPyEnvironment(new_env)


class TourEnCours:
    """Classe prenant en entrée un plateau de jeu et permettant d'effectuer toutes les actions possibles dessus."""

    def __init__(self, plateau):
        self.plt = plateau

    def apply_effects(self, carte, target=None):
        player = self.plt.players[0]
        adv = self.plt.players[1]

        # Résolution des effets d'aura
        ally_aura_servants = [x for x in player.servants if "aura" in set(x.effects)]
        ennemy_aura_servants = [x for x in adv.servants if "aura" in set(x.effects)]
        for servant in ally_aura_servants:
            if "boost" in servant.effects["aura"]:
                if "serviteur" in servant.effects["aura"][1]:
                    if "allié" in servant.effects["aura"][1]:
                        if "alive" in servant.effects["aura"][1]:
                            if servant.name == "Loup alpha redoutable" and len(player.servants) >= 1:
                                if not servant.is_dead():
                                    if player.servants[0] != servant:
                                        player.servants[0].total_temp_boost[0] += 1
                                    if player.servants[-1] != servant:
                                        player.servants[-1].total_temp_boost[0] += 1
                            elif "Pirate" in servant.effects["aura"][1] and [x for x in player.servants if
                                                                             "Pirate" in x.genre and x != servant]:
                                for pirate in [x for x in player.servants if "Pirate" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        pirate.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        pirate.total_temp_boost[1] += servant.effects["aura"][2][1]
                            elif "Murloc" in servant.effects["aura"][1] and [x for x in player.servants if
                                                                             "Murloc" in x.genre and x != servant]:
                                for murloc in [x for x in player.servants if "Murloc" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        murloc.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        murloc.total_temp_boost[1] += servant.effects["aura"][2][1]
                            elif "tous" in servant.effects["aura"][1] and [x for x in player.servants if
                                                                           x != servant]:
                                for serv in [x for x in player.servants if x != servant]:
                                    if not servant.is_dead():
                                        serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                            elif "choisi" in servant.effects["aura"][1]:
                                servant.effects["aura"][1][4].total_temp_boost[0] += servant.effects["aura"][2][0]
                                servant.effects["aura"][1][4].total_temp_boost[1] += servant.effects["aura"][2][1]

                        if servant.effects["aura"][1][
                            3] == "Mort-vivant" and "Mort-vivant" in carte.genre and servant != carte:
                            carte.attack += servant.effects["aura"][2][0]
                            carte.base_attack += servant.effects["aura"][2][0]
                            carte.health += servant.effects["aura"][2][1]
                            carte.base_health += servant.effects["aura"][2][1]
                    if "tous" in servant.effects["aura"][1]:
                        if "alive" in servant.effects["aura"][1]:
                            if "choisi" in servant.effects["aura"][1]:
                                if "camouflage" in servant.effects["aura"]:
                                    if not servant.is_dead():
                                        servant.effects["aura"][1][4].effects["camouflage"] = 1
                                    else:
                                        if not servant.effects["aura"][1][4].is_dead() and "camouflage" in \
                                                servant.effects["aura"][1][4].effects:
                                            servant.effects["aura"][1][4].effects.pop("camouflage")
                                elif "ne peut pas attaquer" in servant.effects["aura"]:
                                    if not servant.is_dead():
                                        servant.effects["aura"][1][4].effects["ne peut pas attaquer"] = 1
                                        servant.effects["aura"][1][4].remaining_atk = 0
                                    else:
                                        if not servant.effects["aura"][1][4].is_dead() and "ne peut pas attaquer" in \
                                                servant.effects["aura"][1][4].effects:
                                            servant.effects["aura"][1][4].effects.pop("ne peut pas attaquer")
                                            servant.effects["aura"][1][4].remaining_atk = 1
                        if "conditional" in servant.effects["aura"][1] and "sort" in servant.effects["aura"][1]:
                            if carte.type == "sort":
                                for servant2 in player.servants:
                                    servant2.damage(servant.effects["aura"][2])
                                for servant2 in adv.servants:
                                    if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                              player.servants]:
                                        servant2.damage(2 * servant.effects["aura"][2])
                elif "self" in servant.effects["aura"][1]:
                    if servant.effects["aura"][1][1] == "allié" and carte in player.servants:
                        if servant.effects["aura"][1][3] == "Murloc" and "Murloc" in set(
                                carte.genre) and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.attack += servant.effects["aura"][2][0]
                            servant.base_attack += servant.effects["aura"][2][0]
                            servant.health += servant.effects["aura"][2][1]
                            servant.base_health += servant.effects["aura"][2][1]
                        elif servant.effects["aura"][1][
                            3] == "Piranha grouillant" and carte.name == "Piranha grouillant" and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.attack += servant.effects["aura"][2][0]
                            servant.base_attack += servant.effects["aura"][2][0]
                            servant.health += servant.effects["aura"][2][1]
                            servant.base_health += servant.effects["aura"][2][1]
                    if servant.effects["aura"][1][1] == "sort":
                        if carte.type == "Sort":
                            if servant.effects["aura"][1][3] == "temp_fullturn":
                                servant.attack += servant.effects["aura"][2][0]
                                servant.health += servant.effects["aura"][2][1]
                                servant.base_health += servant.effects["aura"][2][1]
                    elif servant.effects["aura"][1][1] == "Méca":
                        if carte.type == "Serviteur" and "Méca" in carte.genre and carte != servant and carte in player.servants and not carte.is_dead():
                            servant.attack += servant.effects["aura"][2][0]
                            servant.base_attack += servant.effects["aura"][2][0]
                            servant.health += servant.effects["aura"][2][1]
                            servant.base_health += servant.effects["aura"][2][1]
                    if "heros_allié_attack" in servant.effects["aura"][1]:
                        if player.hero.remaining_atk == 0:
                            servant.attack += servant.effects["aura"][2][0]
                            servant.health += servant.effects["aura"][2][1]
                            servant.base_health += servant.effects["aura"][2][1]
            if "pioche" in servant.effects["aura"]:
                if "allié" in servant.effects["aura"][1]:
                    if "global" in servant.effects["aura"][1] and "damage_self" in servant.effects["aura"][1]:
                        if servant.damage_taken:
                            player.pick_multi(servant.effects["aura"][2])
                            servant.damage_taken = False
                    if "play_cost" in servant.effects["aura"][1] and carte.cost == servant.effects["aura"][1][
                        2] and not (carte.type == "Serviteur" and carte.is_dead()):
                        drawable_cards = [x for x in player.deck if x.cost == servant.effects["aura"][2][1]]
                        if drawable_cards:
                            card_drawn = random.choice(drawable_cards)
                            player.deck.remove(card_drawn)
                            player.hand.add(card_drawn)
                            servant.effects["aura"][1][2] += 1
                            servant.effects["aura"][2][1] += 1
            if "add_hand" in servant.effects["aura"]:
                if "conditional" in servant.effects["aura"][1] and "if_spell" in servant.effects["aura"][1]:
                    if carte.type == "Sort":
                        player.hand.add(Card(**random.choice(all_servants)))
            if "damage" in servant.effects["aura"]:
                if "tous" in servant.effects["aura"][1]:
                    if "ennemi" in servant.effects["aura"][1]:
                        if "heros_allié_attack" in servant.effects["aura"][
                            1] and player.hero.has_attacked == 1 and carte.name == "":
                            for entity in [adv.hero] + adv.servants.cards:
                                entity.damage(servant.effects["aura"][2])
            if "replacement" in servant.effects["aura"]:
                if carte.type == "Serviteur" and carte.is_dead():
                    player.servants.remove(servant)
                    self.invoke_servant(get_card(carte.name, all_servants), 0)
            if "augment" in servant.effects["aura"]:
                if not [servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]] in player.augment:
                    player.augment.append([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
                else:
                    if servant.is_dead():
                        player.augment.remove([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
                if not [servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]] in adv.augment:
                    adv.augment.append([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
                else:
                    if servant.is_dead():
                        adv.augment.remove([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
            if servant.effects["aura"] == "eleveuse de faucons":
                if carte.type == "Serviteur" and not carte.is_dead() and carte != servant:
                    carte.attack += 1
                    carte.base_attack += 1
                    carte.health += 1
                    carte.base_health += 1
                    if "rale d'agonie" in carte.effects:
                        carte.effects["rale d'agonie2"] = ["invocation", ["allié"], "Faucon peregrin"]
                    else:
                        carte.effects["rale d'agonie"] = ["invocation", ["allié"], "Faucon peregrin"]
        for servant in ennemy_aura_servants:
            if "boost" in servant.effects["aura"]:
                if "serviteur" in servant.effects["aura"][1]:
                    if "allié" in servant.effects["aura"][1]:
                        if "alive" in servant.effects["aura"][1]:
                            if servant.name == "Loup alpha redoutable" and len(adv.servants) >= 1:
                                if not servant.is_dead():
                                    if adv.servants[0] != servant:
                                        adv.servants[0].total_temp_boost[0] += 1
                                    if adv.servants[-1] != servant:
                                        adv.servants[-1].total_temp_boost[0] += 1
                            elif "Pirate" in servant.effects["aura"][1] and [x for x in adv.servants if
                                                                             "Pirate" in x.genre and x != servant]:
                                for pirate in [x for x in adv.servants if "Pirate" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        pirate.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        pirate.total_temp_boost[1] += servant.effects["aura"][2][1]
                            elif "Murloc" in servant.effects["aura"][1] and [x for x in adv.servants if
                                                                             "Murloc" in x.genre and x != servant]:
                                for murloc in [x for x in adv.servants if "Murloc" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        murloc.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        murloc.total_temp_boost[1] += servant.effects["aura"][2][1]
                            elif "tous" in servant.effects["aura"][1] and [x for x in adv.servants if x != servant]:
                                for serv in [x for x in adv.servants if x != servant]:
                                    if not servant.is_dead():
                                        serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                            elif "choisi" in servant.effects["aura"][1]:
                                servant.effects["aura"][1][4].total_temp_boost[0] += servant.effects["aura"][2][0]
                                servant.effects["aura"][1][4].total_temp_boost[1] += servant.effects["aura"][2][1]
                        if servant.effects["aura"][1][
                            3] == "Mort-vivant" and "Mort-vivant" in carte.genre and servant != carte:
                            carte.attack += servant.effects["aura"][2][0]
                            carte.base_attack += servant.effects["aura"][2][0]
                            carte.health += servant.effects["aura"][2][1]
                            carte.base_health += servant.effects["aura"][2][1]
                    if "tous" in servant.effects["aura"][1]:
                        if "alive" in servant.effects["aura"][1]:
                            if "camouflage" in servant.effects["aura"]:
                                if not servant.is_dead():
                                    servant.effects["aura"][1][4].effects["camouflage"] = 1
                                else:
                                    if not servant.effects["aura"][1][4].is_dead() and "camouflage" in \
                                            servant.effects["aura"][1][4].effects:
                                        servant.effects["aura"][1][4].effects.pop("camouflage")
                            elif "ne peut pas attaquer" in servant.effects["aura"]:
                                if not servant.is_dead():
                                    servant.effects["aura"][1][4].effects["ne peut pas attaquer"] = 1
                                    servant.effects["aura"][1][4].remaining_atk = 0
                                else:
                                    if not servant.effects["aura"][1][4].is_dead() and "ne peut pas attaquer" in \
                                            servant.effects["aura"][1][4].effects:
                                        servant.effects["aura"][1][4].effects.pop("ne peut pas attaquer")
                                        servant.effects["aura"][1][4].remaining_atk = 1
                elif "self" in servant.effects["aura"][1]:
                    if servant.effects["aura"][1][1] == "allié" and carte in adv.servants:
                        if servant.effects["aura"][1][3] == "Murloc" and "Murloc" in set(
                                carte.genre) and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.attack += servant.effects["aura"][2][0]
                            servant.base_attack += servant.effects["aura"][2][0]
                            servant.health += servant.effects["aura"][2][1]
                            servant.base_health += servant.effects["aura"][2][1]
                        elif servant.effects["aura"][1][
                            3] == "Piranha grouillant" and carte.name == "Piranha grouillant" and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.attack += servant.effects["aura"][2][0]
                            servant.base_attack += servant.effects["aura"][2][0]
                            servant.health += servant.effects["aura"][2][1]
                            servant.base_health += servant.effects["aura"][2][1]
                    if servant.effects["aura"][1][1] == "sort":
                        if carte.type == "Sort":
                            if servant.effects["aura"][1][3] == "temp_fullturn":
                                servant.attack += servant.effects["aura"][2][0]
                                servant.health += servant.effects["aura"][2][1]
                                servant.base_health += servant.effects["aura"][2][1]
                    if "conditional" in servant.effects["aura"][1]:
                        if "if_enemyturn" in servant.effects["aura"][1]:
                            servant.total_temp_boost[0] += servant.effects["aura"][2][0]
                            servant.total_temp_boost[1] += servant.effects["aura"][2][1]
            if "pioche" in servant.effects["aura"]:
                if "allié" in servant.effects["aura"][1]:
                    if "global" in servant.effects["aura"][1] and "damage_self" in servant.effects["aura"][1]:
                        if servant.damage_taken:
                            adv.pick_multi(servant.effects["aura"][2])
                            servant.damage_taken = False
            if "replacement" in servant.effects["aura"]:
                if carte.type == "Serviteur" and carte.is_dead():
                    adv.servants.remove(servant)
                    self.invoke_servant(get_card(carte.name, all_servants), 1)
            if "courbe sort" in servant.effects["aura"]:
                if "serviteur" in servant.effects["aura"][1] and "allié" in servant.effects["aura"][1]:
                    if carte.type == "Sort" and target != servant and target in adv.servants:
                        target = servant
            if "augment" in servant.effects["aura"]:
                if not [servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]] in player.augment:
                    player.augment.append([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
                else:
                    if servant.is_dead():
                        player.augment.remove([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
                if not [servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]] in adv.augment:
                    adv.augment.append([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
                else:
                    if servant.is_dead():
                        adv.augment.remove([servant.effects["aura"][1][0], servant.effects["aura"][1][3], servant.effects["aura"][2]])
        if carte.type == "Serviteur":
            if "charge" in carte.effects or "ruée" in carte.effects:
                carte.remaining_atk = 1
            if "cri de guerre" in carte.effects and not carte.is_dead():
                if "play" in carte.effects["cri de guerre"] and carte.effects["cri de guerre"][2] != "":
                    played_card = get_card(carte.effects["cri de guerre"][2].name, all_cards)
                    if played_card.type == "Serviteur" and not len(player.servants) == 7:
                        player.hand.add(played_card)
                        played_card.cost = 0
                        possible_targets = generate_targets(self.plt)[16 * (len(player.hand) - 1): 16 * len(player.hand) - 1]
                        possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                        target = random.choice(possible_targets_refined)
                        if target == 0:
                            target = None
                        elif target == 1:
                            target = player.hero
                        elif target < 8:
                            target = player.servants[target - 2]
                        elif target == 9:
                            target = adv.hero
                        else:
                            target = adv.servants[target - 10]
                        TourEnCours(self.plt).jouer_carte(played_card, target)
                if "boost" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if type(target) == Card:
                            if "alive" in carte.effects["cri de guerre"][1]:
                                carte.effects["aura"] = ["boost", ["serviteur", "allié", "choisi", "alive", target],
                                                         [3, 0]]
                            else:
                                if "based_on_stats" in carte.effects["cri de guerre"][1]:
                                    target.attack += carte.attack
                                    target.base_attack += carte.attack
                                    target.health += carte.health
                                    target.base_health += carte.health
                                else:
                                    target.attack += carte.effects["cri de guerre"][2][0]
                                    target.base_attack += carte.effects["cri de guerre"][2][0]
                                    target.health += carte.effects["cri de guerre"][2][1]
                                    target.base_health += carte.effects["cri de guerre"][2][1]
                                    if "provocation" in carte.effects["cri de guerre"][1]:
                                        target.effects["provocation"] = 1
                                    if "bouclier divin" in carte.effects["cri de guerre"][1]:
                                        target.effects["bouclier divin"] = 1
                                    if "temp_turn" in carte.effects["cri de guerre"][1]:
                                        target.effects["temp_turn"] = [carte.effects["cri de guerre"][2][0],
                                                                       carte.effects["cri de guerre"][2][1]]
                        elif type(target) == CardGroup:
                            for card in target:
                                card.attack += carte.effects["cri de guerre"][2][0]
                                card.base_attack += carte.effects["cri de guerre"][2][0]
                                card.health += carte.effects["cri de guerre"][2][1]
                                card.base_health += carte.effects["cri de guerre"][2][1]
                                if "provocation" in carte.effects["cri de guerre"][1]:
                                    card.effects["provocation"] = 1
                                if "bouclier divin" in carte.effects["cri de guerre"][1]:
                                    card.effects["bouclier divin"] = 1
                    else:
                        if "self" in carte.effects["cri de guerre"][1]:
                            if carte.name == "Mousse de la voile sanglante" and player.hero.weapon is not None:
                                carte.attack += player.hero.weapon.attack
                            elif "cout_last_card" in carte.effects["cri de guerre"][
                                1] and player.last_card != "" and player.last_card.cost == \
                                    carte.effects["cri de guerre"][1][2]:
                                carte.attack += carte.effects["cri de guerre"][2][0]
                                carte.base_attack += carte.effects["cri de guerre"][2][0]
                                carte.health += carte.effects["cri de guerre"][2][1]
                                carte.base_health += carte.effects["cri de guerre"][2][1]
                            elif "cards_in_hand" in carte.effects["cri de guerre"][1]:
                                carte.health += len(player.hand)
                                carte.base_health += len(player.hand)
                            elif carte.name == "Oiseau libre":
                                carte.attack += player.oiseaux_libres
                                carte.base_attack += player.oiseaux_libres
                                carte.health += player.oiseaux_libres
                                carte.base_health += player.oiseaux_libres
                                player.oiseaux_libres += 1
                        if "heros" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][
                            1]:
                            if carte.effects["cri de guerre"][2] == "inciblable" and "temp_turn" in \
                                    carte.effects["cri de guerre"][1]:
                                adv.hero.effects["inciblable"] = [1, "temp_turn"]
                        if "serviteur" in carte.effects["cri de guerre"][1] and "allié" in \
                                carte.effects["cri de guerre"][1]:
                            if "tous" in carte.effects["cri de guerre"][1] and len(player.servants) > 1:
                                if "Murloc" in carte.effects["cri de guerre"][1]:
                                    for serv in player.servants:
                                        if serv != carte and "Murloc" in serv.genre:
                                            serv.attack += carte.effects["cri de guerre"][2][0]
                                            serv.base_attack += carte.effects["cri de guerre"][2][0]
                                            serv.health += carte.effects["cri de guerre"][2][1]
                                            serv.base_health += carte.effects["cri de guerre"][2][1]
                if "camouflage" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if type(target) == Card:
                            if "alive" in carte.effects["cri de guerre"][1]:
                                carte.effects["aura"] = ["boost", ["serviteur", "tous", "choisi", "alive", target],
                                                         "camouflage"]
                if "gel" in carte.effects["cri de guerre"] and target is not None:
                    if type(target) == Card:
                        target.effects["gel"] = carte.effects["cri de guerre"][2]
                    else:
                        target.gel = carte.effects["cri de guerre"][2]
                if "vol de vie" in carte.effects["cri de guerre"]:
                    if "self" in carte.effects["cri de guerre"][1]:
                        carte.effects['vol de vie'] = 1
                if "attack" in carte.effects["cri de guerre"]:
                    if "self" in carte.effects["cri de guerre"][1]:
                        if "serviteur" in carte.effects["cri de guerre"][2] and "ennemi" in carte.effects["cri de guerre"][2] and "tous" in carte.effects["cri de guerre"][2]:
                            for serv in adv.servants:
                                if not carte.is_dead():
                                    self.attaquer(serv, carte)
                if "suicide" in carte.effects["cri de guerre"]:
                    carte.blessure = 1000
                if "destroy" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if target.type == "Serviteur":
                            target.blessure = 1000
                        elif target.type == "Lieu":
                            target.health = 0
                    if "arme" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                        adv.hero.weapon = None
                if "destroy+boost" in carte.effects["cri de guerre"]:
                    if "tous" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                        if "secret" in carte.effects["cri de guerre"][1]:
                            if adv.secrets.cards:
                                carte.attack += len(adv.secrets.cards)
                                carte.base_attack += len(adv.secrets.cards)
                                carte.health += len(adv.secrets.cards)
                                carte.base_health += len(adv.secrets.cards)
                                adv.secret.cards = []
                if "réincarnation" in carte.effects["cri de guerre"] and target is not None:
                    target.effects["réincarnation"] = carte.effects["cri de guerre"][2]
                if carte.effects["cri de guerre"] == "Sir Finley":
                    if len(player.hand) != 0:
                        new_hand = player.deck.cards[-len(player.hand):].copy()
                        player.deck.cards += player.hand.cards.copy()
                        player.hand.cards = new_hand.copy()
                if "add_durability" in carte.effects["cri de guerre"] and player.hero.weapon is not None:
                    player.hero.weapon.durability += carte.effects["cri de guerre"]
                if "add_armor" in carte.effects["cri de guerre"]:
                    if "tous" in carte.effects["cri de guerre"][1]:
                        adv.hero.armor += carte.effects["cri de guerre"][2]
                    player.hero.armor += carte.effects["cri de guerre"][2]
                if "cout_hp" in carte.effects["cri de guerre"]:
                    player.hero.cout_pouvoir_temp = 0
                if "reduc" in carte.effects["cri de guerre"] and "prochain" in carte.effects["cri de guerre"][1]:
                    player.discount_next.append(
                        [carte.effects["cri de guerre"][1][0], carte.effects["cri de guerre"][1][3],
                         carte.effects["cri de guerre"][2]])
                if "augment" in carte.effects["cri de guerre"]:
                    if "ennemi" in carte.effects["cri de guerre"][1] and "temp_fullturn" in \
                            carte.effects["cri de guerre"][1]:
                        adv.augment.append([carte.effects["cri de guerre"][1][0], carte.effects["cri de guerre"][1][3],
                                            carte.effects["cri de guerre"][2]])
                if "damage" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in player.servants] and type(target) == Card:
                            target.damage(2 * carte.effects["cri de guerre"][2])
                        else:
                            target.damage(carte.effects["cri de guerre"][2])
                    else:
                        if carte.effects["cri de guerre"][1][0] == "tous":
                            if "ennemi" in carte.effects["cri de guerre"][1]:
                                try:
                                    for n in range(0, carte.effects["cri de guerre"][1][3]):
                                        random_target = random.choice([adv.hero] + adv.servants.cards)
                                        if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                                  player.servants] and random_target in adv.servants:
                                            random_target.damage(2 * carte.effects["cri de guerre"][2])
                                        else:
                                            random_target.damage(carte.effects["cri de guerre"][2])
                                except:
                                    pass
                            elif carte.effects["cri de guerre"][1][1] == "tous":
                                try:
                                    for n in range(0, carte.effects["cri de guerre"][1][3]):
                                        random_target = random.choice(
                                            [adv.hero] + [player.hero] + player.servants.cards + adv.servants.cards)
                                        if [x.name for x in player.servants] and "Enchanteur" in [x.name for x
                                                                                                  in
                                                                                                  player.servants] and random_target in adv.servants:
                                            random_target.damage(2 * carte.effects["cri de guerre"][2])
                                        else:
                                            random_target.damage(carte.effects["cri de guerre"][2])
                                except:
                                    pass
                        elif carte.effects["cri de guerre"][1][0] == "serviteur":
                            if len(player.servants) + len(adv.servants) > 1:
                                for serv in [x for x in player.servants.cards + adv.servants.cards if x != carte]:
                                    serv.damage(carte.effects["cri de guerre"][2])
                        elif carte.effects["cri de guerre"][1][0] == "self":
                            carte.damage(carte.effects["cri de guerre"][2])
                        elif carte.effects["cri de guerre"][1][0] == "heros":
                            if "ennemi" in carte.effects["cri de guerre"][1]:
                                if "if_draw" in carte.effects["cri de guerre"][1] and "next_enemyturn" in \
                                        carte.effects["cri de guerre"][1]:
                                    adv.hero.effects["draw"] = ["damage", "temp_turn", 2]
                        elif carte.effects["cri de guerre"][1][0] == "buveuse de vie":
                            adv.hero.damage(3)
                            player.hero.heal(3)
                if "heal" in carte.effects["cri de guerre"]:
                    if target is not None:
                        target.heal(carte.effects["cri de guerre"][2])
                    else:
                        if "tous" in carte.effects["cri de guerre"][1]:
                            if "allié" in carte.effects["cri de guerre"][1]:
                                for entity in [player.hero] + player.servants.cards:
                                    entity.heal(carte.effects["cri de guerre"][2])
                if "ne peut pas attaquer" in carte.effects["cri de guerre"] and target is not None:
                    if target is not None:
                        if type(target) == Card:
                            if "alive" in carte.effects["cri de guerre"][1]:
                                carte.effects["aura"] = ["boost", ["serviteur", "tous", "choisi", "alive", target],
                                                         "ne peut pas attaquer"]
                if "silence" in carte.effects["cri de guerre"]:
                    if target is not None:
                        target.base_attack = get_card(target.name, all_servants).base_attack
                        target.attack = get_card(target.name, all_servants).base_attack
                        target.blessure = min(target.blessure, get_card(target.name, all_servants).base_health - 1)
                        target.base_health = get_card(target.name, all_servants).base_health
                        target.effects = {}
                    elif "tous" in carte.effects["cri de guerre"]:
                        target = [x for x in player.servants.cards + adv.servants.cards if x != carte]
                        for card in target:
                            card.base_attack = get_card(card.name, all_servants).base_attack
                            card.attack = get_card(card.name, all_servants).base_attack
                            card.blessure = min(card.blessure, get_card(card.name, all_servants).base_health - 1)
                            card.base_health = get_card(card.name, all_servants).base_health
                            card.effects = {}
                if "swap" in carte.effects["cri de guerre"] and target is not None:
                    inter_health = target.health
                    target.health = target.attack
                    target.base_health = target.attack
                    target.attack = inter_health
                if "echange" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if "deck" in carte.effects["cri de guerre"][2]:
                            if "serviteur" in carte.effects["cri de guerre"][2] and "ennemi" in carte.effects["cri de guerre"][2]:
                                swapped_card = random.choice(adv.deck.cards)
                                adv.servants.remove(target)
                                adv.deck.add(target)
                                adv.deck.shuffle()
                                adv.servants.add(swapped_card)
                    else:
                        if "deck" in carte.effects["cri de guerre"][1]:
                            if "serviteur" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                                swapped_card = random.choice(adv.deck.cards)
                                player.servants.remove(carte)
                                adv.deck.add(carte)
                                adv.deck.shuffle()
                                player.servants.add(swapped_card)
                if "remontee" in carte.effects["cri de guerre"] and target is not None:
                    player.servants.remove(target)
                    player.hand.add(get_card(target.name, all_servants))
                if "mana_final" in carte.effects["cri de guerre"]:
                    player.mana_final = carte.effects["cri de guerre"][2]
                if "add_hand" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1] and len(player.hand) < 10:
                        if target is not None:
                            if carte.effects["cri de guerre"][2] == "copy":
                                player.hand.add(get_card(target.name, all_servants))
                            else:
                                player.hand.add(get_card(carte.effects["cri de guerre"][2], all_servants))
                        else:
                            if not carte.effects["cri de guerre"][2] == "copy":
                                player.hand.add(get_card(carte.effects["cri de guerre"][2], all_cards))
                                if "porteur d'invitation" in [x.effects for x in player.servants] and len(
                                        player.hand) < 10 and get_card(carte.effects["cri de guerre"][2],
                                                                       all_cards).classe not in ["Neutre", player.classe]:
                                    player.hand.add(get_card(carte.effects["cri de guerre"][2], all_cards))
                    elif "ennemi" in carte.effects["cri de guerre"][1] and len(adv.hand) < 10:
                        if type(carte.effects["cri de guerre"][2]) == list:
                            for card in carte.effects["cri de guerre"][2]:
                                if len(adv.hand) < 10:
                                    adv.hand.add(get_card(card, all_cards))
                        else:
                            if len(adv.hand) < 10:
                                adv.hand.add(get_card(carte.effects["cri de guerre"][2], all_cards))
                if "add_deck" in carte.effects["cri de guerre"]:
                    if "end_deck" in carte.effects["cri de guerre"]:
                        if "colossal" in carte.effects["cri de guerre"][1]:
                            try:
                                cards_to_add = random.sample([x for x in all_servants if "colossal" in x.effects], 3)
                            except:
                                cards_to_add = random.sample([x for x in all_servants], 3)
                            for card_to_add in cards_to_add:
                                player.deck.add(card_to_add)
                    else:
                        card_to_add = get_card(carte.effects["cri de guerre"][1], all_cards)
                        if card_to_add.name == "Instantane de Feplouf":
                            card_to_add.effects["add_hand"] = [get_card(x.name, all_cards) for x in player.hand]
                        player.deck.add(card_to_add)
                        player.deck.shuffle()
                if "pioche" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1]:
                        if "conditional" in carte.effects["cri de guerre"][1]:
                            if "if_weapon_hand" in carte.effects["cri de guerre"][1] and [x for x in player.hand if x.type == "Arme"]:
                                player.pick_multi(carte.effects["cri de guerre"][2])
                        else:
                            if "arme" in carte.effects["cri de guerre"][1]:
                                drawable_cards = [x for x in player.deck if x.type == "weapon"]
                                if drawable_cards:
                                    card_drawn = random.choice(drawable_cards)
                                    player.deck.remove(card_drawn)
                                    player.hand.add(card_drawn)
                            elif "Naga" in carte.effects["cri de guerre"][1]:
                                if carte.effects["cri de guerre"][2] == 1:
                                    drawable_cards = [x for x in player.deck if x.type == "Serviteur" and "Naga" in x.genre]
                                    if drawable_cards:
                                        card_drawn = random.choice(drawable_cards)
                                        player.deck.remove(card_drawn)
                                        player.hand.add(card_drawn)
                            elif "give_spells" in carte.effects["cri de guerre"][1]:
                                for i in range(0, carte.effects["cri de guerre"][2]):
                                    player.pick()
                                    if player.hand.cards[-1].type == "Sort":
                                        adv.hand.add(player.hand.cards[-1])
                                        player.hand.remove(player.hand.cards[-1])
                            else:
                                player.pick_multi(carte.effects["cri de guerre"][2])
                if "dragage" in carte.effects["cri de guerre"]:
                    self.plt.cards_dragage = CardGroup(player.deck.cards[-3:].copy())
                    if "reduc_cost" in carte.effects["cri de guerre"][1]:
                        for card in self.plt.cards_dragage:
                            card.cost -= carte.effects["cri de guerre"][1][1]
                            card.base_cost -= carte.effects["cri de guerre"][1][1]
                if "entrave" in carte.effects["cri de guerre"]:
                    self.plt.cards_entrave = CardGroup(random.sample(adv.hand.cards, min(3, len(adv.hand.cards))))
                if "institutrice" in carte.effects["cri de guerre"]:
                    player.hand.add(get_card("Jeune naga", all_servants))
                    self.plt.cards_chosen = self.choice_decouverte(type="sort", other="institutrice")
                elif "Okani" in carte.effects["cri de guerre"]:
                    self.plt.cards_chosen = self.choice_decouverte(other="Okani")
                elif "nettoyeur a vapeur" in carte.effects["cri de guerre"]:
                    for card in player.deck:
                        if card.id not in [x.id for x in player.initial_deck]:
                            player.deck.remove(card)
                    for card in adv.deck:
                        if card.id not in [x.id for x in adv.initial_deck]:
                            player.deck.remove(card)
                if "invocation" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1] and len(player.servants) < 7:
                        if "aléatoire" in carte.effects["cri de guerre"][1]:
                            if "cout" in carte.effects["cri de guerre"][1]:
                                if 2 in carte.effects["cri de guerre"][1]:
                                    new_servant = Card(**random.choice(
                                        [x for x in all_servants if x["cost"] == 2 and x["decouvrable"] == 1]))
                                    self.invoke_servant(new_servant, 0)
                                if "deck" in carte.effects["cri de guerre"][1] and "cout" in \
                                        carte.effects["cri de guerre"][1]:
                                    if [x for x in player.deck if x.cost <= player.mana and x.type == "Serviteur"]:
                                        new_servant = random.choice(
                                            [x for x in player.deck if x.cost <= player.mana and x.type == "Serviteur"])
                                        self.invoke_servant(new_servant, 0)
                                        player.deck.remove(new_servant)
                        elif "conditional" in carte.effects["cri de guerre"][1]:
                            if "serviteur" in carte.effects["cri de guerre"][1] and "Méca" in carte.effects["cri de guerre"][1] and any("Méca" in sublist for sublist in [x.genre for x in player.servants if x != carte]):
                                if type(carte.effects["cri de guerre"][1]) == list:
                                    for invoked_servant in carte.effects["cri de guerre"][2]:
                                        self.invoke_servant(get_card(invoked_servant, all_servants), 0)
                        elif "copy" in carte.effects["cri de guerre"][1]:
                            if "if_secret" in carte.effects["cri de guerre"][1] and player.secrets:
                                invoked_servant = get_card(carte.effects["cri de guerre"][2], all_servants)
                                invoked_servant.attack, invoked_servant.base_attack = carte.attack, carte.base_attack
                                invoked_servant.health, invoked_servant.base_health = carte.health, carte.base_health
                                invoked_servant.effects = carte.effects.copy()
                                self.invoke_servant(invoked_servant, 0)
                            else:
                                invoked_servant = get_card(carte.effects["cri de guerre"][2], all_servants)
                                invoked_servant.attack, invoked_servant.base_attack = carte.attack, carte.base_attack
                                invoked_servant.health, invoked_servant.base_health = carte.health, carte.base_health
                                invoked_servant.effects = carte.effects.copy()
                                self.invoke_servant(invoked_servant, 0)
                        elif type(carte.effects["cri de guerre"][2]) == list:
                            for invoked_servant in carte.effects["cri de guerre"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), 0)
                        else:
                            self.invoke_servant(get_card(carte.effects["cri de guerre"][2], all_servants), 0)
                    elif "ennemi" in carte.effects["cri de guerre"][1] and len(adv.servants) < 7:
                        if all(x in carte.effects["cri de guerre"][1] for x in ["main", "serviteur", "aléatoire"]):
                            try:
                                played_servant = random.choice([x for x in adv.hand if x.type == "Serviteur"])
                                adv.hand.remove(played_servant)
                                self.invoke_servant(played_servant, 1)
                            except:
                                pass
                        else:
                            played_servant = get_card(carte.effects["cri de guerre"][2], all_cards)
                            self.invoke_servant(played_servant, 1)
                if "copy" in carte.effects["cri de guerre"] and target is not None:
                    player.servants.remove(carte)
                    new_servant = get_card(target.name, all_servants)
                    new_servant.effects = target.effects
                    new_servant.attack, new_servant.base_attack = 3, 3
                    new_servant.health, new_servant.base_health = 3, 3
                    player.servants.add(new_servant)
                if "boosted_copy" in carte.effects["cri de guerre"] and target is not None and len(player.servants) < 7:
                    copy_card = get_card(target.name, all_servants)
                    copy_card.attack, copy_card.base_attack = target.attack, target.base_attack
                    copy_card.health, copy_card.base_health, copy_card.blessure = target.health, target.base_health, target.blessure
                    copy_card.effects = deepcopy(target.effects)
                    copy_card.effects["ruée"], copy_card.effects["bouclier divin"], copy_card.effects["furie des vents"] = 1, 1, 1
                    self.invoke_servant(copy_card, 0)
                if "découverte" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if "serviteur" in carte.effects["cri de guerre"][2]:
                            if "genre" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte("serviteur", target.genre)
                    else:
                        if "conditional" in carte.effects["cri de guerre"][1]:
                            if "serviteur" in carte.effects["cri de guerre"][1] and "allié" in \
                                    carte.effects["cri de guerre"][1]:
                                if "Méca" in carte.effects["cri de guerre"][1] and any("Méca" in sublist for sublist in
                                                                                       [x.genre for x in player.servants
                                                                                        if x != carte]):
                                    self.plt.cards_chosen = self.choice_decouverte(type="serviteur", genre=["Méca"])
                            if "if_death_undead" in carte.effects["cri de guerre"][1]:
                                if player.dead_undeads:
                                    self.plt.cards_chosen = self.choice_decouverte(type="sort", reduc=
                                    carte.effects["cri de guerre"][1][3])
                                else:
                                    self.plt.cards_chosen = self.choice_decouverte(type="sort")
                            if "if_lieu" in carte.effects["cri de guerre"][1] and player.lieux:
                                self.plt.cards_chosen = self.choice_decouverte(card_group=player.deck)
                        else:
                            if "sort" in carte.effects["cri de guerre"][2]:
                                if "secret" in carte.effects["cri de guerre"][2]:
                                    try:
                                        self.plt.cards_chosen = self.choice_decouverte(type="sort", other="Secret")
                                    except:
                                        pass
                                if "classe_adv" in carte.effects["cri de guerre"][2]:
                                    try:
                                        self.plt.cards_chosen = self.choice_decouverte(type="sort", classe=adv.classe)
                                    except:
                                        pass
                                if "choix mystere" in carte.effects["cri de guerre"][2]:
                                    self.plt.cards_chosen = self.choice_decouverte(type="sort", other="choix mystere")
                                else:
                                    self.plt.cards_chosen = self.choice_decouverte(type="sort")
                            elif "serviteur" in carte.effects["cri de guerre"][2]:
                                if "legendaire" in carte.effects["cri de guerre"][2]:
                                    self.plt.cards_chosen = self.choice_decouverte(type="serviteur", other="legendaire")
                            elif "ETC" in carte.effects["cri de guerre"][1]:
                                etc_pack = CardGroup(
                                    [get_card(x, all_cards) for x in carte.effects["cri de guerre"][2]])
                                self.plt.cards_chosen = self.choice_decouverte(card_group=etc_pack)
                            if "deck_adv" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte(card_group=adv.deck)
                if "rale d'agonie" in carte.effects["cri de guerre"] and target is not None:
                    if "rale d'agonie" in target.effects:
                        target.effects["rale d'agonie2"] = carte.effects["cri de guerre"][2]
                    else:
                        target.effects["rale d'agonie"] = carte.effects["cri de guerre"][2]
                carte.effects.pop("cri de guerre")
            if "soif de mana" in carte.effects and carte.effects["soif de mana"][3] <= player.mana_max and not carte.is_dead():
                if "damage" in carte.effects["soif de mana"]:
                    if target is not None:
                        if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                  player.servants] and target in adv.servants:
                            target.damage(2 * carte.effects["soif de mana"][2])
                        else:
                            target.damage(carte.effects["soif de mana"][2])
                    else:
                        if "tous" in carte.effects["soif de mana"][1]:
                            if "ennemi" in carte.effects["soif de mana"][1]:
                                if "aléatoire" in carte.effects["soif de mana"][1]:
                                    try:
                                        for n in range(0, carte.effects["soif de mana"][1][3]):
                                            random_target = random.choice([adv.hero] + adv.servants.cards)
                                            if [x.name for x in player.servants] and "Enchanteur" in [x.name for
                                                                                                      x in
                                                                                                      player.servants] and random_target in adv.servants:
                                                random_target.damage(2 * carte.effects["soif de mana"][2])
                                            else:
                                                random_target.damage(carte.effects["soif de mana"][2])
                                    except:
                                        pass
                if "add_armor" in carte.effects["soif de mana"]:
                    if "tous" in carte.effects["soif de mana"][1]:
                        adv.hero.armor += carte.effects["soif de mana"][2]
                    player.hero.armor += carte.effects["soif de mana"][2]
                if "silence+gel" in carte.effects["soif de mana"] and target is not None:
                    target.base_attack = get_card(target.name, all_servants).base_attack
                    target.attack = get_card(target.name, all_servants).base_attack
                    target.health = max(1, get_card(target.name, all_servants).base_health - target.blessure)
                    target.base_health = get_card(target.name, all_servants).base_health
                    target.effects = {"gel": carte.effects["soif de mana"][2]}
                if "invocation" in carte.effects["soif de mana"]:
                    if "cout" in carte.effects["soif de mana"][1]:
                        if player.mana_max >= 10:
                            new_servant = Card(
                                **random.choice([x for x in all_servants if x["cost"] == 8 and x["decouvrable"] == 1]))
                            self.invoke_servant(new_servant, 0)
                        else:
                            new_servant = Card(
                                **random.choice([x for x in all_servants if x["cost"] == 3 and x["decouvrable"] == 1]))
                            self.invoke_servant(new_servant, 0)
                if "réincarnation" in carte.effects["soif de mana"]:
                    if "self" in carte.effects["soif de mana"][1]:
                        carte.effects["réincarnation"] = 0
                if "heal" in carte.effects["soif de mana"]:
                    if "tous" in carte.effects["soif de mana"][1]:
                        if "allié" in carte.effects["soif de mana"][1]:
                            for entity in [player.hero] + player.servants.cards:
                                entity.heal(carte.effects["soif de mana"][2])
                if "boost" in carte.effects["soif de mana"]:
                    if "self" in carte.effects["soif de mana"][1]:
                        if "bouclier divin" in carte.effects["soif de mana"][1]:
                            carte.effects["bouclier divin"] = 1
                        carte.attack += carte.effects["soif de mana"][2][0]
                        carte.base_attack += carte.effects["soif de mana"][2][0]
                        carte.health += carte.effects["soif de mana"][2][1]
                        carte.base_health += carte.effects["soif de mana"][2][1]
            if "magnetisme" in carte.effects and not carte.is_dead() and target is not None:
                carte.effects.pop("magnetisme")
                target.attack += carte.attack
                target.base_attack += carte.base_attack
                target.health += carte.health
                target.base_health += carte.base_health
                target.effects = target.effects | carte.effects
                player.servants.remove(carte)
            if "réincarnation" in carte.effects and carte.is_dead():
                if carte.effects["réincarnation"] == 0:
                    card_revive = get_card(carte.name, all_servants)
                    card_revive.health = 1
                    card_revive.blessure = card_revive.base_health - card_revive.health
                    if "réincarnation" in card_revive.effects:
                        card_revive.effects.pop("réincarnation")
                    self.invoke_servant(card_revive, 0)
                else:
                    card_revive = get_card(carte.name, all_servants)
                    card_revive.health = 1
                    card_revive.blessure = card_revive.base_health - card_revive.health
                    if "réincarnation" in card_revive.effects:
                        card_revive.effects.pop("réincarnation")
                    self.invoke_servant(card_revive, 1)
            if "rale d'agonie" in carte.effects and carte.is_dead():
                if "serviteur" in carte.effects["rale d'agonie"][1]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre]) \
                                if len(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre]) != 0 else None
                        else:
                            target = random.choice([x for x in self.plt.players[0].servants if x != carte]) \
                                if len([x for x in self.plt.players[0].servants]) > 1 else None
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre]) \
                                if len(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre]) != 0 else None
                        else:
                            target = random.choice([x for x in self.plt.players[1].servants if x != carte]) \
                                if len([x for x in self.plt.players[1].servants]) > 1 else None
                    elif "tous" in carte.effects["rale d'agonie"][1]:
                        target = CardGroup(player.servants.cards + adv.servants.cards)
                elif "heros" in carte.effects["rale d'agonie"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie"][1]:
                            if carte in adv.servants:
                                target = adv.hero
                            else:
                                carte.effects["rale d'agonie"] = ["", [""], ""]
                        else:
                            target = adv.hero
                    elif ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie"][1]:
                            if carte in adv.servants:
                                target = player.hero
                            else:
                                carte.effects["rale d'agonie"] = ["", [""], ""]
                        else:
                            target = player.hero
                elif "tous" in carte.effects["rale d'agonie"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "aléatoire" in carte.effects["rale d'agonie"][1]:
                            target = random.choice([adv.hero] + adv.servants.cards)
                    elif ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "aléatoire" in carte.effects["rale d'agonie"][1]:
                            target = random.choice([player.hero] + player.servants.cards)
                if "damage" in carte.effects["rale d'agonie"] and target is not None:
                    if type(target) in (Hero, Card):
                        if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                  player.servants] and target in adv.servants:
                            target.damage(2 * carte.effects["rale d'agonie"][2])
                        else:
                            target.damage(carte.effects["rale d'agonie"][2])
                    else:
                        for card in target:
                            if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                      player.servants] and target in adv.servants:
                                card.damage(2 * carte.effects["rale d'agonie"][2])
                            else:
                                card.damage(carte.effects["rale d'agonie"][2])
                if "boost" in carte.effects["rale d'agonie"] and target is not None:
                    if type(target) == Card:
                        target.attack += carte.effects["rale d'agonie"][2][0]
                        target.base_attack += carte.effects["rale d'agonie"][2][0]
                        target.health += carte.effects["rale d'agonie"][2][1]
                        target.base_health += carte.effects["rale d'agonie"][2][1]
                if "rebond" in carte.effects["rale d'agonie"] and target is not None and type(target) == Card:
                    if "rale d'agonie" in target.effects:
                        target.effects["rale d'agonie2"] = carte.effects["rale d'agonie"]
                    else:
                        target.effects["rale d'agonie"] = carte.effects["rale d'agonie"]
                if "rale d'agonie" in carte.effects["rale d'agonie"]:
                    if target is not None:
                        if "rale d'agonie" in target.effects:
                            target.effects["rale d'agonie2"] = carte.effects["rale d'agonie"][2]
                        else:
                            target.effects["rale d'agonie"] = carte.effects["rale d'agonie"][2]
                if "invocation" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "mana_dispo" in carte.effects["rale d'agonie"][1]:
                            if player.mana != 0:
                                for n in range(player.mana):
                                    self.invoke_servant(get_card(carte.effects["rale d'agonie"][2], all_servants), 0)
                                player.mana = 0
                        elif type(carte.effects["rale d'agonie"][2]) == list:
                            for invoked_servant in carte.effects["rale d'agonie"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), 0)
                        elif "conditional" in carte.effects["rale d'agonie"][1]:
                            if "if_robaudio" in carte.effects["rale d'agonie"][1]:
                                if [x for x in adv.hand if x.name == "Rob'audio"]:
                                    for robaudio in [x for x in adv.hand if x.name == "Rob'audio"]:
                                        adv.hand.remove(robaudio)
                                        self.invoke_servant(get_card("Rob'audio", all_servants), 0)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            self.invoke_servant(new_servant, 0)
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "mana_dispo" in carte.effects["rale d'agonie"][1] and adv.mana != 0:
                            new_servant = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            for n in range(adv.mana):
                                self.invoke_servant(new_servant, 1)
                            adv.mana = 0
                        elif type(carte.effects["rale d'agonie"][2]) == list:
                            for invoked_servant in carte.effects["rale d'agonie"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), 1)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            self.invoke_servant(new_servant, 1)
                if "pioche" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        player.pick_multi(carte.effects["rale d'agonie"][2])
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        adv.pick_multi(carte.effects["rale d'agonie"][2])
                if "add_hand" in carte.effects["rale d'agonie"]:
                    if "sort" in carte.effects["rale d'agonie"][1]:
                        if "ombre" in carte.effects["rale d'agonie"][1]:
                            if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants) and len(player.hand) < 10:
                                try:
                                    card_to_add = random.choice([x for x in all_spells if x.genre == "Ombre"])
                                    player.hand.add(card_to_add)
                                except:
                                    pass
                            elif "ennemi" in carte.effects["rale d'agonie"][1] and len(adv.hand) < 10:
                                try:
                                    card_to_add = random.choice([x for x in all_spells if x.genre == "Ombre"])
                                    adv.hand.add(card_to_add)
                                except:
                                    pass
                    if "weapon" in carte.effects["rale d'agonie"][1]:
                        if "ennemi" in carte.effects["rale d'agonie"][1] and len(adv.hand) < 10:
                            try:
                                card_to_add = random.choice([x for x in all_cards if x.type == "Arme"])
                                adv.hand.add(card_to_add)
                            except:
                                pass
                    if "serv_transformation" in carte.effects["rale d'agonie"][1]:
                        if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            if [x for x in player.hand if x.type == "Serviteur"]:
                                player.hand.remove(random.choice([x for x in player.hand if x.type == "Serviteur"]))
                                player.hand.add(get_card(carte.effects["rale d'agonie"][2], all_servants))
                        elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            if [x for x in adv.hand if x.type == "Serviteur"]:
                                adv.hand.remove(random.choice([x for x in adv.hand if x.type == "Serviteur"]))
                                adv.hand.add(get_card(carte.effects["rale d'agonie"][2], all_servants))
                if "add_armor" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        player.hero.armor += carte.effects["rale d'agonie"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        adv.hero.armor += carte.effects["rale d'agonie"][2]
            if "rale d'agonie2" in carte.effects and carte.is_dead():
                if "serviteur" in carte.effects["rale d'agonie2"][1]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre]) \
                                if len(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre]) != 0 else None
                        else:
                            target = random.choice([x for x in self.plt.players[0].servants]) \
                                if len([x for x in self.plt.players[0].servants]) != 0 else None
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre]) \
                                if len(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre]) != 0 else None
                        else:
                            target = random.choice([x for x in self.plt.players[1].servants]) \
                                if len([x for x in self.plt.players[1].servants]) != 0 else None
                    elif "tous" in carte.effects["rale d'agonie2"][1]:
                        target = CardGroup(player.servants.cards + adv.servants.cards)
                elif "héros" in carte.effects["rale d'agonie2"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie2"][1]:
                            if carte in adv.servants:
                                target = adv.hero
                            else:
                                carte.effects["rale d'agonie2"] = ["", [""], ""]
                        else:
                            target = adv.hero
                    elif ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie2"][1]:
                            if carte in adv.servants:
                                target = player.hero
                            else:
                                carte.effects["rale d'agonie2"] = ["", [""], ""]
                        else:
                            target = player.hero
                elif "tous" in carte.effects["rale d'agonie2"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "aléatoire" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice([adv.hero] + adv.servants.cards)
                if "damage" in carte.effects["rale d'agonie2"] and target is not None:
                    if type(target) in (Hero, Card):
                        if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                  player.servants] and target in adv.servants:
                            target.damage(2 * carte.effects["rale d'agonie2"][2])
                        else:
                            target.damage(carte.effects["rale d'agonie2"][2])
                    else:
                        for card in target:
                            if [x.name for x in player.servants] and "Enchanteur" in [x.name for x in
                                                                                      player.servants] and target in adv.servants:
                                card.damage(2 * carte.effects["rale d'agonie2"][2])
                            else:
                                card.damage(carte.effects["rale d'agonie2"][2])
                if "boost" in carte.effects["rale d'agonie2"] and target is not None:
                    target.attack += carte.effects["rale d'agonie2"][2][0]
                    target.base_attack += carte.effects["rale d'agonie2"][2][0]
                    target.health += carte.effects["rale d'agonie2"][2][1]
                    target.base_health += carte.effects["rale d'agonie2"][2][1]
                if "rebond" in carte.effects["rale d'agonie2"] and target is not None and type(target) == Card:
                    if "rale d'agonie" in target.effects:
                        target.effects["rale d'agonie2"] = carte.effects["rale d'agonie2"]
                    else:
                        target.effects["rale d'agonie"] = carte.effects["rale d'agonie2"]
                if "invocation" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "mana_dispo" in carte.effects["rale d'agonie2"][1] and player.mana != 0:
                            for n in range(player.mana):
                                self.invoke_servant(get_card(carte.effects["rale d'agonie2"][2], all_servants), 0)
                            player.mana = 0
                        elif type(carte.effects["rale d'agonie2"][2]) == list:
                            for invoked_servant in carte.effects["rale d'agonie2"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), 0)
                        elif "conditional" in carte.effects["rale d'agonie2"][1]:
                            if "if_robaudio" in carte.effects["rale d'agonie2"][1]:
                                if [x for x in adv.hand if x.name == "Rob'audio"]:
                                    for robaudio in [x for x in adv.hand if x.name == "Rob'audio"]:
                                        adv.hand.remove(robaudio)
                                        self.invoke_servant(get_card("Rob'audio", all_servants), 0)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            self.invoke_servant(new_servant, 0)
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "mana_dispo" in carte.effects["rale d'agonie2"][1] and adv.mana != 0:
                            new_servant = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            for n in range(adv.mana):
                                self.invoke_servant(new_servant, 1)
                            adv.mana = 0
                        elif type(carte.effects["rale d'agonie2"][2]) == list:
                            for invoked_servant in carte.effects["rale d'agonie2"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), 1)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            self.invoke_servant(new_servant, 1)
                if "pioche" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        player.pick_multi(carte.effects["rale d'agonie2"][2])
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        adv.pick_multi(carte.effects["rale d'agonie2"][2])
                if "add_hand" in carte.effects["rale d'agonie2"]:
                    if "sort" in carte.effects["rale d'agonie2"][1]:
                        if "ombre" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                    "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                try:
                                    card_to_add = random.choice([x for x in all_spells if x.genre == "Ombre"])
                                    player.hand.add(card_to_add)
                                except:
                                    pass
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                    "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                try:
                                    card_to_add = random.choice([x for x in all_spells if x.genre == "Ombre"])
                                    adv.hand.add(card_to_add)
                                except:
                                    pass
                    if "weapon" in carte.effects["rale d'agonie2"][1]:
                        if "ennemi" in carte.effects["rale d'agonie2"][1] and len(adv.hand) < 10:
                            try:
                                card_to_add = random.choice([x for x in all_cards if x.type == "Arme"])
                                adv.hand.add(card_to_add)
                            except:
                                pass
                    if "serv_transformation" in carte.effects["rale d'agonie2"][1]:
                        if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            if [x for x in player.hand if x.type == "Serviteur"]:
                                player.hand.remove(random.choice([x for x in player.hand if x.type == "Serviteur"]))
                                player.hand.add(get_card(carte.effects["rale d'agonie2"][2], all_servants))
                        elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            if [x for x in adv.hand if x.type == "Serviteur"]:
                                adv.hand.remove(random.choice([x for x in adv.hand if x.type == "Serviteur"]))
                                adv.hand.add(get_card(carte.effects["rale d'agonie2"][2], all_servants))
                if "add_armor" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        player.hero.armor += carte.effects["rale d'agonie2"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        adv.hero.armor += carte.effects["rale d'agonie2"][2]

        if carte.type == "Sort":
            if "add_mana" in carte.effects:
                player.mana += carte.effects["add_mana"]
            if "add_hand" in carte.effects:
                for card in carte.effects["add_hand"]:
                    if len(player.hand) < 10:
                        player.hand.add(card)

    def invoke_servant(self, servant, player):
        if "cri de guerre" in servant.effects:
            servant.effects.pop("cri de guerre")
        if "soif de mana" in servant.effects:
            servant.effects.pop("soif de mana")
        if "final" in servant.effects:
            servant.effects.pop("final")
        if len(self.plt.players[player].servants) < 7:
            self.plt.players[player].servants.add(servant)
            self.apply_effects(servant)

    def jouer_carte(self, carte, target=None):
        """ Action de poser une carte depuis la main du joueur dont c'est le tour.
        Le plateau est mis à jour en conséquence """
        player = self.plt.players[0]
        adv = self.plt.players[1]
        if carte.cost <= player.mana:
            if carte.type.lower() == "sort":
                player.hand.remove(carte)
                player.mana_spend(carte.cost)
                if "counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "sort" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]:
                    print("Sort contré")
                    [x for x in adv.servants if "counter" in x.effects["aura"][0]][0].effects.pop("counter")
                else:
                    self.apply_effects(carte)
                    if [x for x in player.hand if "if_spell" in x.effects]:
                        for serv in [x for x in player.hand if "if_spell" in x.effects]:
                            serv.effects["cri de guerre"][2] = serv.effects["cri de guerre"][3]
            elif carte.type.lower() == "serviteur":
                if len(player.servants) < 7:
                    player.hand.remove(carte)
                    player.mana_spend(carte.cost)
                    if "final" in carte.effects and player.mana == 0:
                        carte.effects["cri de guerre"] = carte.effects["final"]
                        carte.effects.pop("final")
                    if "counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "serviteur" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]:
                        print("Serviteur contré")
                        [x for x in adv.servants if "counter" in x.effects["aura"][0]][0].effects.pop("counter")
                    else:
                        player.servants.add(carte)
                        self.apply_effects(carte, target)
                else:
                    raise PermissionError("Nombre maximum de serviteurs atteint")
        else:
            raise PermissionError("Carte plus chère que la mana du joueur")

    def attaquer(self, attaquant, cible, target=None):
        """ Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi) """
        if type(attaquant) in (Hero, Card) and type(cible) in (Hero, Card):
            if [x.name for x in self.plt.players[0].servants] and "Enchanteur" in [x.name for x in self.plt.players[
                0].servants] and type(cible) == Card:
                cible.damage(2 * attaquant.attack)
            else:
                cible.damage(attaquant.attack)
            if "vol de vie" in attaquant.effects and "bouclier divin" not in cible.effects:
                self.plt.players[0].hero.heal(attaquant.attack)
            if "toxicite" in cible.effects and "bouclier divin" not in attaquant.effects and type(cible) == Card:
                attaquant.blessure = 1000
            attaquant.damage(cible.attack)
            if "vol de vie" in cible.effects and "bouclier divin" not in attaquant.effects:
                self.plt.players[1].hero.heal(cible.attack)
            if "toxicite" in attaquant.effects and "bouclier divin" not in cible.effects and type(cible) == Card:
                cible.blessure = 1000
            attaquant.remaining_atk -= 1
            if "furie des vents" in attaquant.effects and attaquant.effects["furie des vents"] == 1:
                attaquant.effects["furie des vents"] = 0
                attaquant.remaining_atk = 1
            if type(attaquant) == Card:
                if "camouflage" in attaquant.effects:
                    attaquant.effects.pop("camouflage")
                if "aura" in attaquant.effects and attaquant.effects["aura"][2] == "attack":
                    if "self" in attaquant.effects["aura"][1]:
                        if "destroy" in attaquant.effects["aura"]:
                            attaquant.blessure = 1000
            if type(attaquant) == Hero:
                if attaquant.weapon is not None:
                    attaquant.weapon.durability -= 1
                    if attaquant.weapon.durability == 0:
                        attaquant.weapon = None
                attaquant.has_attacked = 1
        else:
            raise TypeError

    def pouvoir_heroique(self, classe, cible):
        player = self.plt.players[0]
        if type(cible) in (Hero, Card):
            if classe == "Mage":
                cible.damage(1)
            elif classe == "Chasseur":
                cible.damage(2)
            elif classe == "Paladin":
                carte = get_card("Recrue de la main d'argent", all_servants)
                player.servants.add(carte)
            elif classe == "Chevalier de la mort":
                carte = get_card("Goule fragile", all_servants)
                self.apply_effects(carte)
                player.servants.add(carte)
            elif classe == "Démoniste":
                cible.damage(2)
                if len(player.deck) > 0:
                    player.pick()
                else:
                    cible.fatigue += 1
            elif classe == "Prêtre":
                cible.heal(2)
            elif classe == "Chasseur de démons":
                cible.attack += 1
            elif classe == "Druide":
                cible.attack += 1
                cible.armor += 1
            elif classe == "Voleur":
                cible.weapon = Weapon("Lame pernicieuse")
                cible.weapon.attack = 1
                cible.weapon.durability = 2
                cible.attack += cible.weapon.attack
            elif classe == "Guerrier":
                cible.armor += 2
            elif classe == "Chaman":
                cartes = [get_card("Totem de soin", all_servants),
                          get_card("Totem incendiaire", all_servants),
                          get_card("Totem de puissance", all_servants),
                          get_card("Totem de griffes de pierre", all_servants)]
                player.servants.add(random.choice(cartes))
            if player.hero.cout_pouvoir_temp != player.hero.cout_pouvoir:
                player.mana_spend(player.hero.cout_pouvoir_temp)
                player.hero.cout_pouvoir_temp = player.hero.cout_pouvoir
            else:
                player.mana_spend(player.hero.cout_pouvoir)
            player.hero.dispo_pouvoir = False
        else:
            raise TypeError

    def choice_decouverte(self, type=None, genre=None, classe=None, other=None, card_group=None, reduc=None):
        global discovery
        if card_group is not None:
            return random.sample(card_group.cards, min(3, len(card_group.cards)))
        if type == "serviteur":
            if genre:
                group_filtered = [x for x in all_servants if
                                  set(genre).intersection(x["genre"]) and x["decouvrable"] == 1]
                discovery = random.sample(group_filtered, min(3, len(group_filtered)))
            elif other:
                group_filtered = [x for x in all_servants if other in x['effects'] and x["decouvrable"] == 1]
                discovery = random.sample(group_filtered, min(3, len(group_filtered)))
            else:
                group_filtered = [x for x in all_servants if x["decouvrable"] == 1]
                discovery = random.sample(group_filtered, 3)

        elif type == "sort":
            if classe:
                try:
                    group_filtered = [x for x in all_spells if
                                      set(classe).intersection(x["classe"]) and x["decouvrable"] == 1]
                    discovery = random.sample(group_filtered, min(3, len(group_filtered)))
                except:
                    raise TypeError
            elif other == "Secret":
                group_filtered = [x for x in all_spells if "secret" in x["effects"] and x["decouvrable"] == 1]
                discovery = random.sample(group_filtered, min(3, len(group_filtered)))
            elif other == "institutrice":
                try:
                    group_filtered = [x for x in all_servants if x["cost"] <= 3 and x["decouvrable"] == 1]
                    discovery = random.sample(group_filtered, min(3, len(group_filtered)))
                except:
                    group_filtered = [x for x in all_servants if x["cost"] <= 3 and x["decouvrable"] == 1]
                    discovery = random.sample(group_filtered, min(3, len(group_filtered)))
            else:
                try:
                    discovery = random.sample([x for x in all_spells if x["decouvrable"] == 1], 3)
                except:
                    group_filtered = [x for x in all_servants if x["decouvrable"] == 1]
                    discovery = random.sample(group_filtered, 3)

        if other == "Okani":
            discovery = [get_card("Riposte de sort", all_spells), get_card("Riposte de serviteur", all_spells)]
        else:
            discovery = [Card(**x) for x in discovery]
        if other == "choix mystere":
            discovery.append("choix mystere")
        if reduc is not None:
            for element in discovery:
                element.cost = max(0, element.cost - reduc)
        return discovery

    def decouverte(self, cards, choice, type_dec="decouverte"):
        if len(self.plt.players[0].hand) < 10 and type_dec == "decouverte":
            if choice != 3:
                if [x for x in self.plt.players[0].hand if x.name == "Jeune naga" and x.effects["cri de guerre"][2] == ""]:
                    [x for x in self.plt.players[0].hand if
                     x.name == "Jeune naga" and x.effects["cri de guerre"][2] == ""][0].effects["cri de guerre"][2] = cards[choice]
                elif cards[choice].name in ["Riposte de sort", "Riposte de serviteur"]:
                    [x for x in self.plt.players[0].servants if x.name == "Maitre lame Okani"][0].effects["aura"] = ["counter", "sort" if cards[choice].name == "Riposte de sort" else "serviteur", ""]
                else:
                    self.plt.players[0].hand.add(cards[choice])
                    if "porteur d'invitation" in [x.effects for x in self.plt.players[0].servants] and len(
                            self.plt.players[0].hand) < 10 and Card(**cards[choice]).classe not in ["Neutre",
                                                                                                    self.plt.players[
                                                                                                        0].classe]:
                        self.plt.players[0].hand.add(Card(**cards[choice]))
            else:
                if cards[choice] == "choix mystere":
                    try:
                        self.plt.players[0].hand.add(Card(**random.choice([x for x in all_spells if x["decouvrable"] == 1])))
                    except:
                        self.plt.players[0].hand.add(Card(**random.choice([x for x in all_servants if x["decouvrable"] == 1])))
            self.plt.cards_chosen = []
        elif type_dec == "dragage":
            self.plt.players[0].deck.cards.pop(-(3-choice))
            self.plt.players[0].deck.cards.insert(0, cards[choice])
            self.plt.cards_dragage = []
        elif type_dec == "entrave":
            cards[choice].effects["entrave"] = 1
            self.plt.cards_entrave = []

    def echange(self, carte):
        player = self.plt.players[0]
        player.hand.remove(carte)
        player.deck.add(carte)
        player.deck.shuffle()
        player.pick()
        player.mana_spend(1)

    def fin_du_tour(self):
        self.plt.tour_suivant()


class Orchestrator:

    def tour_oldia_model(self, plateau, logs, policy):

        """ L'IA génère une action d'après son modèle, on la fait jouer par la classe Tourencours """
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')

        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()
        for classe_heros in classes_heros:
            if action_line[f"is_{classe_heros}"] == -99:
                action_line[f"is_{classe_heros}"] = 0

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        input_state = np.array(itemgetter(*generate_column_state_old(classes_heros_old))(action_line))

        legal_actions = generate_legal_vector(plateau)

        observations = old_env.observation_spec()
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
                                                           name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
                                                             name='valid_actions')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = policy.action(timestep)
        action = int(result.action)

        if action == 0:
            action_line["action"] = "passer_tour"
            logs.append(action_line)
            TourEnCours(plateau).fin_du_tour()
        elif action < 11:
            action_line["action"] = "jouer_carte"
            played_card = plateau.players[0].hand[action - 1]
            action_line["carte_jouee"] = played_card.id  # name ou id ?
            logs.append(action_line)
            TourEnCours(plateau).jouer_carte(played_card)
        elif 11 <= action < 75:
            if (action - 11) // 8 == 0:
                attacker = plateau.players[0].hero
            else:
                attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
            if (action - 11) % 8 == 0:
                target = plateau.players[1].hero
            else:
                target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
            action_line["action"] = "attaquer"
            action_line["attaquant"] = attacker.id if type(attacker) is Card else "heros"
            action_line["attaquant_atq"] = attacker.attack
            action_line["attaquant_pv"] = attacker.health
            action_line["cible"] = target.id if type(target) is Card else "heros"
            action_line["cible_atq"] = target.attack
            action_line["cible_pv"] = target.health
            logs.append(action_line)
            TourEnCours(plateau).attaquer(attacker, target)
        else:
            if action == 75:
                target = plateau.players[0].hero
            elif action == 83:
                target = plateau.players[1].hero
            elif action < 83:
                target = plateau.players[0].servants[action - 76]
            else:
                target = plateau.players[1].servants[action - 84]
            action_line["action"] = "pouvoir_heroique"
            action_line["cible"] = target.id if type(target) is Card else "heros"
            action_line["cible_atq"] = target.attack
            action_line["cible_pv"] = target.health
            logs.append(action_line)
            TourEnCours(plateau).pouvoir_heroique(plateau.players[0].classe, target)

        plateau.update()
        return plateau

    def tour_oldia_training(self, plateau, policy):
        """ L'IA génère une action d'après son modèle, on la fait jouer par la classe Tourencours """
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')

        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()
        for classe_heros in classes_heros:
            if action_line[f"is_{classe_heros}"] == -99:
                action_line[f"is_{classe_heros}"] = 0

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        input_state = np.array(itemgetter(*generate_column_state_old(classes_heros_old))(action_line))

        legal_actions = generate_legal_vector(plateau)

        observations = old_env.observation_spec()
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
                                                           name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
                                                             name='valid_actions')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = policy.action(timestep)
        action = int(result.action)

        if action == 0:
            TourEnCours(plateau).fin_du_tour()
        elif action < 11:
            played_card = plateau.players[0].hand[action - 1]
            TourEnCours(plateau).jouer_carte(played_card)
        elif 11 <= action < 75:
            if (action - 11) // 8 == 0:
                attacker = plateau.players[0].hero
            else:
                attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
            if (action - 11) % 8 == 0:
                target = plateau.players[1].hero
            else:
                target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
            TourEnCours(plateau).attaquer(attacker, target)
        else:
            if action == 75:
                target = plateau.players[0].hero
            elif action == 83:
                target = plateau.players[1].hero
            elif action < 83:
                target = plateau.players[0].servants[action - 76]
            else:
                target = plateau.players[1].servants[action - 84]
            TourEnCours(plateau).pouvoir_heroique(plateau.players[0].classe, target)

        plateau.update()
        return plateau

    def tour_ia_model(self, plateau, logs, policy, generate_logs=True):
        """ L'IA génère une action d'après son modèle, on la fait jouer par la classe Tourencours """
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')

        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()
        for classe_heros in classes_heros:
            if action_line[f"is_{classe_heros}"] == -99:
                action_line[f"is_{classe_heros}"] = 0

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        input_state = np.array(itemgetter(*generate_column_state(classes_heros))(action_line))
        legal_actions = generate_legal_vector(plateau)

        observations = new_env.observation_spec()
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
                                                           name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
                                                             name='valid_actions')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = policy.action(timestep)
        action = int(result.action)

        if action == 0:
            if generate_logs:
                action_line["action"] = "passer_tour"
                logs.append(action_line)
            TourEnCours(plateau).fin_du_tour()
        elif action < 11:
            played_card = plateau.players[0].hand[action - 1]
            if generate_logs:
                action_line["action"] = "jouer_carte"
                action_line["carte_jouee"] = played_card.id  # name ou id ?
                logs.append(action_line)
            TourEnCours(plateau).jouer_carte(played_card)
        elif 11 <= action < 75:
            if (action - 11) // 8 == 0:
                attacker = plateau.players[0].hero
            else:
                attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
            if (action - 11) % 8 == 0:
                target = plateau.players[1].hero
            else:
                target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
            if generate_logs:
                action_line["action"] = "attaquer"
                action_line["attaquant"] = attacker.id if type(attacker) is Card else "heros"
                action_line["attaquant_atq"] = attacker.attack
                action_line["attaquant_pv"] = attacker.health
                action_line["cible"] = target.id if type(target) is Card else "heros"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).attaquer(attacker, target)
        else:
            if action == 75:
                target = plateau.players[0].hero
            elif action == 83:
                target = plateau.players[1].hero
            elif action < 83:
                target = plateau.players[0].servants[action - 76]
            else:
                target = plateau.players[1].servants[action - 84]
            if generate_logs:
                action_line["action"] = "pouvoir_heroique"
                action_line["cible"] = target.id if type(target) is Card else "heros"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).pouvoir_heroique(plateau.players[0].classe, target)

        plateau.update()
        return plateau

    def tour_ia_training(self, plateau, action):
        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()

        if action == 0:
            TourEnCours(plateau).fin_du_tour()
        elif action < 161:
            played_card = plateau.players[0].hand[int((action - 1) // 16)]
            if (action - 1) % 16 == 0:
                target = None
                if "cri de guerre" in played_card.effects and "choisi" not in played_card.effects["cri de guerre"]:
                    if played_card.effects["cri de guerre"][1][0] == "main":
                        if played_card.effects["cri de guerre"][1][1] == "allié":
                            if played_card.effects["cri de guerre"][1][2] == "tous":
                                target = CardGroup(
                                    (x for x in plateau.players[0].hand if x.type.lower() == "serviteur"))
                                target.remove(played_card)
            elif (action - 1) % 16 == 1:
                target = plateau.players[0].hero
            elif (action - 1) % 16 == 8:
                target = plateau.players[1].hero
            elif (action - 1) % 16 < 8:
                target = plateau.players[0].servants[int((action - 1) % 16) - 2]
            else:
                target = plateau.players[1].servants[int((action - 1) % 16) - 9]
            TourEnCours(plateau).jouer_carte(played_card, target)
        elif 161 <= action < 225:
            if (action - 161) // 8 == 0:
                attacker = plateau.players[0].hero
            else:
                attacker = plateau.players[0].servants[int((action - 161) // 8 - 1)]
            if (action - 161) % 8 == 0:
                target = plateau.players[1].hero
            else:
                target = plateau.players[1].servants[int((action - 161) % 8 - 1)]
            TourEnCours(plateau).attaquer(attacker, target)
        else:
            if action == 225:
                target = plateau.players[0].hero
            elif action == 233:
                target = plateau.players[1].hero
            elif action < 233:
                target = plateau.players[0].servants[int(action - 226)]
            else:
                target = plateau.players[1].servants[int(action - 234)]
            TourEnCours(plateau).pouvoir_heroique(plateau.players[0].classe, target)

        dead_servants = plateau.update()
        for servant in dead_servants:
            TourEnCours(plateau).apply_effects(servant)
        return plateau

    def tour_ia_minmax(self, plateau, logs, action, generate_logs=True):

        player = plateau.players[0]
        adv = plateau.players[1]

        """ Transformation des serviteurs concernés """
        if [x for x in player.hand if x.type == "Serviteur" and "transformation" in x.effects]:
            for serv in [x for x in player.hand if x.type == "Serviteur" and "transformation" in x.effects]:
                potential_transform = [get_card(x, all_servants) for x in serv.effects["transformation"]]
                player.hand.cards = [random.choice(potential_transform) if x == serv else x for x in player.hand]

        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()
        if action == 0:
            if generate_logs:
                action_line["action"] = "passer_tour"
                logs.append(action_line)
            TourEnCours(plateau).fin_du_tour()
        elif action < 161:
            played_card = player.hand[(action - 1) // 16]
            if generate_logs:
                action_line["action"] = "jouer_carte"
                action_line["carte_jouee"] = played_card.id  # name ou id ?
                logs.append(action_line)
            if (action - 1) % 16 == 0:
                target = None
                if "cri de guerre" in played_card.effects and "choisi" not in played_card.effects["cri de guerre"]:
                    if "main" in played_card.effects["cri de guerre"][1]:
                        if "allié" in played_card.effects["cri de guerre"][1]:
                            if "tous" in played_card.effects["cri de guerre"][1]:
                                target = CardGroup((x for x in player.hand if x.type == "Serviteur"))
                                target.remove(played_card)
                            elif "1" in played_card.effects["cri de guerre"][1]:
                                if "Méca" in played_card.effects["cri de guerre"][1]:
                                    target = CardGroup(
                                        (x for x in player.hand if x.type == "Serviteur" and "Méca" in x.genre))
                                    target.remove(played_card)
                                    target = random.choice(target) if len(target) > 0 else None
                            elif "chaque type" in played_card.effects["cri de guerre"][1]:
                                potential_boost = [x for x in player.hand if x.genre and x != played_card].copy()
                                target = CardGroup()
                                for genre in ["Méca", "Murloc", "Élémentaire", "Bête", "Mort-vivant", "Totem", "Naga",
                                              "Pirate", "Dragon", "Huran"]:
                                    if [x for x in potential_boost if genre in x.genre]:
                                        boosted_servant = [x for x in potential_boost if genre in x.genre]
                                        boosted_servant = boosted_servant[
                                            np.array([len(x.genre) for x in boosted_servant]).argsort()[0]]
                                        target.add(boosted_servant)
                                        potential_boost.remove(boosted_servant)
                    elif "deck" in played_card.effects["cri de guerre"][1]:
                        if "allié" in played_card.effects["cri de guerre"][1]:
                            if "serviteur" in played_card.effects["cri de guerre"][1] and "tous" in \
                                    played_card.effects["cri de guerre"][1]:
                                if "if_crideguerre" in played_card.effects["cri de guerre"][1]:
                                    target = CardGroup((x for x in player.deck if
                                                        x.type == "Serviteur" and "cri de guerre" in x.effects))
            elif (action - 1) % 16 == 1:
                target = player.hero
            elif (action - 1) % 16 == 8:
                target = adv.hero
            elif (action - 1) % 16 < 8:
                target = player.servants[(action - 1) % 16 - 2]
                if "cri de guerre" in played_card.effects and "voisin" in played_card.effects["cri de guerre"][1] and len(player.servants) > 1:
                    try:
                        target = CardGroup([target] + [player.servants[(action) % 16 - 2]])
                    except:
                        target = CardGroup([target] + [player.servants[(action - 2) % 16 - 2]])
                elif "final" in played_card.effects and "voisin" in played_card.effects["final"][1] and len(player.servants) > 1:
                    try:
                        target = CardGroup([target] + [player.servants[(action) % 16 - 2]])
                    except:
                        target = CardGroup([target] + [player.servants[(action - 2) % 16 - 2]])
            else:
                target = adv.servants[(action - 1) % 16 - 9]
            inter_cost = played_card.cost
            TourEnCours(plateau).jouer_carte(played_card, target)
            player.last_card = played_card
            if inter_cost != played_card.base_cost:
                for discount in played_card.discount:
                    if discount in player.discount_next:
                        for card in player.hand:
                            if discount in card.discount:
                                card.discount.remove(discount)
                        player.discount_next.remove(discount)
                        played_card.discount.remove(discount)
        elif 161 <= action < 225:
            if (action - 161) // 8 == 0:
                attacker = player.hero
            else:
                attacker = player.servants[int((action - 161) // 8 - 1)]
            if (action - 161) % 8 == 0:
                target = adv.hero
            else:
                target = adv.servants[int((action - 161) % 8 - 1)]
            if generate_logs:
                action_line["action"] = "attaquer"
                action_line["attaquant"] = attacker.id if type(attacker) is Card else "heros"
                action_line["attaquant_atq"] = attacker.attack
                action_line["attaquant_pv"] = attacker.health
                action_line["cible"] = target.id if type(target) is Card else "heros"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).attaquer(attacker, target)
        elif action < 241:
            if action == 225:
                target = player.hero
            elif action == 233:
                target = adv.hero
            elif action < 233:
                target = player.servants[action - 226]
            else:
                target = adv.servants[action - 234]
            if generate_logs:
                action_line["action"] = "pouvoir_heroique"
                action_line["cible"] = target.id if type(target) is Card else "heros"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).pouvoir_heroique(player.classe, target)
        elif action < 245:
            if generate_logs:
                action_line[
                    "action"] = "decouverte" if plateau.cards_chosen else "dragage" if plateau.cards_dragage else "entrave"
                logs.append(action_line)
            if plateau.cards_chosen:
                TourEnCours(plateau).decouverte(plateau.cards_chosen, action - 241)
            elif plateau.cards_dragage:
                TourEnCours(plateau).decouverte(plateau.cards_dragage, action - 241, type_dec="dragage")
            elif plateau.cards_entrave:
                TourEnCours(plateau).decouverte(plateau.cards_entrave, action - 241, type_dec="entrave")
        else:
            if generate_logs:
                action_line["action"] = "echange"
                logs.append(action_line)
            TourEnCours(plateau).echange(player.hand[action - 245])

        player = plateau.players[0]
        adv = plateau.players[1]

        """ Application des effets d'aura """
        aura_servants = [x for x in player.servants.cards + adv.servants.cards if
                         "aura" in x.effects and not x.is_dead() and "alive" in x.effects["aura"][1]]
        for creature in player.servants.cards + adv.servants.cards:
            creature.total_temp_boost = [0, 0]
        if aura_servants:
            TourEnCours(plateau).apply_effects(get_card(-1, all_cards))
        for creature in player.servants.cards + adv.servants.cards:
            creature.attack = max(0, creature.base_attack + creature.total_temp_boost[0])
            creature.health = max(0, creature.base_health + creature.total_temp_boost[1] - creature.blessure)
        player.hero.has_attacked = 0

        """ Application des rales d'agonie """
        dead_servants, dead_servants_player = plateau.update()
        while dead_servants:
            for servant in dead_servants:
                TourEnCours(plateau).apply_effects(servant)
                if servant in dead_servants_player and servant in adv.servants:
                    adv.servants.remove(servant)
                elif servant in player.servants:
                    player.servants.remove(servant)
            dead_servants, dead_servants_player = plateau.update()

        player.apply_discount()

        return plateau, logs

    """ Génère un nombre donné de parties et créé les logs associés"""

    # def generate_random_game(self, nb_games, players=()):
    #     logs_hs = []
    #     i = 0
    #     scores = {}
    #     players1 = players
    #     players2 = deepcopy([players[1], players[0]])
    #
    #     """ Sauvegarde temporaire des plateaux initiaux"""
    #     with open('plateau_init1.pickle', 'wb') as f:
    #         pickle.dump(Plateau(players1), f)
    #     with open('plateau_init2.pickle', 'wb') as f:
    #         pickle.dump(Plateau(players2), f)
    #
    #     """ On simule nb_games parties """
    #     """ La moitié où le joueur 1 commence """
    #     for i in range(0, round(nb_games/2)):
    #         logs_inter = []
    #         with open('plateau_init1.pickle', 'rb') as f:
    #             mon_plateau = pickle.load(f)
    #         while mon_plateau.game_on:
    #             mon_plateau = Orchestrator().tour_au_hasard(mon_plateau, logs_inter)
    #
    #         """Actions de fin de partie"""
    #         winner = mon_plateau.winner
    #         logs_inter = pd.DataFrame(logs_inter)
    #         logs_hs.append(logs_inter)
    #         if winner.name in scores.keys():
    #             scores[winner.name] += 1
    #         else:
    #             scores[winner.name] = 1
    #         i += 1
    #         if i % 100 == 0:
    #             print(i)
    #
    #     """ L'autre moitié où le joueur 2 commence """
    #     for i in range(round(nb_games/2), nb_games):
    #         logs_inter = []
    #         with open('plateau_init2.pickle', 'rb') as f:
    #             mon_plateau2 = pickle.load(f)
    #         while mon_plateau2.game_on:
    #             mon_plateau2 = Orchestrator().tour_au_hasard(mon_plateau2, logs_inter)
    #
    #         """Actions de fin de partie"""
    #         winner = mon_plateau2.winner
    #         logs_inter = pd.DataFrame(logs_inter)
    #         logs_hs.append(logs_inter)
    #         if winner.name in scores.keys():
    #             scores[winner.name] += 1
    #         else:
    #             scores[winner.name] = 1
    #         i += 1
    #         if i % 100 == 0:
    #             print(i)
    #
    #     """ Concaténation des logs + suppression des plateaux temporaires """
    #     logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis = 1)
    #     os.remove('plateau_init1.pickle')
    #     os.remove('plateau_init2.pickle')
    #     return logs_hs, scores

    def generate_randomvsia_game(self, nb_games, players=()):
        logs_hs = []
        i = 0
        scores = {}
        players1 = players
        players2 = deepcopy([players[1], players[0]])

        """ Sauvegarde temporaire des plateaux initiaux"""
        with open('plateau_init1.pickle', 'wb') as f:
            pickle.dump(Plateau(players1), f)
        with open('plateau_init2.pickle', 'wb') as f:
            pickle.dump(Plateau(players2), f)

        """ On simule nb_games parties """
        """ La moitié où le joueur 1 commence """
        for i in range(0, round(nb_games / 2)):
            logs_inter = []
            with open('plateau_init1.pickle', 'rb') as f:
                mon_plateau = pickle.load(f)
            while mon_plateau.game_on:
                if mon_plateau.game_turn % 2 == 0:
                    mon_plateau = Orchestrator().tour_au_hasard(mon_plateau, logs_inter)
                else:
                    mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, saved_policy)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            if i % 100 == 0:
                print(i)

        """ L'autre moitié où le joueur 2 commence """
        for i in range(round(nb_games / 2), nb_games):
            logs_inter = []
            with open('plateau_init2.pickle', 'rb') as f:
                mon_plateau2 = pickle.load(f)
            while mon_plateau2.game_on:
                if mon_plateau2.game_turn % 2 == 0:
                    mon_plateau2 = Orchestrator().tour_ia_model(mon_plateau2, logs_inter, saved_policy)
                else:
                    mon_plateau2 = Orchestrator().tour_au_hasard(mon_plateau2, logs_inter)

            """Actions de fin de partie"""
            winner = mon_plateau2.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            if i % 100 == 0:
                print(i)

        """ Concaténation des logs + suppression des plateaux temporaires """
        logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis=1)
        os.remove('plateau_init1.pickle')
        os.remove('plateau_init2.pickle')
        return logs_hs, scores

    def generate_oldia_game(self, nb_games, new_policy=saved_policy, players=(), generate_logs=True):
        global logs_inter, logs_hs
        if generate_logs:
            logs_hs = []
        scores = {}

        """ On simule nb_games parties """
        """ La moitié où le joueur 1 commence """
        for i in range(0, round(nb_games / 2)):
            if generate_logs:
                logs_inter = []
                players1 = deepcopy(players)
                mon_plateau = Plateau(players1)
                while mon_plateau.game_on:
                    if mon_plateau.game_turn % 2 == 0:
                        mon_plateau = Orchestrator().tour_oldia_model(mon_plateau, logs_inter, old_policy)
                    else:
                        mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, new_policy)
            else:
                players1 = deepcopy(players)
                mon_plateau = Plateau(players1)
                while mon_plateau.game_on:
                    if mon_plateau.game_turn % 2 == 0:
                        mon_plateau = Orchestrator().tour_oldia_training(mon_plateau, old_policy)
                    else:
                        mon_plateau = Orchestrator().tour_ia_model(mon_plateau, [], new_policy, False)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            if generate_logs:
                logs_inter = pd.DataFrame(logs_inter)
                logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            if i % 100 == 0:
                print(i)

        for i in range(round(nb_games / 2), nb_games):
            if generate_logs:
                logs_inter = []
                players2 = deepcopy([players[1], players[0]])
                mon_plateau = Plateau(players2)
                while mon_plateau.game_on:
                    if mon_plateau.game_turn % 2 == 0:
                        mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, new_policy)
                    else:
                        mon_plateau = Orchestrator().tour_oldia_model(mon_plateau, logs_inter, old_policy)
            else:
                players2 = deepcopy([players[1], players[0]])
                mon_plateau = Plateau(players2)
                while mon_plateau.game_on:
                    if mon_plateau.game_turn % 2 == 0:
                        mon_plateau = Orchestrator().tour_ia_model(mon_plateau, [], new_policy, False)
                    else:
                        mon_plateau = Orchestrator().tour_oldia_training(mon_plateau, old_policy)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            if generate_logs:
                logs_inter = pd.DataFrame(logs_inter)
                logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            if i % 100 == 0:
                print(i)

        """ Concaténation des logs + suppression des plateaux temporaires """
        if generate_logs:
            logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis=1)
            return logs_hs, scores
        else:
            return scores

    # def generate_ia_game(self, nb_games, players=()):
    #     logs_hs = []
    #     i = 0
    #     scores = {}
    #
    #     players1 = players
    #     players2 = deepcopy([players[1], players[0]])
    #
    #     """ Sauvegarde temporaire des plateaux initiaux"""
    #     with open('plateau_init1.pickle', 'wb') as f:
    #         pickle.dump(Plateau(players1), f)
    #     with open('plateau_init2.pickle', 'wb') as f:
    #         pickle.dump(Plateau(players2), f)
    #
    #
    #
    #     """ On simule nb_games parties """
    #     """ La moitié où le joueur 1 commence """
    #     for i in range(0, round(nb_games/2)):
    #         logs_inter = []
    #         with open('plateau_init1.pickle', 'rb') as f:
    #             mon_plateau = pickle.load(f)
    #         while mon_plateau.game_on:
    #             mon_plateau = Orchestrator().tour_ia(mon_plateau, logs_inter, saved_policy, policy_state)
    #
    #         """Actions de fin de partie"""
    #         winner = mon_plateau.winner
    #         logs_inter = pd.DataFrame(logs_inter)
    #         logs_hs.append(logs_inter)
    #         if winner.name in scores.keys():
    #             scores[winner.name] += 1
    #         else:
    #             scores[winner.name] = 1
    #         i += 1
    #         if i % 100 == 0:
    #             print(i)
    #
    #     for i in range(round(nb_games/2), nb_games):
    #         logs_inter = []
    #         with open('plateau_init2.pickle', 'rb') as f:
    #             mon_plateau = pickle.load(f)
    #         while mon_plateau.game_on:
    #             mon_plateau = Orchestrator().tour_ia(mon_plateau, logs_inter, saved_policy, policy_state)
    #
    #         """Actions de fin de partie"""
    #         winner = mon_plateau.winner
    #         logs_inter = pd.DataFrame(logs_inter)
    #         logs_hs.append(logs_inter)
    #         if winner.name in scores.keys():
    #             scores[winner.name] += 1
    #         else:
    #             scores[winner.name] = 1
    #         i += 1
    #         if i % 100 == 0:
    #             print(i)
    #
    #     """ Concaténation des logs + suppression des plateaux temporaires """
    #     logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis=1)
    #     os.remove('plateau_init1.pickle')
    #     os.remove('plateau_init2.pickle')
    #     return logs_hs, scores


if __name__ == '__main__':
    logs_hs, scores = Orchestrator().generate_random_game(10)
    print(scores)
