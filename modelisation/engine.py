import time
from abc import ABC

import pandas as pd
import numpy as np
from Entities import *
import random
import os
from operator import itemgetter


# def generate_column_state_old(classes_Player):
#     columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
#                             "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]
#
#     """ Player """
#     for classe in classes_Player:
#         columns_actual_state.append(f"is_{classe}")
#
#     """ HAND """
#     for n in range(10):
#         columns_actual_state.append(f"carte_en_main{n + 1}_cost")
#         columns_actual_state.append(f"carte_en_main{n + 1}_atk")
#         columns_actual_state.append(f"carte_en_main{n + 1}_pv")
#
#     """ SERVANTS """
#     for n in range(7):
#         columns_actual_state.append(f"atq_serv{n + 1}_j")
#         columns_actual_state.append(f"pv_serv{n + 1}_j")
#         columns_actual_state.append(f"atq_remain_serv{n + 1}_j")
#
#     for n in range(7):
#         columns_actual_state.append(f"atq_serv{n + 1}_adv")
#         columns_actual_state.append(f"pv_serv{n + 1}_adv")
#
#     return columns_actual_state
#
#
# def generate_column_state(classes_Player):
#     columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
#                             "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]
#
#     """ Player """
#     for classe in classes_Player:
#         columns_actual_state.append(f"is_{classe}")
#
#     """ HAND """
#     for n in range(10):
#         for m in range(len(all_cards)):
#             columns_actual_state.append(f"is_carte{n + 1}_{all_cards[m]['name']}")
#
#     """ SERVANTS """
#     for n in range(7):
#         columns_actual_state.append(f"atq_serv{n + 1}_j")
#         columns_actual_state.append(f"pv_serv{n + 1}_j")
#         columns_actual_state.append(f"atq_remain_serv{n + 1}_j")
#         for m in range(len(all_servants)):
#             columns_actual_state.append(f"is_servant{n + 1}_{all_servants[m]['name']}_j")
#             columns_actual_state.append(f"is_servant{n + 1}_{all_servants[m]['name']}_adv")
#
#     for n in range(7):
#         columns_actual_state.append(f"atq_serv{n + 1}_adv")
#         columns_actual_state.append(f"pv_serv{n + 1}_adv")
#
#     return columns_actual_state
#
#
# def generate_legal_vector_old(state):
#     """ Gestion des actions légales """
#     legal_actions = [True]
#     gamestate = state.get_gamestate()
#     for n in range(90):
#         legal_actions.append(False)
#
#     """ Quelles cartes peut-on jouer ? """
#     for n in range(int(gamestate["nbre_cartes_j"])):
#         for m in range(len(all_cards)):
#             if gamestate[f"is_carte{n + 1}_{all_cards[m]['name']}"] != -99 \
#                     and get_card(all_cards[m]['name'], all_cards).cost <= gamestate["mana_dispo_j"] \
#                     and gamestate[f"pv_serv7_j"] == -99:
#                 legal_actions[n + 1] = True
#
#     """ Quelles cibles peut-on attaquer et avec quels attaquants"""
#     """ Notre héros peut attaquer """
#     if gamestate["remaining_atk_j"] > 0 and gamestate["attaque_j"] > 0:
#         legal_actions[11] = True
#         for m in range(1, 8):
#             if gamestate[f"atq_serv{m}_adv"] != -99:
#                 legal_actions[11 + m] = True
#
#     """ Nos serviteurs peuvent attaquer """
#     is_provoc = False
#     for m in range(1, 8):
#         if gamestate[f"atq_serv{m}_adv"] != -99 and "provocation" in state.players[1].servants[m - 1].effects:
#             is_provoc = True
#             break
#     for n in range(1, 8):
#         if gamestate[f"atq_remain_serv{n}_j"] > 0:
#             if not is_provoc:
#                 legal_actions[11 + 8 * n] = True
#             if "ruée" in state.players[0].servants[n - 1].effects:
#                 if state.players[0].servants[n - 1].effects["ruée"] == 1:
#                     legal_actions[11 + 8 * n] = False
#             for m in range(1, 8):
#                 if not is_provoc:
#                     if gamestate[f"atq_serv{m}_adv"] != -99:
#                         legal_actions[11 + 8 * n + m] = True
#                 else:
#                     if "provocation" in state.players[1].servants[m - 1].effects:
#                         legal_actions[11 + 8 * n + m] = True
#
#     if gamestate["dispo_ph_j"] and gamestate["cout_ph_j"] <= gamestate["mana_dispo_j"]:
#         targets = state.targets_hp()
#         if state.players[0] in targets:
#             legal_actions[75] = True
#         if state.players[1] in targets:
#             legal_actions[83] = True
#         for n in range(1, 8):
#             if gamestate[f"atq_serv{n}_j"] != -99:
#                 if gamestate[f"serv{n}_j"] in targets:
#                     legal_actions[75 + n] = True
#             if gamestate[f"atq_serv{n}_adv"] != -99:
#                 if gamestate[f"serv{n}_adv"] in targets:
#                     legal_actions[83 + n] = True
#
#     return legal_actions
#
#
# def generate_legal_vector(state):
#     """ Gestion des actions légales """
#     legal_actions = [False] * 255
#     player = state.players[0]
#     adv = state.players[1]
#
#     """ decouverte """
#     if state.cards_chosen or state.cards_dragage:
#         legal_actions[0] = False
#         for n in range(241, 241 + len(state.cards_chosen) if state.cards_chosen else 241 + len(state.cards_dragage)):
#             legal_actions[n] = True
#         if state.cards_chosen and len(state.cards_chosen) == 4 and state.cards_chosen[3] == "choix mystere":
#             legal_actions[244] = True
#         return legal_actions
#
#     if state.cards_entrave:
#         for n in range(241, 241 + len(state.cards_entrave)):
#             legal_actions[n] = True
#         return legal_actions
#
#     legal_actions[0] = True
#     gamestate = state.get_gamestate()
#
#     """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
#     for n in range(len(player.hand)):
#         if player.hand[n].cost <= player.mana and "entrave" not in player.hand[n].effects:
#             if len(player.servants) + len(player.lieux) != 7 and player.hand[n].type == "Serviteur":
#
#                 """ Serviteurs avec cris de guerre ciblés """
#                 if "cri de guerre" in player.hand[n].effects and "choisi" in player.hand[n].effects["cri de guerre"][1]:
#                     if "serviteur" in player.hand[n].effects["cri de guerre"][1]:
#                         if "allié" in player.hand[n].effects["cri de guerre"][1] and player.servants.cards:
#                             if "genre" in player.hand[n].effects["cri de guerre"][1]:
#                                 for m in range(len(player.servants)):
#                                     if player.servants[m].genre:
#                                         legal_actions[16 * n + m + 3] = True
#                             elif "Bête" in player.hand[n].effects["cri de guerre"][1]:
#                                 for m in range(len(player.servants)):
#                                     if "Bête" in player.servants[m].genre:
#                                         legal_actions[16 * n + m + 3] = True
#                             elif "Mort-vivant" in player.hand[n].effects["cri de guerre"][1]:
#                                 for m in range(len(player.servants)):
#                                     if "Mort-vivant" in player.servants[m].genre:
#                                         legal_actions[16 * n + m + 3] = True
#                             else:
#                                 for m in range(len(player.servants)):
#                                     legal_actions[16 * n + m + 3] = True
#                         elif "ennemi" in player.hand[n].effects["cri de guerre"][1] and adv.servants.cards:
#                             for m in range(len(adv.servants)):
#                                 if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
#                                     legal_actions[16 * n + m + 10] = True
#                         elif "tous" in player.hand[n].effects["cri de guerre"][1] and (
#                                 player.servants.cards or adv.servants.cards):
#                             if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
#                                 for m in range(len(player.servants)):
#                                     legal_actions[16 * n + m + 3] = True
#                                 for m in range(len(adv.servants)):
#                                     if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
#                                         m].effects:
#                                         legal_actions[16 * n + m + 10] = True
#                             else:
#                                 if "if_attack_greater" in player.hand[n].effects["cri de guerre"][1] and [x for x in
#                                                                                                           player.servants.cards + adv.servants.cards
#                                                                                                           if x.attack >=
#                                                                                                              player.hand[
#                                                                                                                  n].effects[
#                                                                                                                  "cri de guerre"][
#                                                                                                                  1][5]]:
#                                     for m in range(len(player.servants)):
#                                         if player.servants[m].attack >= player.hand[n].effects["cri de guerre"][1][
#                                             5] and player.servants[m] != player.hand[n]:
#                                             legal_actions[16 * n + m + 3] = True
#                                     for m in range(len(adv.servants)):
#                                         if adv.servants[m].attack >= player.hand[n].effects["cri de guerre"][1][5]:
#                                             legal_actions[16 * n + m + 10] = True
#                                 else:
#                                     legal_actions[16 * n + 1] = True
#                         else:
#                             legal_actions[16 * n + 1] = True
#                     elif "tous" in player.hand[n].effects["cri de guerre"][1]:
#                         if "ennemi" in player.hand[n].effects["cri de guerre"][1]:
#                             for m in range(len(adv.servants)):
#                                 if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
#                                     m].effects:
#                                     legal_actions[16 * n + m + 10] = True
#                         else:
#                             if "conditional" not in player.hand[n].effects["cri de guerre"][1]:
#                                 legal_actions[16 * n + 2] = True
#                                 legal_actions[16 * n + 9] = True
#                                 for m in range(len(player.servants)):
#                                     legal_actions[16 * n + m + 3] = True
#                                 for m in range(len(adv.servants)):
#                                     if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
#                                         m].effects:
#                                         legal_actions[16 * n + m + 10] = True
#                             else:
#                                 if "if_weapon" in player.hand[n].effects["cri de guerre"][
#                                     1] and player.weapon is not None \
#                                         or "if_death_undead" in player.hand[n].effects["cri de guerre"][
#                                     1] and player.dead_undeads \
#                                         or "if_dragon_hand" in player.hand[n].effects["cri de guerre"][1] and [x for x
#                                                                                                                in
#                                                                                                                player.hand
#                                                                                                                if
#                                                                                                                "Dragon" in x.genre] \
#                                         or "if_alone" in player.hand[n].effects["cri de guerre"][1] and len(
#                                     player.servants) == 0 \
#                                         or "if_spell" in player.hand[n].effects["cri de guerre"][1] and \
#                                         player.hand[n].effects["cri de guerre"][2] != 0:
#                                     legal_actions[16 * n + 2] = True
#                                     legal_actions[16 * n + 9] = True
#                                     for m in range(len(player.servants)):
#                                         legal_actions[16 * n + m + 3] = True
#                                     for m in range(len(adv.servants)):
#                                         if "camouflage" not in adv.servants[m].effects and "en sommeil" not in \
#                                                 adv.servants[m].effects:
#                                             legal_actions[16 * n + m + 10] = True
#                                 else:
#                                     legal_actions[16 * n + 1] = True
#
#                 # Serviteurs avec soif de mana ciblée
#                 elif "soif de mana" in player.hand[n].effects and "choisi" in player.hand[n].effects["soif de mana"][1]:
#                     if "serviteur" in player.hand[n].effects["soif de mana"][1]:
#                         if "allié" in player.hand[n].effects["soif de mana"][1] and gamestate[f"serv1_j"] != -99:
#                             if "genre" in player.hand[n].effects["soif de mana"][1]:
#                                 for m in range(len(player.servants)):
#                                     if player.servants[m].genre:
#                                         legal_actions[16 * n + m + 3] = True
#                             else:
#                                 for m in range(len(player.servants)):
#                                     legal_actions[16 * n + m + 3] = True
#                         elif "tous" in player.hand[n].effects["soif de mana"][1] and (
#                                 gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
#                             for m in range(len(player.servants)):
#                                 legal_actions[16 * n + m + 3] = True
#                             for m in range(len(adv.servants)):
#                                 if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
#                                     m].effects:
#                                     legal_actions[16 * n + m + 10] = True
#                         else:
#                             legal_actions[16 * n + 1] = True
#                     elif "tous" in player.hand[n].effects["soif de mana"][1]:
#                         if "ennemi" in player.hand[n].effects["soif de mana"][1]:
#                             for m in range(len(adv.servants)):
#                                 if "camouflage" not in adv.servants[m].effects and "en sommeil" not in \
#                                         adv.servants[m].effects:
#                                     legal_actions[16 * n + m + 10] = True
#                         else:
#                             legal_actions[16 * n + 2] = True
#                             legal_actions[16 * n + 9] = True
#                             for m in range(len(player.servants)):
#                                 legal_actions[16 * n + m + 3] = True
#                             for m in range(len(adv.servants)):
#                                 if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[
#                                     m].effects:
#                                     legal_actions[16 * n + m + 10] = True
#                 else:
#                     legal_actions[16 * n + 1] = True
#                 # Serviteurs avec magnétisme
#                 if "magnetisme" in player.hand[n].effects:
#                     for m in range(len(player.servants)):
#                         if "Méca" in player.servants[m].genre:
#                             legal_actions[16 * n + m + 3] = True
#             elif player.hand[n].type.lower() == "sort":
#                 legal_actions[16 * n + 1] = True
#
#     """ Quelles cibles peut-on attaquer et avec quels attaquants"""
#     is_provoc = False
#     for m in range(len(adv.servants)):
#         if "provocation" in adv.servants[m].effects:
#             is_provoc = True
#             break
#     """ Notre héros peut attaquer """
#     if player.remaining_atk > 0 and player.attack > 0:
#         if not is_provoc:
#             legal_actions[161] = True
#         for m in range(len(adv.servants)):
#             if not is_provoc:
#                 if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
#                     legal_actions[161 + m + 1] = True
#             else:
#                 if "provocation" in adv.servants[m].effects:
#                     legal_actions[161 + m + 1] = True
#
#     """ Nos serviteurs peuvent attaquer """
#
#     for n in range(len(player.servants)):
#         if player.servants[n].remaining_atk * player.servants[n].attack > 0 and "en sommeil" not in player.servants[
#             n].effects:
#             if not is_provoc:
#                 legal_actions[161 + 8 * (n + 1)] = True
#             if "ruée" in player.servants[n].effects:
#                 if player.servants[n].effects["ruée"] == 1:
#                     legal_actions[161 + 8 * (n + 1)] = False
#             for m in range(len(adv.servants)):
#                 if not is_provoc:
#                     if "camouflage" not in adv.servants[m].effects and "en sommeil" not in adv.servants[m].effects:
#                         legal_actions[161 + 8 * (n + 1) + (m + 1)] = True
#                 else:
#                     if "provocation" in adv.servants[m].effects:
#                         legal_actions[161 + 8 * (n + 1) + (m + 1)] = True
#
#     """ Pouvoir héroïque """
#     if player.dispo_pouvoir and player.cout_pouvoir_temp <= player.mana:
#         targets = state.targets_hp()
#         if player in targets:
#             legal_actions[225] = True
#         if adv in targets:
#             legal_actions[233] = True
#         if len(targets) >= 2:
#             for n in range(len(player.servants)):
#                 if player.servants[n] in targets:
#                     legal_actions[226 + n] = True
#             for n in range(len(adv.servants)):
#                 if adv.servants[n] in targets and not list(
#                         {"camouflage", "en sommeil", "inciblable"} and set(adv.servants[n].effects)):
#                     legal_actions[234 + n] = True
#
#     """ Mot-clé échangeable """
#     for n in range(len(player.hand)):
#         if player.mana >= 1 and "echangeable" in player.hand[n].effects:
#             legal_actions[245 + n] = True
#
#     return legal_actions


# def estimated_advantage(action, state):
#     """ Simule le plateau qu'aurait donné une certaine action pour en tirer une notion d'avantage gagné ou perdu """
#     actual_state = deepcopy(state)
#     next_state = deepcopy(state)
#     action = int(action)
#
#     if action == 0:
#         TourEnCours(next_state).fin_du_tour()
#         while next_state.get_gamestate()['pseudo_j'] == 'OldIA':
#             next_state = Orchestrator().tour_oldia_training(next_state, old_policy)
#             if not next_state.game_on:
#                 if next_state.winner.name == "NewIA":
#                     return 500
#                 else:
#                     return -500
#     elif action < 11:
#         TourEnCours(next_state).jouer_carte(next_state.players[0].hand[action - 1])
#     elif 11 <= action < 75:
#         if (action - 11) // 8 == 0:
#             attacker = next_state.players[0]
#         else:
#             attacker = next_state.players[0].servants[int((action - 11) // 8 - 1)]
#         if (action - 11) % 8 == 0:
#             target = next_state.players[1]
#         else:
#             target = next_state.players[1].servants[int((action - 11) % 8 - 1)]
#         TourEnCours(next_state).attaquer(attacker, target)
#     elif action >= 75:
#         if action == 75:
#             target = next_state.players[0]
#         elif action == 83:
#             target = next_state.players[1]
#         elif action < 83:
#             target = next_state.players[0].servants[action - 76]
#         else:
#             target = next_state.players[1].servants[action - 84]
#         TourEnCours(next_state).pouvoir_Playerique(next_state.players[0].classe, target)
#
#     next_state.update()
#
#     if not next_state.game_on:
#         if next_state.winner.name == "NewIA":
#             return 500
#         else:
#             return -500
#
#     def calc_advantage(state_game):
#         advantage = (state_game["nbre_cartes_j"] - state_game["nbre_cartes_adv"]) + 0.8 * (
#                 state_game["nbre_cartes_j"] / max(1, state_game["nbre_cartes_adv"]))
#         for n in range(1, 8):
#             if state_game[f"serv{n}_j"] != -99:
#                 advantage += 2 * state_game[f"atq_serv{n}_j"] + 2 * state_game[f"pv_serv{n}_j"]
#             if state_game[f"serv{n}_adv"] != -99:
#                 advantage -= 2 * state_game[f"atq_serv{n}_adv"] + 2 * state_game[f"pv_serv{n}_adv"]
#         advantage += 0.22 * (pow(30 - state_game["pv_adv"], 1.3) - pow(30 - state_game["pv_j"], 1.3))
#         advantage += state_game["attaque_j"]
#         return advantage
#
#     actual_advantage = calc_advantage(actual_state.get_gamestate())
#     predicted_advantage = calc_advantage(next_state.get_gamestate())
#
#     return round(predicted_advantage - actual_advantage, 2)
#
#
# """ Initialisation de l'environnement et chargement du modèle """
#
# old_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')
# saved_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')
#
#
# class Frenchstone_old(py_environment.PyEnvironment, ABC):
#     def __init__(self):
#         super().__init__()
#         self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=90,
#                                                         name='action')
#         self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
#         self._observation_spec = {
#             'observation': array_spec.BoundedArraySpec(
#                 shape=(len(itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate())),),
#                 dtype=np.int32, minimum=-100, maximum=100, name='observation'),
#             'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(91,), dtype=np.bool_)
#         }
#         self._episode_ended = False
#
#     def action_spec(self):
#         return self._action_spec
#
#     def observation_spec(self):
#         return self._observation_spec
#
#     def _reset(self):
#         obs = self.observation_spec()
#
#         """ Gestion des actions légales """
#         legal_actions = generate_legal_vector(self._state)
#
#         obs['observation'] = np.array(
#             itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate()))
#         obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
#         return ts.restart(obs)
#
#     def _step(self, action):
#
#         if self._episode_ended:
#             return self.reset()
#
#         """ Estimation de la récompense """
#         reward = 0
#
#         """ Gestion des actions légales """
#         self._state = Orchestrator().tour_ia_training(self._state, action)
#
#         while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
#             self._state = Orchestrator().tour_oldia_training(self._state, old_policy)
#
#         legal_actions = generate_legal_vector(self._state)
#         obs = self.observation_spec()
#         obs['observation'] = np.array(
#             itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate()),
#             dtype=np.int32)
#         obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
#         if reward in [-500, 500]:
#             self._episode_ended = True
#             return ts.termination(obs, reward)
#         return ts.transition(obs, reward)
#
#
# old_env = Frenchstone_old()
# old_env = tf_py_environment.TFPyEnvironment(old_env)
#
#
# class Frenchstone(py_environment.PyEnvironment):
#     def __init__(self):
#         super().__init__()
#         self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=90,
#                                                         name='action')
#         self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
#         self._observation_spec = {
#             'observation': array_spec.BoundedArraySpec(
#                 shape=(len(itemgetter(*generate_column_state(classes_heros))(self._state.get_gamestate())),),
#                 dtype=np.int32, minimum=-100, maximum=100, name='observation'),
#             'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(91,), dtype=np.bool_)
#         }
#         self._episode_ended = False
#
#     def action_spec(self):
#         return self._action_spec
#
#     def observation_spec(self):
#         return self._observation_spec
#
#     def _reset(self):
#         obs = self.observation_spec()
#
#         """ Gestion des actions légales """
#         legal_actions = generate_legal_vector(self._state)
#
#         obs['observation'] = np.array(itemgetter(*generate_column_state(classes_heros))(self._state.get_gamestate()))
#         obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
#         return ts.restart(obs)
#
#     def _step(self, action):
#
#         if self._episode_ended:
#             return self.reset()
#
#         """ Estimation de la récompense """
#         reward = 0
#
#         """ Gestion des actions légales """
#         self._state = Orchestrator().tour_ia_training(self._state, action)
#
#         while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
#             self._state = Orchestrator().tour_oldia_training(self._state, old_policy)
#
#         legal_actions = generate_legal_vector(self._state)
#         obs = self.observation_spec()
#         obs['observation'] = np.array(itemgetter(*generate_column_state(classes_heros))(self._state.get_gamestate()),
#                                       dtype=np.int32)
#         obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
#         if reward in [-500, 500]:
#             self._episode_ended = True
#             return ts.termination(obs, reward)
#         return ts.transition(obs, reward)
#
#
# new_env = Frenchstone()
# new_env = tf_py_environment.TFPyEnvironment(new_env)

class TourEnCours:
    """Classe prenant en entrée un plateau de jeu et permettant d'effectuer toutes les actions possibles dessus."""

    def __init__(self, plateau):
        self.plt = plateau

    def apply_effects(self, carte, target=None):
        player = self.plt.players[0]
        adv = self.plt.players[1]

        if "Gardien du temps" in player.permanent_buff:
            if "Dragon" in carte.genre:
                carte.effects["provocation"] = 1
                carte.effects["bouclier divin"] = 1
        if carte.name == "Recrue de la main d'argent":
            if "regis" in player.permanent_buff and player.permanent_buff["regis"] == 1:
                carte.boost(3, 3, other={"rale d'agonie": ["regis", ["allié"], 1]})
                player.permanent_buff["regis"] = 0
            if "lothraxion" in player.permanent_buff:
                carte.effects["bouclier divin"] = 1
        elif carte.name == "Automate astral":
            player.automates += 1
        elif carte.name == "Tentacule chaotique":
            player.tentacules += 1

        if carte.type == "Serviteur" and not "titan" in carte.effects:
            if "colossal" in carte.effects and not (carte.is_dead() or "rale_applied" in carte.effects):
                if carte in player.servants:
                    for i in range(carte.effects["colossal"][0]):
                        self.invoke_servant(get_card(carte.effects["colossal"][1], all_servants), player)
                else:
                    for i in range(carte.effects["colossal"][0]):
                        self.invoke_servant(get_card(carte.effects["colossal"][1], all_servants), adv)
            if "cri de guerre" in carte.effects and not (carte.is_dead() or "rale_applied" in carte.effects):
                if "play" in carte.effects["cri de guerre"] and carte.effects["cri de guerre"][2] != "":
                    if "aléatoire" in carte.effects["cri de guerre"][1]:
                        if "tentacule" in carte.effects["cri de guerre"][1]:
                            carte.effects["cri de guerre"][2] = [random.choice([x["name"] for x in all_spells if x["cost"] == min(10, player.tentacules)])]
                    elif "in_deck" in carte.effects["cri de guerre"][1]:
                        to_play = []
                        if "secret" in carte.effects["cri de guerre"][1]:
                            for _ in range(carte.effects["cri de guerre"][2]):
                                if [x for x in player.deck if "secret" in x.effects and x.name not in to_play]:
                                    secret = random.choice([x for x in player.deck if "secret" in x.effects and x.name not in to_play])
                                    to_play.append(secret.name)
                                    player.deck.remove(secret)
                        carte.effects["cri de guerre"][2] = to_play.copy()
                    for card in carte.effects["cri de guerre"][2]:
                        played_card = get_card(card, all_cards)
                        if len(player.servants) + len(player.lieux) < 7:
                            player.hand.add(played_card)
                            played_card.cost = 0
                            possible_targets = generate_targets(self.plt)[17 * (len(player.hand) - 1): 17 * len(player.hand) - 1]
                            player.hand.remove(played_card)
                            possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                            if possible_targets_refined:
                                target = random.choice(possible_targets_refined)
                                if target == 0:
                                    target = None
                                elif target == 1:
                                    target = player
                                elif target < 9:
                                    target = player.servants[target - 2]
                                elif target == 9:
                                    target = adv
                                else:
                                    target = adv.servants[target - 10]
                            if not ("ciblage" in played_card.effects and target is None):
                                TourEnCours(self.plt).apply_effects(played_card, target)
                elif "boost" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if type(target) == Card:
                            if "alive" in carte.effects["cri de guerre"][1]:
                                carte.effects["aura"] = ["boost", ["serviteur", "allié", "choisi", "alive", target],
                                                         [3, 0]]
                            else:
                                if "based_on_stats" in carte.effects["cri de guerre"][1]:
                                    target.boost(carte.attack, carte.health)
                                elif "atq_serv" in carte.effects["cri de guerre"][1]:
                                    target.boost(carte.attack, 0)
                                elif "fixed_stats" in carte.effects["cri de guerre"][1]:
                                    target.attack = carte.effects["cri de guerre"][2][0]
                                    target.base_attack = carte.effects["cri de guerre"][2][0]
                                    target.health = carte.effects["cri de guerre"][2][0]
                                    target.base_health = carte.effects["cri de guerre"][2][1]
                                    target.blessure = 0
                                else:
                                    target.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                    if "provocation" in carte.effects["cri de guerre"][1]:
                                        target.effects["provocation"] = 1
                                    if "bouclier divin" in carte.effects["cri de guerre"][1]:
                                        target.effects["bouclier divin"] = 1
                                    if "vol de vie" in carte.effects["cri de guerre"][1]:
                                        target.effects["vol de vie"] = 1
                                    if "ruée" in carte.effects["cri de guerre"][1]:
                                        target.effects["ruée"] = 1
                                    if "temp_turn" in carte.effects["cri de guerre"][1]:
                                        target.effects["temp_turn"] = [carte.effects["cri de guerre"][2][0],
                                                                       carte.effects["cri de guerre"][2][1]]
                                    if "insensible" in carte.effects["cri de guerre"][1]:
                                        target.effects["bouclier divin"] = 2
                                        target.effects["temp_turn_bonus"] = "bouclier divin"
                        elif type(target) == CardGroup:
                            for card in target:
                                if type(carte.effects["cri de guerre"][2]) == list:
                                    card.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                else:
                                    if carte.effects["cri de guerre"][2] == "double":
                                        card.attack *= 2
                                        card.base_attack *= 2
                                        card.health *= 2
                                        card.base_health *= 2
                                if "provocation" in carte.effects["cri de guerre"][1]:
                                    card.effects["provocation"] = 1
                                if "bouclier divin" in carte.effects["cri de guerre"][1]:
                                    card.effects["bouclier divin"] = 1
                    else:
                        if "self" in carte.effects["cri de guerre"][1]:
                            if carte.name == "Mousse de la voile sanglante" :
                                if player.weapon is not None:
                                    carte.boost(player.weapon.attack, 0)
                            elif "cout_last_card" in carte.effects["cri de guerre"][1] and player.last_card != "" and player.last_card.cost == carte.effects["cri de guerre"][1][2]:
                                carte.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                            elif "cards_in_hand" in carte.effects["cri de guerre"][1]:
                                carte.boost(0, len(player.hand))
                            elif "chaque type" in carte.effects["cri de guerre"][1]:
                                if player.genre_joues:
                                    boosts = random.sample(carte.effects["cri de guerre"][2], min(8, len(player.genre_joues)))
                                    for boost in boosts:
                                        carte.effects[boost] = 1
                            elif "paladin_hand" in carte.effects["cri de guerre"][1]:
                                boosts = random.sample(carte.effects["cri de guerre"][2], min(4, len([x for x in player.hand if x.classe == "Paladin"])))
                                for boost in boosts:
                                    carte.effects[boost] = 1
                            elif carte.name == "Oiseau libre":
                                carte.boost(player.oiseaux_libres, player.oiseaux_libres)
                                player.oiseaux_libres += 1
                            elif carte.name == "Golem terrestre":
                                carte.boost(player.etres_terrestres, player.etres_terrestres)
                                player.etres_terrestres += 1
                            elif "spend_cadavre" in carte.effects["cri de guerre"][1]:
                                if player.cadavres > carte.effects["cri de guerre"][1][-1]:
                                    player.cadavres -= carte.effects["cri de guerre"][1][-1]
                                    player.cadavres_spent += carte.effects["cri de guerre"][1][-1]
                                    carte.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                            elif "combo_played" in carte.effects["cri de guerre"][1]:
                                carte.boost(player.combo_played, player.combo_played)
                            elif "givre_spells" in carte.effects["cri de guerre"][1]:
                                carte.boost(len([x for x in player.hand if x.type == "Sort" and "Givre" in x.genre]), 0)
                            elif "dead_this_turn" in carte.effects["cri de guerre"][1]:
                                carte.boost(len(player.dead_this_turn) + len(adv.dead_this_turn), len(player.dead_this_turn) + len(adv.dead_this_turn))
                            elif "if_atq_sup4" in carte.effects["cri de guerre"][1]:
                                if [x.attack for x in player.servants if x != carte and not "en sommeil" in x.effects] \
                                    and max([x.attack for x in player.servants if x != carte and not "en sommeil" in x.effects]) >= 4:
                                    carte.boost(2, 2)
                            elif "if_sacré_inhand" in carte.effects["cri de guerre"][1]:
                                if [x for x in player.hand if "Sacré" in x.genre]:
                                    carte.effects["provocation"] = 1
                                    carte.effects["bouclier divin"] = 1
                            elif "if_méca_inhand" in carte.effects["cri de guerre"][1]:
                                if [x for x in player.hand if "Méca" in x.genre]:
                                    carte.effects["furie des vents"] = 1
                            elif "if_dragon_inhand" in carte.effects["cri de guerre"][1]:
                                if [x for x in player.hand if "Dragon" in x.genre]:
                                    carte.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                            elif "spells_this_turn" in carte.effects["cri de guerre"][1]:
                                carte.boost(player.spell_this_turn, player.spell_this_turn)
                            elif "if_ombre_hand" in carte.effects["cri de guerre"][1]:
                                if [x for x in player.hand if "Ombre" in x.genre]:
                                    carte.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                            else:
                                carte.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                if "provocation" in carte.effects["cri de guerre"][1]:
                                    carte.effects["provocation"] = 1
                                if "ruée" in carte.effects["cri de guerre"][1]:
                                    carte.effects["ruée"] = 1
                                if "charge" in carte.effects["cri de guerre"][1]:
                                    carte.effects["charge"] = 1
                        if "heros" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                            if carte.effects["cri de guerre"][2] == "inciblable" and "temp_turn" in \
                                    carte.effects["cri de guerre"][1]:
                                adv.effects["inciblable"] = [1, "temp_turn"]
                        if "serviteur" in carte.effects["cri de guerre"][1] and "allié" in carte.effects["cri de guerre"][1]:
                            if "tous" in carte.effects["cri de guerre"][1]:
                                if "Murloc" in carte.effects["cri de guerre"][1]:
                                    for serv in player.servants:
                                        if serv != carte and "Murloc" in serv.genre:
                                            serv.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                elif "Méca" in carte.effects["cri de guerre"][1]:
                                    if [x for x in player.servants if x != carte and "Méca" in x.genre]:
                                        for serv in [x for x in player.servants if x != carte and "Méca" in x.genre]:
                                            serv.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                            if "provocation" in carte.effects["cri de guerre"][2]:
                                                serv.effects["provocation"] = 1
                                            if "bouclier divin" in carte.effects["cri de guerre"][2]:
                                                serv.effects["bouclier divin"] = 1
                                else:
                                    for serv in player.servants:
                                        if serv != carte:
                                            serv.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                if "invocation" in carte.effects["cri de guerre"][1]:
                                    if "Treant taunt" in carte.effects["cri de guerre"][1]:
                                        for _ in range(2):
                                            self.invoke_servant(get_card("Treant taunt", all_servants), player)
                            elif "aléatoire" in carte.effects["cri de guerre"][1]:
                                if "Mort-vivant" in carte.effects["cri de guerre"][1]:
                                    target_boost = random.choice([x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre and x != carte]) \
                                        if len([x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre and x != carte]) != 0 else None
                                    if target_boost is not None:
                                        target_boost.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                                        if "provocation" in carte.effects["cri de guerre"][2]:
                                            target_boost.effects['provocation'] = 1
                                else:
                                    target_boost = random.choice([x for x in self.plt.players[0].servants if x != carte]) \
                                        if len([x for x in self.plt.players[0].servants if x != carte]) != 0 else None
                                    if target_boost is not None:
                                        target_boost.boost(carte.effects["cri de guerre"][2][0], carte.effects["cri de guerre"][2][1])
                            elif "next" in carte.effects["cri de guerre"][1]:
                                if "Bête" in carte.effects["cri de guerre"][1]:
                                    player.boost_next.append(["Bête", carte.effects["cri de guerre"][2]])
                            elif "tete d'hydrolodon" in carte.effects["cri de guerre"][1]:
                                if [x for x in player.servants if x.name == "Tete d'hydrolodon"]:
                                    for creature in [x for x in player.servants if x.name == "Tete d'hydrolodon"]:
                                        creature.effects["ruée"] = 1
                                        self.apply_effects(creature)
                elif "damage" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if "all_hero_attacks" in carte.effects["cri de guerre"][1]:
                            carte.effects["cri de guerre"][2] += player.total_attacks
                        target.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                        if "adjacent" in carte.effects["cri de guerre"][1]:
                            index_target = adv.servants.cards.index(target)
                            if index_target != 0:
                                cible_gauche = adv.servants[index_target - 1]
                                cible_gauche.damage(carte.effects["cri de guerre"][1][-1], toxic=True if "toxicite" in carte.effects else False)
                            try:
                                cible_droite = adv.servants[index_target + 1]
                                cible_droite.damage(carte.effects["cri de guerre"][1][-1], toxic=True if "toxicite" in carte.effects else False)
                            except:
                                pass
                        if "self_heros" in carte.effects["cri de guerre"][1]:
                            player.damage(carte.effects["cri de guerre"][2])
                    else:
                        if carte.effects["cri de guerre"][1][0] == "tous":
                            if "ennemi" in carte.effects["cri de guerre"][1]:
                                if "aléatoire" in carte.effects["cri de guerre"][1]:
                                    if "spend_cadavre" in carte.effects["cri de guerre"][1]:
                                        cadavres_spent = min(carte.effects["cri de guerre"][1][-1], player.cadavres)
                                        carte.effects["cri de guerre"][1][-1] = cadavres_spent
                                        player.cadavres -= cadavres_spent
                                        player.cadavres_spent += cadavres_spent
                                    for n in range(0, carte.effects["cri de guerre"][1][-1]):
                                        if [x for x in [adv] + adv.servants.cards if x.health > 0]:
                                            random_target = random.choice([x for x in [adv] + adv.servants.cards if x.health > 0])
                                            random_target.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                                            if "vol de vie" in carte.effects and not [x for x in adv.servants if "anti_heal" in x.effects]:
                                                player.heal(carte.effects["cri de guerre"][2])
                                else:
                                    if "conditional" in carte.effects["cri de guerre"][1]:
                                        if "heros_allié_attack" in carte.effects["cri de guerre"][1] and player.has_attacked > 0:
                                            for card in [adv] + adv.servants.cards:
                                                card.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                                    else:
                                        for card in [adv] + adv.servants.cards:
                                            card.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                            elif carte.effects["cri de guerre"][1][1] == "tous":
                                try:
                                    for n in range(0, carte.effects["cri de guerre"][1][3]):
                                        random_target = random.choice([adv] + [player] + player.servants.cards + adv.servants.cards)
                                        random_target.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                                except:
                                    pass
                        elif carte.effects["cri de guerre"][1][0] == "serviteur":
                            if "ennemi" in carte.effects["cri de guerre"][1]:
                                if len(adv.servants):
                                    if "nb_ecoles" in carte.effects["cri de guerre"][1]:
                                        carte.effects["cri de guerre"][2] += len(player.ecoles_jouees)
                                    for serv in adv.servants:
                                        serv.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                            else:
                                if len(player.servants) + len(adv.servants) > 1:
                                    for serv in [x for x in player.servants.cards + adv.servants.cards if x != carte]:
                                        serv.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                        elif carte.effects["cri de guerre"][1][0] == "self":
                            carte.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                        elif carte.effects["cri de guerre"][1][0] == "heros":
                            if "ennemi" in carte.effects["cri de guerre"][1]:
                                if "if_draw" in carte.effects["cri de guerre"][1] and "next_enemyturn" in carte.effects["cri de guerre"][1]:
                                    adv.effects["draw"] = ["damage", "temp_turn", 2]
                                elif "end_turn" in carte.effects["cri de guerre"][1]:
                                    player.effects["end_turn"] = ["damage", ["heros", "ennemi"], carte.effects["cri de guerre"][2]]
                            if "allié" in carte.effects["cri de guerre"][1]:
                                if "soifdemana_heal_7" in carte.effects["cri de guerre"][1] and player.mana_max >= 7:
                                    if "kvaldir" in player.permanent_buff:
                                        player.damage(carte.effects["cri de guerre"][2])
                                        player.permanent_buff.pop("kvaldir")
                                    else:
                                        player.heal(carte.effects["cri de guerre"][2])
                                else:
                                    player.damage(carte.effects["cri de guerre"][2])
                        elif carte.effects["cri de guerre"][1][0] == "buveuse de vie":
                            adv.damage(3)
                            if not [x for x in adv.servants if "anti_heal" in x.effects]:
                                if "kvaldir" in player.permanent_buff:
                                    player.damage(3)
                                    player.permanent_buff.pop("kvaldir")
                                else:
                                    player.heal(3)
                elif "camouflage" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if type(target) == Card:
                            if "alive" in carte.effects["cri de guerre"][1]:
                                carte.effects["aura"] = ["boost", ["serviteur", "tous", "choisi", "alive", target],
                                                         "camouflage"]
                elif "gel" in carte.effects["cri de guerre"] :
                    if target is not None:
                        if type(target) == Card:
                            target.effects["gel"] = carte.effects["cri de guerre"][2]
                        else:
                            target.gel = carte.effects["cri de guerre"][2]
                    else:
                        if "tous" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                            target = random.sample([x for x in [adv] + adv.servants.cards], min(len([x for x in [adv] + adv.servants.cards]), carte.effects["cri de guerre"][2]))
                            if target:
                                for creature in target:
                                    creature.effects["gel"] = 1
                elif "vol de vie" in carte.effects["cri de guerre"]:
                    if "self" in carte.effects["cri de guerre"][1]:
                        carte.effects['vol de vie'] = 1
                elif "attack" in carte.effects["cri de guerre"]:
                    if "self" in carte.effects["cri de guerre"][1]:
                        if "serviteur" in carte.effects["cri de guerre"][2] and "ennemi" in carte.effects["cri de guerre"][2] and "tous" in carte.effects["cri de guerre"][2]:
                            for serv in adv.servants:
                                if not carte.is_dead():
                                    self.attaquer(serv, carte)
                elif "hero_attack" in carte.effects["cri de guerre"]:
                    player.inter_attack += carte.effects["cri de guerre"][1]
                elif "suicide" in carte.effects["cri de guerre"]:
                    if "remove" in carte.effects["cri de guerre"][1]:
                        player.servants.remove(carte)
                    else:
                        carte.blessure = 1000
                elif "destroy" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if target.type == "Serviteur":
                            target.blessure = 1000
                        elif target.type == "Lieu":
                            target.health = 0
                    else:
                        if "serviteur" in carte.effects["cri de guerre"][1]:
                            if "tous" in carte.effects["cri de guerre"][1]:
                                for entity in [x for x in player.servants if x != carte]:
                                    if "gain_cadavre" in carte.effects["cri de guerre"][1]:
                                        player.cadavres += 1
                                    entity.blessure = 1000
                                for entity in adv.servants:
                                    if "gain_cadavre" in carte.effects["cri de guerre"][1]:
                                        player.cadavres += 1
                                    entity.blessure = 1000
                            elif "ennemi" in carte.effects["cri de guerre"][1] and "aléatoire" in carte.effects["cri de guerre"][1]:
                                if adv.servants:
                                    target = random.choice(adv.servants.cards)
                                    target.blessure = 1000
                                if "main" in carte.effects["cri de guerre"][1]:
                                    if [x for x in adv.hand if x.type == "Serviteur"]:
                                        target = random.choice([x for x in adv.hand if x.type == "Serviteur"])
                                        adv.hand.remove(target)
                                if "deck" in carte.effects["cri de guerre"][1]:
                                    if [x for x in adv.deck if x.type == "Serviteur"]:
                                        target = random.choice([x for x in adv.deck if x.type == "Serviteur"])
                                        adv.deck.remove(target)
                            if "defausse" in carte.effects["cri de guerre"]:
                                count = len(adv.servants) + len(player.servants) - 1
                                for i in range(min(count, len(player.hand))):
                                    card_to_defausse = random.choice(player.hand)
                                    player.hand.remove(card_to_defausse)
                    if "arme" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                        adv.weapon = None
                elif "take_control" in carte.effects["cri de guerre"]:
                    if target is not None:
                        invoked_servant = get_card(target.name, all_servants)
                        invoked_servant.attack, invoked_servant.base_attack = target.attack, target.base_attack
                        invoked_servant.health, invoked_servant.base_health = target.health, target.base_health
                        invoked_servant.blessure = target.blessure
                        invoked_servant.effects = target.effects.copy()
                        self.invoke_servant(invoked_servant, player)
                        target.blessure = 1000
                elif "destroy+boost" in carte.effects["cri de guerre"]:
                    if "tous" in carte.effects["cri de guerre"][1] and "ennemi" in carte.effects["cri de guerre"][1]:
                        if "secret" in carte.effects["cri de guerre"][1]:
                            if adv.secrets.cards:
                                carte.boost(len(adv.secrets.cards), len(adv.secrets.cards))
                                adv.secrets.cards = []
                    elif "serviteur" in carte.effects["cri de guerre"][1]:
                        if "ennemi" in carte.effects["cri de guerre"][1] and target is not None:
                            if carte.effects["cri de guerre"][2] == "caracs":
                                if type(target) == CardGroup:
                                    for card in target:
                                        card.blessure = 1000
                                        carte.boost(card.attack, card.health)
                                else:
                                    target.blessure = 1000
                                    carte.boost(target.attack, target.health)
                        elif "allié" in carte.effects["cri de guerre"][1] and target is not None:
                            if carte.effects["cri de guerre"][2] == "servs_atq":
                                for servant in player.servants.cards:
                                    if servant != target:
                                        servant.boost(target.attack, 0)
                                target.blessure = 1000
                elif "poof" in carte.effects["cri de guerre"]:
                    player.poofed = [[x for x in player.servants if x != carte].copy(), 2]
                    adv.poofed = [[x for x in adv.servants].copy(), 2]
                    for serv in player.poofed[0]:
                        player.servants.remove(serv)
                    for serv in adv.poofed[0]:
                        adv.servants.remove(serv)
                elif "return_deck" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if target in adv.servants:
                            adv.servants.remove(target)
                            adv.deck.add(target)
                elif "reincarnation" in carte.effects["cri de guerre"] and target is not None:
                    target.effects["reincarnation"] = carte.effects["cri de guerre"][2]
                elif carte.effects["cri de guerre"] == "Sir Finley":
                    if len(player.hand) != 0:
                        player.deck.cards += player.hand.cards.copy()
                        new_hand = player.deck.cards[0:len(player.hand)].copy()
                        player.hand.cards = new_hand.copy()
                        player.deck.cards = player.deck.cards[len(player.hand):].copy()
                elif "add_durability" in carte.effects["cri de guerre"] and player.weapon is not None:
                    player.weapon.health += carte.effects["cri de guerre"]
                elif "equip_weapon" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1]:
                        player.weapon = get_card(carte.effects["cri de guerre"][2], all_weapons)
                        if "cartes_played" in carte.effects["cri de guerre"][1]:
                            player.weapon.attack += len(player.cards_this_turn) - 1
                    if "ennemi" in carte.effects["cri de guerre"][1]:
                        adv.weapon = get_card(carte.effects["cri de guerre"][1][-1], all_weapons)
                elif "add_armor" in carte.effects["cri de guerre"]:
                    if "tous" in carte.effects["cri de guerre"][1]:
                        adv.armor += carte.effects["cri de guerre"][2]
                    player.armor += carte.effects["cri de guerre"][2]
                    if "cost_armor" in carte.effects["cri de guerre"][1]:
                        player.effects["cost_armor"] = 3
                elif "cout_hp" in carte.effects["cri de guerre"]:
                    player.cout_pouvoir_temp = 0
                elif "reinit_hp" in carte.effects["cri de guerre"]:
                    if not player.dispo_pouvoir:
                        player.dispo_pouvoir = True
                elif "reduc" in carte.effects["cri de guerre"]:
                    if "prochain" in carte.effects["cri de guerre"][1]:
                        player.discount_next.append([carte.effects["cri de guerre"][1][0], carte.effects["cri de guerre"][1][3],
                         carte.effects["cri de guerre"][2], carte.effects["cri de guerre"][1][2]])
                        if "destroy_next_rale" in carte.effects["cri de guerre"][1]:
                            player.permanent_buff["destroy_next_rale"] = 1
                    if "left_card" in carte.effects["cri de guerre"][1] and player.hand.cards:
                        player.hand.cards[0].base_cost = max(0, player.hand.cards[0].base_cost - 1)
                    if "right_card" in carte.effects["cri de guerre"][1] and player.hand.cards:
                        player.hand.cards[-1].base_cost = max(0, player.hand.cards[-1].base_cost - 1)
                    if "main" in carte.effects["cri de guerre"][1]:
                        if "allié" in carte.effects["cri de guerre"][1]:
                            if "sort" in carte.effects["cri de guerre"][1] and [x for x in player.hand if x.type == "Sort"]:
                                for spell in [x for x in player.hand if x.type == "Sort"]:
                                    if "milouse" in carte.effects["cri de guerre"][1]:
                                        spell.cost = 0
                                        spell.base_cost = 0
                                        spell.effects["milouse"] = 1
                                    else:
                                        spell.cost = max(0, spell.cost - carte.effects["cri de guerre"][2])
                                        spell.base_cost = max(0, spell.base_cost - carte.effects["cri de guerre"][2])
                            elif "copied_cards" in carte.effects["cri de guerre"][1] and [x for x in player.hand if "copied" in x.effects]:
                                for card in [x for x in player.hand if "copied" in x.effects]:
                                    card.cost = max(0, card.cost - carte.effects["cri de guerre"][2])
                                    card.base_cost = max(0, card.base_cost - carte.effects["cri de guerre"][2])
                    elif "deck" in carte.effects["cri de guerre"][1]:
                        if "if_rale_agonie" in carte.effects["cri de guerre"][1] and [x for x in player.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]:
                            for creature in [x for x in player.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]:
                                creature.cost = max(0, creature.cost + carte.effects["cri de guerre"][2])
                                creature.base_cost = max(0, creature.base_cost + carte.effects["cri de guerre"][2])
                elif "augment" in carte.effects["cri de guerre"]:
                    if "ennemi" in carte.effects["cri de guerre"][1] and "temp_fullturn" in \
                            carte.effects["cri de guerre"][1]:
                        adv.augment.append([carte.effects["cri de guerre"][1][0], carte.effects["cri de guerre"][1][1],
                                            carte.effects["cri de guerre"][2]])
                elif "spell_damage" in carte.effects["cri de guerre"]:
                    if "main" in carte.effects["cri de guerre"][1] and "allié" in carte.effects["cri de guerre"][1]:
                        if "if_arcanes" in carte.effects["cri de guerre"][1] and [x for x in player.hand if x.type == "Sort" and "Arcanes" in x.genre]:
                            for spell in [x for x in player.hand if x.type == "Sort" and "Arcanes" in x.genre]:
                                if type(spell.effects["damage"]) == int:
                                    spell.effects["damage"] += 1
                                elif type(spell.effects["damage"]) == list:
                                    spell.effects["damage"][-1] += 1
                            if "deck" in carte.effects["cri de guerre"][1]:
                                for spell in [x for x in player.deck if x.type == "Sort" and "Arcanes" in x.genre]:
                                    if type(spell.effects["damage"]) == int:
                                        spell.effects["damage"] += 1
                                    elif type(spell.effects["damage"]) == list:
                                        spell.effects["damage"][-1] += 1
                elif "heal" in carte.effects["cri de guerre"]:
                    if target is not None and not [x for x in adv.servants if "anti_heal" in x.effects]:
                        if "kvaldir" in player.permanent_buff:
                            target.damage(carte.effects["cri de guerre"][2])
                            player.permanent_buff.pop("kvaldir")
                        else:
                            target.heal(carte.effects["cri de guerre"][2])
                    else:
                        if "serviteur" in carte.effects["cri de guerre"][1]:
                            if "tous" in carte.effects["cri de guerre"][1]:
                                if "allié" in carte.effects["cri de guerre"][1] and not [x for x in adv.servants if "anti_heal" in x.effects]:
                                    if "kvaldir" in player.permanent_buff:
                                        for entity in player.servants.cards:
                                            entity.damage(carte.effects["cri de guerre"][2])
                                        player.permanent_buff.pop("kvaldir")
                                    else:
                                        for entity in player.servants.cards:
                                            entity.heal(carte.effects["cri de guerre"][2])
                                    if "boost_if_surplus" in carte.effects["cri de guerre"][1] and [x for x in player.servants if x.surplus > 0 and x != carte]:
                                        carte.boost(len([x for x in player.servants if x.surplus > 0 and x != carte]), len([x for x in player.servants if x.surplus > 0 and x != carte]))
                        elif "tous" in carte.effects["cri de guerre"][1]:
                            if "allié" in carte.effects["cri de guerre"][1] and not [x for x in adv.servants if "anti_heal" in x.effects]:
                                if "kvaldir" in player.permanent_buff:
                                    for entity in [player] + player.servants.cards:
                                        entity.damage(carte.effects["cri de guerre"][2])
                                    player.permanent_buff.pop("kvaldir")
                                else:
                                    for entity in [player] + player.servants.cards:
                                        entity.heal(carte.effects["cri de guerre"][2])
                    if "suicide" in carte.effects["cri de guerre"][1]:
                        player.servants.remove(carte)
                elif "heal+pioche" in carte.effects["cri de guerre"]:
                    if target is not None and not [x for x in adv.servants if "anti_heal" in x.effects]:
                        if "kvaldir" in player.permanent_buff:
                            target.damage(carte.effects["cri de guerre"][2])
                            player.permanent_buff.pop("kvaldir")
                        else:
                            target.heal(carte.effects["cri de guerre"][2])
                    player.pick_multi(carte.effects["cri de guerre"][3])
                elif "alextrasza" in carte.effects["cri de guerre"] and target is not None:
                    if target in [adv] + adv.servants.cards:
                        target.damage(carte.effects["cri de guerre"][2], toxic=True if "toxicite" in carte.effects else False)
                    else:
                        if not [x for x in adv.servants if "anti_heal" in x.effects]:
                            if "kvaldir" in player.permanent_buff:
                                target.damage(carte.effects["cri de guerre"][2])
                                player.permanent_buff.pop("kvaldir")
                            else:
                                target.heal(carte.effects["cri de guerre"][2])
                elif "ne peut pas attaquer" in carte.effects["cri de guerre"] and target is not None:
                    if target is not None:
                        if type(target) == Card:
                            if "alive" in carte.effects["cri de guerre"][1]:
                                carte.effects["aura"] = ["boost", ["serviteur", "tous", "choisi", "alive", target],
                                                         "ne peut pas attaquer"]
                elif "silence" in carte.effects["cri de guerre"]:
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
                elif "swap" in carte.effects["cri de guerre"] and target is not None:
                    inter_health = target.health
                    target.health = target.attack
                    target.base_health = target.attack
                    target.attack = inter_health
                elif "swap_spell" in carte.effects["cri de guerre"]:
                    if "sort" in carte.effects["cri de guerre"][1] and "hands" in carte.effects["cri de guerre"][1]:
                        if [x for x in player.hand if x.type == "Sort"] and [x for x in adv.hand if x.type == "Sort"]:
                            sort1 = random.choice([x for x in player.hand if x.type == "Sort"])
                            sort2 = random.choice([x for x in adv.hand if x.type == "Sort"])
                            inter_cost = sort1.cost
                            sort1.cost = sort2.cost
                            sort2.cost = inter_cost
                elif "echange" in carte.effects["cri de guerre"]:
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
                                if adv.deck.cards:
                                    swapped_card = random.choice(adv.deck.cards)
                                    player.servants.remove(carte)
                                    adv.deck.add(carte)
                                    adv.deck.shuffle()
                                    player.servants.add(swapped_card)
                elif "mana_final" in carte.effects["cri de guerre"]:
                    player.mana_final = carte.effects["cri de guerre"][2]
                elif "mana_steal" in carte.effects["cri de guerre"]:
                    player.mana_max = min(player.mana_final, player.mana_max + carte.effects["cri de guerre"][-1])
                    adv.mana_max -= carte.effects["cri de guerre"][-1]
                elif "add_mana" in carte.effects["cri de guerre"]:
                    if "highest_spell" in carte.effects["cri de guerre"][1] and [x for x in player.hand if x.type == "Sort"]:
                        carte.effects["cri de guerre"][-1] = max([x.cost for x in player.hand if x.type == "Sort"])
                    player.mana = min(player.mana_max, player.mana + carte.effects["cri de guerre"][-1])
                elif "refresh_mana" in carte.effects["cri de guerre"]:
                    if "spells_this_turn" in carte.effects["cri de guerre"][1]:
                        player.mana = min(player.mana_max, player.mana + player.spell_this_turn)
                elif "add_hand" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1]:
                        if target is not None:
                            if carte.effects["cri de guerre"][2] == "copy":
                                player.hand.add(get_card(target.name, all_servants))
                            else:
                                player.hand.add(get_card(carte.effects["cri de guerre"][2], all_servants))
                        else:
                            if carte.effects["cri de guerre"][2] == "several":
                                if "left_right" in carte.effects["cri de guerre"][1] and "reduc" in carte.effects["cri de guerre"][1]:
                                    if len(player.hand) < 10:
                                        while True:
                                            card1 = random.choice(all_cards)
                                            if "marginal" in card1["effects"]:
                                                break
                                        card1 = Card(**card1)
                                        card1.base_cost = max(0, card1.base_cost - 2)
                                        player.hand.cards.insert(0, card1)
                                        if len(player.hand) < 10:
                                            while True:
                                                card2 = random.choice(all_cards)
                                                if "marginal" in card2["effects"]:
                                                    break
                                            card2 = Card(**card2)
                                            card2.base_cost = max(0, card2.base_cost - 2)
                                            player.hand.add(card2)
                            else:
                                if type(carte.effects["cri de guerre"][2]) == list:
                                    if "serviteur" in carte.effects["cri de guerre"][1]:
                                        if "Méca" in carte.effects["cri de guerre"][1]:
                                            for _ in range(carte.effects["cri de guerre"][1][-1]):
                                                carte.effects["cri de guerre"][2].append(random.choice([x["name"] for x in all_servants if x["decouvrable"] == 1 and "Méca" in x["genre"]]))
                                    elif "sort" in carte.effects["cri de guerre"][1]:
                                        if "feu" in carte.effects["cri de guerre"][1]:
                                            if "mage" in carte.effects["cri de guerre"][1]:
                                                for _ in range(carte.effects["cri de guerre"][1][-1]):
                                                    carte.effects["cri de guerre"][2].append(random.choice([x["name"] for x in all_spells if x["decouvrable"] == 1 and "Feu" in x["genre"] and x["classe"] == "Mage"]))
                                            if "démoniste" in carte.effects["cri de guerre"][1]:
                                                for _ in range(carte.effects["cri de guerre"][1][-1]):
                                                    if [x["name"] for x in all_spells if x["decouvrable"] == 1 and "Feu" in x["genre"] and x["classe"] == "Démoniste"]:
                                                        carte.effects["cri de guerre"][2].append(random.choice([x["name"] for x in all_spells if x["decouvrable"] == 1 and "Feu" in x["genre"] and x["classe"] == "Démoniste"]))
                                        elif "givre" in carte.effects["cri de guerre"][1]:
                                            for _ in range(carte.effects["cri de guerre"][1][-1]):
                                                carte.effects["cri de guerre"][2].append(random.choice([x["name"] for x in all_spells if x["decouvrable"] == 1 and "Givre" in x["genre"]]))
                                        elif "secret" in carte.effects["cri de guerre"][1] and "mage" in carte.effects["cri de guerre"][1]:
                                            for _ in range(carte.effects["cri de guerre"][1][-1]):
                                                carte.effects["cri de guerre"][2].append(random.choice([x["name"] for x in all_spells if x["decouvrable"] == 1 and "secret" in x["effects"] and x["classe"] == "Mage"]))
                                    if "conditional" in carte.effects["cri de guerre"][1]:
                                        if "if_pur" and [x for x in player.deck if x.classe == "Neutre"]:
                                            carte.effects["cri de guerre"][2] = []
                                    for card_to_add in carte.effects["cri de guerre"][2]:
                                        player.hand.add(get_card(card_to_add, all_cards))
                                else:
                                    card_to_draw = None
                                    if "serviteur" in carte.effects["cri de guerre"][1]:
                                        if "Bête" in carte.effects["cri de guerre"][1]:
                                            while True:
                                                card_to_draw = random.choice(all_servants)
                                                if "Bête" in card_to_draw["genre"] and card_to_draw["decouvrable"] == 1:
                                                    break
                                            card_to_draw = Card(**card_to_draw)
                                    elif "sort" in carte.effects["cri de guerre"][1]:
                                        if "Mage" in carte.effects["cri de guerre"][1]:
                                            while True:
                                                card_to_draw = random.choice(all_spells)
                                                if card_to_draw["classe"] == "Mage" and card_to_draw["decouvrable"] == 1:
                                                    break
                                            card_to_draw = Card(**card_to_draw)
                                    elif "copy" in carte.effects["cri de guerre"][1]:
                                        if "from_adv_deck" in carte.effects["cri de guerre"][1]:
                                            if adv.deck.cards:
                                                card_to_draw = copy_card(random.choice([x for x in adv.deck]))
                                                card_to_draw.effects["copied"] = 1
                                            else:
                                                card_to_draw = None
                                        elif "topdeck_adv" in carte.effects["cri de guerre"][1]:
                                            if adv.deck.cards:
                                                card_to_draw = copy_card(adv.deck.cards[0])
                                        elif "from_adv_hand" in carte.effects["cri de guerre"][1]:
                                            if adv.hand.cards:
                                                card_to_draw = copy_card(random.choice([x for x in adv.hand]))
                                                card_to_draw.effects["copied"] = 1
                                            else:
                                                card_to_draw = None
                                    elif "decoction" in carte.effects["cri de guerre"][1]:
                                        while True:
                                            card_to_draw = random.choice(all_spells)
                                            if "decoction" in card_to_draw["effects"]:
                                                break
                                        card_to_draw = Card(**card_to_draw)
                                    elif "combo" in carte.effects["cri de guerre"][1]:
                                        while True:
                                            card_to_draw = random.choice(all_spells)
                                            if "combo" in card_to_draw["effects"] and card_to_draw["decouvrable"] == 1 and card_to_draw["name"] != carte.name:
                                                break
                                        card_to_draw = Card(**card_to_draw)
                                    elif "other_class" in carte.effects["cri de guerre"][1]:
                                        while True:
                                            card_to_draw = random.choice(all_cards)
                                            if card_to_draw["decouvrable"] == 1 and card_to_draw["classe"] not in [carte.classe,"Neutre"]:
                                                break
                                        card_to_draw = Card(**card_to_draw)
                                    else:
                                        card_to_draw = get_card(carte.effects["cri de guerre"][2], all_cards)
                                    if card_to_draw is None:
                                        print(carte, carte.effects, target)
                                        raise TypeError
                                    if card_to_draw is not None:
                                        player.hand.add(card_to_draw)
                                    if "porteur d'invitation" in [x.effects for x in player.servants] and get_card(carte.effects["cri de guerre"][2],
                                                                           all_cards).classe not in ["Neutre", player.classe]:
                                        player.hand.add(card_to_draw)
                    elif "ennemi" in carte.effects["cri de guerre"][1]:
                        if type(carte.effects["cri de guerre"][2]) == list:
                            for card in carte.effects["cri de guerre"][2]:
                                adv.hand.add(get_card(card, all_cards))
                        else:
                            if "until_full" in carte.effects["cri de guerre"][1]:
                                if len(adv.hand) < 10:
                                    for _ in range(10 - len(adv.hand)):
                                        adv.hand.add(get_card(carte.effects["cri de guerre"][2], all_cards))
                            else:
                                adv.hand.add(get_card(carte.effects["cri de guerre"][2], all_cards))
                elif "spell_transformation" in carte.effects["cri de guerre"] and [x for x in player.hand if x.type == "Sort"]:
                    if "addcost_2" in carte.effects["cri de guerre"][1]:
                        for spell in [x for x in player.hand if x.type == "Sort"]:
                            index_spell = player.hand.cards.index(spell)
                            while True:
                                new_spell = random.choice(all_spells)
                                if new_spell["decouvrable"] == 1 and new_spell["cost"] == min(10, player.hand.cards[index_spell].cost + 2):
                                    break
                            new_spell = Card(**new_spell)
                            new_spell.cost -= 2
                            new_spell.base_cost -= 2
                            player.hand.cards[index_spell] = new_spell
                elif "add_deck" in carte.effects["cri de guerre"]:
                    if "end_deck" in carte.effects["cri de guerre"]:
                        if "colossal" in carte.effects["cri de guerre"][1]:
                            cards_to_add = []
                            while len(cards_to_add) < 3:
                                card_to_add = random.choice(all_servants)
                                if "colossal" in card_to_add["effects"] and card_to_add not in cards_to_add:
                                    cards_to_add.append(Card(**card_to_add))
                            for card_to_add in cards_to_add:
                                player.deck.add(card_to_add)
                        else:
                            for card in carte.effects["cri de guerre"][2]:
                                player.deck.add(get_card(card, all_cards))
                    else:
                        for card in carte.effects["cri de guerre"][2]:
                            card_to_add = get_card(card, all_cards)
                            if card_to_add.name == "Instantane de Feplouf":
                                card_to_add.effects["add_hand"] = [get_card(x.name, all_cards) for x in player.hand]
                            player.deck.add(card_to_add)
                            player.deck.shuffle()
                elif "sap" in carte.effects["cri de guerre"]:
                    if target in player.servants:
                        player.servants.remove(target)
                        player.hand.add(get_card(target.name, all_servants))
                    elif target in adv.servants:
                        adv.servants.remove(target)
                        adv.hand.add(get_card(target.name, all_servants))
                elif "defausse" in carte.effects["cri de guerre"]:
                    if "all_hand" in carte.effects["cri de guerre"][1]:
                        player.hand = CardGroup()
                elif "pioche" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1]:
                        if "conditional" in carte.effects["cri de guerre"][1]:
                            if "if_weapon_hand" in carte.effects["cri de guerre"][1] and [x for x in player.hand if x.type == "Arme"]:
                                player.pick_multi(carte.effects["cri de guerre"][2])
                            elif "if_spell" in carte.effects["cri de guerre"][1]:
                                if "Naga" in carte.effects["cri de guerre"][1] and carte.effects["cri de guerre"][2] != 0:
                                    drawable_cards = [x for x in player.deck if x.type == "Serviteur" and "Naga" in x.genre]
                                    if drawable_cards:
                                        card_drawn = random.choice(drawable_cards)
                                        player.deck.remove(card_drawn)
                                        player.hand.add(card_drawn)
                            elif "if_alone" in carte.effects["cri de guerre"][1] and len(player.servants) == 1:
                                if [x for x in player.deck if x.type == "Sort"]:
                                    card_to_draw1 = random.choice([x for x in player.deck if x.type == "Sort"])
                                    player.deck.remove(card_to_draw1)
                                    player.hand.add(card_to_draw1)
                                if [x for x in player.deck if x.type == "Serviteur"]:
                                    card_to_draw2 = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                    player.deck.remove(card_to_draw2)
                                    player.hand.add(card_to_draw2)
                                if [x for x in player.deck if x.type == "Arme"]:
                                    card_to_draw3 = random.choice([x for x in player.deck if x.type == "Arme"])
                                    player.deck.remove(card_to_draw3)
                                    player.hand.add(card_to_draw3)
                            elif "if_pur" in carte.effects["cri de guerre"][1] and len([x for x in player.deck if x.classe == "Neutre"]) == 0:
                                if "chaque_type" in carte.effects["cri de guerre"][1]:
                                    potential_boost = [x for x in player.deck if x.genre].copy()
                                    for genre in all_genre_servants:
                                        if [x for x in potential_boost if genre in x.genre]:
                                            boosted_servant = [x for x in potential_boost if genre in x.genre]
                                            boosted_servant = boosted_servant[
                                                np.array([len(x.genre) for x in boosted_servant]).argsort()[0]]
                                            player.hand.add(boosted_servant)
                                            player.deck.remove(boosted_servant)
                                            potential_boost.remove(boosted_servant)
                        else:
                            if "arme" in carte.effects["cri de guerre"][1]:
                                drawable_cards = [x for x in player.deck if x.type == "Arme"]
                                if drawable_cards:
                                    card_drawn = random.choice(drawable_cards)
                                    player.deck.remove(card_drawn)
                                    player.hand.add(card_drawn)
                            elif "Murloc" in carte.effects["cri de guerre"][1]:
                                drawable_cards = [x for x in player.deck if x.type == "Serviteur" and "Murloc" in x.genre]
                                if drawable_cards:
                                    for i in range(min(carte.effects["cri de guerre"][2], len(drawable_cards))):
                                        card_drawn = random.choice(drawable_cards)
                                        drawable_cards.remove(card_drawn)
                                        player.deck.remove(card_drawn)
                                        player.hand.add(card_drawn)
                            elif "Bête" in carte.effects["cri de guerre"][1]:
                                drawable_cards = [x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]
                                if drawable_cards:
                                    for i in range(min(carte.effects["cri de guerre"][2], len(drawable_cards))):
                                        card_drawn = random.choice(drawable_cards)
                                        drawable_cards.remove(card_drawn)
                                        player.deck.remove(card_drawn)
                                        player.hand.add(card_drawn)
                            elif "give_spells" in carte.effects["cri de guerre"][1]:
                                for i in range(0, carte.effects["cri de guerre"][2]):
                                    player.pick()
                                    if player.hand.cards[-1].type == "Sort":
                                        adv.hand.add(player.hand.cards[-1])
                                        player.hand.remove(player.hand.cards[-1])
                            elif "sort" in carte.effects["cri de guerre"][1]:
                                if "until_full" in carte.effects["cri de guerre"][1]:
                                    while len(player.hand) < 10:
                                        try:
                                            spell_to_draw = random.choice([x for x in player.deck if x.type == "Sort"])
                                            player.deck.remove(spell_to_draw)
                                            player.hand.add(spell_to_draw)
                                        except:
                                            break
                                elif "Nature" in carte.effects["cri de guerre"][1]:
                                    if [x for x in player.deck if x.type == "Sort" and "Nature" in x.genre]:
                                        card_to_draw = random.choice([x for x in player.deck if x.type == "Sort" and "Nature" in x.genre])
                                        player.deck.remove(card_to_draw)
                                        player.hand.add(card_to_draw)
                                    if "mana_growth" in carte.effects["cri de guerre"][1]:
                                        player.mana_max = min(player.mana_final, player.mana_max + 1)
                                elif "secret" in carte.effects["cri de guerre"][1]:
                                    if [x for x in player.deck if x.type == "Sort" and "secret" in x.effects]:
                                        card_to_draw = random.choice([x for x in player.deck if x.type == "Sort" and "secret" in x.effects])
                                        player.deck.remove(card_to_draw)
                                        player.hand.add(card_to_draw)
                                elif "cost_1" in carte.effects["cri de guerre"][1]:
                                    if [x for x in player.deck if x.type == "Sort" and x.cost == 1]:
                                        card_to_draw = random.choice([x for x in player.deck if x.type == "Sort" and x.cost == 1])
                                        player.deck.remove(card_to_draw)
                                        player.hand.add(card_to_draw)
                                else:
                                    for _ in range(carte.effects["cri de guerre"][2]):
                                        if [x for x in player.deck if x.type == "Sort"]:
                                            spell_to_draw = random.choice([x for x in player.deck if x.type == "Sort"])
                                            player.deck.remove(spell_to_draw)
                                            player.hand.add(spell_to_draw)
                            elif "serviteur" in carte.effects["cri de guerre"][1]:
                                for _ in range(carte.effects["cri de guerre"][2]):
                                    if [x for x in player.deck if x.type == "Serviteur"]:
                                        serv_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                        player.deck.remove(serv_to_draw)
                                        player.hand.add(serv_to_draw)
                            elif "until_5" in carte.effects["cri de guerre"][1] and len(player.hand) < 5:
                                player.pick_multi(5 - len(player.hand))
                            elif "card_sup6" in carte.effects["cri de guerre"][1]:
                                for _ in range(carte.effects["cri de guerre"][2]):
                                    if [x for x in player.deck if x.cost >= 6]:
                                        card_to_draw = random.choice([x for x in player.deck if x.cost >= 6])
                                        player.deck.remove(card_to_draw)
                                        player.hand.add(card_to_draw)
                                        if "reduc" in carte.effects["cri de guerre"][1]:
                                            card_to_draw.base_cost -= 1
                            elif "rale d'agonie" in carte.effects["cri de guerre"][1]:
                                if [x for x in player.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]:
                                    card_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects])
                                    player.deck.remove(card_to_draw)
                                    player.hand.add(card_to_draw)
                                    if "gain_rale" in carte.effects["cri de guerre"][1]:
                                        carte.effects["rale d'agonie"] = card_to_draw.effects["rale d'agonie"]
                            elif "nb_elem_prec" in carte.effects["cri de guerre"][1]:
                                carte.effects["cri de guerre"][2] += player.elem_before
                                player.pick_multi(carte.effects["cri de guerre"][2])
                            else:
                                player.pick_multi(carte.effects["cri de guerre"][2])
                    if "ennemi" in carte.effects["cri de guerre"][1]:
                        if "until_5" in carte.effects["cri de guerre"][1] and len(adv.hand) < 5:
                            adv.pick_multi(5 - len(adv.hand))
                elif "pioche+decouverte" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1]:
                        if "serviteur" in carte.effects["cri de guerre"][1] and "Bête" in carte.effects["cri de guerre"][1]:
                            drawable_cards = [x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]
                            if drawable_cards:
                                for i in range(min(carte.effects["cri de guerre"][2], len(drawable_cards))):
                                    card_drawn = random.choice(drawable_cards)
                                    drawable_cards.remove(card_drawn)
                                    player.deck.remove(card_drawn)
                                    player.hand.add(card_drawn)
                            self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Bête"])
                elif "dragage" in carte.effects["cri de guerre"]:
                    if "ennemi" in carte.effects["cri de guerre"][1]:
                        self.plt.cards_dragage = [CardGroup(adv.deck.cards[-3:].copy())]
                    else:
                        self.plt.cards_dragage = [CardGroup(player.deck.cards[-3:].copy())]
                    if "reduc_cost" in carte.effects["cri de guerre"][1]:
                        for card in self.plt.cards_dragage[0]:
                            card.cost -= carte.effects["cri de guerre"][1][1]
                            card.base_cost -= carte.effects["cri de guerre"][1][1]
                elif "entrave" in carte.effects["cri de guerre"]:
                    self.plt.cards_entrave = [CardGroup(random.sample(adv.hand.cards, min(3, len(adv.hand.cards))))]
                elif "curse" in carte.effects["cri de guerre"]:
                    if "ennemi" in carte.effects["cri de guerre"][1]:
                        adv.curses[carte.effects["cri de guerre"][2]] = 1
                elif "institutrice" in carte.effects["cri de guerre"]:
                    player.hand.add(get_card("Jeune naga", all_servants))
                    self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="institutrice")
                elif "Okani" in carte.effects["cri de guerre"]:
                    self.plt.cards_chosen = self.choice_decouverte(carte, other="Okani")
                elif "nettoyeur a vapeur" in carte.effects["cri de guerre"]:
                    for card in player.deck:
                        if card.id not in [x.id for x in player.initial_deck]:
                            player.deck.remove(card)
                    for card in adv.deck:
                        if card.id not in [x.id for x in adv.initial_deck]:
                            adv.deck.remove(card)
                elif "geolier" in carte.effects["cri de guerre"]:
                    player.deck = CardGroup()
                    player.geolier = 1
                elif "cadavre" in carte.effects["cri de guerre"]:
                    if "destroy_serv" in carte.effects["cri de guerre"][1]:
                        if "deck" in carte.effects["cri de guerre"][1] and "allié" in carte.effects["cri de guerre"][1] and [x for x in player.deck if x.type == "Serviteur"]:
                            player.deck.remove(random.choice([x for x in player.deck if x.type == "Serviteur"]))
                            player.cadavres += carte.effects["cri de guerre"][2]
                    else:
                        player.cadavres += carte.effects["cri de guerre"][2]
                elif "rommath" in carte.effects["cri de guerre"] and player.indirect_spells:
                    shuffle(player.indirect_spells)
                    for spell in player.indirect_spells:
                        spell_to_play = get_card(spell, all_spells)
                        player.hand.cards.insert(0, spell_to_play)
                        spell_to_play.cost = 0
                        possible_targets = generate_targets(self.plt)[0: 16]
                        player.hand.remove(spell_to_play)
                        possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                        if possible_targets_refined:
                            target = random.choice(possible_targets_refined)
                            if target == 0:
                                target = None
                            elif target == 1:
                                target = player
                            elif target < 9:
                                target = player.servants[target - 2]
                            elif target == 9:
                                target = adv
                            else:
                                target = adv.servants[target - 10]
                        if not ("ciblage" in spell_to_play.effects and target is None):
                            TourEnCours(self.plt).apply_effects(spell_to_play, target)
                elif "tess" in carte.effects["cri de guerre"] and [x for x in player.cards_played if get_card(x, all_cards).classe not in [player.classe, "Neutre"]]:
                    other_class_cards = [x for x in player.cards_played if get_card(x, all_cards).classe not in [player.classe, "Neutre"]]
                    shuffle(other_class_cards)
                    for card in other_class_cards:
                        card_to_play = get_card(card, all_cards)
                        player.hand.cards.insert(0, card_to_play)
                        card_to_play.cost = 0
                        possible_targets = generate_targets(self.plt)[0: 16]
                        player.hand.remove(card_to_play)
                        possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                        if possible_targets_refined:
                            target = random.choice(possible_targets_refined)
                            if target == 0:
                                target = None
                            elif target == 1:
                                target = player
                            elif target < 9:
                                target = player.servants[target - 2]
                            elif target == 9:
                                target = adv
                            else:
                                target = adv.servants[target - 10]
                        if not ("ciblage" in card_to_play.effects and target is None):
                            TourEnCours(self.plt).apply_effects(card_to_play, target)
                elif "invocation" in carte.effects["cri de guerre"]:
                    if "allié" in carte.effects["cri de guerre"][1] and len(player.servants) + len(player.lieux) < 7:
                        if "conditional" in carte.effects["cri de guerre"][1]:
                            if "serviteur" in carte.effects["cri de guerre"][1] and "Méca" in \
                                    carte.effects["cri de guerre"][1] and any(
                                    "Méca" in sublist for sublist in [x.genre for x in player.servants if x != carte]):
                                if type(carte.effects["cri de guerre"][1]) == list:
                                    for invoked_servant in carte.effects["cri de guerre"][2]:
                                        self.invoke_servant(get_card(invoked_servant, all_servants), player)
                            elif "until_cadavre" in carte.effects["cri de guerre"][1] and player.cadavres > 0:
                                invoked_servant = get_card(carte.effects["cri de guerre"][2], all_servants)
                                invoked_servant.boost(min(8, player.cadavres), min(8, player.cadavres), fixed_stats=True)
                                player.cadavres -= min(8, player.cadavres)
                                player.cadavres_spent += min(8, player.cadavres)
                                self.invoke_servant(invoked_servant, player)
                            elif "if_no_double" in carte.effects["cri de guerre"][1] and len([x.name for x in player.deck]) == len(set([x.name for x in player.deck])):
                                potential_servants = [copy_card(x) for x in player.deck if x.type == "Serviteur"]
                                if "four_copies_44" in carte.effects["cri de guerre"][1] and potential_servants:
                                    to_invoke = random.sample(potential_servants, min(4, len(potential_servants)))
                                    for card in to_invoke:
                                        if len(player.servants) + len(player.lieux) < 7:
                                            card.boost(4, 4, fixed_stats=True)
                                            self.invoke_servant(card, player)
                            elif "if_alone" in carte.effects["cri de guerre"][1] and len(player.servants) == 1:
                                for crea in carte.effects["cri de guerre"][2]:
                                    if len(player.servants) + len(player.lieux) < 7:
                                        self.invoke_servant(get_card(crea, all_servants), player)
                        elif "until_cadavre" in carte.effects["cri de guerre"][1]:
                            if player.cadavres > 0:
                                invoked_creatures = []
                                for cadavre in range(min(player.cadavres, carte.effects["cri de guerre"][1][-1])):
                                    invoked_creatures.append(carte.effects["cri de guerre"][2])
                                carte.effects["cri de guerre"][2] = invoked_creatures
                            else:
                                carte.effects["cri de guerre"][2] = []
                        elif "nb_squelettes" in carte.effects["cri de guerre"][1] and player.dead_squelette != 0:
                            carte.effects["cri de guerre"][2] = ["Squelette instable"] * min(player.dead_squelette, 7 - (len(player.servants) + len(player.lieux)))
                            player.dead_squelette -= min(player.dead_squelette, 7 - (len(player.servants) + len(player.lieux)))
                        if "aléatoire" in carte.effects["cri de guerre"][1]:
                            if "cout" in carte.effects["cri de guerre"][1]:
                                if 2 in carte.effects["cri de guerre"][1]:
                                    while True:
                                        new_servant = random.choice(all_servants)
                                        if new_servant["cost"] == 2 and new_servant["decouvrable"] == 1:
                                            break
                                    new_servant = Card(**new_servant)
                                    self.invoke_servant(new_servant, player)
                                if "deck" in carte.effects["cri de guerre"][1] and "cout" in \
                                        carte.effects["cri de guerre"][1]:
                                    if [x for x in player.deck if x.cost <= player.mana and x.type == "Serviteur"]:
                                        new_servant = random.choice(
                                            [x for x in player.deck if x.cost <= player.mana and x.type == "Serviteur"])
                                        self.invoke_servant(new_servant, player)
                                        player.deck.remove(new_servant)
                            elif "if_death_undead" in carte.effects["cri de guerre"][1] and player.dead_undeads:
                                invoked_servant = get_card(carte.effects["cri de guerre"][2], all_servants)
                                self.invoke_servant(invoked_servant, player)
                        elif "copy" in carte.effects["cri de guerre"][1]:
                            if "if_secret" in carte.effects["cri de guerre"][1] and player.secrets:
                                invoked_servant = copy_card(carte.effects["cri de guerre"][2])
                                self.invoke_servant(invoked_servant, player)
                            else:
                                try:
                                    for nb_copy in range(carte.effects["cri de guerre"][1][-1]):
                                        invoked_servant = get_card(carte.effects["cri de guerre"][2], all_servants)
                                        invoked_servant.attack, invoked_servant.base_attack = carte.attack, carte.base_attack
                                        invoked_servant.health, invoked_servant.base_health = carte.health, carte.base_health
                                        invoked_servant.effects = carte.effects.copy()
                                        self.invoke_servant(invoked_servant, player)
                                except:
                                    print(carte, carte.effects)
                        elif "compagnon" in carte.effects["cri de guerre"][1]:
                            invoked_servants = random.sample([get_card(x["name"], all_servants) for x in all_servants if "compagnon" in x["effects"]], carte.effects["cri de guerre"][2])
                            for compagnon in invoked_servants:
                                self.invoke_servant(compagnon, player)
                        elif "graine" in carte.effects["cri de guerre"][1]:
                            while True:
                                invoked_servant = random.choice(all_servants)
                                if "graine" in invoked_servant["effects"]:
                                    break
                            invoked_servant = Card(**invoked_servant)
                            self.invoke_servant(invoked_servant, player)
                        elif "dead_234_paladin" in carte.effects["cri de guerre"][1]:
                            if [x for x in player.all_dead_servants if x.classe == "Paladin" and 2 <= x.cost <= 4]:
                                if [x for x in player.all_dead_servants if x.classe == "Paladin" and x.cost == 2]:
                                    resurrect_2 = random.choice([get_card(x.name, all_servants) for x in player.all_dead_servants if x.classe == "Paladin" and x.cost == 2])
                                    self.invoke_servant(resurrect_2, player)
                                if [x for x in player.all_dead_servants if x.classe == "Paladin" and x.cost == 3]:
                                    resurrect_3 = random.choice([get_card(x.name, all_servants) for x in player.all_dead_servants if x.classe == "Paladin" and x.cost == 3])
                                    self.invoke_servant(resurrect_3, player)
                                if [x for x in player.all_dead_servants if x.classe == "Paladin" and x.cost == 4]:
                                    resurrect_4 = random.choice([get_card(x.name, all_servants) for x in player.all_dead_servants if x.classe == "Paladin" and x.cost == 4])
                                    self.invoke_servant(resurrect_4, player)
                        elif "all_dead_undeads" in carte.effects["cri de guerre"][1]:
                            if player.dead_undeads:
                                for creature in player.dead_undeads:
                                    if len(player.servants) + len(player.lieux) < 7:
                                        self.invoke_servant(get_card(creature.name, all_servants), player)
                        elif type(carte.effects["cri de guerre"][2]) == list:
                            for invoked_servant in carte.effects["cri de guerre"][2]:
                                if len(player.servants) + len(player.lieux) < 7:
                                    real_servant = get_card(invoked_servant, all_servants)
                                    self.invoke_servant(real_servant, player)
                                    if "until_cadavre" in carte.effects["cri de guerre"][1]:
                                        player.cadavres -= 1
                                        player.cadavres_spent += 1
                                    elif "boosted_invoked" in carte.effects["cri de guerre"][1]:
                                        real_servant.boost(carte.effects["cri de guerre"][1][-1][0], carte.effects["cri de guerre"][1][-1][1])
                                        if "bouclier divin" in carte.effects["cri de guerre"][1]:
                                            real_servant.effects["bouclier divin"] = 1
                            if "boost" in carte.effects["cri de guerre"][1]:
                                if "until_cadavre" in carte.effects["cri de guerre"][1]:
                                    while player.cadavres > 0 and [x for x in player.servants if x.name == "Golem ressuscite"]:
                                        player.cadavres -= 1
                                        player.cadavres_spent += 1
                                        target = random.choice([x for x in player.servants if x.name == "Golem ressuscite"])
                                        target.boost(2, 2)
                                elif "boost_atk" in carte.effects["cri de guerre"][1] and "boost_armor" in carte.effects["cri de guerre"][1]:
                                    for creature in [x for x in player.servants if x.name == "Fan de voilegroin"]:
                                        creature.boost(max(0, player.attack - player.atk_this_turn), max(0, player.armor - player.armor_this_turn))
                        elif "from_deck" in carte.effects["cri de guerre"][1]:
                            if "Démon" in carte.effects["cri de guerre"][1] and carte.effects["cri de guerre"][2] == 1 and len(player.servants) + len(player.lieux) < 7:
                                serv_to_invoke = random.choice([x for x in player.deck if "Démon" in x.genre])
                                player.deck.remove(serv_to_invoke)
                                player.servants.add(serv_to_invoke)
                        else:
                            self.invoke_servant(get_card(carte.effects["cri de guerre"][2], all_servants), player)
                            if "nb_squelettes" in carte.effects["cri de guerre"][1] and player.dead_squelette != 0:
                                for _ in range(player.dead_squelette):
                                    cible = random.choice([x for x in [adv] + adv.servants.cards if not x.is_dead()])
                                    cible.damage(2, toxic=True if "toxicite" in carte.effects else False)
                                    print(cible, "Squelettes !")
                    elif "ennemi" in carte.effects["cri de guerre"][1] and len(adv.servants) + len(adv.lieux) < 7:
                        if all(x in carte.effects["cri de guerre"][1] for x in ["main", "serviteur", "aléatoire"]):
                            try:
                                played_servant = random.choice([x for x in adv.hand if x.type == "Serviteur"])
                                adv.hand.remove(played_servant)
                                self.invoke_servant(played_servant, adv)
                            except:
                                pass
                        else:
                            played_servant = get_card(carte.effects["cri de guerre"][2], all_cards)
                            self.invoke_servant(played_servant, adv)
                elif "mutation" in carte.effects["cri de guerre"]:
                    if target is not None:
                        player.servants.remove(target)
                        self.invoke_servant(get_card(carte.effects["cri de guerre"][2], all_servants), player)
                    else:
                        if "all_treant" in carte.effects["cri de guerre"][1] and [x for x in player.servants if x.name == "Treant"]:
                            player.servants.cards = [get_card("Ancien", all_servants) if x.name == "Treant" else x for x in player.servants.cards]
                elif "launch" in carte.effects["cri de guerre"] and target is not None:
                    if "serviteur" in carte.effects["cri de guerre"][2] and "main" in carte.effects["cri de guerre"][2]:
                        if [x for x in player.hand if x.type == "Serviteur"] and len(player.servants) + len(player.lieux) < 7:
                            launched_servant = random.choice([x for x in player.hand if x.type == "Serviteur"])
                            player.hand.remove(launched_servant)
                            self.invoke_servant(launched_servant, player)
                            self.attaquer(launched_servant, target)
                elif "copy" in carte.effects["cri de guerre"]:
                    player.servants.remove(carte)
                    new_servant = copy_card(target)
                    new_servant.boost(carte.effects["cri de guerre"][-1][0], carte.effects["cri de guerre"][-1][1], fixed_stats = True)
                    self.invoke_servant(new_servant, player)
                elif "boosted_copy" in carte.effects["cri de guerre"] and target is not None and len(player.servants) + len(player.lieux) < 7:
                    card_to_invoke = copy_card(target)
                    card_to_invoke.remaining_atk = 1
                    self.invoke_servant(card_to_invoke, player)
                elif "duplicate" in carte.effects["cri de guerre"]:
                    if "main" in carte.effects["cri de guerre"][1]:
                        hand = player.hand.cards.copy()
                        for card in hand:
                            player.hand.add(get_card(card.name, all_cards))
                    if "board" in carte.effects["cri de guerre"][1]:
                        board = player.servants.cards.copy()
                        for card in board:
                            if len(player.servants) + len(player.lieux) < 7 and card != carte:
                                self.invoke_servant(get_card(card.name, all_servants), player)
                elif "decouverte" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if "serviteur" in carte.effects["cri de guerre"][2]:
                            if "genre" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, "serviteur", target.genre)
                    else:
                        if "conditional" in carte.effects["cri de guerre"][1]:
                            if "serviteur" in carte.effects["cri de guerre"][1] and "allié" in \
                                    carte.effects["cri de guerre"][1]:
                                if "Méca" in carte.effects["cri de guerre"][1] and any("Méca" in sublist for sublist in
                                                                                       [x.genre for x in player.servants
                                                                                        if x != carte]):
                                    self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Méca"])
                            elif "if_death_undead" in carte.effects["cri de guerre"][1]:
                                if player.dead_undeads:
                                    if "reduc" in carte.effects["cri de guerre"][1] and "sort" in carte.effects["cri de guerre"][2]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", reduc=carte.effects["cri de guerre"][1][3])
                                    elif "vert" in carte.effects["cri de guerre"][2]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, other="vert")
                                else:
                                    if "reduc" in carte.effects["cri de guerre"][1] and "sort" in carte.effects["cri de guerre"][2]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort")
                            elif "if_cadavre" in carte.effects["cri de guerre"][1]:
                                if player.cadavres >= carte.effects["cri de guerre"][1][-1]:
                                    player.cadavres -= carte.effects["cri de guerre"][1][-1]
                                    player.cadavres_spent += carte.effects["cri de guerre"][1][-1]
                                    self.plt.cards_chosen = self.choice_decouverte(carte, other="rouge")
                            elif "if_lieu" in carte.effects["cri de guerre"][1] and player.lieux:
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([get_card(x.name, all_cards) for x in player.deck]))
                            elif "if_alone" in carte.effects["cri de guerre"][1] and len(player.servants) == 1:
                                self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="Secret")
                            elif "if_spell_before" in carte.effects["cri de guerre"][1] and player.spell_before:
                                self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Élémentaire"])
                            elif "if_dragon_inhand" in carte.effects["cri de guerre"][1] and [x for x in player.hand if "Dragon" in x.genre]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([copy_card(x) for x in adv.deck]))
                            elif "if_secret" in carte.effects["cri de guerre"][1] and player.secrets:
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=adv.hand)
                        else:
                            if "sort" in carte.effects["cri de guerre"][2]:
                                if "secret" in carte.effects["cri de guerre"][2]:
                                    try:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="Secret")
                                    except:
                                        pass
                                elif "classe_adv" in carte.effects["cri de guerre"][2]:
                                    self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", classe=adv.classe)
                                elif "other_class" in carte.effects["cri de guerre"][2]:
                                    if "cost_under3" in carte.effects["cri de guerre"][2]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", classe="other_class", cost="under3")
                                    else:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", classe="other_class")
                                elif "choix mystere" in carte.effects["cri de guerre"][2]:
                                    self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="choix mystere")
                                elif 2 in carte.effects["cri de guerre"][2]:
                                    self.plt.cards_chosen = self.choice_decouverte(carte, type="sort") + self.choice_decouverte(carte, type="sort")
                                else:
                                    if "reduc" in carte.effects["cri de guerre"][2]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", reduc=carte.effects["cri de guerre"][2][-1])
                                    else:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort")
                            elif "serviteur" in carte.effects["cri de guerre"][2]:
                                if "legendaire" in carte.effects["cri de guerre"][2]:
                                    if "prêtre" in carte.effects["cri de guerre"][2]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", classe="Prêtre", other="legendaire")
                                    else:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", other="legendaire")
                                elif "Bête" in carte.effects["cri de guerre"][2]:
                                    if "in_deck" in carte.effects["cri de guerre"][2] and [x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([copy_card(x) for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]))
                                    else:
                                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Bête"])
                                elif "Dragon" in carte.effects["cri de guerre"][2]:
                                    self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Dragon"])
                            elif "ETC" in carte.effects["cri de guerre"][1]:
                                etc_pack = CardGroup(
                                    [get_card(x, all_cards) for x in carte.effects["cri de guerre"][2]])
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=etc_pack)
                            elif "Anneau des marees" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=[get_card(x.name, all_spells) for x in carte.effects["cri de guerre"][2]])
                            elif "hand_to_deck" in carte.effects["cri de guerre"][1] and player.hand.cards:
                                self.plt.cards_hands_to_deck = [CardGroup(random.sample(player.hand.cards, min(3, len(player.hand.cards))))]
                            elif "relique" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="relique")
                            elif "dead rale d'agonie" in carte.effects["cri de guerre"][2] and player.dead_rale:
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([get_card(x.name, all_servants) for x in player.dead_rale if "rale d'agonie" in get_card(x.name, all_servants).effects]))
                            elif "classe" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, classe=carte.effects["cri de guerre"][2][-1])
                            if "adv_hand" in carte.effects["cri de guerre"][2] and "player_hand" in carte.effects["cri de guerre"][2]:
                                if player.hand.cards and adv.hand.cards:
                                    self.plt.cards_chosen = self.choice_decouverte(carte, card_group=adv.hand) + self.choice_decouverte(carte, card_group=player.hand)
                            if "deck_adv" in carte.effects["cri de guerre"][2]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, card_group=adv.deck)
                elif "rale d'agonie" in carte.effects["cri de guerre"]:
                    if target is not None:
                        if "rale d'agonie" in target.effects:
                            target.effects["rale d'agonie2"] = carte.effects["cri de guerre"][2]
                        else:
                            target.effects["rale d'agonie"] = carte.effects["cri de guerre"][2]
                    else:
                        if "serviteur" in carte.effects["cri de guerre"][1]:
                            if "ennemi" in carte.effects["cri de guerre"][1]:
                                if "tous" in carte.effects["cri de guerre"][1] and adv.servants.cards:
                                    for creature in adv.servants:
                                        if "rale d'agonie" in creature.effects:
                                            creature.effects["rale d'agonie2"] = carte.effects["cri de guerre"][2]
                                        else:
                                            creature.effects["rale d'agonie"] = carte.effects["cri de guerre"][2]
                elif "apply_rale" in carte.effects["cri de guerre"] and target is not None:
                    creature = target
                    creature.effects["rale_applied"] = 1
                    self.apply_effects(creature)
                    self.apply_effects(creature)
                    creature.effects.pop("rale_applied")
                elif "apply_gain_rale" in carte.effects["cri de guerre"]:
                    if "if_cadavre" in carte.effects["cri de guerre"][1] and player.cadavres >= carte.effects["cri de guerre"][1][-1] and player.dead_rale:
                        player.cadavres -= carte.effects["cri de guerre"][1][-1]
                        player.cadavres_spent += carte.effects["cri de guerre"][1][-1]
                        creature = random.choice(player.dead_rale)
                        carte.effects["rale d'agonie"] = creature.effects["rale d'agonie"].copy()
                        carte.effects["rale_applied"] = 1
                        carte.effects.pop("cri de guerre")
                        self.apply_effects(carte)
                        carte.effects.pop("rale_applied")
                elif "permanent_buff" in carte.effects["cri de guerre"]:
                    if carte.effects["cri de guerre"][2] == "jotun":
                        if player.first_spell is None:
                            player.permanent_buff["jotun"] = 1
                        else:
                            player.permanent_buff["jotun"] = 0
                    elif carte.effects["cri de guerre"][2] == "topior":
                        player.permanent_buff["topior"] = 1
                    elif carte.effects["cri de guerre"][2] == "hodir":
                        player.permanent_buff["hodir"] = 3
                    elif carte.effects["cri de guerre"][2] == "Gardien du temps":
                        player.permanent_buff["Gardien du temps"] = 2
                    elif carte.effects["cri de guerre"][2] == "lothraxion":
                        player.permanent_buff["lothraxion"] = 1
                    elif carte.effects["cri de guerre"][2] == "croise sanglant":
                        player.permanent_buff["croise sanglant"] = 1
                    elif carte.effects["cri de guerre"][2] == "kvaldir":
                        player.permanent_buff["kvaldir"] = 1
                elif "hp_boost" in carte.effects["cri de guerre"]:
                    if "armure" in carte.effects["cri de guerre"][1]:
                        if "armure" in player.hp_boost:
                            player.hp_boost["armure"] += carte.effects["cri de guerre"][2]
                        else:
                            player.hp_boost["armure"] = carte.effects["cri de guerre"][2]
                    if "attack" in carte.effects["cri de guerre"][1]:
                        if "attack" in player.hp_boost:
                            player.hp_boost["attack"] += carte.effects["cri de guerre"][2]
                        else:
                            player.hp_boost["attack"] = carte.effects["cri de guerre"][2]
                elif "choix_des_armes" in carte.effects["cri de guerre"]:
                    if "prochain" in carte.effects["cri de guerre"][1] and "combined" in carte.effects["cri de guerre"][1]:
                        player.next_choix_des_armes = 1
                elif "double_spell" in carte.effects["cri de guerre"] and carte.effects["cri de guerre"][2] == 1:
                    player.next_spell.append("double")
                elif "cri de guerre" in carte.effects:
                    carte.effects.pop("cri de guerre")
            elif "magnetisme" in carte.effects and not (carte.is_dead() or "rale_applied" in carte.effects) and target is not None:
                carte.effects.pop("magnetisme")
                target.attack += carte.attack
                target.base_attack += carte.base_attack
                target.health += carte.health
                target.base_health += carte.base_health
                target.effects = target.effects | carte.effects
                if "rale d'agonie" in target.effects and "magnetised" in target.effects["rale d'agonie"][1]:
                    target.effects["rale d'agonie"][2].append(carte.name)
                player.servants.remove(carte)
            elif "reincarnation" in carte.effects and (carte.is_dead() or "rale_applied" in carte.effects):
                if carte.effects["reincarnation"]:
                    card_revive = get_card(carte.name, all_servants)
                    card_revive.health = 1
                    card_revive.blessure = card_revive.base_health - card_revive.health
                    if "reincarnation" in card_revive.effects:
                        card_revive.effects.pop("reincarnation")
                    if carte in player.servants:
                        self.invoke_servant(card_revive, player)
                    else:
                        self.invoke_servant(card_revive, adv)
            if "choix_des_armes" in carte.effects and not (carte.is_dead() or "rale_applied" in carte.effects):
                if not player.next_choix_des_armes:
                    self.plt.choix_des_armes = carte
                else:
                    combined_card = get_card(carte.name + " combine", all_servants)
                    combined_card.cost, combined_card.base_cost = 0, 0
                    combined_card.effects["mandatory"] = 1
                    player.hand.add(combined_card)
                    player.next_choix_des_armes = 0
            if "soif de mana" in carte.effects and carte.effects["soif de mana"][3] <= player.mana_max and not (carte.is_dead() or "rale_applied" in carte.effects):
                if "damage" in carte.effects["soif de mana"]:
                    if target is not None:
                        target.damage(carte.effects["soif de mana"][2], toxic=True if "toxicite" in carte.effects else False)
                    else:
                        if "tous" in carte.effects["soif de mana"][1]:
                            if "ennemi" in carte.effects["soif de mana"][1]:
                                if "aléatoire" in carte.effects["soif de mana"][1]:
                                    try:
                                        for n in range(0, carte.effects["soif de mana"][1][3]):
                                            random_target = random.choice([adv] + adv.servants.cards)
                                            random_target.damage(carte.effects["soif de mana"][2], toxic=True if "toxicite" in carte.effects else False)
                                    except:
                                        pass
                elif "add_armor" in carte.effects["soif de mana"]:
                    if "tous" in carte.effects["soif de mana"][1]:
                        adv.armor += carte.effects["soif de mana"][2]
                    player.armor += carte.effects["soif de mana"][2]
                elif "silence+gel" in carte.effects["soif de mana"] and target is not None:
                    target.base_attack = get_card(target.name, all_servants).base_attack
                    target.attack = get_card(target.name, all_servants).base_attack
                    target.health = max(1, get_card(target.name, all_servants).base_health - target.blessure)
                    target.base_health = get_card(target.name, all_servants).base_health
                    target.effects = {"gel": carte.effects["soif de mana"][2]}
                elif "invocation" in carte.effects["soif de mana"]:
                    if "cout" in carte.effects["soif de mana"][1]:
                        if player.mana_max >= 10:
                            while True:
                                new_servant = random.choice(all_servants)
                                if new_servant["cost"] == 8 and new_servant["decouvrable"] == 1:
                                    break
                            new_servant = Card(**new_servant)
                            self.invoke_servant(new_servant, player)
                        else:
                            while True:
                                new_servant = random.choice(all_servants)
                                if new_servant["cost"] == 3 and new_servant["decouvrable"] == 1:
                                    break
                            new_servant = Card(**new_servant)
                            self.invoke_servant(new_servant, player)
                elif "reincarnation" in carte.effects["soif de mana"]:
                    if "self" in carte.effects["soif de mana"][1]:
                        carte.effects["reincarnation"] = 0
                elif "heal" in carte.effects["soif de mana"]:
                    if "tous" in carte.effects["soif de mana"][1]:
                        if "allié" in carte.effects["soif de mana"][1] and not [x for x in adv.servants if "anti_heal" in x.effects]:
                            if "kvaldir" in player.permanent_buff:
                                for entity in [player] + player.servants.cards:
                                    entity.damage(carte.effects["soif de mana"][2])
                                player.permanent_buff.pop("kvaldir")
                            else:
                                for entity in [player] + player.servants.cards:
                                    entity.heal(carte.effects["soif de mana"][2])
                elif "boost" in carte.effects["soif de mana"]:
                    if "self" in carte.effects["soif de mana"][1]:
                        if "bouclier divin" in carte.effects["soif de mana"][1]:
                            carte.effects["bouclier divin"] = 1
                        carte.boost(carte.effects["soif de mana"][2][0], carte.effects["soif de mana"][2][1])
            if "rale d'agonie" in carte.effects and (carte.is_dead() or "rale_applied" in carte.effects):
                if "serviteur" in carte.effects["rale d'agonie"][1]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre and x != carte]) \
                                if len(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre and x != carte]) != 0 else None
                        elif carte.effects["rale d'agonie"][2] == "nbre_tentacules":
                            nbre_tentacules = len([x for x in adv.servants if x.name == "Tentacule d'ozumat"])
                            if nbre_tentacules == 0 or not player.servants.cards:
                                target = None
                            else:
                                target = random.sample(player.servants.cards, min(nbre_tentacules, len(player.servants)))
                        elif "tous" in carte.effects["rale d'agonie"][1]:
                            target = player.servants
                        elif "main" in carte.effects["rale d'agonie"][1]:
                            target = random.choice([x for x in player.hand if x.type == "Serviteur"]) if [x for x in player.hand if x.type == "Serviteur"] else None
                        else:
                            target = random.choice([x for x in player.servants if x != carte]) \
                                if len([x for x in player.servants]) > 1 else None
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre and x.name != carte.name]) \
                                if len(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre and x.name != carte.name]) != 0 else None
                        elif carte.effects["rale d'agonie"][2] == "nbre_tentacules":
                            nbre_tentacules = len([x for x in player.servants if x.name == "Tentacule d'ozumat"])
                            if nbre_tentacules == 0 or not adv.servants.cards:
                                target = None
                            else:
                                target = random.sample(adv.servants.cards, min(nbre_tentacules, len(adv.servants)))
                        elif "tous" in carte.effects["rale d'agonie"][1]:
                            target = adv.servants
                        elif "main" in carte.effects["rale d'agonie"][1]:
                            target = random.choice([x for x in adv.hand if x.type == "Serviteur"]) if [x for x in adv.hand if x.type == "Serviteur"] else None
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
                                target = adv
                            else:
                                carte.effects["rale d'agonie"] = ["", [""], ""]
                        else:
                            target = adv
                    elif ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie"][1]:
                            if carte in adv.servants:
                                target = player
                            else:
                                carte.effects["rale d'agonie"] = ["", [""], ""]
                        else:
                            target = player
                elif "tous" in carte.effects["rale d'agonie"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "aléatoire" in carte.effects["rale d'agonie"][1]:
                            target = random.choice([adv] + adv.servants.cards)
                    elif ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "aléatoire" in carte.effects["rale d'agonie"][1]:
                            target = random.choice([player] + player.servants.cards)
                if "damage" in carte.effects["rale d'agonie"] and target is not None:
                    if type(target) in (Player, Card):
                        if type(carte.effects["rale d'agonie"][2]) == list:
                            target.damage(random.choice(carte.effects["rale d'agonie"][2]), toxic=True if "toxicite" in carte.effects else False)
                        else:
                            target.damage(carte.effects["rale d'agonie"][2], toxic=True if "toxicite" in carte.effects else False)
                    else:
                        for card in target:
                            card.damage(carte.effects["rale d'agonie"][2], toxic=True if "toxicite" in carte.effects else False)
                if "destroy" in carte.effects["rale d'agonie"] and target is not None:
                    if type(target) == list:
                        for serv in target:
                            serv.blessure = 1000
                            serv.health = max(0, serv.base_health + serv.total_temp_boost[1] - serv.blessure)
                    else:
                        target.blessure = 1000
                        target.health = max(0, target.base_health + target.total_temp_boost[1] - target.blessure)
                if "boost" in carte.effects["rale d'agonie"]:
                    if target is not None:
                        if type(target) == Card:
                            target.boost(carte.effects["rale d'agonie"][2][0], carte.effects["rale d'agonie"][2][1])
                            if "provocation" in carte.effects["rale d'agonie"][2]:
                                target.effects["provocation"] = 1
                    else:
                        if "next_serv_drawn" in carte.effects["rale d'agonie"][1]:
                            if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                player.hand.aegwynn = True
                            elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                adv.hand.aegwynn = True
                        if "secret" in carte.effects["rale d'agonie"][1]:
                            if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                                    "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                if player.secrets:
                                    secret_booste = random.choice(player.secrets)
                                    secret_booste.effects["halkias"] = 1
                            elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                                    "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                if adv.secrets:
                                    secret_booste = random.choice(adv.secrets)
                                    secret_booste.effects["halkias"] = 1
                if "heal" in carte.effects["rale d'agonie"] and target is not None and not [x for x in adv.servants if "anti_heal" in x.effects]:
                    if "kvaldir" in player.permanent_buff:
                        target.damage(carte.effects["rale d'agonie"][2])
                        player.permanent_buff.pop("kvaldir")
                    else:
                        target.heal(carte.effects["rale d'agonie"][2])
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
                                    self.invoke_servant(get_card(carte.effects["rale d'agonie"][2], all_servants), player)
                                player.mana = 0
                        elif type(carte.effects["rale d'agonie"][2]) == list:
                            if "if_hydrolodon" in carte.effects["rale d'agonie"][1] and not "Hydrolodon" in [x.name for x in player.servants]:
                                carte.effects["rale d'agonie"][2] = []
                            for invoked_servant in carte.effects["rale d'agonie"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), player)
                        elif "conditional" in carte.effects["rale d'agonie"][1]:
                            if "if_robaudio" in carte.effects["rale d'agonie"][1]:
                                if [x for x in adv.hand if x.name == "Rob'audio"]:
                                    for robaudio in [x for x in adv.hand if x.name == "Rob'audio"]:
                                        adv.hand.remove(robaudio)
                                        self.invoke_servant(get_card("Rob'audio", all_servants), player)
                            elif "spend_cadavre" in carte.effects["rale d'agonie"][1] and player.cadavres >= carte.effects["rale d'agonie"][1][-1]:
                                player.cadavres -= carte.effects["rale d'agonie"][1][-1]
                                player.cadavres_spent += carte.effects["rale d'agonie"][1][-1]
                                self.invoke_servant(get_card(carte.effects["rale d'agonie"][2], all_servants), player)
                        elif "copy_deck" in carte.effects["rale d'agonie"][1]:
                            if [x.name for x in player.deck if x.type == "Serviteur" and x.name != carte.name]:
                                new_servant = get_card(random.choice([x.name for x in player.deck if x.type == "Serviteur" and x.name != carte.name]), all_servants)
                                new_servant.attack, new_servant.base_attack, new_servant.health, new_servant.base_health = 2, 2, 2, 2
                                self.invoke_servant(new_servant, player)
                        elif "in_deck" in carte.effects["rale d'agonie"][1]:
                            if "lower_attack" in carte.effects["rale d'agonie"][1] and [x for x in player.deck if x.type == "Serviteur" and x.attack < carte.attack]:
                                invoked_servant = random.choice([x for x in player.deck if x.type == "Serviteur" and x.attack < carte.attack])
                                player.deck.remove(invoked_servant)
                                self.invoke_servant(invoked_servant, player)
                        elif "aléatoire" in carte.effects["rale d'agonie"][1]:
                            if "cout" in carte.effects["rale d'agonie"][1]:
                                if 5 in carte.effects["rale d'agonie"][1]:
                                    while True:
                                        new_servant = random.choice(all_servants)
                                        if new_servant["cost"] == 5 and new_servant["decouvrable"] == 1:
                                            break
                                    new_servant = Card(**new_servant)
                                    self.invoke_servant(new_servant, player)
                                elif "Méca" in carte.effects["rale d'agonie"][1] and "<=3" in carte.effects["rale d'agonie"][1]:
                                    for i in range(2):
                                        while True:
                                            new_servant = random.choice(all_servants)
                                            if new_servant["cost"] <= 3 and new_servant["decouvrable"] == 1 and "Méca" in new_servant["genre"]:
                                                break
                                        new_servant = Card(**new_servant)
                                        self.invoke_servant(new_servant, player)
                            elif "Bête" in carte.effects["rale d'agonie"][1] and "in_deck" in carte.effects["rale d'agonie"][1]:
                                if [x for x in player.deck if "Bête" in x.genre]:
                                    new_servant = random.choice([x for x in player.deck if "Bête" in x.genre])
                                    self.invoke_servant(new_servant, player)
                        elif "dead_undead" in carte.effects["rale d'agonie"][1]:
                            if player.dead_zombies:
                                to_invoke = random.choice([get_card(x, all_servants) for x in player.dead_zombies])
                                self.invoke_servant(to_invoke, player)
                        elif "all_serv_indirect" in carte.effects["rale d'agonie"][1]:
                            if player.dead_indirect:
                                for creature in player.dead_indirect:
                                    if len(player.servants) + len(player.lieux) < 7:
                                        self.invoke_servant(get_card(creature, all_servants), player)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            self.invoke_servant(new_servant, player)
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "mana_dispo" in carte.effects["rale d'agonie"][1] and adv.mana != 0:
                            new_servant = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            for n in range(adv.mana):
                                self.invoke_servant(new_servant, adv)
                            adv.mana = 0
                        elif type(carte.effects["rale d'agonie"][2]) == list:
                            if "if_hydrolodon" in carte.effects["rale d'agonie"][1] and not "Hydrolodon" in [x.name for x in adv.servants]:
                                carte.effects["rale d'agonie"][2] = []
                            for invoked_servant in carte.effects["rale d'agonie"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), adv)
                        elif "conditional" in carte.effects["rale d'agonie"][1]:
                            if "if_robaudio" in carte.effects["rale d'agonie"][1]:
                                if [x for x in player.hand if x.name == "Rob'audio"]:
                                    for robaudio in [x for x in player.hand if x.name == "Rob'audio"]:
                                        player.hand.remove(robaudio)
                                        self.invoke_servant(get_card("Rob'audio", all_servants), adv)
                            elif "spend_cadavre" in carte.effects["rale d'agonie"][1] and adv.cadavres >= carte.effects["rale d'agonie"][1][-1]:
                                adv.cadavres -= carte.effects["rale d'agonie"][1][-1]
                                self.invoke_servant(get_card(carte.effects["rale d'agonie"][2], all_servants), adv)
                        elif "copy_deck" in carte.effects["rale d'agonie"][1]:
                            if [x.name for x in adv.deck if x.type == "Serviteur" and x.name != carte.name]:
                                new_servant = get_card(random.choice([x.name for x in adv.deck if x.type == "Serviteur" and x.name != carte.name]), all_servants)
                                new_servant.attack, new_servant.base_attack, new_servant.health, new_servant.base_health = 2, 2, 2, 2
                                self.invoke_servant(new_servant, adv)
                        elif "in_deck" in carte.effects["rale d'agonie"][1]:
                            if "lower_attack" in carte.effects["rale d'agonie"][1] and [x for x in adv.deck if x.type == "Serviteur" and x.attack < carte.attack]:
                                invoked_servant = random.choice([x for x in adv.deck if x.type == "Serviteur" and x.attack < carte.attack])
                                adv.deck.remove(invoked_servant)
                                self.invoke_servant(invoked_servant, adv)
                        elif "aléatoire" in carte.effects["rale d'agonie"][1]:
                            if "cout" in carte.effects["rale d'agonie"][1]:
                                if 5 in carte.effects["rale d'agonie"][1]:
                                    while True:
                                        new_servant = random.choice(all_servants)
                                        if new_servant["cost"] == 5 and new_servant["decouvrable"] == 1:
                                            break
                                    new_servant = Card(**new_servant)
                                    self.invoke_servant(new_servant, adv)
                                elif "Méca" in carte.effects["rale d'agonie"][1] and "<=3" in carte.effects["rale d'agonie"][1]:
                                    for i in range(2):
                                        while True:
                                            new_servant = random.choice(all_servants)
                                            if new_servant["cost"] <= 3 and new_servant["decouvrable"] == 1 and "Méca" in new_servant["genre"]:
                                                break
                                        new_servant = Card(**new_servant)
                                        self.invoke_servant(new_servant, adv)
                            elif "Bête" in carte.effects["rale d'agonie"][1] and "in_deck" in carte.effects["rale d'agonie"][1]:
                                if [x for x in adv.deck if "Bête" in x.genre]:
                                    new_servant = random.choice([x for x in adv.deck if "Bête" in x.genre])
                                    self.invoke_servant(new_servant, adv)
                        elif "dead_undead" in carte.effects["rale d'agonie"][1]:
                            if adv.dead_zombies:
                                to_invoke = random.choice([get_card(x, all_servants) for x in adv.dead_zombies])
                                self.invoke_servant(to_invoke, adv)
                        elif "all_serv_indirect" in carte.effects["rale d'agonie"][1]:
                            if adv.dead_indirect:
                                for creature in adv.dead_indirect:
                                    if len(player.servants) + len(player.lieux) < 7:
                                        self.invoke_servant(get_card(creature, all_servants), adv)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            self.invoke_servant(new_servant, adv)
                if "pioche" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "highest_servant" in carte.effects["rale d'agonie"][1]:
                            if [x for x in player.deck if x.type == "Serviteur"]:
                                card_to_draw = max([x.cost for x in player.deck if x.type == "Serviteur"])
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur" and x.cost == card_to_draw])
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                        elif "sort" in carte.effects["rale d'agonie"][1] and "givre" in carte.effects["rale d'agonie"][1]:
                            if [x for x in player.deck if x.type == "Sort" and "Givre" in x.genre]:
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Sort" and "Givre" in x.genre])
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                        elif "serviteur" in carte.effects["rale d'agonie"][1]:
                            if "reduc" in carte.effects["rale d'agonie"][1] and [x for x in player.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = max(0, card_to_draw.base_cost - carte.effects["rale d'agonie"][1][-1])
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                            elif "all_stats5" in carte.effects["rale d'agonie"][1] and [x for x in player.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = 5
                                card_to_draw.attack = 5
                                card_to_draw.base_attack = 5
                                card_to_draw.health = 5
                                card_to_draw.base_health = 5
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                        else:
                            player.pick_multi(carte.effects["rale d'agonie"][2])
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "highest_servant" in carte.effects["rale d'agonie"][1]:
                            if adv.deck.cards:
                                card_to_draw = max([x.cost for x in adv.deck if x.type == "Serviteur"])
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Serviteur" and x.cost == card_to_draw])
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                        elif "sort" in carte.effects["rale d'agonie"][1] and "givre" in carte.effects["rale d'agonie"][1]:
                            if [x for x in adv.deck if x.type == "Sort" and "Givre" in x.genre]:
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Sort" and "Givre" in x.genre])
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                        elif "serviteur" in carte.effects["rale d'agonie"][1]:
                            if "reduc" in carte.effects["rale d'agonie"][1] and [x for x in adv.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = max(0, card_to_draw.base_cost - carte.effects["rale d'agonie"][1][-1])
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                            elif "all_stats5" in carte.effects["rale d'agonie"][1] and [x for x in adv.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = 5
                                card_to_draw.attack = 5
                                card_to_draw.base_attack = 5
                                card_to_draw.health = 5
                                card_to_draw.base_health = 5
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                        else:
                            adv.pick_multi(carte.effects["rale d'agonie"][2])
                if "pioche+invocation" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if [x for x in player.deck if "Mort-vivant" in x.genre]:
                            card_to_draw = random.choice([x for x in player.deck if "Mort-vivant" in x.genre])
                            player.deck.remove(card_to_draw)
                            player.hand.add(card_to_draw)
                            if len(player.servants) + len(player.lieux) < 7:
                                self.invoke_servant(get_card(card_to_draw.name, all_servants), player)
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if [x for x in adv.deck if "Mort-vivant" in x.genre]:
                            card_to_draw = random.choice([x for x in adv.deck if "Mort-vivant" in x.genre])
                            adv.deck.remove(card_to_draw)
                            adv.hand.add(card_to_draw)
                            if len(adv.servants) + len(adv.lieux) < 7:
                                self.invoke_servant(get_card(card_to_draw.name, all_servants), adv)
                if "add_hand" in carte.effects["rale d'agonie"]:
                    if "sort" in carte.effects["rale d'agonie"][1]:
                        if "ombre" in carte.effects["rale d'agonie"][1]:
                            if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                while True:
                                    card_to_add = random.choice(all_spells)
                                    if "Ombre" in card_to_add["genre"] and card_to_add["decouvrable"] == 1:
                                        break
                                card_to_add = Card(**card_to_add)
                                player.hand.add(card_to_add)
                            elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                while True:
                                    card_to_add = random.choice(all_spells)
                                    if "Ombre" in card_to_add["genre"] and card_to_add["decouvrable"] == 1:
                                        break
                                card_to_add = Card(**card_to_add)
                                adv.hand.add(card_to_add)
                        elif "givre" in carte.effects["rale d'agonie"][1] and "copy" in carte.effects["rale d'agonie"][1]:
                            if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                if [x for x in player.hand if "Givre" in x.genre]:
                                    for spell in [x for x in player.hand if "Givre" in x.genre]:
                                        if len(player.hand) < 10:
                                            card_to_add = get_card(spell.name, all_spells)
                                            player.hand.add(card_to_add)
                            elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                if [x for x in adv.hand if "Givre" in x.genre]:
                                    for spell in [x for x in adv.hand if "Givre" in x.genre]:
                                        card_to_add = get_card(spell.name, all_spells)
                                        adv.hand.add(card_to_add)
                        elif "arcanes" in carte.effects["rale d'agonie"][1] and "mage" in carte.effects["rale d'agonie"][1]:
                            if "brulure" in carte.effects["rale d'agonie"][1]:
                                if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                    for _ in range(carte.effects["rale d'agonie"][-1]):
                                        while True:
                                            card_to_add = random.choice(all_spells)
                                            if card_to_add["classe"] == "Mage" and "Arcanes" in card_to_add["genre"]:
                                                break
                                        card_to_add = Card(**card_to_add)
                                        card_to_add.effects["brulure"] = 1
                                        player.hand.add(card_to_add)
                                elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                    for _ in range(carte.effects["rale d'agonie"][-1]):
                                        while True:
                                            card_to_add = random.choice(all_spells)
                                            if card_to_add["classe"] == "Mage" and "Arcanes" in card_to_add["genre"]:
                                                break
                                        card_to_add = Card(**card_to_add)
                                        card_to_add.effects["brulure"] = 1
                                        adv.hand.add(card_to_add)
                        elif "copy" in carte.effects["rale d'agonie"][1] and "highest_spell" in carte.effects["rale d'agonie"][1]:
                            if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                if [x for x in player.hand if x.type == "Sort"]:
                                    highest_spell = max([x.cost for x in player.hand if x.type == "Sort"])
                                    highest_spell = random.choice([x.name for x in player.hand if x.type == "Sort" and x.cost == highest_spell])
                                    player.hand.add(get_card(highest_spell, all_spells))
                            elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                                if [x for x in adv.hand if x.type == "Sort"]:
                                    highest_spell = max([x.cost for x in adv.hand if x.type == "Sort"])
                                    highest_spell = random.choice([x.name for x in adv.hand if x.type == "Sort" and x.cost == highest_spell])
                                    adv.hand.add(get_card(highest_spell, all_spells))
                    elif "weapon" in carte.effects["rale d'agonie"][1]:
                        if "ennemi" in carte.effects["rale d'agonie"][1]:
                            try:
                                card_to_add = random.choice(all_weapons)
                                adv.hand.add(card_to_add)
                            except:
                                pass
                    elif "serv_transformation" in carte.effects["rale d'agonie"][1]:
                        if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            if [x for x in player.hand if x.type == "Serviteur"]:
                                player.hand.remove(random.choice([x for x in player.hand if x.type == "Serviteur"]))
                                player.hand.add(get_card(carte.effects["rale d'agonie"][2], all_servants))
                        elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            if [x for x in adv.hand if x.type == "Serviteur"]:
                                adv.hand.remove(random.choice([x for x in adv.hand if x.type == "Serviteur"]))
                                adv.hand.add(get_card(carte.effects["rale d'agonie"][2], all_servants))
                    elif "cost_pv" in carte.effects["rale d'agonie"][1]:
                        if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            card_to_add = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            card_to_add.effects["cost_pv"] = ["", 1]
                            player.hand.add(card_to_add)
                        elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            card_to_add = get_card(carte.effects["rale d'agonie"][2], all_servants)
                            card_to_add.effects["cost_pv"] = ["", 1]
                            adv.hand.add(card_to_add)
                    elif "copy" in carte.effects["rale d'agonie"][1]:
                        if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                                "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            if "from_adv_deck" in carte.effects["rale d'agonie"][1]:
                                if adv.deck.cards:
                                    card_to_draw = copy_card(random.choice([x for x in adv.deck]))
                                    card_to_draw.effects["copied"] = 1
                                    player.hand.add(card_to_draw)
                            if "in_deck" in carte.effects["rale d'agonie"][1]:
                                if "serviteur" in carte.effects["rale d'agonie"][1] and "if_rale_agonie" in carte.effects["rale d'agonie"][1]:
                                    if [x for x in player.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]:
                                        card_to_draw = copy_card(random.choice([x for x in player.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]))
                                        card_to_draw.base_cost = max(0, card_to_draw.base_cost - 4)
                                        card_to_draw.boost(4, 4, fixed_stats=True)
                                        player.hand.add(card_to_draw)
                        elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                                "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            if "from_adv_deck" in carte.effects["rale d'agonie"][1]:
                                if player.deck.cards:
                                    card_to_draw = copy_card(random.choice([x for x in player.deck]))
                                    card_to_draw.effects["copied"] = 1
                                    adv.hand.add(card_to_draw)
                            if "in_deck" in carte.effects["rale d'agonie"][1]:
                                if "serviteur" in carte.effects["rale d'agonie"][1] and "if_rale_agonie" in carte.effects["rale d'agonie"][1]:
                                    if [x for x in adv.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]:
                                        card_to_draw = copy_card(random.choice([x for x in adv.deck if x.type == "Serviteur" and "rale d'agonie" in x.effects]))
                                        card_to_draw.base_cost = max(0, card_to_draw.base_cost - 4)
                                        card_to_draw.boost(4, 4, fixed_stats=True)
                                        adv.hand.add(card_to_draw)
                    else:
                        if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            for card in carte.effects["rale d'agonie"][2]:
                                player.hand.add(get_card(card, all_cards))
                        elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                            for card in carte.effects["rale d'agonie"][2]:
                                adv.hand.add(get_card(card, all_cards))
                if "haunt" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if player.hand.cards:
                            haunted_card = random.choice(player.hand.cards)
                            haunted_card.effects["haunted"] = carte.effects["rale d'agonie"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if adv.hand.cards:
                            haunted_card = random.choice(adv.hand.cards)
                            haunted_card.effects["haunted"] = carte.effects["rale d'agonie"][2]
                if "add_deck" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        for card in carte.effects["rale d'agonie"][2]:
                            card_to_add = get_card(card, all_servants)
                            if "boost" in carte.effects["rale d'agonie"][1]:
                                card_to_add.attack = carte.attack + carte.effects["rale d'agonie"][1][-1][0]
                                card_to_add.base_attack = carte.base_attack + carte.effects["rale d'agonie"][1][-1][0]
                                card_to_add.base_health = carte.base_health + carte.effects["rale d'agonie"][1][-1][1]
                                card_to_add.health = card_to_add.base_health
                            player.deck.add(card_to_add)
                        if not "end_deck" in carte.effects["rale d'agonie"][1]:
                            player.deck.shuffle()
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        for card in carte.effects["rale d'agonie"][2]:
                            card_to_add = get_card(card, all_servants)
                            if "boost" in carte.effects["rale d'agonie"][1]:
                                card_to_add.attack = carte.attack + carte.effects["rale d'agonie"][1][-1][0]
                                card_to_add.base_attack = carte.base_attack + carte.effects["rale d'agonie"][1][-1][0]
                                card_to_add.base_health = carte.base_health + carte.effects["rale d'agonie"][1][-1][1]
                                card_to_add.health = card_to_add.base_health
                            adv.deck.add(card_to_add)
                        if not "end_deck" in carte.effects["rale d'agonie"][1]:
                            adv.deck.shuffle()
                if "add_armor" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        player.armor += carte.effects["rale d'agonie"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        adv.armor += carte.effects["rale d'agonie"][2]
                if "equip_weapon" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if player.weapon is not None:
                            player.weapon.health = 0
                            player.dead_weapon = player.weapon
                        player.weapon = get_card(carte.effects["rale d'agonie"][2], all_weapons)
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if adv.weapon is not None:
                            adv.weapon.health = 0
                            adv.dead_weapon = player.weapon
                        adv.weapon = get_card(carte.effects["rale d'agonie"][2], all_weapons)
                if "murmegivre" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        player.effects["murmegivre"] = 3
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        adv.effects["murmegivre"] = 3
                if "hp_boost" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "armure" in carte.effects["rale d'agonie"][1]:
                            if "armure" in player.hp_boost:
                                player.hp_boost["armure"] += carte.effects["rale d'agonie"][2]
                            else:
                                player.hp_boost["armure"] = carte.effects["rale d'agonie"][2]
                        if "attack" in carte.effects["rale d'agonie"][1]:
                            if "attack" in player.hp_boost:
                                player.hp_boost["attack"] += carte.effects["rale d'agonie"][2]
                            else:
                                player.hp_boost["attack"] = carte.effects["rale d'agonie"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        if "armure" in carte.effects["rale d'agonie"][1]:
                            if "armure" in adv.hp_boost:
                                adv.hp_boost["armure"] += carte.effects["rale d'agonie"][2]
                            else:
                                adv.hp_boost["armure"] = carte.effects["rale d'agonie"][2]
                        if "attack" in carte.effects["rale d'agonie"][1]:
                            if "attack" in adv.hp_boost:
                                adv.hp_boost["attack"] += carte.effects["rale d'agonie"][2]
                            else:
                                adv.hp_boost["attack"] = carte.effects["rale d'agonie"][2]
                if "regis" in carte.effects["rale d'agonie"]:
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        player.permanent_buff["regis"] = 1
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        adv.permanent_buff["regis"] = 1
                if "swap" in carte.effects["rale d'agonie"] and target is not None:
                    swapped_card = get_card(carte.name, all_servants)
                    player.hand.add(swapped_card)
                    if ("allié" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        target.effects["vol de vie"] = 1
                        self.invoke_servant(target, player)
                    elif ("ennemi" in carte.effects["rale d'agonie"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie"][1] and carte in adv.servants):
                        target.effects["vol de vie"] = 1
                        self.invoke_servant(target, adv)
            if "rale d'agonie2" in carte.effects and (carte.is_dead() or "rale_applied" in carte.effects):
                if "serviteur" in carte.effects["rale d'agonie2"][1]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre and x != carte]) \
                                if len(
                                [x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre and x != carte]) != 0 else None
                        elif carte.effects["rale d'agonie2"][2] == "nbre_tentacules":
                            nbre_tentacules = len([x for x in adv.servants if x.name == "Tentacule d'ozumat"])
                            if nbre_tentacules == 0 or not player.servants.cards:
                                target = None
                            else:
                                target = random.sample(player.servants.cards, min(nbre_tentacules, len(player.servants)))
                        elif "tous" in carte.effects["rale d'agonie2"][1]:
                            target = player.servants
                        elif "main" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice([x for x in player.hand if x.type == "Serviteur"]) if [x for x in player.hand if x.type == "Serviteur"] else None
                        else:
                            target = random.choice([x for x in self.plt.players[0].servants]) \
                                if len([x for x in self.plt.players[0].servants]) != 0 else None
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "Mort-vivant" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre and x.name != carte.name]) \
                                if len(
                                [x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre and x.name != carte.name]) != 0 else None
                        elif carte.effects["rale d'agonie2"][2] == "nbre_tentacules":
                            nbre_tentacules = len([x for x in player.servants if x.name == "Tentacule d'ozumat"])
                            if nbre_tentacules == 0 or not adv.servants.cards:
                                target = None
                            else:
                                target = random.sample(adv.servants.cards, min(nbre_tentacules, len(adv.servants)))
                        elif "tous" in carte.effects["rale d'agonie2"][1]:
                            target = adv.servants
                        elif "main" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice([x for x in adv.hand if x.type == "Serviteur"]) if [x for x in adv.hand if x.type == "Serviteur"] else None
                        else:
                            target = random.choice([x for x in self.plt.players[1].servants]) \
                                if len([x for x in self.plt.players[1].servants]) != 0 else None
                    elif "tous" in carte.effects["rale d'agonie2"][1]:
                        target = CardGroup(player.servants.cards + adv.servants.cards)
                elif "heros" in carte.effects["rale d'agonie2"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie2"][1]:
                            if carte in adv.servants:
                                target = adv
                            else:
                                carte.effects["rale d'agonie2"] = ["", [""], ""]
                        else:
                            target = adv
                    elif ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "if_enemyturn" in carte.effects["rale d'agonie2"][1]:
                            if carte in adv.servants:
                                target = player
                            else:
                                carte.effects["rale d'agonie2"] = ["", [""], ""]
                        else:
                            target = player
                elif "tous" in carte.effects["rale d'agonie2"][1]:
                    if ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "aléatoire" in carte.effects["rale d'agonie2"][1]:
                            target = random.choice([adv] + adv.servants.cards)
                if "damage" in carte.effects["rale d'agonie2"] and target is not None:
                    if type(target) in (Player, Card):
                        if type(carte.effects["rale d'agonie2"][2]) == list:
                            target.damage(random.choice(carte.effects["rale d'agonie2"][2]), toxic=True if ("toxicite" in carte.effects) else False)
                        else:
                            target.damage(carte.effects["rale d'agonie2"][2], toxic=True if ("toxicite" in carte.effects) else False)
                    else:
                        for card in target:
                            card.damage(carte.effects["rale d'agonie2"][2], toxic=True if "toxicite" in carte.effects else False)
                if "destroy" in carte.effects["rale d'agonie2"] and target is not None:
                    if type(target) == list:
                        for serv in target:
                            serv.blessure = 1000
                            serv.health = max(0, serv.base_health + serv.total_temp_boost[1] - serv.blessure)
                    else:
                        target.blessure = 1000
                        target.health = max(0, target.base_health + target.total_temp_boost[1] - target.blessure)
                if "boost" in carte.effects["rale d'agonie2"]:
                    if target is not None:
                        target.boost(carte.effects["rale d'agonie2"][2][0], carte.effects["rale d'agonie2"][2][1])
                        if "provocation" in carte.effects["rale d'agonie2"][2]:
                            target.effects["provocation"] = 1
                    else:
                        if "next_serv_drawn" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                player.hand.aegwynn = True
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                adv.hand.aegwynn = True
                        if "secret" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                    "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                if player.secrets:
                                    secret_booste = random.choice(player.secrets)
                                    secret_booste.effects["halkias"] = 1
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                    "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                if adv.secrets:
                                    secret_booste = random.choice(adv.secrets)
                                    secret_booste.effects["halkias"] = 1
                if "heal" in carte.effects["rale d'agonie2"] and target is not None and not [x for x in adv.servants if "anti_heal" in x.effects]:
                    if "kvaldir" in player.permanent_buff:
                        target.damage(carte.effects["rale d'agonie2"][2])
                        player.permanent_buff.pop("kvaldir")
                    else:
                        target.heal(carte.effects["rale d'agonie2"][2])
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
                                self.invoke_servant(get_card(carte.effects["rale d'agonie2"][2], all_servants), player)
                            player.mana = 0
                        elif type(carte.effects["rale d'agonie2"][2]) == list:
                            if "if_hydrolodon" in carte.effects["rale d'agonie2"][1] and not "Hydrolodon" in [x.name for x in player.servants]:
                                carte.effects["rale d'agonie2"][2] = []
                            for invoked_servant in carte.effects["rale d'agonie2"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), player)
                        elif "conditional" in carte.effects["rale d'agonie2"][1]:
                            if "if_robaudio" in carte.effects["rale d'agonie2"][1]:
                                if [x for x in adv.hand if x.name == "Rob'audio"]:
                                    for robaudio in [x for x in adv.hand if x.name == "Rob'audio"]:
                                        adv.hand.remove(robaudio)
                                        self.invoke_servant(get_card("Rob'audio", all_servants), player)
                            elif "spend_cadavre" in carte.effects["rale d'agonie2"][1] and player.cadavres >= carte.effects["rale d'agonie2"][1][-1]:
                                player.cadavres -= carte.effects["rale d'agonie2"][1][-1]
                                player.cadavres_spent += carte.effects["rale d'agonie2"][1][-1]
                                self.invoke_servant(get_card(carte.effects["rale d'agonie2"][2], all_servants), player)
                        elif "copy_deck" in carte.effects["rale d'agonie2"][1]:
                            if player.deck.cards:
                                new_servant = get_card(random.choice([x.name for x in player.deck if x.type == "Serviteur"]), all_servants)
                                new_servant.attack, new_servant.base_attack, new_servant.health, new_servant.base_health = 2, 2, 2, 2
                                self.invoke_servant(new_servant, player)
                        elif "in_deck" in carte.effects["rale d'agonie2"][1]:
                            if "lower_attack" in carte.effects["rale d'agonie2"][1] and [x for x in player.deck if x.type == "Serviteur" and x.attack < carte.attack]:
                                invoked_servant = random.choice([x for x in player.deck if x.type == "Serviteur" and x.attack < carte.attack])
                                player.deck.remove(invoked_servant)
                                self.invoke_servant(invoked_servant, player)
                        elif "aléatoire" in carte.effects["rale d'agonie2"][1]:
                            if "cout" in carte.effects["rale d'agonie2"][1]:
                                if 5 in carte.effects["rale d'agonie2"][1]:
                                    while True:
                                        new_servant = random.choice(all_servants)
                                        if new_servant["cost"] == 5 and new_servant["decouvrable"] == 1:
                                            break
                                    new_servant = Card(**new_servant)
                                    self.invoke_servant(new_servant, player)
                            elif "Méca" in carte.effects["rale d'agonie2"][1] and "<=3" in \
                                    carte.effects["rale d'agonie2"][1]:
                                for i in range(2):
                                    while True:
                                        new_servant = random.choice(all_servants)
                                        if new_servant["cost"] <= 3 and new_servant["decouvrable"] == 1 and "Méca" in \
                                                new_servant["genre"]:
                                            break
                                    new_servant = Card(**new_servant)
                                    self.invoke_servant(new_servant, player)
                            elif "Bête" in carte.effects["rale d'agonie2"][1] and "in_deck" in carte.effects["rale d'agonie2"][1]:
                                if [x for x in player.deck if "Bête" in x.genre]:
                                    new_servant = random.choice([x for x in player.deck if "Bête" in x.genre])
                                    self.invoke_servant(new_servant, player)
                        elif "dead_undead" in carte.effects["rale d'agonie2"][1]:
                            if player.dead_zombies:
                                to_invoke = random.choice([get_card(x, all_servants) for x in player.dead_zombies])
                                self.invoke_servant(to_invoke, player)
                        elif "all_serv_indirect" in carte.effects["rale d'agonie2"][1]:
                            if player.dead_indirect:
                                for creature in player.dead_indirect:
                                    if len(player.servants) + len(player.lieux) < 7:
                                        self.invoke_servant(get_card(creature, all_servants), player)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            self.invoke_servant(new_servant, player)
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "mana_dispo" in carte.effects["rale d'agonie2"][1] and adv.mana != 0:
                            new_servant = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            for n in range(adv.mana):
                                self.invoke_servant(new_servant, adv)
                            adv.mana = 0
                        elif type(carte.effects["rale d'agonie2"][2]) == list:
                            if "if_hydrolodon" in carte.effects["rale d'agonie2"][1] and not "Hydrolodon" in [x.name for x in adv.servants]:
                                carte.effects["rale d'agonie2"][2] = []
                            for invoked_servant in carte.effects["rale d'agonie2"][2]:
                                self.invoke_servant(get_card(invoked_servant, all_servants), adv)
                        elif "conditional" in carte.effects["rale d'agonie2"][1]:
                            if "if_robaudio" in carte.effects["rale d'agonie2"][1]:
                                if [x for x in player.hand if x.name == "Rob'audio"]:
                                    for robaudio in [x for x in player.hand if x.name == "Rob'audio"]:
                                        player.hand.remove(robaudio)
                                        self.invoke_servant(get_card("Rob'audio", all_servants), adv)
                            elif "spend_cadavre" in carte.effects["rale d'agonie2"][1] and adv.cadavres >= carte.effects["rale d'agonie2"][1][-1]:
                                adv.cadavres -= carte.effects["rale d'agonie2"][1][-1]
                                self.invoke_servant(get_card(carte.effects["rale d'agonie2"][2], all_servants), adv)
                        elif "copy_deck" in carte.effects["rale d'agonie2"][1]:
                            if adv.deck.cards:
                                new_servant = get_card(random.choice([x.name for x in adv.deck if x.type == "Serviteur"]), all_servants)
                                new_servant.attack, new_servant.base_attack, new_servant.health, new_servant.base_health = 2, 2, 2, 2
                                self.invoke_servant(new_servant, adv)
                        elif "in_deck" in carte.effects["rale d'agonie2"][1]:
                            if "lower_attack" in carte.effects["rale d'agonie2"][1] and [x for x in adv.deck if x.type == "Serviteur" and x.attack < carte.attack]:
                                invoked_servant = random.choice([x for x in adv.deck if x.type == "Serviteur" and x.attack < carte.attack])
                                adv.deck.remove(invoked_servant)
                                self.invoke_servant(invoked_servant, player)
                        elif "aléatoire" in carte.effects["rale d'agonie2"][1]:
                            if "cout" in carte.effects["rale d'agonie2"][1]:
                                if 5 in carte.effects["rale d'agonie2"][1]:
                                    while True:
                                        new_servant = random.choice(all_servants)
                                        if new_servant["cost"] == 5 and new_servant["decouvrable"] == 1:
                                            break
                                    new_servant = Card(**new_servant)
                                    self.invoke_servant(new_servant, adv)
                                elif "Méca" in carte.effects["rale d'agonie2"][1] and "<=3" in \
                                        carte.effects["rale d'agonie2"][1]:
                                    for i in range(2):
                                        while True:
                                            new_servant = random.choice(all_servants)
                                            if new_servant["cost"] <= 3 and new_servant["decouvrable"] == 1 and "Méca" in new_servant["genre"]:
                                                break
                                        new_servant = Card(**new_servant)
                                        self.invoke_servant(new_servant, adv)
                            elif "Bête" in carte.effects["rale d'agonie2"][1] and "in_deck" in carte.effects["rale d'agonie2"][1]:
                                if [x for x in adv.deck if "Bête" in x.genre]:
                                    new_servant = random.choice([x for x in adv.deck if "Bête" in x.genre])
                                    self.invoke_servant(new_servant, adv)
                        elif "dead_undead" in carte.effects["rale d'agonie2"][1]:
                            if adv.dead_zombies:
                                to_invoke = random.choice([get_card(x, all_servants) for x in adv.dead_zombies])
                                self.invoke_servant(to_invoke, adv)
                        elif "all_serv_indirect" in carte.effects["rale d'agonie2"][1]:
                            if adv.dead_indirect:
                                for creature in adv.dead_indirect:
                                    if len(player.servants) + len(player.lieux) < 7:
                                        self.invoke_servant(get_card(creature, all_servants), player)
                        else:
                            new_servant = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            self.invoke_servant(new_servant, adv)
                if "pioche" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "highest_servant" in carte.effects["rale d'agonie2"][1]:
                            card_to_draw = max([x.cost for x in player.deck if x.type == "Serviteur"])
                            card_to_draw = random.choice(
                                [x for x in player.deck if x.type == "Serviteur" and x.cost == card_to_draw])
                            player.deck.remove(card_to_draw)
                            player.hand.add(card_to_draw)
                        elif "sort" in carte.effects["rale d'agonie2"][1] and "givre" in carte.effects["rale d'agonie2"][1]:
                            if [x for x in player.deck if x.type == "Sort" and "Givre" in x.genre]:
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Sort" and "Givre" in x.genre])
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                        elif "serviteur" in carte.effects["rale d'agonie2"][1]:
                            if "reduc" in carte.effects["rale d'agonie2"][1] and [x for x in player.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = max(0, card_to_draw.base_cost - carte.effects["rale d'agonie2"][1][-1])
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                            elif "all_stats5" in carte.effects["rale d'agonie2"][1] and [x for x in player.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = 5
                                card_to_draw.attack = 5
                                card_to_draw.base_attack = 5
                                card_to_draw.health = 5
                                card_to_draw.base_health = 5
                                player.deck.remove(card_to_draw)
                                player.hand.add(card_to_draw)
                        else:
                            player.pick_multi(carte.effects["rale d'agonie2"][2])
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "highest_servant" in carte.effects["rale d'agonie2"][1]:
                            card_to_draw = max([x.cost for x in adv.deck if x.type == "Serviteur"])
                            card_to_draw = random.choice(
                                [x for x in adv.deck if x.type == "Serviteur" and x.cost == card_to_draw])
                            adv.deck.remove(card_to_draw)
                            adv.hand.add(card_to_draw)
                        elif "sort" in carte.effects["rale d'agonie2"][1] and "givre" in carte.effects["rale d'agonie2"][1]:
                            if [x for x in adv.deck if x.type == "Sort" and "Givre" in x.genre]:
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Sort" and "Givre" in x.genre])
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                        elif "serviteur" in carte.effects["rale d'agonie2"][1]:
                            if "reduc" in carte.effects["rale d'agonie2"][1] and [x for x in adv.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = max(0, card_to_draw.base_cost - carte.effects["rale d'agonie2"][1][-1])
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                            elif "all_stats5" in carte.effects["rale d'agonie2"][1] and [x for x in adv.deck if x.type == "Serviteur"]:
                                card_to_draw = random.choice([x for x in adv.deck if x.type == "Serviteur"])
                                card_to_draw.base_cost = 5
                                card_to_draw.attack = 5
                                card_to_draw.base_attack = 5
                                card_to_draw.health = 5
                                card_to_draw.base_health = 5
                                adv.deck.remove(card_to_draw)
                                adv.hand.add(card_to_draw)
                        else:
                            adv.pick_multi(carte.effects["rale d'agonie2"][2])
                if "pioche+invocation" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if [x for x in player.deck if "Mort-vivant" in x.genre]:
                            card_to_draw = random.choice([x for x in player.deck if "Mort-vivant" in x.genre])
                            player.deck.remove(card_to_draw)
                            player.hand.add(card_to_draw)
                            if len(player.servants) + len(player.lieux) < 7:
                                self.invoke_servant(get_card(card_to_draw.name, all_servants), player)
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if [x for x in adv.deck if "Mort-vivant" in x.genre]:
                            card_to_draw = random.choice([x for x in adv.deck if "Mort-vivant" in x.genre])
                            adv.deck.remove(card_to_draw)
                            adv.hand.add(card_to_draw)
                            if len(adv.servants) + len(adv.lieux) < 7:
                                self.invoke_servant(get_card(card_to_draw.name, all_servants), adv)
                if "add_hand" in carte.effects["rale d'agonie2"]:
                    if "sort" in carte.effects["rale d'agonie2"][1]:
                        if "ombre" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                while True:
                                    card_to_add = random.choice(all_spells)
                                    if "Ombre" in card_to_add["genre"] and card_to_add["decouvrable"] == 1:
                                        break
                                card_to_add = Card(**card_to_add)
                                player.hand.add(card_to_add)
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                while True:
                                    card_to_add = random.choice(all_spells)
                                    if "Ombre" in card_to_add["genre"] and card_to_add["decouvrable"] == 1:
                                        break
                                card_to_add = Card(**card_to_add)
                                adv.hand.add(card_to_add)
                        elif "givre" in carte.effects["rale d'agonie2"][1] and "copy" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                if [x for x in player.hand if "Givre" in x.genre]:
                                    for spell in [x for x in player.hand if "Givre" in x.genre]:
                                        if len(player.hand) < 10:
                                            card_to_add = get_card(spell.name, all_spells)
                                            player.hand.add(card_to_add)
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                if [x for x in adv.hand if "Givre" in x.genre]:
                                    for spell in [x for x in adv.hand if "Givre" in x.genre]:
                                        card_to_add = get_card(spell.name, all_spells)
                                        adv.hand.add(card_to_add)
                        elif "arcanes" in carte.effects["rale d'agonie2"][1] and "mage" in carte.effects["rale d'agonie2"][1]:
                            if "brulure" in carte.effects["rale d'agonie2"][1]:
                                if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                    for _ in range(carte.effects["rale d'agonie2"][-1]):
                                        while True:
                                            card_to_add = random.choice(all_spells)
                                            if card_to_add["classe"] == "Mage" and "Arcanes" in card_to_add["genre"]:
                                                break
                                        card_to_add = Card(**card_to_add)
                                        card_to_add.effects["brulure"] = 1
                                        player.hand.add(card_to_add)
                                elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                    for _ in range(carte.effects["rale d'agonie2"][-1]):
                                        while True:
                                            card_to_add = random.choice(all_spells)
                                            if card_to_add["classe"] == "Mage" and "Arcanes" in card_to_add["genre"]:
                                                break
                                        card_to_add = Card(**card_to_add)
                                        card_to_add.effects["brulure"] = 1
                                        adv.hand.add(card_to_add)
                        elif "copy" in carte.effects["rale d'agonie2"][1] and "highest_spell" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                if [x for x in player.hand if x.type == "Sort"]:
                                    highest_spell = max([x.cost for x in player.hand if x.type == "Sort"])
                                    highest_spell = random.choice([x.name for x in player.hand if x.type == "Sort" and x.cost == highest_spell])
                                    player.hand.add(get_card(highest_spell, all_spells))
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                if [x for x in adv.hand if x.type == "Sort"]:
                                    highest_spell = max([x.cost for x in adv.hand if x.type == "Sort"])
                                    highest_spell = random.choice([x.name for x in adv.hand if x.type == "Sort" and x.cost == highest_spell])
                                    adv.hand.add(get_card(highest_spell, all_spells))
                    elif "weapon" in carte.effects["rale d'agonie2"][1]:
                        if "ennemi" in carte.effects["rale d'agonie2"][1]:
                            try:
                                card_to_add = random.choice(all_weapons)
                                adv.hand.add(card_to_add)
                            except:
                                pass
                    elif "serv_transformation" in carte.effects["rale d'agonie2"][1]:
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
                        elif "cost_pv" in carte.effects["rale d'agonie2"][1]:
                            if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                card_to_add = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                                card_to_add.effects["cost_pv"] = ["", 1]
                                player.hand.add(card_to_add)
                            elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                                card_to_add = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                                card_to_add.effects["cost_pv"] = ["", 1]
                                adv.hand.add(card_to_add)
                    elif "cost_pv" in carte.effects["rale d'agonie2"][1]:
                        if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            card_to_add = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            card_to_add.effects["cost_pv"] = ["", 1]
                            player.hand.add(card_to_add)
                        elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            card_to_add = get_card(carte.effects["rale d'agonie2"][2], all_servants)
                            card_to_add.effects["cost_pv"] = ["", 1]
                            adv.hand.add(card_to_add)
                    elif "copy" in carte.effects["rale d'agonie2"][1]:
                        if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            if "from_adv_deck" in carte.effects["rale d'agonie2"][1]:
                                if adv.deck.cards:
                                    card_to_draw = copy_card(random.choice([x for x in adv.deck]))
                                    card_to_draw.effects["copied"] = 1
                                    player.hand.add(card_to_draw)
                            if "in_deck" in carte.effects["rale d'agonie2"][1]:
                                if "serviteur" in carte.effects["rale d'agonie2"][1] and "if_rale_agonie" in carte.effects["rale d'agonie2"][1]:
                                    if [x for x in player.deck if x.type == "Serviteur" and "rale d'agonie2" in x.effects]:
                                        card_to_draw = copy_card(random.choice([x for x in player.deck if x.type == "Serviteur" and "rale d'agonie2" in x.effects]))
                                        card_to_draw.base_cost = max(0, card_to_draw.base_cost - 4)
                                        card_to_draw.boost(4, 4, fixed_stats=True)
                                        player.hand.add(card_to_draw)
                        elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                                "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            if "from_adv_deck" in carte.effects["rale d'agonie2"][1]:
                                if player.deck.cards:
                                    card_to_draw = copy_card(random.choice([x for x in player.deck]))
                                    card_to_draw.effects["copied"] = 1
                                    adv.hand.add(card_to_draw)
                            if "in_deck" in carte.effects["rale d'agonie2"][1]:
                                if "serviteur" in carte.effects["rale d'agonie2"][1] and "if_rale_agonie" in carte.effects["rale d'agonie2"][1]:
                                    if [x for x in adv.deck if x.type == "Serviteur" and "rale d'agonie2" in x.effects]:
                                        card_to_draw = copy_card(random.choice([x for x in adv.deck if x.type == "Serviteur" and "rale d'agonie2" in x.effects]))
                                        card_to_draw.base_cost = max(0, card_to_draw.base_cost - 4)
                                        card_to_draw.boost(4, 4, fixed_stats=True)
                                        adv.hand.add(card_to_draw)
                    else:
                        if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            for card in carte.effects["rale d'agonie2"][2]:
                                player.hand.add(get_card(card, all_cards))
                        elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                            for card in carte.effects["rale d'agonie2"][2]:
                                adv.hand.add(get_card(card, all_cards))
                if "haunt" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if player.hand.cards:
                            haunted_card = random.choice(player.hand.cards)
                            haunted_card.effects["haunted"] = carte.effects["rale d'agonie2"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or ("allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if adv.hand.cards:
                            haunted_card = random.choice(adv.hand.cards)
                            haunted_card.effects["haunted"] = carte.effects["rale d'agonie2"][2]
                if "add_deck" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        for card in carte.effects["rale d'agonie2"][2]:
                            card_to_add = get_card(card, all_servants)
                            if "boost" in carte.effects["rale d'agonie2"][1]:
                                card_to_add.attack = carte.attack + carte.effects["rale d'agonie2"][1][-1][0]
                                card_to_add.base_attack = carte.base_attack + carte.effects["rale d'agonie2"][1][-1][0]
                                card_to_add.base_health = carte.base_health + carte.effects["rale d'agonie2"][1][-1][1]
                                card_to_add.health = card_to_add.base_health
                            player.deck.add(card_to_add)
                        if not "end_deck" in carte.effects["rale d'agonie2"][1]:
                            player.deck.shuffle()
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        for card in carte.effects["rale d'agonie2"][2]:
                            card_to_add = get_card(card, all_servants)
                            if "boost" in carte.effects["rale d'agonie2"][1]:
                                card_to_add.attack = carte.attack + carte.effects["rale d'agonie2"][1][-1][0]
                                card_to_add.base_attack = carte.base_attack + carte.effects["rale d'agonie2"][1][-1][0]
                                card_to_add.base_health = carte.base_health + carte.effects["rale d'agonie2"][1][-1][1]
                                card_to_add.health = card_to_add.base_health
                            adv.deck.add(card_to_add)
                        if not "end_deck" in carte.effects["rale d'agonie2"][1]:
                            adv.deck.shuffle()
                if "add_armor" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        player.armor += carte.effects["rale d'agonie2"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        adv.armor += carte.effects["rale d'agonie2"][2]
                if "equip_weapon" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if player.weapon is not None:
                            player.weapon.health = 0
                            player.dead_weapon = player.weapon
                        player.weapon = get_card(carte.effects["rale d'agonie2"][2], all_weapons)
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if adv.weapon is not None:
                            adv.weapon.health = 0
                            adv.dead_weapon = player.weapon
                        adv.weapon = get_card(carte.effects["rale d'agonie2"][2], all_weapons)
                if "murmegivre" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        player.effects["murmegivre"] = 3
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        adv.effects["murmegivre"] = 3
                if "hp_boost" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "armure" in carte.effects["rale d'agonie2"][1]:
                            if "armure" in player.hp_boost:
                                player.hp_boost["armure"] += carte.effects["rale d'agonie2"][2]
                            else:
                                player.hp_boost["armure"] = carte.effects["rale d'agonie2"][2]
                        if "attack" in carte.effects["rale d'agonie2"][1]:
                            if "attack" in player.hp_boost:
                                player.hp_boost["attack"] += carte.effects["rale d'agonie2"][2]
                            else:
                                player.hp_boost["attack"] = carte.effects["rale d'agonie2"][2]
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        if "armure" in carte.effects["rale d'agonie2"][1]:
                            if "armure" in adv.hp_boost:
                                adv.hp_boost["armure"] += carte.effects["rale d'agonie2"][2]
                            else:
                                adv.hp_boost["armure"] = carte.effects["rale d'agonie2"][2]
                        if "attack" in carte.effects["rale d'agonie2"][1]:
                            if "attack" in adv.hp_boost:
                                adv.hp_boost["attack"] += carte.effects["rale d'agonie2"][2]
                            else:
                                adv.hp_boost["attack"] = carte.effects["rale d'agonie2"][2]
                if "regis" in carte.effects["rale d'agonie2"]:
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        player.permanent_buff["regis"] = 1
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        adv.permanent_buff["regis"] = 1
                if "swap" in carte.effects["rale d'agonie2"] and target is not None:
                    swapped_card = get_card(carte.name, all_servants)
                    player.hand.add(swapped_card)
                    if ("allié" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "ennemi" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        target.effects["vol de vie"] = 1
                        self.invoke_servant(target, player)
                    elif ("ennemi" in carte.effects["rale d'agonie2"][1] and carte in player.servants) or (
                            "allié" in carte.effects["rale d'agonie2"][1] and carte in adv.servants):
                        target.effects["vol de vie"] = 1
                        self.invoke_servant(target, adv)
            if carte.name in ["Treant", "Treant taunt"] and not (carte.is_dead() or "rale_applied" in carte.effects):
                player.treants_invoked += 1
            if player.boost_next:
                for boost in player.boost_next:
                    if boost[0] in carte.genre:
                        carte.boost(boost[1][0], boost[1][1])
                        player.boost_next.remove(boost)
        elif carte.type == "Serviteur" and "titan" in carte.effects:
            if target is not None:
                if "decouverte" in target:
                    if "rale d'agonie" in target and "reduc" in target:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", other="rale d'agonie", reduc=3)
                elif "reduc" in target:
                    if "serv_hand" in target and [x for x in player.hand if x.type == "Serviteur"]:
                        for serv in [x for x in player.hand if x.type == "Serviteur"]:
                            serv.base_cost = max(0, serv.base_cost - 2)
                elif "augment" in target:
                    if "main" in target and "ennemi" in target and adv.hand:
                        for card in adv.hand:
                            card.effects["temp_augment"] = target[-1]
                elif "boost" in target:
                    if "serviteur" in target:
                        if "allié" in target and "tous" in target:
                            for serv in player.servants:
                                serv.boost(target[-1][0], target[-1][1])
                        elif "ennemi" in target and "tous" in target:
                            if "fixed_stats" in target:
                                for serv in adv.servants:
                                    serv.boost(target[-1][0], target[-1][1], fixed_stats=True)
                    elif "self" in target:
                        other_target = None
                        carte.boost(target[-1][0], target[-1][1])
                        if "repeat" in target and len([x for x in player.servants if x != carte]) >= 1:
                            other_target = random.choice([x for x in player.servants if x != carte])
                        if other_target is not None:
                            other_target.boost(target[-1][0], target[-1][1])
                        if "damage" in target:
                            to_damage = random.choice([adv] + adv.servants.cards)
                            to_damage.damage(target[-2], toxic=True if "toxicite" in carte.effects else False)
                            if other_target is not None:
                                to_damage = random.choice([adv] + adv.servants.cards)
                                to_damage.damage(target[-2], toxic=True if "toxicite" in other_target.effects else False)
                        if "pioche" in target:
                            player.pick_multi(target[-2])
                            if other_target is not None:
                                player.pick_multi(target[-2])
                        if "inciblable" in target:
                            carte.effects["inciblable"] = 1
                            if other_target is not None:
                                other_target.effects["inciblable"] = 1
                elif "launch_secret" in target:
                    if "mage" in target:
                        for _ in range(target[-1]):
                            already_secrets = [x.name for x in player.secrets]
                            secret_to_launch = get_card(random.choice([x["name"] for x in all_spells if "secret" in x["effects"] and x["name"] not in already_secrets and x["classe"] == "Mage"]), all_spells)
                            self.apply_effects(secret_to_launch)
                elif "invocation" in target and len(player.servants) + len(player.lieux) < 7:
                    if "aléatoire" in target[1]:
                        if "cost6" in target[1]:
                            while True:
                                to_invoke = random.choice(all_servants)
                                if to_invoke["cost"] == 6 and to_invoke["decouvrable"] == 1 :
                                    break
                            to_invoke = Card(**to_invoke)
                            to_invoke.effects["provocation"] = 1
                            to_invoke.effects["vol de vie"] = 1
                            self.invoke_servant(to_invoke, player)
                    else:
                        for serv in target[1]:
                            if len(player.servants) + len(player.lieux) < 7:
                                to_invoke = get_card(serv, all_servants)
                                self.invoke_servant(to_invoke, player)
                elif "pioche" in target:
                    if "until_full" in target:
                        player.pick_multi(10 - len(player.hand))
                    elif "serviteur" in target:
                        if "fixed_stats" in target:
                            for _ in range(target[-1]):
                                if [x for x in player.deck if x.type == "Serviteur"]:
                                    to_draw_serv = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                    to_draw_serv.boost(2, 2, fixed_stats=True)
                                    to_draw_serv.base_cost = 2
                                    player.deck.remove(to_draw_serv)
                                    player.hand.add(to_draw_serv)
                elif "add_hand" in target:
                    card_to_add = get_card(target[1], all_spells)
                    if card_to_add.name == "Norgannon damage":
                        card_to_add.effects["damage"] = target[-1]
                    player.hand.add(card_to_add)
                elif "heal" in target:
                    if "until_full" in target and "heros" in target:
                        player.health = player.base_health
                elif "mana_refresh" in target:
                    if "until_full" in target:
                        player.mana = player.mana_max
                elif "boost_weapon" in target and player.weapon is not None:
                    if "aura" not in player.weapon.effects:
                        player.weapon.effects["aura"] = ["", ["if_attack"]]
                    if "insensible" in target:
                        player.weapon.effects["aura"].append("boost")
                        player.weapon.effects["aura"][1].append("insensible_attack")
                        player.weapon.attack += target[-1][0]
                    elif "if_attack" in target:
                        if "pioche" in target:
                            player.weapon.effects["aura"].append("pioche")
                        elif "invocation" in target[-1]:
                            player.weapon.effects["aura"].append("invocation")
                            player.weapon.effects["aura"].append("Combattant vrykul")
                if "on_use" in carte.effects:
                    if "invocation" in carte.effects["on_use"]:
                        for card in carte.effects["on_use"][1]:
                            self.invoke_servant(get_card(card, all_servants), player)
                    elif "double_other" in carte.effects["on_use"]:
                        for effect in carte.effects["titan"]:
                            if type(effect) == list:
                                effect[-1] = 2 * effect[-1]
                    elif "decouverte" in carte.effects["on_use"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", other="legendaire")
            elif "cri de guerre" in carte.effects:
                if "equip_weapon" in carte.effects["cri de guerre"]:
                    if player.weapon is not None:
                        player.weapon.health = 0
                        player.dead_weapon = copy_card(player.weapon)
                    player.weapon = get_card(carte.effects["cri de guerre"][2], all_weapons)
        elif carte.type == "Sort":
            if "choix_des_armes" in carte.effects:
                if not player.next_choix_des_armes:
                    self.plt.choix_des_armes = carte
                else:
                    combined_card = get_card(carte.name + " combine", all_spells)
                    combined_card.cost, combined_card.base_cost = 0, 0
                    combined_card.effects["mandatory"] = 1
                    player.hand.add(combined_card)
                    player.next_choix_des_armes = 0
            if "final" in carte.effects and player.mana == 0:
                carte.effects[carte.effects["final"][0]] = carte.effects["final"][1]
                carte.effects.pop("final")
            if "soif de mana" in carte.effects and player.mana_max >= carte.effects["soif de mana"][0]:
                carte.effects[carte.effects["soif de mana"][1]] = carte.effects["soif de mana"][2]
                carte.effects.pop("soif de mana")
            if "play" in carte.effects:
                if "aléatoire" in carte.effects["play"] and "druide" in carte.effects["play"]:
                    for _ in range(carte.effects["play"][-1]):
                        while True:
                            played_card = random.choice(all_spells)
                            if played_card["classe"] == "Druide" and played_card["decouvrable"] == 1:
                                break
                        played_card = Card(**played_card)
                        if "choix_des_armes" in carte.effects:
                            choice = random.randint(0, 1)
                            played_card.effects[played_card.effects["choix_des_armes"][choice][0]] = played_card.effects["choix_des_armes"][choice][1]
                            played_card.effects.pop("choix_des_armes")
                        player.hand.cards.insert(0, played_card)
                        played_card.cost = 0
                        possible_targets = generate_targets(self.plt)[0: 16]
                        player.hand.remove(played_card)
                        possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                        if possible_targets_refined:
                            target = random.choice(possible_targets_refined)
                            if target == 0:
                                target = None
                            elif target == 1:
                                target = player
                            elif target < 9:
                                target = player.servants[target - 2]
                            elif target == 9:
                                target = adv
                            else:
                                target = adv.servants[target - 10]
                        if not ("ciblage" in played_card.effects and target is None):
                            TourEnCours(self.plt).apply_effects(played_card, target)
                if "secret" in carte.effects["play"] and "other_class" in carte.effects["play"]:
                    while True:
                        played_card = random.choice(all_spells)
                        if played_card["classe"] not in ["Neutre", player.classe] and played_card["decouvrable"] == 1 and "secret" in played_card["effects"]:
                            break
                    played_card = Card(**played_card)
                    player.hand.cards.insert(0, played_card)
                    played_card.cost = 0
                    possible_targets = generate_targets(self.plt)[0: 16]
                    player.hand.remove(played_card)
                    possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                    if possible_targets_refined:
                        target = random.choice(possible_targets_refined)
                        if target == 0:
                            target = None
                        elif target == 1:
                            target = player
                        elif target < 9:
                            target = player.servants[target - 2]
                        elif target == 9:
                            target = adv
                        else:
                            target = adv.servants[target - 10]
                    if not ("ciblage" in played_card.effects and target is None):
                        TourEnCours(self.plt).apply_effects(played_card, target)
            if "hero_attack" in carte.effects:
                if type(carte.effects["hero_attack"]) == list:
                    if "conditional" in carte.effects["hero_attack"]:
                        carte.effects["hero_attack"] = 0
                player.inter_attack += carte.effects["hero_attack"]
                player.attack += carte.effects["hero_attack"]
                if "supp_attack" in carte.effects:
                    player.remaining_atk += 0.5
                if "hero_insensible" in carte.effects:
                    player.effects["insensible_attack"] = 1
            elif "equip_weapon" in carte.effects:
                weapon = get_card(carte.effects["equip_weapon"][-1], all_weapons)
                if player.weapon is not None:
                    player.weapon.health = 0
                    player.dead_weapon = player.weapon
                player.weapon = weapon
            if "boost" in carte.effects:
                if target is not None and "arme" not in carte.effects["boost"]:
                    if "fixed_stats" in carte.effects["boost"] and "health" in carte.effects["boost"]:
                        target.boost(0, carte.effects["boost"][-1][1])
                        target.blessure = 0
                        target = None
                        carte.effects.pop("ciblage")
                    else:
                        try:
                            target.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                        except:
                            print(carte, carte.effects, target)
                            raise TypeError
                    if "ruée" in carte.effects["boost"][0]:
                        target.effects["ruée"] = 1
                    if "provocation" in carte.effects["boost"][0]:
                        target.effects["provocation"] = 1
                    if "inciblable" in carte.effects["boost"][0]:
                        target.effects["inciblable"] = 1
                    if "bouclier divin" in carte.effects["boost"][0]:
                        target.effects["bouclier divin"] = 1
                    if "suppr_bouclier" in carte.effects["boost"][0]:
                        target.effects.pop("bouclier divin")
                    if "pietinement" in carte.effects["boost"][0]:
                        target.effects["pietinement"] = 1
                    if "camouflage_temp" in carte.effects["boost"][0]:
                        target.effects["camouflage"] = 0
                    if "en sommeil" in carte.effects["boost"][0]:
                        target.effects["en sommeil"] = carte.effects["boost"][1]
                    if "baston" in carte.effects["boost"][0]:
                        target.effects["baston"] = 1
                    if "swap_carac" in carte.effects["boost"][0]:
                        target.effects["swap_carac"] = 1
                    if "start_turn" in carte.effects["boost"]:
                        target.effects["aura"] = ["suicide", ["start_turn"], "start_turn"]
                    if "allservdamage_atk" in carte.effects["boost"]:
                        for serv in player.servants.cards + adv.servants.cards:
                            if serv != target:
                                serv.damage(target.attack, toxic=True if "toxicite" in target.effects else False)
                    if "dead_neg_atk" in carte.effects["boost"] and target.attack <= 0:
                        target.blessure = 1000
                else:
                    if "deck" in carte.effects["boost"] and "allié" in carte.effects["boost"]:
                        if "serviteur" in carte.effects["boost"] and [x for x in player.deck if x.type == "Serviteur"]:
                            if "tous" in carte.effects["boost"]:
                                for creature in [x for x in player.deck if x.type == "Serviteur"]:
                                    creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                    if "board" in carte.effects["boost"] and "allié" in carte.effects["boost"]:
                        if "serviteur" in carte.effects["boost"] and player.servants:
                            if "tous" in carte.effects["boost"]:
                                for creature in player.servants:
                                    creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                    if "main" in carte.effects["boost"] and "allié" in carte.effects["boost"]:
                        if "serviteur" in carte.effects["boost"] and [x for x in player.hand if x.type == "Serviteur"]:
                            if "tous" in carte.effects["boost"]:
                                for creature in [x for x in player.hand if x.type == "Serviteur"]:
                                    creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                                if "repeat_if_cadavre" in carte.effects and player.cadavres >= carte.effects["repeat_if_cadavre"]:
                                    player.cadavres -= carte.effects["repeat_if_cadavre"]
                                    player.cadavres_spent += carte.effects["repeat_if_cadavre"]
                                    for creature in [x for x in player.hand if x.type == "Serviteur"]:
                                        creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                            elif type(carte.effects["boost"][3]) == int:
                                boosted_servants = random.sample([x for x in player.hand if x.type == "Serviteur"], min(carte.effects["boost"][3], len([x for x in player.hand if x.type == "Serviteur"])))
                                for creature in boosted_servants:
                                    creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                    elif "heros" in carte.effects["boost"] and "allié" in carte.effects["boost"]:
                        player.health += carte.effects["boost"][2][1]
                        player.base_health += carte.effects["boost"][2][1]
                        if "if_cadavre" in carte.effects and player.cadavres >= carte.effects["if_cadavre"]:
                            player.health += carte.effects["boost"][3][1]
                            player.base_health += carte.effects["boost"][3][1]
                        if "temp_vol de vie" in carte.effects["boost"][2]:
                            player.effects["vol de vie"] = 1
                    elif "serviteur" in carte.effects["boost"]:
                        if "allié" in carte.effects["boost"]:
                            if "tous" in carte.effects["boost"] and player.servants.cards:
                                if "spend_cadavre" in carte.effects and player.cadavres >= carte.effects["spend_cadavre"]:
                                    player.cadavres -= carte.effects["spend_cadavre"]
                                    player.cadavres_spent += carte.effects["spend_cadavre"]
                                    carte.effects["boost"][-1] = carte.effects["boost"][-2]
                            for creature in player.servants:
                                creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                                if "inciblable" in carte.effects["boost"]:
                                    creature.effects["inciblable"] = 1
                                if "provocation" in carte.effects["boost"]:
                                    creature.effects["provocation"] = 1
                        elif "ennemi" in carte.effects["boost"]:
                            for creature in adv.servants:
                                creature.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                                if "dead_neg_atk" in carte.effects["boost"] and creature.attack <= 0:
                                    creature.blessure = 1000
                        elif "tous" in carte.effects["boost"]:
                            if "fixed_stats" in carte.effects["boost"] and "health" in carte.effects["boost"]:
                                for servant in player.servants.cards + adv.servants.cards:
                                    servant.health = 1
                                    servant.base_health = 1
                                    servant.blessure = 0
                            elif "aléatoire" in carte.effects["boost"]:
                                if "5_depending_shots" in carte.effects["boost"]:
                                    for _ in range(5):
                                        if [x for x in player.servants.cards + adv.servants.cards if not x.is_dead()]:
                                            cible = random.choice([x for x in player.servants.cards + adv.servants.cards if not x.is_dead()])
                                            if cible in player.servants.cards:
                                                cible.boost(carte.effects["boost"][-1][0], carte.effects["boost"][-1][1])
                                            else:
                                                cible.damage(2 + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                    elif "arme" in carte.effects["boost"]:
                        if "allié" in carte.effects["boost"] and player.weapon is not None:
                            player.weapon.attack += carte.effects["boost"][-1][0]
                            player.weapon.health += carte.effects["boost"][-1][1]
            if "silence" in carte.effects:
                if target is not None:
                    target.base_attack = get_card(target.name, all_servants).base_attack
                    target.attack = get_card(target.name, all_servants).base_attack
                    target.blessure = min(target.blessure, get_card(target.name, all_servants).base_health - 1)
                    target.base_health = get_card(target.name, all_servants).base_health
                    target.effects = {}
                else:
                    if "tous" in carte.effects["silence"]:
                        if "ennemi" in carte.effects["silence"] and adv.servants.cards:
                            for creature in adv.servants:
                                creature.base_attack = get_card(creature.name, all_servants).base_attack
                                creature.attack = get_card(creature.name, all_servants).base_attack
                                creature.blessure = min(creature.blessure, get_card(creature.name, all_servants).base_health - 1)
                                creature.base_health = get_card(creature.name, all_servants).base_health
                                creature.effects = {}
            if "rale d'agonie" in carte.effects:
                if "serviteur" in carte.effects["rale d'agonie"][0]:
                    if "allié" in carte.effects["rale d'agonie"][0]:
                        if "tous" in carte.effects["rale d'agonie"][0] and player.servants.cards:
                            for creature in player.servants:
                                if "rale d'agonie" in creature.effects:
                                    creature.effects["rale d'agonie2"] = carte.effects["rale d'agonie"][1]
                                else:
                                    creature.effects["rale d'agonie"] = carte.effects["rale d'agonie"][1]
                elif target is not None:
                    if "rale d'agonie" in target.effects:
                        target.effects["rale d'agonie2"] = carte.effects["rale d'agonie"]
                    else:
                        target.effects["rale d'agonie"] = carte.effects["rale d'agonie"]
            if "damage" in carte.effects:
                if target is not None:
                    if type(carte.effects["damage"]) == list:
                        if "cadavres_spent" in carte.effects["damage"]:
                            carte.effects["damage"] = 5 + player.cadavres_repartis[0]
                        elif "double" in carte.effects["damage"]:
                            carte.effects["damage"] = carte.effects["damage"][-1]
                            target.damage(carte.effects["damage"] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        elif "pioche_damage" in carte.effects["damage"]:
                            player.pick_multi(carte.effects["damage"][0] + player.spell_damage)
                            carte.effects["damage"] = carte.effects["damage"][0]
                        elif "surplus" in carte.effects["damage"]:
                            carte.effects["damage"] = carte.effects["damage"][-1]
                            if "bouclier divin" not in target.effects and "insensible" not in target.effects:
                                player.damage(carte.effects["damage"] + player.spell_damage - target.health)
                        elif "hero_if_dead_3" in carte.effects["damage"]:
                            carte.effects["damage"] = carte.effects["damage"][-1]
                            if "bouclier divin" not in target.effects and "insensible" not in target.effects and target.health <= carte.effects["damage"]:
                                adv.damage(3 + player.spell_damage)
                        elif type(carte.effects["damage"][0]) == list:
                            if "aléatoire" in carte.effects["damage"][0] and "atk_serv" in carte.effects["damage"][0]:
                                nb_pioupiou = target.attack
                                for _ in range(nb_pioupiou):
                                    if [x for x in adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects]:
                                        cible = random.choice([x for x in adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects])
                                        cible.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        elif "atk_serv" in carte.effects["damage"]:
                            carte.effects["damage"] = target.attack
                        elif "allié_or_adv" in carte.effects["damage"]:
                            if target in [adv] + adv.servants.cards:
                                target.damage(carte.effects["damage"][-1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                            else:
                                target.heal(carte.effects["damage"][1])
                        elif "if_otherclass_played" in carte.effects["damage"]:
                            if player.otherclass_played:
                                carte.effects["damage"] = carte.effects["damage"][1]
                            else:
                                carte.effects["damage"] = carte.effects["damage"][-1]
                    elif carte.effects["damage"] == "hero_attack":
                        carte.effects["damage"] = player.attack
                    if type(carte.effects["damage"]) != list:
                        target.damage(carte.effects["damage"] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                    if "cleave" in carte.effects:
                        if target in adv.servants:
                            index_target = adv.servants.cards.index(target)
                            if index_target != 0:
                                cible_gauche = adv.servants[index_target - 1]
                                cible_gauche.damage(carte.effects["damage"] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                            try:
                                cible_droite = adv.servants[index_target + 1]
                                cible_droite.damage(carte.effects["damage"] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                            except:
                                pass
                        else:
                            index_target = player.servants.cards.index(target)
                            if index_target != 0:
                                cible_gauche = player.servants[index_target - 1]
                                cible_gauche.damage(carte.effects["damage"] + player.spell_damage,
                                                    toxic=True if "toxicite" in carte.effects else False)
                            try:
                                cible_droite = player.servants[index_target + 1]
                                cible_droite.damage(carte.effects["damage"] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                            except:
                                pass
                    if "vol de vie" in carte.effects and "bouclier divin" not in target.effects and not [x for x in adv.servants if "anti_heal" in x.effects]:
                        player.heal(carte.effects["damage"] + player.spell_damage)
                    if "cadavre_if_killed" in carte.effects and target.is_dead():
                        player.cadavres += carte.effects["cadavre_if_killed"]
                    elif "if_killed" in carte.effects and target.is_dead():
                        carte.effects[carte.effects["if_killed"][0]] = carte.effects["if_killed"][1]
                        carte.effects.pop("if_killed")
                    if carte.name == "Decoction melangee":
                        target = None
                elif "ciblage" in carte.effects:
                    pass
                elif "serviteur" in carte.effects["damage"][0]:
                    if "if_cadavre" in carte.effects["damage"][0] and player.cadavres > 0:
                        player.cadavres -= 1
                        player.cadavres_spent += 1
                        for creature in player.servants.cards + adv.servants.cards:
                            creature.damage(carte.effects["damage"][-1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        dead_servants, dead_servants_player = self.plt.update()
                        while dead_servants:
                            for servant in dead_servants:
                                TourEnCours(self.plt).apply_effects(servant)
                                if servant in adv.servants:
                                    adv.servants.remove(servant)
                                else:
                                    player.servants.remove(servant)
                            if [x for x in dead_servants if "reinvoke" in x.effects]:
                                for servant in [x for x in dead_servants if "reinvoke" in x.effects]:
                                    player.servants.add(get_card(servant.name, all_servants))
                            dead_servants, dead_servants_player = self.plt.update()
                    if "repeat_if_cadavre_and_serv" in carte.effects and player.cadavres > 0 and len(player.servants.cards + adv.servants.cards) > 0:
                        TourEnCours(self.plt).apply_effects(carte)
                        """ Application des rales d'agonie """
                        dead_servants, dead_servants_player = self.plt.update()
                        while dead_servants:
                            for servant in dead_servants:
                                TourEnCours(self.plt).apply_effects(servant)
                                if servant in adv.servants:
                                    adv.servants.remove(servant)
                                else:
                                    player.servants.remove(servant)
                            if [x for x in dead_servants if "reinvoke" in x.effects]:
                                for servant in [x for x in dead_servants if "reinvoke" in x.effects]:
                                    player.servants.add(get_card(servant.name, all_servants))
                            dead_servants, dead_servants_player = self.plt.update()
                    elif "ennemi" in carte.effects["damage"][0] and "aléatoire" in carte.effects["damage"][0] and adv.servants:
                        if "deux" in carte.effects["damage"][0] and "relique" in carte.effects:
                            for _ in range(2):
                                if [x for x in adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects]:
                                    target = random.choice([x for x in adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects])
                                    target.damage(carte.effects["damage"][1] + player.reliques - 1 + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        elif "decreasing" in carte.effects["damage"][0]:
                            damage_made = carte.effects["damage"][1]
                            for _ in range(carte.effects["damage"][1]):
                                if [x for x in adv.servants if not x.is_dead()]:
                                    potential_target = random.choice([x for x in adv.servants if not x.is_dead()])
                                    potential_target.damage(damage_made + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                                    damage_made -= 1
                        elif "trois" in carte.effects["damage"][0]:
                            for _ in range(3):
                                if [x for x in adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects]:
                                    target = random.choice([x for x in adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects])
                                    adv.damage(max(0, carte.effects["damage"][1] + player.spell_damage - target.health))
                                    target.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        elif [x for x in adv.servants if not x.is_dead()]:
                            potential_target = random.choice([x for x in adv.servants if not x.is_dead()])
                            potential_target.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                    elif "tous" in carte.effects["damage"][0]:
                        if "double" in carte.effects["damage"][0]:
                            for creature in player.servants.cards + adv.servants.cards:
                                creature.damage(carte.effects["damage"][-1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                                """ Application des rales d'agonie """
                                dead_servants, dead_servants_player = self.plt.update()
                                while dead_servants:
                                    for servant in dead_servants:
                                        TourEnCours(self.plt).apply_effects(servant)
                                        if servant in adv.servants:
                                            adv.servants.remove(servant)
                                        else:
                                            player.servants.remove(servant)
                                    if [x for x in dead_servants if "reinvoke" in x.effects]:
                                        for servant in [x for x in dead_servants if "reinvoke" in x.effects]:
                                            player.servants.add(get_card(servant.name, all_servants))
                                    dead_servants, dead_servants_player = self.plt.update()
                                TourEnCours(self.plt).apply_effects(carte)
                                creature.damage(carte.effects["damage"][-1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        elif "ennemi" in carte.effects["damage"][0]:
                            if adv.servants:
                                for creature in adv.servants:
                                    creature.damage(carte.effects["damage"][-1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                                    if "gel" in carte.effects["damage"][0]:
                                        creature.effects["gel"] = 1
                        elif "atk_serv" in carte.effects["damage"][0]:
                            if player.servants.cards + adv.servants.cards:
                                for creature in player.servants.cards + adv.servants.cards:
                                    creature.damage(creature.attack + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        else:
                            for creature in player.servants.cards + adv.servants.cards:
                                creature.damage(carte.effects["damage"][-1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                                if "invocation_if_dead" in carte.effects["damage"][0] and creature.is_dead():
                                    carte.effects["damage"][0][-1] += 1
                            """ Application des rales d'agonie """
                            dead_servants, dead_servants_player = self.plt.update()
                            while dead_servants:
                                for servant in dead_servants:
                                    TourEnCours(self.plt).apply_effects(servant)
                                    if servant in adv.servants:
                                        adv.servants.remove(servant)
                                    else:
                                        player.servants.remove(servant)
                                if [x for x in dead_servants if "reinvoke" in x.effects]:
                                    for servant in [x for x in dead_servants if "reinvoke" in x.effects]:
                                        player.servants.add(get_card(servant.name, all_servants))
                                dead_servants, dead_servants_player = self.plt.update()
                            if "invocation_if_dead" in carte.effects["damage"][0]:
                                for _ in range(carte.effects["damage"][0][-1]):
                                    if len(player.servants) + len(player.lieux) < 7:
                                        card_to_invoke = get_card(carte.effects["damage"][0][-2], all_servants)
                                        self.invoke_servant(card_to_invoke, player)
                elif "tous" in carte.effects["damage"][0]:
                    if "except_self" in carte.effects["damage"][0]:
                        for entity in [x for x in [player, adv] + player.servants.cards + adv.servants.cards if x!= carte]:
                            entity.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                    elif "ennemi" in carte.effects["damage"][0]:
                        if "aléatoire" in carte.effects["damage"][0]:
                            if "jeu_lumiere" in carte.effects["damage"][0]:
                                nb_targets = 1 + player.jeu_lumiere
                            else:
                                nb_targets = min(carte.effects["damage"][0][-1], len([adv] + adv.servants.cards))
                            for _ in range(nb_targets):
                                if [x for x in [adv] + adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects]:
                                    target = random.choice([x for x in [adv] + adv.servants.cards if not x.is_dead() and not "en sommeil" in x.effects])
                                    target.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                        else:
                            if "double" in carte.effects["damage"][0] and "if_death_undead" in carte.effects["damage"][0] and not player.dead_undeads:
                                carte.effects["damage"][0].remove("double")
                            for entity in [x for x in [adv] + adv.servants.cards]:
                                entity.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                                if "vol de vie" in carte.effects and "bouclier divin" not in entity.effects and not [x for x in adv.servants if "anti_heal" in x.effects]:
                                    player.heal(carte.effects["damage"][1] + player.spell_damage)
                            if "double" in carte.effects["damage"][0]:
                                """ Application des rales d'agonie """
                                dead_servants, dead_servants_player = self.plt.update()
                                while dead_servants:
                                    for servant in dead_servants:
                                        TourEnCours(self.plt).apply_effects(servant)
                                        if servant in adv.servants:
                                            adv.servants.remove(servant)
                                        else:
                                            player.servants.remove(servant)
                                    if [x for x in dead_servants if "reinvoke" in x.effects]:
                                        for servant in [x for x in dead_servants if "reinvoke" in x.effects]:
                                            player.servants.add(get_card(servant.name, all_servants))
                                    dead_servants, dead_servants_player = self.plt.update()
                                for entity in [x for x in [adv] + adv.servants.cards]:
                                    entity.damage(carte.effects["damage"][1] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
                                    if "vol de vie" in carte.effects and "bouclier divin" not in entity.effects and not [x for x in adv.servants if "anti_heal" in x.effects]:
                                        player.heal(carte.effects["damage"][1] + player.spell_damage)
                    elif "allié" in carte.effects["damage"][0]:
                        for entity in [x for x in [player] + player.servants.cards]:
                            entity.damage(carte.effects["damage"][1] + adv.spell_damage, toxic=True if "toxicite" in carte.effects else False)
            if "damage_all_adv_except_target" in carte.effects:
                for entity in [adv] + adv.servants.cards:
                    if entity != target:
                        entity.damage(carte.effects["damage_all_adv_except_target"] + player.spell_damage, toxic=True if "toxicite" in carte.effects else False)
            elif "drain" in carte.effects and target is not None:
                if "allié" in carte.effects["drain"] and "Mort-vivant" in carte.effects["drain"] and [x for x in player.servants if "Mort-vivant" in x.genre]:
                    for creature in [x for x in player.servants if "Mort-vivant" in x.genre]:
                        if not target.is_dead():
                            creature.boost(carte.effects["drain"][-1][0], carte.effects["drain"][-1][1])
                            target.boost(carte.effects["drain"][-1][0], carte.effects["drain"][-1][1])
            if "heal" in carte.effects:
                if target is not None:
                    if "kvaldir" in player.permanent_buff:
                        target.damage(carte.effects["heal"])
                    else:
                        amount_to_heal = carte.effects["heal"][-1] if type(carte.effects["heal"]) == list else carte.effects["heal"]
                        target.heal(amount_to_heal)
                    if "voisin" in carte.effects["ciblage"]:
                        if target in player.servants:
                            index_target = player.servants.cards.index(target)
                            try:
                                if index_target != 0:
                                    if "kvaldir" in player.permanent_buff:
                                        player.servants.cards[index_target - 1].damage(carte.effects["heal"])
                                    else:
                                        player.servants.cards[index_target - 1].heal(carte.effects["heal"])
                            except:
                                pass
                            try:
                                if "kvaldir" in player.permanent_buff:
                                    player.servants.cards[index_target + 1].damage(carte.effects["heal"])
                                else:
                                    player.servants.cards[index_target + 1].heal(carte.effects["heal"])
                            except:
                                pass
                        else:
                            index_target = adv.servants.cards.index(target)
                            try:
                                if index_target != 0:
                                    if "kvaldir" in player.permanent_buff:
                                        adv.servants.cards[index_target - 1].damage(carte.effects["heal"])
                                    else:
                                        adv.servants.cards[index_target - 1].heal(carte.effects["heal"])
                            except:
                                pass
                            try:
                                if "kvaldir" in player.permanent_buff:
                                    adv.servants.cards[index_target + 1].damage(carte.effects["heal"])
                                else:
                                    adv.servants.cards[index_target + 1].heal(carte.effects["heal"])
                            except:
                                pass
                    if "kvaldir" in player.permanent_buff:
                        player.permanent_buff.pop("kvaldir")
                    if type(carte.effects["heal"]) == list:
                        if "if_surplus" in carte.effects["heal"] and target.surplus > 0:
                            if "decouverte" in carte.effects["heal"]:
                                self.plt.cards_chosen = self.choice_decouverte(carte, cost=target.surplus)
                                target.surplus = 0
                else:
                    if "tous" in carte.effects["heal"]:
                        if "allié" in carte.effects["heal"]:
                            for entity in [player] + player.servants.cards:
                                entity.heal(carte.effects["heal"][-1])
            if "add_armor" in carte.effects:
                if type(carte.effects["add_armor"]) == list and "ennemi" in carte.effects["add_armor"]:
                    adv.armor += carte.effects["add_armor"][-1]
                else:
                    player.armor += carte.effects["add_armor"]
            if "infection" in carte.effects:
                if target is not None:
                    target.effects["infection"] = carte.effects["infection"]
                else:
                    if "serviteur" in carte.effects["infection"][0] and "ennemi" in carte.effects["infection"][0]:
                        if "tous" in carte.effects["infection"][0]:
                            if adv.servants:
                                for creature in adv.servants.cards:
                                    creature.effects["infection"] = carte.effects["infection"][-1]
            elif "self_damage" in carte.effects:
                player.damage(carte.effects["self_damage"] + player.spell_damage)
            elif "curse_link" in carte.effects:
                target.effects["curse_link"] = 1
                target.cursed_player = adv
            if "next_spell" in carte.effects:
                if carte.effects["next_spell"] == "double":
                    player.next_spell.append("double")
            if "gel" in carte.effects:
                if type(carte.effects["gel"]) == list and "serviteur" in carte.effects["gel"]:
                    if "tous" in carte.effects["gel"] and "ennemi" in carte.effects["gel"]:
                        for creature in adv.servants:
                            creature.effects["gel"] = 1
                elif target is not None:
                    if "gel" in target.effects and carte.effects["gel"] == 2:
                        target.blessure = 1000
                    else:
                        target.effects["gel"] = 1
            elif "mutation" in carte.effects and target is not None:
                if target in player.servants:
                    player.servants.remove(target)
                    self.invoke_servant(get_card(carte.effects["mutation"], all_servants), player)
                else:
                    try:
                        adv.servants.remove(target)
                        self.invoke_servant(get_card(carte.effects["mutation"], all_servants), adv)
                    except:
                        pass
            elif "resurrect" in carte.effects:
                if "allié" in carte.effects["resurrect"]:
                    if "tous" in carte.effects["resurrect"]:
                        if "under2_cost" in carte.effects["resurrect"] and len(player.servants) < 7 and [x for x in player.all_dead_servants if x.cost <= 2]:
                            cards_to_ressurect = random.sample([x for x in player.all_dead_servants if x.cost <= 2], min(7 - len(player.servants), len([x for x in player.all_dead_servants if x.cost <= 2])))
                            cards_to_ressurect = [get_card(x.name, all_servants) for x in cards_to_ressurect]
                            player.servants.cards = player.servants.cards + cards_to_ressurect
                        if "Bête" in carte.effects["resurrect"] and "cost_sup5" in carte.effects["resurrect"] and len(player.servants) < 7 and [x for x in player.all_dead_servants if x.cost >= 5 and "Bête" in x.genre]:
                            cards_to_ressurect = random.sample([x for x in player.all_dead_servants if x.cost >= 5 and "Bête" in x.genre], min(7 - len(player.servants), len([x for x in player.all_dead_servants if x.cost >= 5 and "Bête" in x.genre])))
                            cards_to_ressurect = [get_card(x.name, all_servants) for x in cards_to_ressurect]
                            player.servants.cards = player.servants.cards + cards_to_ressurect
                    elif "aléatoire" in carte.effects["resurrect"]:
                        if "class" in carte.effects["resurrect"] and [x for x in player.all_dead_servants if x.classe == player.classe]:
                            to_ressurect = random.sample([get_card(x.name, all_servants) for x in [x for x in player.all_dead_servants if x.classe == player.classe]], min(carte.effects["resurrect"][-1], len([x for x in player.all_dead_servants if x.classe == player.classe])))
                            for card in to_ressurect:
                                card.boost(2, 2, fixed_stats = True)
                                self.invoke_servant(card, player)
                        elif "under3_cost" in carte.effects["resurrect"] and [x for x in player.all_dead_servants if x.cost <= 3]:
                            to_ressurect = random.choice([get_card(x.name, all_servants) for x in [x for x in player.all_dead_servants if x.cost <= 3]])
                            self.invoke_servant(to_ressurect, player)
            if "add_mana" in carte.effects:
                player.mana += carte.effects["add_mana"]
            elif "refresh_mana" in carte.effects:
                if carte.effects["refresh_mana"] == "surplus":
                    carte.effects["refresh_mana"] = len([x for x in player.servants if x.surplus > 0])
                player.mana = min(player.mana_max, player.mana + carte.effects["refresh_mana"])
            elif "mana_growth" in carte.effects:
                if "empty" in carte.effects["mana_growth"]:
                    if player.mana_max == player.mana_final:
                        player.hand.add(get_card("Exces de mana", all_spells))
                    player.mana_max = min(player.mana_final, player.mana_max + carte.effects["mana_growth"][-1])
                elif "full" in carte.effects["mana_growth"]:
                    player.mana_max = min(player.mana_final, player.mana_max + carte.effects["mana_growth"][-1])
                    player.mana += carte.effects["mana_growth"][-1]
            if "add_hand" in carte.effects:
                try:
                    if "allié" in carte.effects["add_hand"][0]:
                        if target is not None and carte.effects["add_hand"][1] == "copy_target":
                            card_to_add = get_card(target.name, all_servants)
                            if "boosted" in carte.effects["add_hand"][0]:
                                target.boost(carte.effects["add_hand"][0][-1][0], carte.effects["add_hand"][0][-1][1])
                                card_to_add.boost(carte.effects["add_hand"][0][-1][0], carte.effects["add_hand"][0][-1][1])
                            player.hand.add(card_to_add)
                        else:
                            if "aléatoire" in carte.effects["add_hand"][1]:
                                if "serviteur" in carte.effects["add_hand"][1]:
                                    if "colossal" in carte.effects["add_hand"][1]:
                                        while True:
                                            card_to_add = random.choice(all_servants)
                                            if "colossal" in card_to_add["effects"]:
                                                break
                                        card_to_add = Card(**card_to_add)
                                        card_to_add.cost, card_to_add.base_cost = 1, 1
                                        player.hand.add(card_to_add)
                                    elif "Élémentaire" in carte.effects["add_hand"][1] and "123" in carte.effects["add_hand"][1]:
                                        for i in range(3):
                                            while True:
                                                card_to_add = random.choice(all_servants)
                                                if "Élémentaire" in card_to_add["genre"] and card_to_add["cost"] == i + 1 and card_to_add["decouvrable"] == 1:
                                                    break
                                            card_to_add = Card(**card_to_add)
                                            player.hand.add(card_to_add)
                                    elif "bot_etincelle" in carte.effects["add_hand"][1]:
                                        for _ in range(carte.effects["add_hand"][1][-1]):
                                            while True:
                                                card_to_add = random.choice(all_servants)
                                                if "bot_etincelle" in card_to_add["effects"]:
                                                    break
                                            card_to_add = Card(**card_to_add)
                                            player.hand.add(card_to_add)
                                elif "sort" in carte.effects["add_hand"][1]:
                                    if "until_full" in carte.effects["add_hand"][1]:
                                        while len(player.hand) < 10:
                                            while True:
                                                card_to_add = random.choice(all_spells)
                                                if card_to_add["decouvrable"] == 1:
                                                    break
                                            card_to_add = Card(**card_to_add)
                                            player.hand.add(card_to_add)
                                    elif "Nature" in carte.effects["add_hand"][1]:
                                        for _ in range(carte.effects["add_hand"][1][-1]):
                                            while True:
                                                card_to_add = random.choice(all_spells)
                                                if card_to_add["decouvrable"] == 1 and "Nature" in card_to_add["genre"] and card_to_add["name"] != carte.name:
                                                    break
                                            card_to_add = Card(**card_to_add)
                                            player.hand.add(card_to_add)
                                    elif "mage" in carte.effects["add_hand"][1]:
                                        if "reduc" in carte.effects["add_hand"][1]:
                                            for _ in range(carte.effects["add_hand"][1][-1]):
                                                while True:
                                                    card_to_add = random.choice(all_spells)
                                                    if card_to_add["decouvrable"] == 1 and card_to_add["classe"] == "Mage" and card_to_add["name"] != carte.name:
                                                        break
                                                card_to_add = Card(**card_to_add)
                                                card_to_add.cost = max(0, card_to_add.cost - carte.effects["add_hand"][1][-1])
                                                card_to_add.base_cost = max(0, card_to_add.base_cost - carte.effects["add_hand"][1][-1])
                                                player.hand.add(card_to_add)
                                    elif "other_class" in carte.effects["add_hand"][1]:
                                        if "cost_sup5" in carte.effects["add_hand"][1]:
                                            for _ in range(carte.effects["add_hand"][1][-1]):
                                                while True:
                                                    card_to_add = random.choice(all_spells)
                                                    if card_to_add["classe"] not in ["Neutre", player.classe] and card_to_add["cost"] >= 5 and card_to_add["decouvrable"] == 1:
                                                        break
                                                card_to_add = Card(**card_to_add)
                                                player.hand.add(card_to_add)
                                    else:
                                        for _ in range(carte.effects["add_hand"][1][-1]):
                                            while True:
                                                card_to_add = random.choice(all_spells)
                                                if card_to_add["decouvrable"] == 1 and card_to_add["name"] != carte.name:
                                                    break
                                            card_to_add = Card(**card_to_add)
                                            player.hand.add(card_to_add)
                                else:
                                    if "other_class" in carte.effects["add_hand"][1]:
                                        while True:
                                            card_to_add = random.choice(all_cards)
                                            if card_to_add["decouvrable"] == 1 and card_to_add["classe"] not in [carte.classe, "Neutre"]:
                                                break
                                        card_to_add = Card(**card_to_add)
                                        if "reduc" in carte.effects["add_hand"][1]:
                                            card_to_add.cost = max(0, card_to_add.cost - 3)
                                            card_to_add.base_cost = max(0, card_to_add.base_cost - 3)
                                            player.hand.add(card_to_add)
                                        if "double" in carte.effects["add_hand"][1]:
                                            while True:
                                                card_to_add = random.choice(all_cards)
                                                if card_to_add["decouvrable"] == 1 and card_to_add["classe"] not in [carte.classe, "Neutre"]:
                                                    break
                                            card_to_add = Card(**card_to_add)
                                            if "reduc" in carte.effects["add_hand"][1]:
                                                card_to_add.cost = max(0, card_to_add.cost - 3)
                                                card_to_add.base_cost = max(0, card_to_add.base_cost - 3)
                                                player.hand.add(card_to_add)
                            elif type(carte.effects["add_hand"][1]) == list:
                                for card in carte.effects["add_hand"][1]:
                                    try:
                                        player.hand.add(get_card(card, all_cards))
                                    except:
                                        print(carte, carte.effects, card)
                                        raise TypeError
                except:
                    print(carte, carte.effects)
                    raise TypeError
                if "ennemi" in carte.effects["add_hand"][0]:
                    if "played_this_turn" in carte.effects["add_hand"][1]:
                        for card in player.cards_this_turn:
                            adv.hand.add(get_card(card, all_cards))
                elif type(carte.effects["add_hand"]) == CardGroup:
                    for card in carte.effects["add_hand"]:
                        player.hand.add(get_card(card, all_cards))
                elif type(carte.effects["add_hand"]) == str:
                    player.hand.add(get_card(carte.effects["add_hand"], all_cards))
                elif "end_turn" in carte.effects["add_hand"]:
                    player.end_turn_cards.append(carte.effects["add_hand"][-1])
            elif "return_hand" in carte.effects:
                if target is not None:
                    basic_card = get_card(target.name, all_servants)
                    if target in player.servants:
                        player.servants.remove(target)
                        player.hand.add(basic_card)
                    elif target in adv.servants:
                        adv.servants.remove(target)
                        adv.hand.add(basic_card)
                    else:
                        try:
                            adv.hand.add(basic_card)
                        except:
                            print(carte, carte.effects, target)
                            raise TypeError
                    if type(carte.effects["return_hand"]) == list:
                        if "add_cost" in carte.effects["return_hand"]:
                            basic_card.cost += carte.effects["return_hand"][-1]
                            basic_card.base_cost += carte.effects["return_hand"][-1]
                        elif "reduc" in carte.effects["return_hand"]:
                            basic_card.cost = max(0, basic_card.cost - carte.effects["return_hand"][-1])
                            basic_card.base_cost = max(0, basic_card.base_cost - carte.effects["return_hand"][-1])
                        elif "invocation" in carte.effects["return_hand"]:
                            to_invoke = get_card(carte.effects["return_hand"][-1], all_servants)
                            if "same_stats" in carte.effects["return_hand"]:
                                to_invoke.boost(target.attack, target.health, fixed_stats=True)
                            self.invoke_servant(to_invoke, player)
                else:
                    if "tous" in carte.effects["return_hand"]:
                        if "allié" in carte.effects["return_hand"] and player.servants:
                            for creature in player.servants:
                                player.servants.remove(creature)
                                player.hand.add(creature)
                                player.base_cost = 1
                                player.effects["temp_reduc"] = 1
            elif "transformation_main" in carte.effects:
                if "allié" in carte.effects["transformation_main"]:
                    if "serviteur" in carte.effects["transformation_main"]:
                        for serv in [x for x in player.hand if x.type == "Serviteur"]:
                            index_serv = player.hand.cards.index(serv)
                            while True:
                                new_serv = random.choice(all_servants)
                                if new_serv["decouvrable"] == 1 and new_serv["cost"] == min(10, serv.cost + 3):
                                    break
                            new_serv = Card(**new_serv)
                            new_serv.cost = serv.cost
                            new_serv.base_cost = serv.base_cost
                            player.hand.cards[index_serv] = new_serv
            if "reorganize" in carte.effects:
                player.deck.cards.sort(key=lambda x: x.cost, reverse=True)
            if "pioche" in carte.effects:
                if "allié" in carte.effects["pioche"]:
                    if "arme" in carte.effects["pioche"]:
                        drawable_cards = [x for x in player.deck if x.type == "Arme"]
                        if drawable_cards:
                            card_drawn = random.choice(drawable_cards)
                            player.deck.remove(card_drawn)
                            player.hand.add(card_drawn)
                            if "reduc_if_cadavre" in carte.effects:
                                if player.cadavres >= carte.effects["reduc_if_cadavre"]:
                                    player.cadavres -= carte.effects["reduc_if_cadavre"]
                                    player.cadavres_spent += carte.effects["reduc_if_cadavre"]
                                    card_drawn.cost -= carte.effects["reduc_if_cadavre"]
                                    card_drawn.base_cost -= carte.effects["reduc_if_cadavre"]
                    elif "lowest_serv" in carte.effects["pioche"]:
                        for _ in range(carte.effects["pioche"][-1]):
                            if [x for x in player.deck.cards if x.type == "Serviteur"]:
                                min_health = min([x.health for x in player.deck.cards if x.type == "Serviteur"])
                                drawn_card = random.choice([x for x in player.deck.cards if x.type == "Serviteur" and x.health == min_health])
                                player.deck.remove(drawn_card)
                                player.hand.add(drawn_card)
                    elif "ruée" in carte.effects["pioche"]:
                        for _ in range(carte.effects["pioche"][-1]):
                            if [x for x in player.deck.cards if x.type == "Serviteur" and "ruée" in x.effects]:
                                drawn_card = random.choice([x for x in player.deck.cards if x.type == "Serviteur" and "ruée" in x.effects])
                                player.deck.remove(drawn_card)
                                player.hand.add(drawn_card)
                                if "reduc" in carte.effects["pioche"][1]:
                                    drawn_card.base_cost -= carte.effects["pioche"][1][-1]
                    elif "serviteur" in carte.effects["pioche"]:
                        if "Méca" in carte.effects["pioche"]:
                            if "end_deck" in carte.effects["pioche"]:
                                for i in range(min(carte.effects["pioche"][-1], len(player.deck))):
                                    if "Méca" in player.deck.cards[-(i+1)].genre:
                                        card_to_draw = player.deck.cards[-(i+1)]
                                        player.deck.remove(card_to_draw)
                                        player.hand.add(card_to_draw)
                            else:
                                for _ in range(carte.effects["pioche"][-1]):
                                    if [x for x in player.deck.cards if x.type == "Serviteur" and "Méca" in x.genre]:
                                        drawn_card = random.choice([x for x in player.deck.cards if x.type == "Serviteur"  and "Méca" in x.genre])
                                        player.deck.remove(drawn_card)
                                        player.hand.add(drawn_card)
                        else:
                            indeck_servs = [x for x in player.deck if x.type == "Serviteur"]
                            serv_to_draw = random.sample(indeck_servs, min(len(indeck_servs), carte.effects["pioche"][-1]))
                            for serv in serv_to_draw:
                                player.deck.remove(serv)
                                player.hand.add(serv)
                            if "swap_pv" in carte.effects["pioche"] and len(serv_to_draw) == 2:
                                serv_to_draw[0].health, serv_to_draw[0].base_health, serv_to_draw[1].health, serv_to_draw[1].base_health = \
                                    serv_to_draw[1].health, serv_to_draw[1].base_health, serv_to_draw[0].health, serv_to_draw[0].base_health
                    elif "choix_des_armes" in carte.effects["pioche"]:
                        for _ in range(carte.effects["pioche"][-1]):
                            if [x for x in player.deck.cards if "choix_des_armes" in x.effects]:
                                drawn_card = random.choice([x for x in player.deck.cards if "choix_des_armes" in x.effects])
                                player.deck.remove(drawn_card)
                                if "combined" in carte.effects["pioche"]:
                                    drawn_card = get_card(drawn_card.name + " combine", all_cards)
                                player.hand.add(drawn_card)
                    elif "sort" in carte.effects["pioche"]:
                        if "naga" in carte.effects["pioche"]:
                            for _ in range(carte.effects["pioche"][-1]):
                                if [x for x in player.deck.cards if x.type == "Serviteur" and "Naga" in x.genre]:
                                    drawn_card = random.choice([x for x in player.deck.cards if x.type == "Serviteur" and "Naga" in x.genre])
                                    player.deck.remove(drawn_card)
                                    player.hand.add(drawn_card)
                        for _ in range(carte.effects["pioche"][-1]):
                            if [x for x in player.deck.cards if x.type == "Sort"]:
                                drawn_card = random.choice([x for x in player.deck.cards if x.type == "Sort"])
                                player.deck.remove(drawn_card)
                                player.hand.add(drawn_card)
                                if "decouverte" in carte.effects and "spells_drawn" in carte.effects["decouverte"]:
                                    carte.effects["decouverte"].append(drawn_card.name)
                                if "fragile_copy" in carte.effects["pioche"]:
                                    fragile_copy = copy_card(drawn_card)
                                    fragile_copy.effects["fragile"] = 1
                                    player.hand.add(fragile_copy)
                    else:
                        if "dead_this_turn" in carte.effects["pioche"]:
                            carte.effects["pioche"] = ["allié", len(player.dead_this_turn)]
                        elif "until_adv" in carte.effects["pioche"] and len(player.hand) < len(adv.hand):
                            player.pick_multi(len(adv.hand) - len(player.hand))
                        elif "if_empty_hand" in carte.effects["pioche"] and len(player.hand) == 0:
                            carte.effects["pioche"][-1] = 1
                        elif "return_deck_lr" in carte.effects["pioche"]:
                            if player.hand.cards:
                                left_card = player.hand.cards[0]
                                player.hand.remove(left_card)
                                player.deck.add(left_card)
                            if player.hand.cards:
                                right_card = player.hand.cards[-1]
                                player.hand.remove(right_card)
                                player.deck.add(right_card)
                            player.deck.shuffle()
                        if "if_cadavre" in carte.effects:
                            if player.cadavres >= carte.effects["if_cadavre"]:
                                player.cadavres -= carte.effects["if_cadavre"]
                                player.cadavres_spent += carte.effects["if_cadavre"]
                                player.pick_multi(carte.effects["pioche"][1])
                        player.pick_multi(carte.effects["pioche"][-1])
                        if "if_not_serv" in carte.effects and player.hand[-1].type != "Serviteur":
                            lowest_health = min([x.health for x in adv.servants.cards + [adv]])
                            target = random.choice([x for x in adv.servants.cards + [adv] if x.health == lowest_health])
                            target.damage(carte.effects["if_not_serv"], toxic=True if "toxicite" in carte.effects else False)
                        elif "reduc" in carte.effects["pioche"]:
                            if "relique" in carte.effects:
                                for card in player.hand.cards[-carte.effects["pioche"][-1]:]:
                                    card.base_cost = max(0, card.base_cost - player.reliques)
                    if "shuffle" in carte.effects["pioche"]:
                        player.deck.shuffle()
                elif "ennemi" in carte.effects["pioche"]:
                    adv.pick_multi(carte.effects["pioche"][-1])
            elif "propagation" in carte.effects and target is not None:
                if "rale d'agonie" in carte.effects["propagation"]:
                    if target in player.servants and len(player.servants) > 1:
                        index_target = player.servants.cards.index(target)
                        if index_target == 0:
                            if "rale d'agonie" in player.servants[1].effects:
                                player.servants[1].effects["rale d'agonie2"] = target.effects["rale d'agonie"]
                            else:
                                try:
                                    player.servants[1].effects["rale d'agonie"] = target.effects["rale d'agonie"]
                                except:
                                    print(carte, carte.effects, target, target.effects)
                                    raise TypeError
                        elif index_target == len(player.servants) - 1:
                            if "rale d'agonie" in player.servants[1].effects:
                                player.servants[len(player.servants) - 2].effects["rale d'agonie2"] = target.effects["rale d'agonie"]
                            else:
                                player.servants[1].effects["rale d'agonie"] = target.effects["rale d'agonie"]
                        else:
                            if "rale d'agonie" in player.servants[index_target - 1].effects:
                                player.servants[index_target - 1].effects["rale d'agonie2"] = target.effects["rale d'agonie"]
                            else:
                                player.servants[index_target - 1].effects["rale d'agonie"] = target.effects["rale d'agonie"]
                            if "rale d'agonie" in player.servants[index_target + 1].effects:
                                player.servants[index_target + 1].effects["rale d'agonie2"] = target.effects["rale d'agonie"]
                            else:
                                player.servants[index_target + 1].effects["rale d'agonie"] = target.effects["rale d'agonie"]
                    elif target in adv.servants and len(adv.servants) > 1:
                        index_target = adv.servants.cards.index(target)
                        if index_target == 0:
                            if "rale d'agonie" in adv.servants[1].effects:
                                adv.servants[1].effects["rale d'agonie2"] = target.effects["rale d'agonie"]
                            else:
                                adv.servants[1].effects["rale d'agonie"] = target.effects["rale d'agonie"]
                        elif index_target == len(adv.servants) - 1:
                            if "rale d'agonie" in adv.servants[1].effects:
                                adv.servants[len(adv.servants) - 2].effects["rale d'agonie2"] = target.effects[
                                    "rale d'agonie"]
                            else:
                                adv.servants[1].effects["rale d'agonie"] = target.effects["rale d'agonie"]
                        else:
                            if "rale d'agonie" in adv.servants[index_target - 1].effects:
                                adv.servants[index_target - 1].effects["rale d'agonie2"] = target.effects[
                                    "rale d'agonie"]
                            else:
                                adv.servants[index_target - 1].effects["rale d'agonie"] = target.effects[
                                    "rale d'agonie"]
                            if "rale d'agonie" in adv.servants[index_target + 1].effects:
                                adv.servants[index_target + 1].effects["rale d'agonie2"] = target.effects[
                                    "rale d'agonie"]
                            else:
                                adv.servants[index_target + 1].effects["rale d'agonie"] = target.effects[
                                    "rale d'agonie"]
            if "invocation" in carte.effects:
                if "until_cadavre" in carte.effects["invocation"]:
                    if player.cadavres > 0:
                        invoked_creatures = []
                        for cadavre in range(min(player.cadavres, carte.effects["invocation"][-1])):
                            invoked_creatures.append(carte.effects["invocation"][0])
                        player.cadavres -= min(player.cadavres, carte.effects["invocation"][-1])
                        player.cadavres_spent += min(player.cadavres, carte.effects["invocation"][-1])
                        carte.effects["invocation"] = invoked_creatures
                    else:
                        carte.effects["invocation"] = []
                elif "until_full" in carte.effects["invocation"]:
                    if "Mort-vivant" in carte.effects["invocation"]:
                        creatures_invoked = []
                        nb_invoked = 7 - len(player.servants) - len(player.lieux)
                        for i in range(nb_invoked):
                            creatures_invoked.append(random.choice([x["name"] for x in all_servants if "Mort-vivant" in x["genre"] and x["decouvrable"] == 1]))
                        carte.effects["invocation"] = creatures_invoked
                    elif "from_deck" in carte.effects["invocation"]:
                        if "tous" in carte.effects["invocation"]:
                            while [x for x in player.deck.cards + adv.deck.cards if x.type == "Serviteur"] and len(player.servants) + len(player.lieux) < 7 and len(adv.servants) + len(adv.lieux) < 7:
                                if [x for x in player.deck if x.type == "Serviteur"]:
                                    to_invoke = random.choice([x for x in player.deck if x.type == "Serviteur"])
                                    player.deck.remove(to_invoke)
                                    self.invoke_servant(to_invoke, player)
                                if [x for x in adv.deck if x.type == "Serviteur"]:
                                    to_invoke = random.choice([x for x in adv.deck if x.type == "Serviteur"])
                                    adv.deck.remove(to_invoke)
                                    self.invoke_servant(to_invoke, adv)
                        carte.effects["invocation"] = []
                elif "cadavres_spent" in carte.effects["invocation"]:
                    carte.effects["invocation"] = ["Fanshee"] * (2 + player.cadavres_repartis[3])
                elif "aléatoire" in carte.effects["invocation"]:
                    if "cost3" in carte.effects["invocation"]:
                        carte.effects["invocation"] = [random.choice([x["name"] for x in all_servants if x["cost"] == 3 and x["decouvrable"] == 1])]
                        if carte.effects["invocation"][-1] == 2:
                            carte.effects["invocation"].append(random.choice([x["name"] for x in all_servants if x["cost"] == 3 and x["decouvrable"] == 1]))
                    elif "cost6" in carte.effects["invocation"]:
                        carte.effects["invocation"] = [random.choice([x["name"] for x in all_servants if x["cost"] == 6 and x["decouvrable"] == 1])]
                    elif "graine" in carte.effects["invocation"]:
                        if "double" in carte.effects["invocation"]:
                            carte.effects["invocation"] = random.sample([x["name"] for x in all_servants if "graine" in x["effects"]], 2)
                        else:
                            carte.effects["invocation"] = [random.choice([x["name"] for x in all_servants if "graine" in x["effects"]])]
                    elif "compagnon" in carte.effects["invocation"]:
                        carte.effects["invocation"] = [random.choice([x["name"] for x in all_servants if "compagnon" in x["effects"]])]
                elif "spell_damage" in carte.effects["invocation"]:
                    carte.effects["invocation"] = [carte.effects["invocation"][0]] * (player.spell_damage + 1)
                elif "main" in carte.effects["invocation"]:
                    if "highest_bête" in carte.effects["invocation"]:
                        if [x for x in player.hand if x.type == "Serviteur" and "Bête" in x.genre]:
                            highest_cost = max([x.cost for x in player.hand if x.type == "Serviteur" and "Bête" in x.genre])
                            invoked_servant = random.choice([x.name for x in player.hand if x.type == "Serviteur" and "Bête" in x.genre and x.cost == highest_cost])
                            carte.effects["invocation"] = [invoked_servant]
                        else:
                            carte.effects["invocation"] = []
                elif "in_deck" in carte.effects["invocation"]:
                    if "cost_1" in carte.effects["invocation"]:
                        if [x for x in player.deck if x.type == "Serviteur" and x.cost == 1]:
                            potential_cards = [x for x in player.deck if x.type == "Serviteur" and x.cost == 1]
                            cards_to_invoke = random.sample(potential_cards, min(carte.effects["invocation"][-1], len(potential_cards)))
                            for serv in cards_to_invoke:
                                player.deck.remove(serv)
                                self.invoke_servant(serv, player)
                                if "provocation" in carte.effects["invocation"]:
                                    serv.effects["provocation"] = 1
                        carte.effects["invocation"] = []
                if "conditional" in carte.effects["invocation"]:
                    if "no_serv_deck" in carte.effects["invocation"]:
                        if [x for x in player.deck if x.type == "Serviteur"]:
                            carte.effects["invocation"] = carte.effects["invocation"][-2]
                        else:
                            carte.effects["invocation"] = carte.effects["invocation"][-1]
                    elif "dead_demon" in carte.effects["invocation"]:
                        if player.dead_demons:
                            carte.effects["invocation"] = random.sample([x.name for x in player.dead_demons], min(len(player.dead_demons), carte.effects["invocation"][-1]))
                        else:
                            carte.effects["invocation"] = []
                    elif "ecoles_jouees" in carte.effects["invocation"]:
                        if player.ecoles_jouees:
                            carte.effects["invocation"] = [carte.effects["invocation"][0]] * min(7, len(player.ecoles_jouees))
                        else:
                            carte.effects["invocation"] = []
                for creature in carte.effects["invocation"]:
                    if len(adv.servants) + len(adv.lieux) < 7:
                        try:
                            invoked_creature = get_card(creature, all_servants)
                        except:
                            print(carte, carte.effects)
                            raise TypeError
                        if "trigger" in carte.effects:
                            if carte.name == "Manoeuvre d'urgence":
                                invoked_creature.effects["en sommeil"] = 1
                            self.invoke_servant(invoked_creature, adv)
                        else:
                            self.invoke_servant(invoked_creature, player)
                        if "boosted_invoked" in carte.effects:
                            invoked_creature.boost(carte.effects["boosted_invoked"][0], carte.effects["boosted_invoked"][1])
                            if "en sommeil" in carte.effects["boosted_invoked"]:
                                invoked_creature.effects["en sommeil"] = carte.effects["boosted_invoked"][-1]
                        if "spend_cadavre" in carte.effects and player.cadavres >= carte.effects["spend_cadavre"][0] and "reincarnation" in carte.effects["spend_cadavre"]:
                            invoked_creature.effects["reincarnation"] = 1
                        elif carte.name == "Vive explosion necrotique":
                            invoked_creature.boost(player.cadavres_repartis[1], player.cadavres_repartis[2])
                        elif "relique" in carte.effects:
                            invoked_creature.boost(player.reliques - 1, player.reliques - 1)
                        elif carte.name == "Croissance miraculeuse":
                            invoked_creature.attack = min(10, len(player.hand))
                            invoked_creature.base_attack = min(10, len(player.hand))
                            invoked_creature.health = min(10, len(player.hand))
                            invoked_creature.base_health = min(10, len(player.hand))
                        elif carte.name == "Inspiration elementaire":
                            bonus_effect = random.choice(["ruée", "vol de vie", "bouclier divin", "provocation", "furie des vents", "camouflage", "reincarnation", "toxicite"])
                            invoked_creature.effects[bonus_effect] = 1
                if carte.name == "Fonction de jure":
                    for serv in [x for x in player.servants if x.name == "Recrue de la main d'argent"]:
                        serv.boost(1, 1)
                if "spend_cadavre" in carte.effects and player.cadavres >= carte.effects["spend_cadavre"][0]:
                    player.cadavres -= carte.effects["spend_cadavre"][0]
                    player.cadavres_spent += carte.effects["spend_cadavre"][0]
            elif "copy" in carte.effects and target is not None:
                if "same_stats" in carte.effects["copy"]:
                    to_invoke = get_card(carte.effects["copy"][0], all_servants)
                    to_invoke.attack, to_invoke.base_attack = target.attack, target.base_attack
                    to_invoke.health, to_invoke.base_health = target.health, target.base_health
                    to_invoke.blessure = target.blessure
                else:
                    to_invoke = copy_card(target)
                if "debuff" in carte.effects["copy"]:
                    if "fragile" in carte.effects["copy"]:
                        to_invoke.effects["fragile"] = 1
                        target.effects["fragile"] = 1
                elif "boosted" in carte.effects["copy"]:
                    to_invoke.boost(carte.effects["copy"][1][0], carte.effects["copy"][1][1])
                for _ in range(carte.effects["copy"][-1]):
                    self.invoke_servant(to_invoke, player)
                if "add_deck" in carte.effects and target is not None:
                    target = None
            if "add_deck" in carte.effects:
                if "allié" in carte.effects["add_deck"][0]:
                    if target is not None:
                        if "end_deck" in carte.effects["add_deck"][0]:
                            player.deck.add(target)
                            if target in adv.servants:
                                adv.servants.remove(target)
                    else:
                        if "sort" in carte.effects["add_deck"][0]:
                            if type(carte.effects["add_deck"][1]) == list and "fix_cost" in carte.effects["add_deck"][1]:
                                for _ in range(carte.effects["add_deck"][2]):
                                    while True:
                                        card_to_add = random.choice(all_spells)
                                        if card_to_add["decouvrable"] == 1:
                                            break
                                    card_to_add = Card(**card_to_add)
                                    player.deck.add(card_to_add)
                                player.deck.shuffle()
                        elif type(carte.effects["add_deck"][1]) == list:
                            for element in carte.effects["add_deck"][1]:
                                player.deck.add(get_card(element, all_cards))
                            if not "end_deck" in carte.effects["add_deck"][0]:
                                player.deck.shuffle()
            if "attack+invoke" in carte.effects:
                if "serviteur" in carte.effects["attack+invoke"] and "allié" in carte.effects["attack+invoke"]:
                    if "tous" in carte.effects["attack+invoke"] and len(player.servants) > 0:
                        deadies = []
                        for creature in player.servants:
                            self.attaquer(creature, target)
                            if creature.is_dead():
                                deadies.append(get_card(creature.name, all_servants))
                            if target.is_dead():
                                break
                        if deadies:
                            for creature in deadies:
                                if len(player.servants) + len(player.lieux) < 7:
                                    self.invoke_servant(creature, player)
                else:
                    if "crea" in carte.effects["attack+invoke"]:
                        to_invoke = carte.effects["attack+invoke"][-1]
                        if len(adv.servants) + len(adv.lieux) < 7:
                            self.invoke_servant(to_invoke, adv)
                            try:
                                if not target.is_dead():
                                    self.attaquer(to_invoke, target)
                            except:
                                print(target)
                                raise TypeError
                    else:
                        for creature in carte.effects["attack+invoke"]:
                            to_invoke = get_card(creature, all_servants)
                            if len(adv.servants) + len(adv.lieux) < 7:
                                self.invoke_servant(to_invoke, adv)
                                try:
                                    if not target.is_dead():
                                        self.attaquer(to_invoke, target)
                                except:
                                    print(target)
                                    raise TypeError
            elif "attack_heros" in carte.effects:
                if "serviteur" in carte.effects["attack_heros"] and "ennemi" in carte.effects["attack_heros"]:
                    if "tous" in carte.effects["attack_heros"] and len(adv.servants) > 0:
                        for creature in adv.servants:
                            self.attaquer(player, creature)
            elif "attack" in carte.effects:
                if "baston" in carte.effects["attack"] and "copy_dead" in carte.effects["attack"]:
                    bastonned = [x for x in adv.servants if "baston" in x.effects][0]
                    self.attaquer(target, bastonned)
                    if target.is_dead():
                        player.hand.add(get_card(target.name, all_servants))
                    if bastonned.is_dead():
                        player.hand.add(get_card(bastonned.name, all_servants))
                elif "swap_carac" in carte.effects["attack"]:
                    if [x for x in adv.servants if "swap_carac" in x.effects]:
                        bastonned = [x for x in adv.servants if "swap_carac" in x.effects][0]
                        bastonned.blessure, target.blessure = 0, 0
                        inter_stats = [bastonned.attack, bastonned.health].copy()
                        bastonned.boost(target.attack, target.health, fixed_stats=True)
                        target.boost(inter_stats[0], inter_stats[1], fixed_stats=True)
                    else:
                        bastonned = [x for x in player.servants if "swap_carac" in x.effects][0]
                        bastonned.blessure, target.blessure = 0, 0
                        inter_stats = [bastonned.attack, bastonned.health].copy()
                        bastonned.boost(target.attack, target.health, fixed_stats=True)
                        target.boost(inter_stats[0], inter_stats[1], fixed_stats=True)
            if "destroy" in carte.effects:
                if target is not None:
                    target.blessure = 1000
                    if type(carte.effects["destroy"]) == list and "heal" in carte.effects["destroy"]:
                        if "allié" in carte.effects["destroy"] and "tous" in carte.effects["destroy"] and "pv" in carte.effects["destroy"]:
                            for entity in [player] + player.servants.cards:
                                if "kvaldir" in player.permanent_buff:
                                    entity.damage(carte.effects["heal"])
                                else:
                                    entity.heal(target.health)
                            if "kvaldir" in player.permanent_buff:
                                player.permanent_buff.remove("kvaldir")
                else:
                    try:
                        if "highest_atq_adv" in carte.effects["destroy"] and adv.servants.cards:
                            highest_attack = max([x.attack for x in adv.servants])
                            target = random.choice([x for x in adv.servants if x.attack == highest_attack])
                            target.blessure = 1000
                        elif "tous" in carte.effects["destroy"]:
                            if "if_atk_sup5" in carte.effects["destroy"] and [x for x in player.servants.cards + adv.servants.cards if x.attack >= 5]:
                                for creature in [x for x in player.servants.cards + adv.servants.cards if x.attack >= 5]:
                                    creature.blessure = 1000
                            elif "if_atk_inf3" in carte.effects["destroy"] and [x for x in player.servants.cards + adv.servants.cards if x.attack <= 3]:
                                for creature in [x for x in player.servants.cards + adv.servants.cards if x.attack <= 3]:
                                    creature.blessure = 1000
                            elif "if_atk_inf6" in carte.effects["destroy"] and [x for x in player.servants.cards + adv.servants.cards if x.attack <= 6]:
                                for creature in [x for x in player.servants.cards + adv.servants.cards if x.attack <= 6]:
                                    creature.blessure = 1000
                            else:
                                for servant in player.servants.cards + adv.servants.cards:
                                    servant.blessure = 1000
                                    if "copies" in carte.effects["destroy"]:
                                        if [x for x in player.hand if x.name == servant.name]:
                                            for crea in [x for x in player.hand if x.name == servant.name]:
                                                player.hand.remove(crea)
                                        if [x for x in adv.hand if x.name == servant.name]:
                                            for crea in [x for x in adv.hand if x.name == servant.name]:
                                                adv.hand.remove(crea)
                                        if [x for x in player.deck if x.name == servant.name]:
                                            for crea in [x for x in player.deck if x.name == servant.name]:
                                                player.deck.remove(crea)
                                        if [x for x in adv.deck if x.name == servant.name]:
                                            for crea in [x for x in adv.deck if x.name == servant.name]:
                                                adv.deck.remove(crea)
                        elif "aléatoire" in carte.effects["destroy"]:
                            if "ennemi" in carte.effects["destroy"] and adv.servants.cards:
                                cibles = random.sample(adv.servants.cards, min(len(adv.servants.cards), carte.effects["destroy"][-1]))
                                for cible in cibles:
                                    cible.blessure = 1000
                    except:
                        print(carte, carte.effects)
                        raise TypeError
            elif "destroy+invoke" in carte.effects:
                if target is not None:
                    player.servants.remove(target)
                    to_invoke = get_card(carte.effects["destroy+invoke"][-1], all_servants)
                    to_invoke.effects["rale d'agonie"][-1] = [target.name]
                    self.invoke_servant(to_invoke, adv)
                else:
                    if "serviteur" in carte.effects["destroy+invoke"] and "allié" in carte.effects["destroy+invoke"] and "tous" in carte.effects["destroy+invoke"]:
                        if "Mort-vivant" in carte.effects["destroy+invoke"] and [x for x in player.servants if "Mort-vivant" in x.genre]:
                            for creature in [x for x in player.servants if "Mort-vivant" in x.genre]:
                                creature.blessure = 1000
                                creature.effects["reinvoke"] = 1
            elif "remove" in carte.effects:
                if target is not None:
                    if target in player.servants:
                        player.servants.remove(target)
                    else:
                        adv.servants.remove(target)
            if "reduc" in carte.effects and not "self" in carte.effects["reduc"]:
                if "permanent" in carte.effects["reduc"] and "main" in carte.effects["reduc"]:
                    if "sort" in carte.effects["reduc"]:
                        if [x for x in player.hand if x.type == "Sort"]:
                            for spell in [x for x in player.hand if x.type == "Sort"]:
                                spell.base_cost = max(0, spell.base_cost - carte.effects["reduc"][-1])
                    elif "serviteur" in carte.effects["reduc"]:
                        if "Méca" in carte.effects["reduc"]:
                            if [x for x in player.hand if x.type == "Serviteur" and "Méca" in x.genre]:
                                for spell in [x for x in player.hand if x.type == "Serviteur" and "Méca" in x.genre]:
                                    spell.base_cost = max(0, spell.base_cost - carte.effects["reduc"][-1])
                else:
                    if [carte.effects["reduc"][0][0], carte.effects["reduc"][0][3], carte.effects["reduc"][1], carte.effects["reduc"][0][2]] not in player.discount_next:
                        player.discount_next.append([carte.effects["reduc"][0][0], carte.effects["reduc"][0][3], carte.effects["reduc"][1], carte.effects["reduc"][0][2]])
            elif "augment" in carte.effects:
                if "ennemi" in carte.effects["augment"]:
                    adv.augment.append([carte.effects["augment"][0], carte.effects["augment"][2], carte.effects["augment"][3]])
            if "cadavre" in carte.effects:
                player.cadavres += carte.effects["cadavre"]
            if "reveil" in carte.effects:
                if "graine" in carte.effects["reveil"]:
                    for servant in [x for x in player.servants if "graine" in x.effects and "en sommeil" in x.effects]:
                        servant.effects["en sommeil"] -= 1
                        if servant.effects["en sommeil"] == 0:
                            servant.effects.pop("en sommeil")
                            if "insensible" in servant.effects:
                                servant.effects.pop("insensible")
                            if "awaken" in servant.effects:
                                servant.effects["cri de guerre"] = servant.effects["awaken"]
                                servant.effects.pop("awaken")
            if "decouverte" in carte.effects:
                if "tous" in carte.effects["decouverte"]:
                    if "bleu" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, other="bleu")
                    elif "marginal" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, other="marginal")
                    elif "non_neutre" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([x for x in player.deck if x.classe != "Neutre"]))
                elif "sort" in carte.effects["decouverte"]:
                    if "Fiel" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", genre="Fiel")
                    if "ombre" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", genre="Ombre")
                    elif "reduc" in carte.effects["decouverte"]:
                        if "temp_turn" in carte.effects["decouverte"]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="temp_turn", reduc=carte.effects["decouverte"][-1])
                        elif "permanent" in carte.effects["decouverte"]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", reduc=carte.effects["decouverte"][-1])
                    elif "in_deck" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([x for x in player.deck if x.type == "Sort"]))
                    elif "secret" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="Secret")
                        if "other_class" in carte.effects["decouverte"]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="Secret", classe="other_class")
                    elif "decoction" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="decoction")
                    elif "not_used_ecole" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="not_used_ecole")
                    elif "cost_under3" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="institutrice")
                    elif "already_played" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([get_card(x, all_spells) for x in player.spells_played]))
                    else:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort")
                elif "serviteur" in carte.effects["decouverte"]:
                    if "in_deck" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([x for x in player.deck if x.type == "Serviteur"]))
                        if "Méca" in carte.effects["decouverte"]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([x for x in player.deck if x.type == "Serviteur" and "Méca" in x.genre]))
                    elif "dragon" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Dragon"])
                    elif "Méca" in carte.effects["decouverte"]:
                        if "other_class" in carte.effects["decouverte"]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", genre=["Méca"], classe="other")
                    elif "cost" in carte.effects["decouverte"]:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur", cost=carte.effects["decouverte"][-1])
                    elif "legendaire" in carte.effects["decouverte"]:
                        if "reduc" in carte.effects["decouverte"]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, type="serviteur",
                                                                           reduc=carte.effects["decouverte"][-1],
                                                                           other="legendaire")
                elif "hand_to_deck" in carte.effects["decouverte"] and player.hand.cards:
                    self.plt.cards_hands_to_deck = [CardGroup(random.sample(player.hand.cards, min(3, len(player.hand.cards))))]
                elif "institutrice" in carte.effects["decouverte"]:
                    self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="institutrice")
                    player.copies_to_deck = 2
                elif "ames_liees" in carte.effects["decouverte"]:
                    self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup(player.ames_liees))
                elif "in_deck" in carte.effects["decouverte"] and player.deck.cards:
                    if "Bête" in carte.effects["decouverte"]:
                        if [x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]:
                            self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]))
                    else:
                        self.plt.cards_chosen = self.choice_decouverte(carte, card_group=player.deck)
                elif "adv_hand" in carte.effects["decouverte"] and adv.hand.cards:
                    self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([copy_card(x) for x in adv.hand]))
                    carte.effects["second_time"] = 1
                elif "adv_already_played" in carte.effects["decouverte"] and adv.cards_played:
                    self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([get_card(x, all_cards) for x in adv.cards_played]))
                elif "spells_drawn" in carte.effects["decouverte"] and len(carte.effects["decouverte"]) > 1:
                    carte.effects["decouverte"].remove("spells_drawn")
                    self.plt.cards_chosen = self.choice_decouverte(carte, card_group=CardGroup([get_card(x, all_spells) for x in carte.effects["decouverte"]]))
            if "dragage" in carte.effects and player.deck.cards:
                if player.randomade == 0:
                    self.plt.cards_dragage = [CardGroup(player.deck.cards[-min(3, len(player.deck.cards)):].copy())]
                else:
                    self.plt.cards_dragage = [CardGroup(player.deck.cards[-min(1, len(player.deck.cards)):].copy())]
            if "hero_power_replacement" in carte.effects:
                player.power = carte.effects["hero_power_replacement"]
                player.cout_pouvoir = carte.effects["hero_power_replacement"][2]
            elif "permanent_buff" in carte.effects:
                if "heros" in carte.effects["permanent_buff"][1]:
                    if "allié" in carte.effects["permanent_buff"][1]:
                        if "pioche" in carte.effects["permanent_buff"]:
                            if "pioche" in player.permanent_buff:
                                player.permanent_buff["pioche"] += 1
                            else:
                                player.permanent_buff["pioche"] = 1
                        elif "alibi solide" in carte.effects["permanent_buff"]:
                            player.permanent_buff["alibi solide"] = 1
                        elif "enchanteur" in carte.effects["permanent_buff"]:
                            player.permanent_buff["enchanteur"] = 1
                            for creature in adv.servants.cards + player.servants.cards:
                                creature.effects["enchanteur"] = 1
                        elif "groove stellaire" in carte.effects["permanent_buff"]:
                            player.permanent_buff["groove stellaire"] = 1
                            player.effects["bouclier divin"] = 1
                        elif "eternel amour" in carte.effects["permanent_buff"]:
                            player.permanent_buff["eternel amour"] = 0
                    if "ennemi" in carte.effects["permanent_buff"][1]:
                        if "pioche" in carte.effects["permanent_buff"]:
                            if "pioche" in adv.permanent_buff:
                                adv.permanent_buff["pioche"] += 1
                            else:
                                adv.permanent_buff["pioche"] = 1
            elif "attach_hero" in carte.effects:
                for element in carte.effects["attach_hero"]:
                    if len(player.attached) + len(player.secrets) < 5 and element[0] not in [x[0] for x in player.attached]:
                        player.attached.append(element)
            elif "secret" in carte.effects:
                if len(player.attached) + len(player.secrets) < 5 and carte.name not in [x.name for x in player.secrets]:
                    player.secrets.add(carte)
            elif "temp_buff" in carte.effects:
                player.effects[carte.effects["temp_buff"][0]] = carte.effects["temp_buff"][1]
            if "next_turn" in carte.effects:
                player.next_turn.append(carte.effects["next_turn"])
        elif carte.type == "Lieu":
            if "random_spell" in carte.effects["use"]:
                player.randomade = 1
                for _ in range(carte.effects["use"][2]):
                    while True:
                        played_card = random.choice(all_spells)
                        if played_card["decouvrable"] == 1:
                            break
                    played_card = Card(**played_card)
                    if "choix_des_armes" in carte.effects:
                        choice = random.randint(0, 1)
                        played_card.effects[played_card.effects["choix_des_armes"][choice][0]] = played_card.effects["choix_des_armes"][choice][1]
                        played_card.effects.pop("choix_des_armes")
                    player.hand.cards.insert(0, played_card)
                    played_card.cost = 0
                    possible_targets = generate_targets(self.plt)[0: 16]
                    player.hand.remove(played_card)
                    possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                    if possible_targets_refined:
                        target = random.choice(possible_targets_refined)
                        if target == 0:
                            target = None
                        elif target == 1:
                            target = player
                        elif target < 9:
                            target = player.servants[target - 2]
                        elif target == 9:
                            target = adv
                        else:
                            target = adv.servants[target - 10]
                    else:
                        target = None
                    if not ("ciblage" in played_card.effects and target is None):
                        TourEnCours(self.plt).apply_effects(played_card, target)
                player.randomade = 0
            elif "reincarnation" in carte.effects["use"] and target is not None:
                target.effects["reincarnation"] = 1
                player.cadavres -= carte.effects["use"][1][-1]
                player.cadavres_spent += carte.effects["use"][1][-1]
            elif "ruée" in carte.effects["use"]:
                for serv in player.servants:
                    serv.effects["ruée"] = 1
            elif "rale d'agonie" in carte.effects["use"] and target is not None:
                creature = target
                creature.effects["rale_applied"] = 1
                self.apply_effects(creature)
                creature.effects.pop("rale_applied")
            elif "destroy+invocation" in carte.effects["use"]:
                target.blessure = 1000
                self.invoke_servant(get_card(carte.effects["use"][2], all_servants), player)
            elif "double" in carte.effects["use"]:
                if "relique" in carte.effects["use"][1]:
                    player.double_relique = 1
            elif "boost" in carte.effects["use"] and target is not None:
                if "fixed_stats" in carte.effects["use"][1]:
                    target.attack = carte.effects["use"][-1][0]
                    target.base_attack = carte.effects["use"][-1][0]
                    target.health = carte.effects["use"][-1][1]
                    target.base_health = carte.effects["use"][-1][1]
                    target.blessure = 0
                else:
                    target.boost(carte.effects["use"][-1][0], carte.effects["use"][-1][1])
                if "if_bete" in carte.effects["use"][1] and "ruée" in carte.effects["use"][1] and "Bête" in target.genre:
                    target.effects["ruée"] = 1
                if "pioche" in carte.effects["use"][1]:
                    player.pick_multi(carte.effects["use"][1][-1])
            elif "invocation" in carte.effects["use"]:
                if "cards_played_boost" in carte.effects["use"][1]:
                    if len(player.servants) + len(player.lieux) < 7:
                        to_invoke = get_card(carte.effects["use"][2], all_servants)
                        to_invoke.boost(len(player.cards_this_turn), len(player.cards_this_turn))
                        self.invoke_servant(to_invoke, player)
            elif "gel+invocation" in carte.effects["use"] and target is not None:
                target.effects["gel"] = 1
                self.invoke_servant(get_card(carte.effects["use"][2], all_servants), player)
            elif "heal" in carte.effects["use"]:
                if "tous" in carte.effects["use"][1] and "allié" in carte.effects["use"][1] and not [x for x in adv.servants if "anti_heal" in x.effects]:
                    if "kvaldir" in player.permanent_buff:
                        for entity in [player] + player.servants.cards:
                            entity.damage(carte.effects["use"][2])
                    else:
                        for entity in [player] + player.servants.cards:
                            entity.heal(carte.effects["use"][2])
        elif carte.type == "Arme":
            if "cri de guerre" in carte.effects:
                if "gel" in carte.effects["cri de guerre"]:
                    if "spend_cadavre" in carte.effects["cri de guerre"][1] and player.cadavres > 0 and adv.servants.cards:
                        targets = random.sample(adv.servants.cards, min(player.cadavres, 3, len(adv.servants)))
                        player.cadavres -= len(targets)
                        player.cadavres_spent += len(targets)
                        for target in targets:
                            target.effects["gel"] = 1
                if "dragage" in carte.effects["cri de guerre"]:
                    self.plt.cards_dragage = [CardGroup(player.deck.cards[-3:].copy())]
            if "rale d'agonie" in carte.effects and (carte.is_dead() or "rale_applied" in carte.effects):
                if "invocation" in carte.effects["rale d'agonie"] and len(player.servants) + len(player.lieux) < 7:
                    if "stack" in carte.effects:
                        servant_invoked = get_card(carte.effects["rale d'agonie"][2], all_servants)
                        self.invoke_servant(servant_invoked, player)
                        servant_invoked.boost(carte.effects["stack"], carte.effects["stack"])
                    elif "aléatoire" in carte.effects["rale d'agonie"][1]:
                        if "Bête" in carte.effects["rale d'agonie"][1]:
                            while True:
                                invoked_servant = random.choice(all_servants)
                                if "Bête" in invoked_servant["genre"] and invoked_servant["cost"] == carte.effects["rale d'agonie"][2]:
                                    break
                            invoked_servant = Card(**invoked_servant)
                            self.invoke_servant(invoked_servant, player)
                    else:
                        if "card_sup5_played" in carte.effects["rale d'agonie"][1]:
                            carte.effects["rale d'agonie"][2] = carte.effects["rale d'agonie"][2] * carte.effects["rale d'agonie"][1][-1]
                        for creature in carte.effects["rale d'agonie"][2]:
                            if len(player.servants) + len(player.lieux) < 7:
                                servant_invoked = get_card(creature, all_servants)
                                self.invoke_servant(servant_invoked, player)
                elif "add_hand" in carte.effects["rale d'agonie"]:
                    while True:
                        card_to_add = random.choice(all_cards)
                        if card_to_add["decouvrable"] == 1 and "marginal" in card_to_add["effects"]:
                            break
                    card_to_add = Card(**card_to_add)
                    player.hand.add(card_to_add)
                elif "pioche" in carte.effects["rale d'agonie"]:
                    player.pick_multi(carte.effects["rale d'agonie"][2])
                elif "boost" in carte.effects["rale d'agonie"]:
                    if "serviteur" in carte.effects["rale d'agonie"][1] and "allié" in carte.effects["rale d'agonie"][1] and "aléatoire" in carte.effects["rale d'agonie"][1]:
                        if player.servants.cards:
                            boosted_serv = random.choice(player.servants)
                            boosted_serv.boost(carte.effects["rale d'agonie"][2][0], carte.effects["rale d'agonie"][2][1])
                elif "refresh_mana" in carte.effects["rale d'agonie"]:
                    player.mana = min(player.mana_max, player.mana + carte.effects["rale d'agonie"][-1])

        # Résolution des effets d'aura
        ally_aura_servants = [x for x in player.servants if "aura" in set(x.effects)]
        ennemy_aura_servants = [x for x in adv.servants if "aura" in set(x.effects)]
        ally_aura_hand = [x for x in player.hand if "aura" in set(x.effects)]
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
                            if "right_serv" in servant.effects["aura"][1] and "vol de vie" in servant.effects["aura"][1]:
                                index_servant = player.servants.cards.index(servant)
                                try:
                                    player.servants.cards[index_servant + 1].effects["vol de vie"] = 1
                                except:
                                    pass
                            if "left_serv" in servant.effects["aura"][1] and "ruée" in servant.effects["aura"][1]:
                                index_servant = player.servants.cards.index(servant)
                                try:
                                    player.servants.cards[index_servant - 1].effects["ruée"] = 1
                                except:
                                    pass
                            if "Pirate" in servant.effects["aura"][1] and [x for x in player.servants if
                                                                             "Pirate" in x.genre and x != servant]:
                                for pirate in [x for x in player.servants if "Pirate" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        pirate.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        pirate.total_temp_boost[1] += servant.effects["aura"][2][1]
                            if "Murloc" in servant.effects["aura"][1] and [x for x in player.servants if
                                                                             "Murloc" in x.genre and x != servant]:
                                for murloc in [x for x in player.servants if "Murloc" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        murloc.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        murloc.total_temp_boost[1] += servant.effects["aura"][2][1]
                            if "tous_bouclier" in servant.effects["aura"][1]:
                                for serv in [x for x in player.servants if "bouclier divin" in x.effects]:
                                    if not servant.is_dead():
                                        serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                            if "recrues" in servant.effects["aura"][1] and [x for x in player.servants if x.name == "Recrue de la main d'argent"]:
                                for serv in [x for x in player.servants if x.name == "Recrue de la main d'argent"]:
                                    if not servant.is_dead():
                                        serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                                        serv.effects["provocation"] = 1
                                    else:
                                        if "provocation" in serv.effects:
                                            serv.effects.pop("provocation")
                            if "crabatoa" in servant.effects["aura"][1]:
                                if [x for x in player.servants if x.name == "Patte de crabatoa"]:
                                    for serv in [x for x in player.servants if x.name == "Patte de crabatoa"]:
                                        if not servant.is_dead():
                                            serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                            serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                                if player.weapon is not None and player.weapon.name == "Pince de crabatoa":
                                    player.weapon.total_temp_boost[0] = servant.effects["aura"][2][0]
                            if "tous" in servant.effects["aura"][1]:
                                for serv in [x for x in player.servants if x != servant]:
                                    if not servant.is_dead():
                                        if type(servant.effects["aura"][2]) == list:
                                            serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                            serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                                        else:
                                            serv.effects["camouflage"] = 1
                                    else:
                                        if "camouflage" in serv.effects:
                                            serv.effects.pop("camouflage")
                            if "choisi" in servant.effects["aura"][1]:
                                servant.effects["aura"][1][4].total_temp_boost[0] += servant.effects["aura"][2][0]
                                servant.effects["aura"][1][4].total_temp_boost[1] += servant.effects["aura"][2][1]
                        if servant.effects["aura"][1][3] == "Mort-vivant" and "Mort-vivant" in carte.genre and servant != carte:
                            carte.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                        if "conditional" in servant.effects["aura"][1]:
                            if "if_sup_attack" in servant.effects["aura"][1] and carte.type == "Serviteur" and not carte.is_dead() and carte.attack > servant.attack:
                                for creature in player.servants.cards:
                                    creature.boost(servant.effects["aura"][2][0], 0)
                            elif "if_inf_atq" in servant.effects["aura"][1] and carte.type == "Serviteur" and not carte.is_dead() and carte.attack < servant.attack:
                                carte.effects["bouclier divin"] = 1
                                carte.effects["ruée"] = 1
                            elif "if_targeted_spell" in servant.effects["aura"][1] and carte.type == "Sort" and target is not None and target in player.servants.cards:
                                if target.health < target.attack:
                                    target.boost(0, target.attack - target.health)
                                else:
                                    target.boost(target.health - target.attack, 0)
                            elif "if_surplus" in servant.effects["aura"][1] and servant.surplus > 0:
                                if "aléatoire" in servant.effects["aura"][1]:
                                    target_boost = random.choice([x for x in self.plt.players[0].servants if x != carte]) \
                                        if len([x for x in self.plt.players[0].servants if x != carte]) != 0 else None
                                    if target_boost is not None:
                                        target_boost.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                                    servant.surplus = 0
                    elif "tous" in servant.effects["aura"][1]:
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
                                    servant2.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                                for servant2 in adv.servants:
                                    servant2.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                elif "self" in servant.effects["aura"][1]:
                    if servant.effects["aura"][1][1] == "allié" and carte in player.servants:
                        if servant.effects["aura"][1][3] == "Murloc" and "Murloc" in set(
                                carte.genre) and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                        elif servant.effects["aura"][1][
                            3] == "Piranha grouillant" and carte.name == "Piranha grouillant" and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                    if servant.effects["aura"][1][1] == "sort":
                        if carte.type == "Sort":
                            if servant.effects["aura"][1][3] == "temp_fullturn":
                                servant.total_temp_boost[0] += servant.effects["aura"][2][0]
                                servant.total_temp_boost[1] += servant.effects["aura"][2][1]
                    elif servant.effects["aura"][1][1] == "Méca":
                        if carte.type == "Serviteur" and "Méca" in carte.genre and carte != servant and carte in player.servants and not carte.is_dead():
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                    elif servant.effects["aura"][1][1] == "cards_drawn":
                        servant.total_temp_boost[0] = player.drawn_this_turn
                    elif servant.effects["aura"][1][1] == "automates":
                        servant.total_temp_boost[0] = player.automates - 1
                        servant.total_temp_boost[1] = player.automates - 1
                    elif servant.effects["aura"][1][1] == "if_carapace":
                        if [x for x in player.servants if x.name == "Carapace de colaque"]:
                            servant.effects["bouclier_divin"] = 2
                            servant.effects["camouflage"] = 1
                        else:
                            if "boulier divin" in servant.effects:
                                servant.effects.pop("bouclier divin")
                            if "camouflage" in servant.effects:
                                servant.effects.pop("camouflage")
                    elif "conditional" in servant.effects["aura"][1]:
                        if "if_secret_revealed" in servant.effects["aura"][1] and carte in player.secrets and not "secret" in carte.effects:
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                            if "launch_secret" in servant.effects["aura"][1]:
                                already_secrets = [x.name for x in player.secrets]
                                secret_to_launch = random.choice([x["name"] for x in all_spells if "secret" in x["effects"] and x["name"] not in already_secrets])
                                player.secrets.add(get_card(secret_to_launch, all_spells))
                        elif "if_surplus" in servant.effects["aura"][1] and servant.surplus > 0:
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                            servant.surplus = 0
                elif "heros" in servant.effects["aura"][1]:
                    if "allié" in servant.effects["aura"][1]:
                        if "vol de vie" in servant.effects["aura"][1]:
                            if not servant.is_dead():
                                player.effects["vol de vie"] = 1
                            else:
                                if "vol de vie" in player.effects:
                                    player.effects.pop("vol de vie")
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
                    if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                        player.pick_multi(servant.effects["aura"][2])
                    elif "if_spell_self" in servant.effects["aura"][1] and carte.type == "Sort" and target == servant:
                        player.pick_multi(servant.effects["aura"][2])
                    elif "if_dead_undead" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and "Mort-vivant" in carte.genre and carte in player.servants:
                        player.pick_multi(servant.effects["aura"][2])
                    elif "if_surplus" in servant.effects["aura"][1] and servant.surplus > 0:
                        player.pick_multi(servant.effects["aura"][2])
                        servant.surplus = 0
            if "invocation" in servant.effects["aura"]:
                if "if_surplus" in servant.effects["aura"][1] and servant.surplus > 0:
                    if "egal_surplus" in servant.effects["aura"][1]:
                        servant.effects["aura"][2] = random.choice([x["name"] for x in all_servants if x["cost"] == servant.surplus])
                    servant.surplus = 0
                    self.invoke_servant(get_card(servant.effects["aura"][2], all_servants), player)
            if "add_hand" in servant.effects["aura"]:
                if "conditional" in servant.effects["aura"][1]:
                    if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                        player.hand.add(Card(**random.choice(all_servants)))
                    elif "if_meca_played" in servant.effects["aura"][1] and carte.type == "Serviteur" and "Méca" in carte.genre and servant != carte:
                        while True:
                            card_to_add = random.choice(all_cards)
                            if "gadget" in card_to_add["effects"]:
                                break
                        card_to_add = Card(**card_to_add)
                        player.hand.add(card_to_add)
                    elif "if_marginal" in servant.effects["aura"][1] and "marginal" in get_card(carte.name, all_cards).effects and not (carte.type == "Serviteur" and carte.is_dead()):
                        while True:
                            card_to_add = random.choice(all_cards)
                            if card_to_add["decouvrable"] == 1 and "marginal" in card_to_add["effects"]:
                                break
                        card_to_add = Card(**card_to_add)
                        player.hand.add(card_to_add)
                    elif "if_copied_card" in servant.effects["aura"][1] and "copied" in carte.effects:
                        if [x for x in adv.deck.cards + adv.hand.cards if x.name == carte.name]:
                            card_to_add = random.choice([x for x in adv.deck.cards + adv.hand.cards if x.name == carte.name])
                            player.hand.add(card_to_add)
                            if card_to_add in adv.deck.cards:
                                adv.deck.remove(card_to_add)
                            else:
                                adv.hand.remove(card_to_add)
                    elif "if_dead_undead" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and "Mort-vivant" in carte.genre and carte in player.servants and carte != servant:
                        if "sort" in servant.effects["aura"][1] and "ombre" in servant.effects["aura"][1] and "pretre" in servant.effects["aura"][1]:
                            while True:
                                card_to_add = random.choice(all_spells)
                                if "Ombre" in card_to_add["genre"] and card_to_add["classe"] == "Prêtre":
                                    break
                            card_to_add = Card(**card_to_add)
                            player.hand.add(card_to_add)
                            adv.damage(servant.effects["aura"][2])
                    elif "if_serv_death" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and carte != servant:
                        if "decoction" in servant.effects["aura"][1]:
                            while True:
                                card_to_add = random.choice(all_spells)
                                if "decoction" in card_to_add["effects"]:
                                    break
                            card_to_add = Card(**card_to_add)
                            player.hand.add(card_to_add)
            if "decouverte" in servant.effects["aura"]:
                if "conditional" in servant.effects["aura"][1]:
                    if "if_secret_played" in servant.effects["aura"][1] and "secret" in carte.effects:
                        self.plt.cards_chosen = self.choice_decouverte(carte, type="sort", other="Secret", classe="other_class")
            if "damage" in servant.effects["aura"]:
                if "serviteur" in servant.effects["aura"][1]:
                    if "ennemi" in servant.effects["aura"][1]:
                        if "conditional" in servant.effects["aura"][1]:
                            if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                                for creature in adv.servants.cards:
                                    creature.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                    elif "tous" in servant.effects["aura"][1]:
                        if "conditional" in servant.effects["aura"][1]:
                            if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                                for creature in player.servants.cards + adv.servants.cards:
                                    creature.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                elif "tous" in servant.effects["aura"][1]:
                    if "ennemi" in servant.effects["aura"][1]:
                        if "heros_allié_attack" in servant.effects["aura"][1] and player.has_attacked == 1 and carte.name == "":
                            for entity in [adv] + adv.servants.cards:
                                entity.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                        elif "aléatoire" in servant.effects["aura"][1]:
                            if "conditional" in servant.effects["aura"][1]:
                                if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                                    if "lowest_health" in servant.effects["aura"][1]:
                                        lowest_health = min([x.health for x in adv.servants.cards + [adv]])
                                        potential_target = [random.choice([x for x in adv.servants.cards + [adv] if x.health == lowest_health])]
                                    else:
                                        if "disjoint" in servant.effects["aura"][1]:
                                            potential_target = [adv] + adv.servants.cards
                                            potential_target = random.sample(potential_target, min(servant.effects["aura"][1][-1], len([adv] + adv.servants.cards)))
                                    for cible in potential_target:
                                        cible.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                                elif "if_dead" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and carte in player.servants:
                                    potential_target = random.choice([adv] + adv.servants.cards)
                                    potential_target.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                                elif "if_meca" in servant.effects["aura"][1] and carte.type == "Serviteur" and "Méca" in carte.genre and carte != servant:
                                    for _ in range(servant.effects["aura"][1][-1]):
                                        cible = random.choice([adv] + adv.servants.cards)
                                        cible.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                                elif "if_surplus" in servant.effects["aura"][1] and servant.surplus > 0:
                                    cible = random.choice([adv] + adv.servants.cards)
                                    cible.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                                    servant.surplus = 0
                elif "heros" in servant.effects["aura"][1]:
                    if "ennemi" in servant.effects["aura"][1]:
                        if "conditional" in servant.effects["aura"][1]:
                            if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort" and "cost_spell" in servant.effects["aura"][1]:
                                adv.damage(carte.cost)
            if "destroy" in servant.effects["aura"]:
                if "if_gele" in servant.effects["aura"][1] and adv.servants:
                    for creature in adv.servants.cards:
                        if "gel" in creature.effects:
                            creature.blessure = 1000
            if "attack" in servant.effects["aura"]:
                if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                    if "ennemi" in servant.effects["aura"][1] and "lowest_health" in servant.effects["aura"][1]:
                        lowest_health = min([x.health for x in adv.servants.cards + [adv]])
                        target = random.choice([x for x in adv.servants.cards + [adv] if x.health == lowest_health])
                        self.attaquer(servant, target)
            if "play" in servant.effects["aura"]:
                if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                    if "if_sacré" in servant.effects["aura"][1] and carte.genre == "Sacré" and len([x for x in player.servants if not "en sommeil" in x.effects]) > 1:
                        played_card = get_card(carte.name, all_spells)
                        player.hand.cards.insert(0, played_card)
                        played_card.cost = 0
                        possible_targets = generate_targets(self.plt)[0: 16]
                        player.hand.remove(played_card)
                        possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n] and 2 <= n < 9 and player.servants[n + 2] != servant]
                        if possible_targets_refined:
                            target = random.choice(possible_targets_refined)
                            target = player.servants[target - 2]
                        if not ("ciblage" in played_card.effects and target is None):
                            TourEnCours(self.plt).apply_effects(played_card, target)
            if "replacement" in servant.effects["aura"]:
                if carte.type == "Serviteur" and carte.is_dead():
                    player.servants.remove(servant)
                    self.invoke_servant(get_card(carte.name, all_servants), player)
            if "reduc" in servant.effects["aura"]:
                if "if_third" in servant.effects["aura"][1] and len(player.serv_this_turn.cards) == 2:
                    if not ["serviteur", "", 0, "end_turn"] in player.discount_next:
                        player.discount_next.append(["serviteur", "", 0, "end_turn"])
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
            if "deck_swap" in servant.effects["aura"]:
                if servant.effects["aura"][1] == 1:
                    inter_deck = pickle.load(pickle.dumps(player.deck, -1))
                    player.deck = pickle.load(pickle.dumps(adv.deck, -1))
                    adv.deck = inter_deck
                    servant.effects["aura"][1] = 0
                else:
                    if servant.is_dead():
                        inter_deck = pickle.load(pickle.dumps(player.deck, -1))
                        player.deck = pickle.load(pickle.dumps(adv.deck, -1))
                        adv.deck = inter_deck
            if "modif_damage" in servant.effects["aura"]:
                if "ennemi" in servant.effects["aura"][1]:
                    if servant.effects["aura"][2] == 1:
                        adv.curses[servant.effects["aura"][1][-1]] = 1
                elif "allié" in servant.effects["aura"][1]:
                    if servant.effects["aura"][2] == 1:
                        player.curses[servant.effects["aura"][1][-1]] = 1
                elif "tous" in servant.effects["aura"][1]:
                    if servant.effects["aura"][2] == 1:
                        player.curses[servant.effects["aura"][1][-1]] = 1
                        adv.curses[servant.effects["aura"][1][-1]] = 1
            if "add_armor" in servant.effects["aura"]:
                if "if_spell" in servant.effects["aura"][1] and carte.type == "Sort":
                    player.armor += carte.cost
            if "refresh_mana" in servant.effects["aura"]:
                if "conditional"in servant.effects["aura"][1]:
                    if "if_naga" in servant.effects["aura"][1] and "Naga" in carte.genre and servant.effects["aura"][2] == 1 and carte != servant:
                        player.mana = min(player.mana_max, player.mana + servant.effects["aura"][-1])
                        servant.effects["aura"][2] = 0
                    elif "if_spell" in servant.effects["aura"][1] and carte.type == "Sort" and servant.effects["aura"][2] == 0:
                        player.mana = min(player.mana_max, player.mana + servant.effects["aura"][-1])
                        servant.effects["aura"][2] = 1
            if servant.effects["aura"] == "eleveuse de faucons":
                if carte.type == "Serviteur" and not carte.is_dead() and carte != servant and not "invoked" in carte.effects:
                    if not ("titan" in carte.effects and carte.effects["titan"][-1] == 0):
                        carte.boost(1, 1)
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
                            if "Pirate" in servant.effects["aura"][1] and [x for x in adv.servants if
                                                                             "Pirate" in x.genre and x != servant]:
                                for pirate in [x for x in adv.servants if "Pirate" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        pirate.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        pirate.total_temp_boost[1] += servant.effects["aura"][2][1]
                            if "Murloc" in servant.effects["aura"][1] and [x for x in adv.servants if
                                                                             "Murloc" in x.genre and x != servant]:
                                for murloc in [x for x in adv.servants if "Murloc" in x.genre and x != servant]:
                                    if not servant.is_dead():
                                        murloc.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        murloc.total_temp_boost[1] += servant.effects["aura"][2][1]
                            if "recrues" in servant.effects["aura"][1] and [x for x in adv.servants if x.name == "Recrue de la main d'argent"]:
                                for serv in [x for x in adv.servants if x.name == "Recrue de la main d'argent"]:
                                    if not servant.is_dead():
                                        serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                                        serv.effects["provocation"] = 1
                                    else:
                                        if "provocation" in serv.effects:
                                            serv.effects.pop("provocation")
                            if "crabatoa" in servant.effects["aura"][1]:
                                if [x for x in adv.servants if x.name == "Patte de crabatoa"]:
                                    for serv in [x for x in adv.servants if x.name == "Patte de crabatoa"]:
                                        if not servant.is_dead():
                                            serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                            serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                                if adv.weapon is not None and adv.weapon.name == "Pince de crabatoa":
                                    adv.weapon.total_temp_boost[0] = servant.effects["aura"][2][0]
                            if "tous" in servant.effects["aura"][1] and [x for x in adv.servants if x != servant]:
                                for serv in [x for x in adv.servants if x != servant]:
                                    if not servant.is_dead():
                                        if type(servant.effects["aura"][2]) == list:
                                            serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                            serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                                        else:
                                            serv.effects["camouflage"] = 1
                                    else:
                                        if "camouflage" in serv.effects:
                                            serv.effects.pop("camouflage")
                            if "tous_bouclier" in servant.effects["aura"][1]:
                                for serv in [x for x in adv.servants if "bouclier divin" in x.effects]:
                                    if not servant.is_dead():
                                        serv.total_temp_boost[0] += servant.effects["aura"][2][0]
                                        serv.total_temp_boost[1] += servant.effects["aura"][2][1]
                            if "choisi" in servant.effects["aura"][1]:
                                servant.effects["aura"][1][4].total_temp_boost[0] += servant.effects["aura"][2][0]
                                servant.effects["aura"][1][4].total_temp_boost[1] += servant.effects["aura"][2][1]
                        if servant.effects["aura"][1][3] == "Mort-vivant" and "Mort-vivant" in carte.genre and servant != carte and carte in adv.servants:
                            carte.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                    elif "tous" in servant.effects["aura"][1]:
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
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                        elif servant.effects["aura"][1][
                            3] == "Piranha grouillant" and carte.name == "Piranha grouillant" and servant != carte and carte in player.servants and not carte.is_dead():
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                    elif servant.effects["aura"][1][1] == "sort":
                        if carte.type == "Sort":
                            if servant.effects["aura"][1][3] == "temp_fullturn":
                                servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                    elif servant.effects["aura"][1][1] == "if_carapace":
                        if [x for x in adv.servants if x.name == "Carapace de colaque"]:
                            servant.effects["bouclier_divin"] = 2
                            servant.effects["camouflage"] = 1
                        else:
                            if "boulier divin" in servant.effects:
                                servant.effects.pop("bouclier divin")
                            if "camouflage" in servant.effects:
                                servant.effects.pop("camouflage")
                    if "conditional" in servant.effects["aura"][1]:
                        if "if_enemyturn" in servant.effects["aura"][1]:
                            servant.total_temp_boost[0] = servant.effects["aura"][2][0]
                            servant.total_temp_boost[1] = servant.effects["aura"][2][1]
                        elif "if_secret_revealed" in servant.effects["aura"][1] and carte in adv.secrets and not "secret" in carte.effects:
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                            if "launch_secret" in servant.effects["aura"][1]:
                                already_secrets = [x.name for x in adv.secrets]
                                secret_to_launch = random.choice([x["name"] for x in all_spells if "secret" in x["effects"] and x["name"] not in already_secrets])
                                adv.secrets.add(get_card(secret_to_launch, all_spells))
            if "destroy" in servant.effects["aura"]:
                if "if_gele" in servant.effects["aura"][1] and player.servants:
                    for creature in player.servants.cards:
                        if "gel" in creature.effects:
                            creature.blessure = 1000
            if "damage" in servant.effects["aura"]:
                if "tous" in servant.effects["aura"][1]:
                    if "ennemi" in servant.effects["aura"][1]:
                        if "aléatoire" in servant.effects["aura"][1]:
                            if "conditional" in servant.effects["aura"][1]:
                                if "if_dead" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and carte in adv.servants:
                                    potential_target = random.choice([player] + player.servants.cards)
                                    potential_target.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
            if "pioche" in servant.effects["aura"]:
                if "allié" in servant.effects["aura"][1]:
                    if "global" in servant.effects["aura"][1] and "damage_self" in servant.effects["aura"][1]:
                        if servant.damage_taken:
                            adv.pick_multi(servant.effects["aura"][2])
                            servant.damage_taken = False
                    elif "if_dead_undead" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and "Mort-vivant" in carte.genre and carte in adv.servants:
                        adv.pick_multi(servant.effects["aura"][2])
            if "add_hand" in servant.effects["aura"]:
                if "conditional" in servant.effects["aura"][1]:
                    if "if_dead_undead" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and "Mort-vivant" in carte.genre and carte in adv.servants and carte != servant:
                        if "sort" in servant.effects["aura"][1] and "ombre" in servant.effects["aura"][1] and "pretre" in servant.effects["aura"][1]:
                            while True:
                                card_to_add = random.choice(all_spells)
                                if "Ombre" in card_to_add["genre"] and card_to_add["classe"] == "Prêtre":
                                    break
                            card_to_add = Card(**card_to_add)
                            adv.hand.add(card_to_add)
                            player.damage(servant.effects["aura"][2])
                    elif "if_serv_death" in servant.effects["aura"][1] and carte.type == "Serviteur" and carte.is_dead() and carte != servant:
                        if "decoction" in servant.effects["aura"][1]:
                            while True:
                                card_to_add = random.choice(all_spells)
                                if "decoction" in card_to_add["effects"]:
                                    break
                            card_to_add = Card(**card_to_add)
                            adv.hand.add(card_to_add)
            if "replacement" in servant.effects["aura"]:
                if carte.type == "Serviteur" and carte.is_dead():
                    adv.servants.remove(servant)
                    self.invoke_servant(get_card(carte.name, all_servants), adv)
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
            if "modif_damage" in servant.effects["aura"]:
                if "allié" in servant.effects["aura"][1]:
                    if servant.effects["aura"][2] == 1:
                        adv.curses[servant.effects["aura"][1][-1]] = 1
                elif "tous" in servant.effects["aura"][1]:
                    if servant.effects["aura"][2] == 1:
                        player.curses[servant.effects["aura"][1][-1]] = 1
                        adv.curses[servant.effects["aura"][1][-1]] = 1
        for card in ally_aura_hand:
            if "temp_copy" in card.effects["aura"]:
                if "last_spell" in card.effects["aura"] and carte.type == "Sort":
                    card.genre = copy_card(carte)
                    card.effects["aura"] = ["temp_copy", ["allié", "last_spell"]]
            if "transformation" in card.effects["aura"]:
                if "if_feu" in card.effects["aura"][1] and carte.type == "Sort" and "Feu" in carte.genre:
                    index_servant_hand = player.hand.cards.index(card)
                    player.hand.remove(card)
                    player.hand.cards.insert(index_servant_hand, get_card("Dame Naz'jar feu", all_servants))
                if "if_arcanes" in card.effects["aura"][1] and carte.type == "Sort" and "Arcanes" in carte.genre:
                    index_servant_hand = player.hand.cards.index(card)
                    player.hand.remove(card)
                    player.hand.cards.insert(index_servant_hand, get_card("Dame Naz'jar arcanes", all_servants))
                if "if_givre" in card.effects["aura"][1] and carte.type == "Sort" and "Givre" in carte.genre:
                    index_servant_hand = player.hand.cards.index(card)
                    player.hand.remove(card)
                    player.hand.cards.insert(index_servant_hand, get_card("Dame Naz'jar givre", all_servants))
        if player.weapon is not None and "aura" in player.weapon.effects:
            if "damage" in player.weapon.effects["aura"]:
                if "conditional" in player.weapon.effects["aura"] and "if_spell" in player.weapon.effects["aura"] and carte.type == "Sort":
                    adv.damage(player.weapon.effects["aura"][2], toxic=True if "toxicite" in player.effects else False)
                    player.weapon.health -= 1
            elif "boost" in player.weapon.effects["aura"]:
                if "insensible_attack" in player.weapon.effects["aura"][1]:
                    player.effects["insensible_attack"] = 1
            elif "invocation" in player.weapon.effects["aura"]:
                if "if_spell" in player.weapon.effects["aura"][1] and carte.type == "Sort" and carte.cost != 0 and player.weapon.health > 0:
                    player.weapon.health -= 1
                    invoked_servant = get_card(player.weapon.effects["aura"][-1], all_servants)
                    invoked_servant.attack = carte.cost
                    invoked_servant.base_attack = carte.cost
                    invoked_servant.health = carte.cost
                    invoked_servant.base_health = carte.cost
                    self.invoke_servant(invoked_servant, player)
            elif "hp_boost" in player.weapon.effects["aura"]:
                if "reduc" in player.weapon.effects["aura"][1]:
                    player.cout_pouvoir_temp = 0

    def invoke_servant(self, servant, player):
        if "cri de guerre" in servant.effects:
            servant.effects.pop("cri de guerre")
        elif "on_invoke" in servant.effects:
            servant.effects["cri de guerre"] = servant.effects["on_invoke"]
            servant.effects.pop("on_invoke")
        if "soif de mana" in servant.effects:
            servant.effects.pop("soif de mana")
        if "final" in servant.effects:
            servant.effects.pop("final")
        if "choix_des_armes" in servant.effects:
            servant.effects.pop("choix_des_armes")
        servant.effects["invoked"] = 1
        if len(player.servants) < 7:
            player.servants.add(servant)
            self.apply_effects(servant)

    def jouer_carte(self, carte, target=None):
        """ Action de poser une carte depuis la main du joueur dont c'est le tour.
        Le plateau est mis à jour en conséquence """
        player = self.plt.players[0]
        adv = self.plt.players[1]
        player.cards_this_turn.append(carte.name)

        """ Actions pré_effet """
        if carte.cost >= 5 and player.weapon is not None and player.weapon.name == "Tambourin des bois":
            player.weapon.effects["rale d'agonie"][1][-1] += 1
        if [x for x in player.servants if "aura" in x.effects and "if_right_played" in x.effects["aura"][1] and "pioche" in x.effects["aura"]]:
            if carte == player.hand.cards[-1]:
                player.pick()
        if "combo" in carte.effects:
            if player.last_card.name != "":
                carte.effects[carte.effects["combo"][0]] = carte.effects["combo"][1]
                if player.weapon is not None and player.weapon.name == "Glaivetar":
                    player.weapon.effects["rale d'agonie"][2] += 1
            player.combo_played += 1
        if "marginal" in carte.effects:
            if carte in [player.hand[0], player.hand[-1]]:
                carte.effects[carte.effects["marginal"][0]] = carte.effects["marginal"][1]
                carte.effects.pop("marginal")
            if player.weapon is not None and player.weapon.name == "Platine":
                player.weapon.effects["rale d'agonie"][2] += 1

        """ Carte jouée """
        if carte.type.lower() == "sort" and not "mandatory" in carte.effects:
            if "toxispell" in player.effects:
                carte.effects["toxicite"] = 1
            if "groove stellaire" in player.permanent_buff:
                player.effects["bouclier divin"] = 1
            if "final" in carte.effects and player.mana == 0:
                carte.effects[carte.effects["final"][0]] = carte.effects["final"][1]
                carte.effects.pop("final")
            if carte.id not in [x.id for x in player.initial_deck]:
                player.indirect_spells.append(carte.name)
            player.hand.remove(carte)
            player.mana_spend(carte.cost)
            if ("counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "sort" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]) \
                    or (adv.secrets and "counter" in [x.effects["secret"] for x in adv.secrets if x.effects["trigger"] == "if_spell_played"]):
                if "counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "sort" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]:
                    print([x for x in adv.servants if "aura" in x.effects and "counter" in x.effects["aura"][0]][0].effects)
                    [x for x in adv.servants if "aura" in x.effects and "counter" in x.effects["aura"][0]][0].effects.pop("aura")
                else:
                    secret = [x for x in adv.secrets if x.effects["trigger"] == "if_spell_played" and x.effects["secret"] == "counter"][0]
                    secret.effects.pop("secret")
                    self.apply_effects(secret, target)
                    adv.secrets.remove(secret)
                    adv.secrets_declenches += 1
                    if "halkias" in secret.effects:
                        self.invoke_servant(get_card("Halkias", all_servants), adv)
            else:
                t0 = time.perf_counter()
                player.mana_spend_spells += carte.cost
                if "relique" in carte.effects:
                    player.reliques += 1
                    if player.double_relique == 1:
                        self.apply_effects(carte, target)
                        player.reliques += 1
                        player.double_relique = 0
                elif carte.name == "Jeu de lumiere":
                    player.jeu_lumiere += 1
                if player.first_spell is None:
                    player.first_spell = carte.name
                if carte.genre and carte.genre[0] not in player.ecoles_jouees:
                    player.ecoles_jouees.append(carte.genre[0])
                if "Sacré" in carte.genre:
                    player.sacre_spent += carte.cost
                self.apply_effects(carte, target)
                player.spells_played.append(carte.name)
                player.spell_this_turn += 1
                if "double" in player.next_spell:
                    player.next_spell.remove("double")
                    self.apply_effects(carte, target)
                if [x for x in player.servants if "aura" in x.effects and not x.is_dead() and "double_spell_arcanes" in x.effects["aura"]] and "Arcanes" in carte.genre:
                    self.apply_effects(carte, target)
                if "jotun" in player.permanent_buff and player.first_spell is not None and player.permanent_buff["jotun"] == 1:
                    played_card = get_card(player.first_spell, all_spells)
                    player.hand.cards.insert(0, played_card)
                    if "marginal" in played_card.effects:
                        played_card.effects.pop("marginal")
                    played_card.cost = 0
                    possible_targets = generate_targets(self.plt)[0: 17]
                    possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                    if possible_targets_refined:
                        target = random.choice(possible_targets_refined)
                        if target == 0:
                            target = None
                        elif target == 1:
                            target = player
                        elif target < 9:
                            target = player.servants[target - 2]
                        elif target == 9:
                            target = adv
                        else:
                            target = adv.servants[target - 10]
                    if not ("ciblage" in played_card.effects and target is None):
                        player.permanent_buff["jotun"] = 0
                        TourEnCours(self.plt).jouer_carte(played_card, target)
                if "topior" in player.permanent_buff and "Nature" in carte.genre:
                    self.invoke_servant(get_card("Minigazzor", all_servants), player)
                if [x for x in player.servants.cards if "en sommeil" in x.effects and type(x.effects["en sommeil"]) == list and "mana_spend_spells" in x.effects["en sommeil"]]:
                    for creature in [x for x in player.servants.cards if "en sommeil" in x.effects and type(x.effects["en sommeil"]) == list and "mana_spend_spells" in x.effects["en sommeil"]]:
                        creature.effects["en sommeil"][1] -= carte.cost
                        if creature.effects["en sommeil"][1] == 0:
                            creature.effects.pop("en sommeil")
                if [x for x in player.hand if "cri de guerre" in x.effects and "if_spell" in x.effects["cri de guerre"][1]]:
                    for serv in [x for x in player.hand if "cri de guerre" in x.effects and "if_spell" in x.effects["cri de guerre"][1]]:
                        if "cost_spell" in serv.effects["cri de guerre"][1]:
                            serv.effects["cri de guerre"][2].append(random.choice([x["name"] for x in all_servants if x["cost"] == carte.cost and x["decouvrable"] == 1]))
                        else:
                            if "add_hand" in serv.effects["cri de guerre"] and serv.effects["cri de guerre"][1][-1] > 0:
                                serv.effects["cri de guerre"][3].append(carte.name)
                            serv.effects["cri de guerre"][1][-1] -= 1
                            if serv.effects["cri de guerre"][1][-1] <= 0:
                                serv.effects["cri de guerre"][2] = serv.effects["cri de guerre"][3]
                if [x for x in player.hand if "rale d'agonie" in x.effects and "if_spell" in x.effects["rale d'agonie"][1]]:
                    for card in [x for x in player.hand if "rale d'agonie" in x.effects and "if_spell" in x.effects["rale d'agonie"][1]]:
                        card.effects["rale d'agonie"][2] = min(10, card.effects["rale d'agonie"][2] + 1)
                if [x for x in player.hand if "cri de guerre" in x.effects and "if_fiel" in x.effects["cri de guerre"][1]] and "Fiel" in carte.genre:
                    for serv in [x for x in player.hand if "cri de guerre" in x.effects and "if_fiel" in x.effects["cri de guerre"][1]]:
                        serv.effects[serv.effects["cri de guerre"][0]] = serv.effects["cri de guerre"][2]
                if [x for x in player.hand if "cri de guerre" in x.effects and "if_nature" in x.effects["cri de guerre"][1]] and "Nature" in carte.genre:
                    for serv in [x for x in player.hand if "cri de guerre" in x.effects and "if_nature" in x.effects["cri de guerre"][1]]:
                        serv.effects["cri de guerre"][2] = serv.effects["cri de guerre"][3]
                if [x for x in player.hand if "cri de guerre" in x.effects and "if_sacré" in x.effects["cri de guerre"][1]] and "Sacré" in carte.genre:
                    for serv in [x for x in player.hand if "cri de guerre" in x.effects and "if_sacré" in x.effects["cri de guerre"][1]]:
                        serv.effects["cri de guerre"][2] = serv.effects["cri de guerre"][3]
                if [x for x in player.hand if x.type == "Serviteur" and "if_spell" in x.effects]:
                    for creature in [x for x in player.hand if x.type == "Serviteur" and "if_spell" in x.effects]:
                        creature.effects["cri de guerre"] = creature.effects["if_spell"]
                        creature.effects.pop("if_spell")
            if "milouse" in carte.effects:
                player.milouse += 1
            if "eternel amour" in player.permanent_buff and player.permanent_buff["eternel amour"] == 1:
                player.permanent_buff["eternel amour"] = 0
            if adv.secrets and "if_spell_played" in [x.effects["trigger"] for x in adv.secrets]:
                for secret in adv.secrets:
                    if secret.effects["trigger"] == "if_spell_played":
                        if "ciblage" in secret.effects["secret"]:
                            target = carte
                            secret.effects["secret"].remove("ciblage")
                        else:
                            target = None
                        secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                        secret.effects.pop("secret")
                        self.apply_effects(secret, target)
                        adv.secrets.remove(secret)
                        adv.secrets_declenches += 1
                        if "halkias" in secret.effects:
                            self.invoke_servant(get_card("Halkias", all_servants), adv)
        elif carte.type.lower() == "sort" and "mandatory" in carte.effects:
            player.hand.remove(carte)
            self.apply_effects(carte, target)
        elif carte.type.lower() == "serviteur":
            if len(player.servants) + len(player.lieux) < 7:
                if player.weapon is not None and player.weapon.name == "Masse disco":
                    player.weapon.effects["rale d'agonie"][2][0] += 1
                    player.weapon.effects["rale d'agonie"][2][1] += 1
                player.hand.remove(carte)
                if "cost_armor" not in player.effects:
                    player.mana_spend(carte.cost)
                else:
                    player.armor -= carte.cost
                    player.effects["cost_armor"] -= 1
                    if player.effects["cost_armor"] == 0:
                        player.effects.pop("cost_armor")
                if "final" in carte.effects and player.mana == 0:
                    carte.effects["cri de guerre"] = carte.effects["final"]
                    carte.effects.pop("final")
                    if carte.name == "Sectatrice hardcore":
                        target = None
                if "Naga" in carte.genre:
                    if [x for x in player.hand if "reduc" in x.effects and "if_naga" in x.effects["reduc"]]:
                        for card in [x for x in player.hand if "reduc" in x.effects and "if_naga" in x.effects["reduc"]]:
                            card.base_cost = card.effects["reduc"][1]
                    if [x for x in player.hand if "hero_attack" in x.effects and type(x.effects["hero_attack"]) == list and "if_naga" in x.effects["hero_attack"]]:
                        for card in [x for x in player.hand if "hero_attack" in x.effects and type(x.effects["hero_attack"]) == list and "if_naga" in x.effects["hero_attack"]]:
                            card.effects["hero_attack"] = card.effects["hero_attack"][-1]
                    if [x for x in player.hand if "add_hand" in x.effects and "if_naga" in x.effects["add_hand"]]:
                        for card in [x for x in player.hand if "add_hand" in x.effects and "if_naga" in x.effects["add_hand"]]:
                            card.effects["add_hand"][0] = ["allié"]
                    if [x for x in player.hand if "boosted_invoked" in x.effects and "if_naga" in x.effects["boosted_invoked"]]:
                        for card in [x for x in player.hand if "boosted_invoked" in x.effects and "if_naga" in x.effects["boosted_invoked"]]:
                            card.effects["boosted_invoked"] = [1, 1]
                    if [x for x in player.hand if "pioche" in x.effects and "if_naga" in x.effects["pioche"]]:
                        for card in [x for x in player.hand if "pioche" in x.effects and "if_naga" in x.effects["pioche"]]:
                            card.effects["pioche"][-1] = 2
                if ("counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "serviteur" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]) \
                        or (adv.secrets and "counter" in [x.effects["secret"] for x in adv.secrets if x.effects["trigger"] == "if_serv_played"]):
                    if "counter" in [x.effects["aura"][0] for x in adv.servants if "aura" in x.effects] and "serviteur" in [x.effects["aura"][1] for x in adv.servants if "aura" in x.effects]:
                        [x for x in adv.servants if "counter" in x.effects["aura"][0]][0].effects.pop("counter")
                    else:
                        secret = [x for x in adv.secrets if
                                  x.effects["trigger"] == "if_serv_played" and x.effects["secret"] == "counter"][0]
                        secret.effects.pop("secret")
                        self.apply_effects(secret, target)
                        adv.secrets.remove(secret)
                        adv.secrets_declenches += 1
                        if "halkias" in secret.effects:
                            self.invoke_servant(get_card("Halkias", all_servants), adv)
                else:
                    player.servants.add(carte)
                    self.apply_effects(carte, target)
                if len(player.serv_this_turn.cards) == 3:
                    player.serv_this_turn = CardGroup()
                else:
                    player.serv_this_turn.add(carte)
                if "Élémentaire" in carte.genre:
                    player.elem_this_turn += 1
                if "Mort-vivant" in carte.genre and "allies immortels" in player.effects:
                    carte.effects["reincarnation"] = 1
                if "cost_pv" in carte.effects and carte.effects["cost_pv"][1] == 1:
                    player.damage(carte.base_cost)
                    if "croise sanglant" in player.permanent_buff:
                        player.permanent_buff.pop("croise sanglant")
                        for serv in [x for x in player.hand if "cost_pv" in x.effects]:
                            serv.effects.pop("cost_pv")
                if "hodir" in player.permanent_buff:
                    carte.attack = 8
                    carte.base_attack = 8
                    carte.health = 8
                    carte.base_health = 8
                    player.permanent_buff["hodir"] -= 1
                    if player.permanent_buff == 0:
                        player.permanent_buff.remove("hodir")
                if "destroy_next_rale" in player.permanent_buff and "rale d'agonie" in carte.effects:
                    carte.blessure = 1000
                if adv.secrets and "if_serv_played" in [x.effects["trigger"] for x in adv.secrets] and "en sommeil" not in carte.effects:
                    for secret in adv.secrets:
                        if secret.effects["trigger"] == "if_serv_played" and carte in player.servants:
                            if "ciblage" in secret.effects["secret"]:
                                target = carte
                                secret.effects["secret"].remove("ciblage")
                            else:
                                target = None
                            secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                            secret.effects.pop("secret")
                            self.apply_effects(secret, target)
                            adv.secrets.remove(secret)
                            adv.secrets_declenches += 1
                            if "halkias" in secret.effects:
                                self.invoke_servant(get_card("Halkias", all_servants), adv)
            else:
                pass
        elif carte.type.lower() == "lieu":
            if len(player.servants) + len(player.lieux) < 7:
                player.hand.remove(carte)
                player.mana_spend(carte.cost)
                player.lieux.add(carte)
        elif carte.type.lower() == "arme":
            player.hand.remove(carte)
            player.mana_spend(carte.cost)
            if player.weapon is not None:
                player.weapon.health = 0
                player.dead_weapon = player.weapon
            player.weapon = carte
            player.weapons_played += 1
            self.apply_effects(carte)

            if [x for x in player.servants if "aura" in x.effects and "if_weapon_invoked" in x.effects["aura"][1]]:
                for servant in [x for x in player.servants if "aura" in x.effects and "if_weapon_invoked" in x.effects["aura"][1]]:
                    if "boost" in servant.effects["aura"]:
                        player.weapon.attack += servant.effects["aura"][-1][0]

        """ Après avoir joué la carte """
        if "haunted" in carte.effects:
            self.invoke_servant(get_card(carte.effects["haunted"], all_servants), player)
        if adv.secrets and "if_three_played" in [x.effects["trigger"] for x in adv.secrets] and len(player.cards_this_turn) >= 3:
            for secret in adv.secrets:
                if secret.effects["trigger"] == "if_three_played":
                    if "ciblage" in secret.effects["secret"]:
                        target = player
                        secret.effects["secret"].remove("ciblage")
                    else:
                        target = None
                    secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                    secret.effects.pop("secret")
                    self.apply_effects(secret, target)
                    adv.secrets.remove(secret)
                    adv.secrets_declenches += 1
                    if "halkias" in secret.effects:
                        self.invoke_servant(get_card("Halkias", all_servants), adv)
        if [x for x in player.servants.cards + adv.servants.cards if "infection" in x.effects and "conditional" in x.effects["infection"]]:
            for infected_creature in [x for x in player.servants.cards + adv.servants.cards if "infection" in x.effects and "conditional" in x.effects["infection"]]:
                if "if_copied_played" in infected_creature.effects["infection"] and "destroyed" in infected_creature.effects["infection"]:
                    if "copied" in carte.effects:
                        infected_creature.blessure = 1000
        if [x for x in player.hand if "aura" in x.effects and "transformation_inhand" in x.effects["aura"]]:
            if carte.type.lower() == "sort" and not "mandatory" in carte.effects:
                for card in [x for x in player.hand if "aura" in x.effects and "transformation_inhand" in x.effects["aura"]]:
                    transformed_card = copy_card(carte)
                    transformed_card.effects["aura"] = ["transformation_inhand", "last_spell"]
                    index_card = player.hand.cards.index(card)
                    player.hand.remove(card)
                    player.hand.cards.insert(index_card, transformed_card)
        if carte.classe == "Paladin":
            player.paladin_played += 1
        if carte.classe not in [player.classe, "Neutre"] and not player.otherclass_played:
            player.otherclass_played = True
        player.cards_played.append(carte.name)

    def util_lieu(self, carte, target=None):
        player = self.plt.players[0]
        adv = self.plt.players[1]
        self.apply_effects(carte, target)
        carte.health -= 1
        carte.attack -= 1
        if carte.health == 0:
            player.lieux.remove(carte)

    def attaquer(self, attaquant, cible, target=None):
        """ Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi) """
        player = self.plt.players[0]
        adv = self.plt.players[1]
        if type(attaquant) in (Player, Card) and type(cible) in (Player, Card):
            """ Avant attaque """
            if attaquant in player.servants.cards + [player] and adv.secrets and "if_serv_attacked" in [x.effects["trigger"] for x in adv.secrets] and type(cible) == Card:
                for secret in adv.secrets:
                    if secret.effects["trigger"] == "if_serv_attacked":
                        if "cible" in secret.effects["secret"][1][0]:
                            target = cible
                        else:
                            target = None
                        secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                        secret.effects.pop("secret")
                        self.apply_effects(secret, target)
                        adv.secrets.remove(secret)
                        adv.secrets_declenches += 1
                        if "halkias" in secret.effects:
                            self.invoke_servant(get_card("Halkias", all_servants), adv)
            elif attaquant in player.servants.cards and adv.secrets and "if_serv_attacks" in [x.effects["trigger"] for x in adv.secrets]:
                for secret in adv.secrets:
                    if secret.effects["trigger"] == "if_serv_attacks":
                        target = attaquant
                        secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                        secret.effects.pop("secret")
                        self.apply_effects(secret, target)
                        adv.secrets.remove(secret)
                        adv.secrets_declenches += 1
                        if "halkias" in secret.effects:
                            self.invoke_servant(get_card("Halkias", all_servants), adv)
            elif attaquant in player.servants.cards + [player] and adv.secrets and "if_hero_attacked" in [x.effects["trigger"] for x in adv.secrets] and type(cible) == Player:
                for secret in adv.secrets:
                    if secret.effects["trigger"] == "if_hero_attacked":
                        secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                        secret.effects.pop("secret")
                        self.apply_effects(secret)
                        adv.secrets.remove(secret)
                        adv.secrets_declenches += 1
                        if "halkias" in secret.effects:
                            self.invoke_servant(get_card("Halkias", all_servants), adv)
                        if secret.name == "Monstre errant":
                            cible = adv.servants.cards[-1]
            elif attaquant in player.servants.cards and adv.secrets and "if_hero_attacked_byserv" in [x.effects["trigger"] for x in adv.secrets] and type(cible) == Player:
                for secret in adv.secrets:
                    if secret.effects["trigger"] == "if_hero_attacked_byserv":
                        to_invoke = get_card(attaquant.name, all_servants)
                        to_invoke.attack, to_invoke.base_attack, to_invoke.health, to_invoke.base_health, to_invoke.blessure, to_invoke.effects = \
                            attaquant.attack, attaquant.base_attack, attaquant.health, attaquant.base_health, attaquant.blessure, attaquant.effects
                        secret.effects["secret"][1] = ["crea", to_invoke]
                        secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                        secret.effects.pop("secret")
                        target = player
                        self.apply_effects(secret, target)
                        adv.secrets.remove(secret)
                        adv.secrets_declenches += 1
                        if "halkias" in secret.effects:
                            self.invoke_servant(get_card("Halkias", all_servants), adv)
            elif "aura" in attaquant.effects and "before_attack" in attaquant.effects["aura"]:
                if "pioche" in attaquant.effects["aura"]:
                    if "serviteur" in attaquant.effects["aura"][1] and "Bête" in attaquant.effects["aura"][1]:
                        if [x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre]:
                            drawn_servant = random.choice(
                                [x for x in player.deck if x.type == "Serviteur" and "Bête" in x.genre])
                            player.deck.remove(drawn_servant)
                            player.hand.add(drawn_servant)
                            if "boost_caracs" in attaquant.effects["aura"][1]:
                                attaquant.boost(drawn_servant.attack, drawn_servant.health)
            if type(attaquant) == Player and type(cible) == Card:
                if [x for x in player.servants if "aura" in x.effects and "before_heros_allié_attack" in x.effects["aura"][1]]:
                    for servant in [x for x in player.servants if "aura" in x.effects and "before_heros_allié_attack" in x.effects["aura"][1]]:
                        if "debuff" in servant.effects["aura"] and "until_1pv" in servant.effects["aura"][2]:
                            cible.health = 1
                            cible.base_health = 1
                if attaquant.weapon is not None and "aura" in attaquant.weapon.effects and "before_attack" in attaquant.weapon.effects["aura"][1]:
                    if "boost" in attaquant.weapon.effects["aura"]:
                        if "cible" in attaquant.weapon.effects["aura"][1]:
                            cible.boost(attaquant.weapon.effects["aura"][2][0], attaquant.weapon.effects["aura"][2][1], fixed_stats=True)

            """ Attaque """
            if not attaquant.is_dead() and attaquant in player.servants.cards + adv.servants.cards + [player] + [adv]:
                if ([x for x in player.attached if x[0] == "Aura des croises"] and attaquant in player.servants.cards) or ([x for x in adv.attached if x[0] == "Aura des croises"] and attaquant in adv.servants.cards):
                    attaquant.boost(2, 1)
                if "gel_attack" in attaquant.effects and "bouclier divin" not in cible.effects and "insensible_attack" not in cible.effects:
                    cible.effects["gel"] = 1
                if "pietinement" in attaquant.effects and "bouclier divin" not in cible.effects:
                    adv.damage(max(0, attaquant.attack - cible.health)) if attaquant in player.servants else player.damage(max(0, attaquant.attack - cible.health))
                if "cleave" in attaquant.effects and type(cible) == Card:
                    index_target = adv.servants.cards.index(cible)
                    if index_target != 0:
                        cible_gauche = adv.servants[index_target - 1]
                        if "bouclier divin" not in cible_gauche.effects:
                            player.heal(attaquant.attack)
                    try:
                        cible_droite = adv.servants[index_target + 1]
                        if "bouclier divin" not in cible_droite.effects:
                            player.heal(attaquant.attack)
                    except:
                        pass
                if "vol de vie" in cible.effects and "bouclier divin" not in attaquant.effects and not [x for x in adv.servants if "anti_heal" in x.effects] and "insensible_attack" not in attaquant.effects:
                    adv.heal(cible.attack) if cible in adv.servants else player.heal(cible.attack)
                if "gel_attack" in cible.effects and "bouclier divin" not in attaquant.effects and "insensible_attack" not in attaquant.effects:
                    attaquant.effects["gel"] = 1
                if "aura" in attaquant.effects and "Neptulon" in attaquant.effects["aura"] and [x for x in
                                                                                                player.servants if
                                                                                                x.name == "Main de neptulon"]:
                    for main_nept in [x for x in player.servants if x.name == "Main de neptulon"]:
                        cible.damage(main_nept.attack, toxic=True if "toxicite" in main_nept.effects else False)
                else:
                    cible.damage(attaquant.attack, toxic=True if "toxicite" in attaquant.effects else False)
                    if "boost_attack" in attaquant.effects:
                        cible.damage(attaquant.effects["boost_attack"])
                    if "cleave" in attaquant.effects and type(cible) == Card:
                        index_target = adv.servants.cards.index(cible)
                        if index_target != 0:
                            cible_gauche = adv.servants[index_target - 1]
                            cible_gauche.damage(attaquant.attack, toxic=True if "toxicite" in attaquant.effects else False)
                        try:
                            cible_droite = adv.servants[index_target + 1]
                            cible_droite.damage(attaquant.attack, toxic=True if "toxicite" in attaquant.effects else False)
                        except:
                            pass
                if "vengeance" in attaquant.effects and not attaquant.is_dead():
                    adv.damage(cible.attack) if cible in adv.servants else player.damage(cible.attack)
                if "vengeance" in cible.effects and not cible.is_dead():
                    player.damage(attaquant.attack) if attaquant in player.servants else adv.damage(attaquant.attack)
                if not "insensible_attack" in attaquant.effects:
                    if not ("aura" in attaquant.effects and "Neptulon" in attaquant.effects["aura"] and [x for x in player.servants if x.name == "Main de neptulon"]):
                        attaquant.damage(cible.attack, toxic=True if "toxicite" in cible.effects else False)
                if "vol de vie" in attaquant.effects and "bouclier divin" not in cible.effects and not [x for x in adv.servants if "anti_heal" in x.effects]:
                    player.heal(attaquant.attack) if attaquant in player.servants.cards + [player] else adv.heal(attaquant.attack)
                attaquant.remaining_atk -= 1
                if "furie des vents" in attaquant.effects and attaquant.effects["furie des vents"] == 1:
                    attaquant.effects["furie des vents"] = 0
                    attaquant.remaining_atk = 1

                """ Après attaque"""
                if type(attaquant) == Card:
                    if [x for x in player.servants if "aura" in x.effects and "if_meca_attacks" in x.effects["aura"][1]] and "Méca" in attaquant.genre:
                        for entity in [adv] + adv.servants.cards:
                            entity.damage(1)
                    if "camouflage" in attaquant.effects:
                        attaquant.effects.pop("camouflage")
                    if "ruée" in attaquant.effects:
                        if [x for x in player.servants if "aura" in set(x.effects) and "if_ruee_attack" in set(x.effects["aura"][1])]:
                            for crea in player.servants:
                                crea.boost(1, 0)
                    if "gel_attack" in attaquant.effects and attaquant.attack != 0 and "bouclier divin" not in cible.effects:
                        cible.effects["gel"] = 1
                    if "aura" in attaquant.effects:
                        if attaquant.effects["aura"][2] == "attack":
                            if "self" in attaquant.effects["aura"][1]:
                                if "destroy" in attaquant.effects["aura"]:
                                    attaquant.blessure = 1000
                        if "if_attack" in attaquant.effects["aura"][1]:
                            if "damage" in attaquant.effects["aura"]:
                                if "heros" in attaquant.effects["aura"] and not [x for x in adv.servants if "anti_heal" in x.effects]:
                                    adv.damage(attaquant.effects["aura"][2])
                                    player.heal(attaquant.effects["aura"][2])
                                elif "serviteur" in attaquant.effects["aura"][1] and "aléatoire" in attaquant.effects["aura"][1] and adv.servants.cards:
                                    target = random.choice(adv.servants.cards)
                                    target.damage(attaquant.effects["aura"][2])
                            elif "boost" in attaquant.effects["aura"]:
                                if "Bête" in attaquant.effects["aura"][1]:
                                    for card in [x for x in player.servants if x.type == "Serviteur" and "Bête" in x.genre]:
                                        card.boost(attaquant.effects["aura"][2][0], attaquant.effects["aura"][2][1])
                                elif "aléatoire" in attaquant.effects["aura"][1] and [x for x in player.hand if x.type == "Serviteur"]:
                                    card = random.choice([x for x in player.hand if x.type == "Serviteur"])
                                    card.boost(attaquant.effects["aura"][2][0], attaquant.effects["aura"][2][1])
                                else:
                                    for card in [x for x in player.hand if x.type == "Serviteur"]:
                                        card.boost(attaquant.effects["aura"][2][0], attaquant.effects["aura"][2][1])
                            elif "pioche" in attaquant.effects["aura"]:
                                player.pick_multi(attaquant.effects["aura"][2])
                            elif "add_hand" in attaquant.effects["aura"]:
                                player.hand.add(get_card(attaquant.effects["aura"][2], all_spells))
                            elif "dragage" in attaquant.effects["aura"]:
                                self.plt.cards_dragage = [CardGroup(player.deck.cards[-3:].copy())]
                if type(attaquant) == Player:
                    if attaquant.weapon is not None:
                        if "aura" in attaquant.weapon.effects:
                            if "if_attack" in attaquant.weapon.effects["aura"][1]:
                                if "damage" in attaquant.weapon.effects["aura"] and "heros" in attaquant.weapon.effects["aura"][1] and "ennemi" in attaquant.weapon.effects["aura"][1]:
                                    adv.damage(attaquant.weapon.effects["aura"][2])
                                elif "heal" in attaquant.weapon.effects["aura"] and "heros" in attaquant.weapon.effects["aura"][1] and "allié" in attaquant.weapon.effects["aura"][1]:
                                    if "kvaldir" in player.permanent_buff:
                                        player.heal(attaquant.weapon.effects["aura"][2])
                                        player.permanent_buff.pop("kvaldir")
                                    else:
                                        player.heal(attaquant.weapon.effects["aura"][2])
                                elif "cadavre" in attaquant.weapon.effects["aura"]:
                                    if cible.is_dead():
                                        player.cadavres += attaquant.weapon.effects["aura"][2]
                                elif "reduc" in attaquant.weapon.effects["aura"]:
                                    if [x for x in player.hand if x.type == "Sort"]:
                                        random.choice([x for x in player.hand if x.type == "Sort"]).base_cost -= 1
                                elif "pioche" in attaquant.weapon.effects["aura"]:
                                    if "until_3" in attaquant.weapon.effects["aura"][1] and len(player.hand) < 3:
                                        player.pick_multi(3 - len(player.hand))
                                    else:
                                        player.pick_multi(1)
                                elif "dragage" in attaquant.weapon.effects["aura"]:
                                    self.plt.cards_dragage = [CardGroup(player.deck.cards[-min(1, len(player.deck.cards)):].copy())]
                                elif "boost" in attaquant.weapon.effects["aura"]:
                                    if "board" in attaquant.weapon.effects["aura"][1] and player.servants:
                                        for creature in player.servants:
                                            creature.boost(1, 1)
                                    if "main" in attaquant.weapon.effects["aura"][1] and [x for x in player.hand if x.type == "Serviteur"]:
                                        for creature in [x for x in player.hand if x.type == "Serviteur"]:
                                            creature.boost(1, 1)
                                    if "deck" in attaquant.weapon.effects["aura"][1] and [x for x in player.deck if x.type == "Serviteur"]:
                                        for creature in [x for x in player.deck if x.type == "Serviteur"]:
                                            creature.boost(1, 1)
                                if "invocation" in attaquant.weapon.effects["aura"]:
                                    if "Combattant vrykul" in attaquant.weapon.effects["aura"]:
                                        self.invoke_servant(get_card("Combattant vrykul", all_servants), player)
                        attaquant.weapon.health -= 1
                        if attaquant.weapon.health == 0:
                            player.dead_weapon = attaquant.weapon
                            if "rale d'agonie" in attaquant.weapon.effects:
                                if "if_dead_target" in attaquant.weapon.effects["rale d'agonie"][1] and cible.is_dead():
                                    attaquant.weapon.effects["rale d'agonie"][2].append(cible.name)
                            if [x for x in player.servants if "aura" in x.effects and "equip_weapon" in x.effects["aura"]]:
                                attaquant.weapon = Card(**random.choice([x for x in all_weapons if x["classe"] == "Chasseur de démons"]))
                            elif [x for x in player.servants if "aura" in x.effects and "insensible_attack" in x.effects["aura"][1]]:
                                player.effects.pop("insensible_attack")
                            else:
                                attaquant.weapon = None
                    attaquant.total_attacks += 1
                    if [x for x in player.servants if "aura" in x.effects and "heros_allié_attack" in x.effects["aura"][1]]:
                        for servant in [x for x in player.servants if "aura" in x.effects and "heros_allié_attack" in x.effects["aura"][1]]:
                            if "boost" in servant.effects["aura"][1]:
                                servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                            elif "pioche" in servant.effects["aura"]:
                                if "sort" in servant.effects["aura"][1] and "Fiel" in servant.effects["aura"][1]:
                                    drawable_cards = [x for x in player.deck if x.type == "Sort" and "Fiel" in x.genre]
                                    if drawable_cards:
                                        drawn_card = random.choice(drawable_cards)
                                        player.deck.remove(drawn_card)
                                        player.hand.add(drawn_card)
                                elif "Pirate" in servant.effects["aura"][1]:
                                    drawable_cards = [x for x in player.deck if x.type == "Serviteur" and "Pirate" in x.genre]
                                    if drawable_cards:
                                        drawn_card = random.choice(drawable_cards)
                                        player.deck.remove(drawn_card)
                                        player.hand.add(drawn_card)
                            elif "return_hand" in servant.effects["aura"]:
                                player.servants.remove(servant)
                                if len(player.hand) < 10:
                                    card_to_hand = get_card(servant.name, all_servants)
                                    card_to_hand.base_cost = 1
                                    player.hand.add(card_to_hand)
                            elif "attack" in servant.effects["aura"] and not cible.is_dead():
                                self.attaquer(servant, cible)
                            elif "invocation" in servant.effects["aura"] and len(player.servants) + len(player.lieux) < 7:
                                self.invoke_servant(get_card(servant.effects["aura"][-1], all_servants), player)
                attaquant.has_attacked = 1
        else:
            raise TypeError

    def pouvoir_heroique(self, classe, cible):
        player = self.plt.players[0]
        adv = self.plt.players[1]
        if type(cible) in (Player, Card):
            if player.power is None:
                if classe == "Mage":
                    cible.damage(1)
                elif classe == "Chasseur":
                    cible.damage(2)
                elif classe == "Paladin":
                    carte = get_card("Recrue de la main d'argent", all_servants)
                    self.invoke_servant(carte, player)
                elif classe == "Chevalier de la mort":
                    carte = get_card("Goule fragile", all_servants)
                    self.invoke_servant(carte, player)
                elif classe == "Démoniste":
                    cible.damage(2)
                    if len(player.deck) > 0:
                        player.pick()
                    else:
                        cible.fatigue += 1
                elif classe == "Prêtre" and not [x for x in adv.servants if "anti_heal" in x.effects]:
                    if "kvaldir" in player.permanent_buff:
                        cible.damage(2)
                        player.permanent_buff.pop("kvaldir")
                    else:
                        cible.heal(2)
                elif classe == "Chasseur de démons":
                    cible.inter_attack += 1
                    if "attack" in player.hp_boost:
                        cible.inter_attack += player.hp_boost["attack"]
                elif classe == "Druide":
                    cible.inter_attack += 1
                    cible.armor += 1
                    if "armure" in player.hp_boost:
                        cible.armor += player.hp_boost["armure"]
                    if "attack" in player.hp_boost:
                        cible.inter_attack += player.hp_boost["attack"]
                elif classe == "Voleur":
                    cible.weapon = get_card("Lame pernicieuse", all_weapons)
                    cible.attack += cible.weapon.attack
                    if [x for x in player.servants if "aura" in x.effects and "if_weapon_invoked" in x.effects["aura"][1]]:
                        for servant in [x for x in player.servants if "aura" in x.effects and "if_weapon_invoked" in x.effects["aura"][1]]:
                            if "boost" in servant.effects["aura"]:
                                player.weapon.attack += servant.effects["aura"][-1][0]
                elif classe == "Guerrier":
                    cible.armor += 2
                elif classe == "Chaman":
                    cartes = [get_card("Totem de soin", all_servants),
                              get_card("Totem incendiaire", all_servants),
                              get_card("Totem de puissance", all_servants),
                              get_card("Totem de griffes de pierre", all_servants)]
                    self.invoke_servant(random.choice(cartes), player)
                if player.cout_pouvoir_temp != player.cout_pouvoir:
                    player.mana_spend(player.cout_pouvoir_temp)
                    player.cout_pouvoir_temp = player.cout_pouvoir
                else:
                    player.mana_spend(player.cout_pouvoir)
            elif player.power[0] == "Explosion demoniaque":
                cible.damage(4)
                player.power[1] -= 1
                player.mana_spend(player.cout_pouvoir)
                if player.power[1] == 0:
                    player.power = None
                    player.cout_pouvoir = 2 if not player.classe == "Chasseur de démons" else 1
            elif player.power[0] == "Pretre ombre":
                cible.damage(2)
                if player.cout_pouvoir_temp != player.cout_pouvoir:
                    player.mana_spend(player.cout_pouvoir_temp)
                    player.cout_pouvoir_temp = player.cout_pouvoir
                else:
                    player.mana_spend(player.cout_pouvoir)
            player.dispo_pouvoir = False
            if player.weapon is not None and "aura" in player.weapon.effects and "hp_boost" in player.weapon.effects["aura"]:
                player.weapon.health -= 1
            if [x for x in player.servants if "aura" in x.effects and "if_hero_power" in x.effects["aura"][1]]:
                for creature in [x for x in player.servants if "aura" in x.effects and "if_hero_power" in x.effects["aura"][1]]:
                    if "damage" in creature.effects["aura"]:
                        potential_target = random.choice(adv.servants + [adv])
                        potential_target.damage(5)
        else:
            raise TypeError

    def choice_decouverte(self, carte, type=None, genre=None, classe=None, other=None, card_group=None, reduc=None, cost=None):
        player = self.plt.players[0]
        discovery = []
        if card_group is not None and card_group:
            return [random.sample(card_group.cards, min(3, len(card_group.cards)))]
        if type == "serviteur":
            if genre:
                if classe is not None:
                    if classe == "other":
                        while len(discovery) < 3:
                            x = random.choice(all_servants)
                            if set(genre).intersection(x["genre"]) and x["decouvrable"] == 1 and x["classe"] != carte.classe and x["classe"] != "Neutre" and x not in discovery:
                                discovery.append(x)
                else:
                    while len(discovery) < 3:
                        x = random.choice(all_servants)
                        if set(genre).intersection(x["genre"]) and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                            discovery.append(x)
            elif other:
                if classe is not None:
                    while len(discovery) < 3:
                        x = random.choice(all_servants)
                        if other in x['effects'] and x["decouvrable"] == 1 and x["name"] != carte.name and x["classe"] == classe and x not in discovery:
                            discovery.append(x)
                else:
                    while len(discovery) < 3:
                        x = random.choice(all_servants)
                        if other in x['effects'] and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                            discovery.append(x)
            elif cost:
                while len(discovery) < 3:
                    x = random.choice(all_servants)
                    if x['cost'] == cost and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)
            else:
                while len(discovery) < 3:
                    x = random.choice(all_servants)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)
        elif type == "sort":
            if classe:
                if classe == "other_class":
                    if cost == "under3":
                        while len(discovery) < 3:
                            x = random.choice(all_spells)
                            if x["classe"] not in ["Neutre", player.classe] and x["decouvrable"] == 1 and x["cost"] <= 3 and x not in discovery:
                                discovery.append(x)
                    if other == "Secret":
                        while len(discovery) < 3:
                            x = random.choice(all_spells)
                            if "secret" in x["effects"] and x["decouvrable"] == 1 and x["classe"] not in [player.classe, "Neutre"] and x not in discovery:
                                discovery.append(x)
                    else:
                        while len(discovery) < 3:
                            x = random.choice(all_spells)
                            if x["classe"] not in ["Neutre", player.classe] and x["decouvrable"] == 1 and x not in discovery:
                                discovery.append(x)
                else:
                    while len(discovery) < 3:
                        x = random.choice(all_spells)
                        if set(classe).intersection(x["classe"]) and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                            discovery.append(x)
            elif other == "Secret":
                while len(discovery) < 3:
                    x = random.choice(all_spells)
                    if "secret" in x["effects"] and x["decouvrable"] == 1 and x not in discovery:
                        discovery.append(x)
            elif other == "decoction":
                while len(discovery) < 3:
                    x = random.choice(all_spells)
                    if "decoction" in x["effects"] and x not in discovery:
                        discovery.append(x)
            elif other == "not_used_ecole":
                if len(player.ecoles_jouees) != 8:
                    while len(discovery) < 3:
                        x = random.choice(all_spells)
                        if x["genre"] and x["genre"][0] not in player.ecoles_jouees and x["decouvrable"] == 1 and x not in discovery:
                            discovery.append(x)
                else:
                    if len(player.ecoles_jouees) != 8:
                        while len(discovery) < 3:
                            x = random.choice(all_spells)
                            if x["decouvrable"] == 1 and x not in discovery:
                                discovery.append(x)
            elif other == "relique":
                while len(discovery) < 3:
                    x = random.choice(all_spells)
                    if "Relique" in x["name"] and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)
            elif other == "institutrice":
                while len(discovery) < 3:
                    x = random.choice(all_spells)
                    if x["cost"] <= 3 and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)
            elif genre:
                while len(discovery) < 3:
                    x = random.choice(all_spells)
                    if genre in x["genre"] and x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)
            else:
                while len(discovery) < 3:
                    x = random.choice(all_spells)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)
        else:
            if other in ["vert", "bleu", "rouge"]:
                while len(discovery) < 3:
                    x = random.choice(all_cards)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and other in x["effects"] and x not in discovery:
                        discovery.append(x)
            elif other == "marginal":
                while len(discovery) < 3:
                    x = random.choice(all_cards)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and "marginal" in x["effects"] and x not in discovery:
                        discovery.append(x)
            elif classe is not None:
                while len(discovery) < 3:
                    x = random.choice(all_cards)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and x["classe"] == classe and x not in discovery:
                        discovery.append(x)
            elif cost is not None:
                while len(discovery) < 3:
                    x = random.choice(all_cards)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and x["cost"] == cost and x not in discovery:
                        discovery.append(x)
            else:
                while len(discovery) < 3:
                    x = random.choice(all_cards)
                    if x["decouvrable"] == 1 and x["name"] != carte.name and x not in discovery:
                        discovery.append(x)

        if other == "Okani":
            discovery = [get_card("Riposte de sort", all_spells), get_card("Riposte de serviteur", all_spells)]
        else:
            discovery = [Card(**x) for x in discovery]
        if other == "choix mystere":
            discovery.append("choix mystere")
        if reduc is not None:
            for element in discovery:
                if other == "temp_turn":
                    element.effects["temp_reduc"] = 1
                element.base_cost = max(0, element.base_cost - reduc)
        if self.plt.players[0].randomade:
            return [[random.choice(discovery)]]
        else:
            return [discovery]

    def decouverte(self, cards, choice, type_dec="decouverte", target=None):
        player = self.plt.players[0]
        adv = self.plt.players[1]
        if type_dec == "decouverte":
            if choice != 3:
                if [x for x in player.hand if x.name == "Jeune naga" and x.effects["cri de guerre"][2] == ""]:
                    [x for x in player.hand if
                     x.name == "Jeune naga" and x.effects["cri de guerre"][2] == ""][0].effects["cri de guerre"][2] = [cards[choice].name]
                elif cards[choice].name in ["Riposte de sort", "Riposte de serviteur"]:
                    [x for x in player.servants if x.name == "Maitre lame Okani"][0].effects["aura"] = ["counter", "sort" if cards[choice].name == "Riposte de sort" else "serviteur", ""]
                elif len(player.servants) != 0 and player.last_card.name == "Theotar le duc fou":
                    if len(self.plt.cards_chosen) == 1:
                        self.plt.players[1].hand.add(cards[choice])
                        player.hand.remove(cards[choice])
                    elif len(self.plt.cards_chosen) == 2:
                        player.hand.add(cards[choice])
                        self.plt.players[1].hand.remove(cards[choice])
                elif player.servants.cards and player.servants.cards[-1].name == "Artificier Xy'mox" and "Relique" in cards[choice].name:
                    self.apply_effects(cards[choice])
                elif player.last_card.name == "Bourgeon de belladone" or player.last_card.name == "Bourgeon de belladone combine":
                    if cards[choice].type == "Serviteur":
                        self.invoke_servant(cards[choice], player)
                        if player.last_card.name == "Bourgeon de belladone combine":
                            self.plt.cards_chosen = self.choice_decouverte(get_card("Bourgeon de belladone combine", all_spells), card_group=CardGroup([x for x in player.deck if x.type == "Sort"]))
                    else:
                        self.apply_effects(cards[choice])
                elif player.last_card.name in ["Piege forge par les titans", "Piege forge par les titans forge", "Harmoniciste soliste", "Parjure"]:
                    self.apply_effects(cards[choice])
                elif player.last_card.name == "Carquois arcanique" and "Arcanes" in cards[choice].genre and "damage" in cards[choice].effects:
                    if type(cards[choice].effects["damage"]) == int:
                        cards[choice].effects["damage"] += 1
                    elif type(cards[choice].effects["damage"]) == list:
                        cards[choice].effects["damage"][-1] += 1
                elif player.last_card.name == "Fossoyeuse spectrale" and adv.hand.cards:
                    adv.hand.remove(cards[choice])
                    adv.deck.add(cards[choice])
                    adv.deck.shuffle()
                else:
                    if player.last_card.name in ["Eleveur selectif", "Protocole de la creation", "Protocole de la creation forge", "Epanouissement dans l'ombre"]:
                        player.hand.add(copy_card(cards[choice]))
                        if player.last_card.name == "Protocole de la creation forge":
                            player.hand.add(copy_card(cards[choice]))
                    else:
                        player.hand.add(cards[choice])
                        if cards[choice] in player.deck:
                            player.deck.remove(cards[choice])
                    if "porteur d'invitation" in [x.effects for x in player.servants] and Card(**cards[choice]).classe not in ["Neutre",
                                                                                                    self.plt.players[
                                                                                                        0].classe]:
                        player.hand.add(Card(**cards[choice]))
                    if player.ames_liees and cards[choice] in player.ames_liees:
                        player.ames_liees.remove(cards[choice])
            else:
                if cards[choice] == "choix mystere":
                    while True:
                        card_to_add = random.choice(all_spells)
                        if card_to_add["decouvrable"] == 1:
                            break
                    card_to_add = Card(**card_to_add)
                    player.hand.add(card_to_add)
            self.plt.cards_chosen.pop(0)
            if player.decouverte:
                if cards[choice].name != player.decouverte[1].name:
                    player.hand.remove(cards[choice])
                player.decouverte = []
            if player.last_card.name == "Dompteur du fleau" and "second_time" in player.last_card.effects:
                self.plt.cards_chosen = self.choice_decouverte(player.last_card, type="serviteur", genre=["Bête"])
                player.last_card.effects.pop("second_time")
            elif player.last_card.name == "Grande sagesse" and "second_time" in player.last_card.effects:
                self.plt.cards_chosen = self.choice_decouverte(player.last_card, type="sort", other="institutrice")
                player.last_card.effects.pop("second_time")
            elif player.last_card.name == "Usurpation d'identite" and "second_time" in player.last_card.effects and adv.deck.cards:
                self.plt.cards_chosen = self.plt.cards_chosen = self.choice_decouverte(player.last_card, card_group=CardGroup([get_card(x.name, all_cards) for x in adv.deck]))
                player.last_card.effects.pop("second_time")
            elif player.last_card.name == "Ceinture a potions" and "second_time" in player.last_card.effects:
                self.plt.cards_chosen = self.choice_decouverte(player.last_card, type="sort", other="decoction")
                player.last_card.effects.pop("second_time")
            elif player.last_card.name == "Piege forge par les titans forge" and "second_time" in player.last_card.effects:
                self.plt.cards_chosen = self.choice_decouverte(get_card("Piege forge par les titans forge", all_spells), type="sort", other="Secret")
                player.last_card.effects.pop("second_time")
            elif player.last_card.name == "Dompteur du fleau":
                player.hand.cards[-2].boost(player.hand.cards[-1].base_attack, player.hand.cards[-1].base_health)
                player.hand.cards[-2].cost += player.hand.cards[-1].cost
                player.hand.cards[-2].base_cost += player.hand.cards[-1].base_cost
                player.hand.cards[-2].effects.update(player.hand.cards[-1].effects)
                player.hand.cards.pop(-1)
            elif player.last_card.name == "Grande sagesse":
                player.hand.cards[-2].cost, player.hand.cards[-1].cost = player.hand.cards[-1].cost, player.hand.cards[-2].cost
                player.hand.cards[-2].base_cost, player.hand.cards[-1].base_cost = player.hand.cards[-1].base_cost, player.hand.cards[-2].base_cost
            elif player.last_card.name == "Avocat de la defense Nathanos":
                player.last_card.effects["rale d'agonie"] = cards[choice].effects["rale d'agonie"]
                player.last_card.effects["rale_applied"] = 1
                self.apply_effects(player.last_card)
                player.last_card.effects.pop("rale_applied")
            elif player.last_card.name == "Fideles compagnons":
                player.hand.remove(cards[choice])
                self.invoke_servant(cards[choice], player)
                if player.mana_max >= 10 and [x for x in player.hand if "Bête" in x.genre]:
                    beast_to_invoke = random.choice([x for x in player.hand if "Bête" in x.genre])
                    player.hand.remove(beast_to_invoke)
                    self.invoke_servant(beast_to_invoke, player)
            elif player.last_card.name in ["Disco harmonique", "Disco dissonant"]:
                if player.last_card.name == "Disco harmonique":
                    cards[choice].boost(1, 1)
                elif player.last_card.name == "Disco dissonant":
                    cards[choice].boost(5, 5)
                player.hand.remove(cards[choice])
                self.invoke_servant(cards[choice], player)
            elif player.last_card.name in ["Alchimiste suspecte", "Appariteur suspect"]:
                adv.decouverte = [[get_card(x.name, all_cards) for x in cards], cards[choice]]
                player.last_card = get_card(-1, all_cards)
            elif player.last_card.name == "Cloche de service":
                if [x for x in player.deck if x.name == cards[choice].name]:
                    for card in [x for x in player.deck if x.name == cards[choice].name]:
                        player.deck.remove(card)
                        player.hand.add(card)
            elif player.last_card.name == "Point de ravitaillement":
                try:
                    cards[choice].boost(2, 1)
                except:
                    pass
        elif type_dec == "dragage":
            try:
                if not player.last_card.name == "Elementaire desarmant" and player.deck.cards:
                    player.deck.cards.remove(cards[choice])
                    if player.weapon is not None and player.weapon.name == "Fusil harpon" and cards[choice].type == "Serviteur" and "Bête" in cards[choice].genre:
                        cards[choice].base_cost = max(0, cards[choice].base_cost - 2)
                    if player.last_card.name == "Sauveteuse des grands fonds" and cards[choice].type == "Serviteur":
                        cards[choice].boost(player.last_card.base_attack, player.last_card.base_health)
                    elif player.last_card.name == "Cab o tron" and cards[choice].cost == 1 and cards[choice].type == "Serviteur":
                        self.invoke_servant(cards[choice], player)
                    elif player.last_card.name == "Forme aquatique" and player.mana >= cards[choice].cost:
                        player.hand.add(cards[choice])
                    elif player.last_card.name == "Arpenteur des fosses" and "Méca" in cards[choice].genre:
                        player.hand.add(cards[choice])
                    elif player.last_card.name == "Illumination" and cards[choice].type == "Sort":
                        cards[choice].base_cost = max(0, cards[choice].base_cost - 3)
                        player.deck.cards.insert(0, cards[choice])
                    elif player.last_card.name == "Necromancienne putrefiee" and "Mort-vivant" in cards[choice].genre:
                        adv.damage(5)
                        player.deck.cards.insert(0, cards[choice])
                    elif player.last_card.name == "Espadon" and "Pirate" in cards[choice].genre:
                        player.weapon.attack += 2
                        cards[choice].boost(2, 2)
                    else:
                        player.deck.cards.insert(0, cards[choice])
                elif player.last_card.name == "Elementaire desarmant" and adv.deck.cards:
                    adv.deck.cards.remove(cards[choice])
                    cards[choice].base_cost = 6
                    adv.deck.cards.insert(0, cards[choice])
            except:
                pass
            self.plt.cards_dragage.pop(0)
        elif type_dec == "entrave":
            cards[choice].effects["entrave"] = 1
            self.plt.cards_entrave.pop(0)
        elif type_dec == "hand_to_deck":
            try:
                player.hand.remove(cards[choice])
                player.deck.add(cards[choice])
                player.deck.shuffle()
                self.plt.cards_hands_to_deck.pop(0)
            except:
                print(player.lieux)
                print(player.hand, cards, cards[choice])
                raise TypeError
        elif type_dec == "choix_des_armes":
            if cards.type == "Serviteur":
                cards.effects["cri de guerre"] = cards.effects["choix_des_armes"][choice]
            elif cards.type == "Sort":
                cards.effects[cards.effects["choix_des_armes"][choice][0]] = cards.effects["choix_des_armes"][choice][1]
            cards.effects.pop("choix_des_armes")
            self.plt.choix_des_armes = None
            self.apply_effects(cards)

    def echange(self, carte):
        player = self.plt.players[0]
        player.hand.remove(carte)
        player.deck.add(carte)
        player.deck.shuffle()
        player.pick()
        player.mana_spend(1)
        if carte.effects["echangeable"] != 1:
            if carte.effects["echangeable"] == "rush_serv_allié" and player.servants.cards:
                target = random.choice(player.servants.cards)
                target.effects["ruée"] = 1

    def forge(self, carte):
        player = self.plt.players[0]
        player.hand.remove(carte)
        player.hand.add(get_card(carte.effects["forge"], all_cards))
        player.mana_spend(2)

    def fin_du_tour(self):
        player = self.plt.players[0]
        adv = self.plt.players[1]
        """ Effets de fin de tour """
        for servant in player.servants:
            servant.damage_taken = False
            if "aura" in servant.effects and "end_turn" in servant.effects["aura"][1]:
                if "boost" in servant.effects["aura"]:
                    if "self" in servant.effects["aura"][1]:
                        if "random_lose" in servant.effects["aura"][1]:
                            if random.randint(0, 1) == 0:
                                servant.attack -= 1
                                servant.base_attack -= 1
                            else:
                                servant.health -= 1
                                servant.base_health -= 1
                        elif "if_mana_left" in servant.effects["aura"][1]:
                            if player.mana > 0:
                                servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                        else:
                            servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                    elif "allié" in servant.effects["aura"][1] and "aléatoire" in servant.effects["aura"][1]:
                        if len(player.servants) > 1:
                            boosted_servant = random.choice([x for x in player.servants if x != servant])
                            boosted_servant.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                elif "main" in servant.effects["aura"][1]:
                    if "allié" in servant.effects["aura"][1] and "serviteur" in servant.effects["aura"][1]:
                        if [x for x in player.hand if x.type == "Serviteur"]:
                            target = random.choice([x for x in player.hand if x.type == "Serviteur"])
                            target.boost(servant.effects["aura"][2][0], servant.effects["aura"][2][1])
                elif "pioche" in servant.effects["aura"]:
                    if "adv_dmg" in servant.effects["aura"][1] and adv.damage_this_turn >= 3:
                        player.pick()
                    elif "sort" in servant.effects["aura"][1]:
                        if "secret" in servant.effects["aura"][1] and [x for x in player.deck if "secret" in x.effects]:
                            card_to_draw = random.choice([x for x in player.deck if "secret" in x.effects])
                            player.deck.remove(card_to_draw)
                            player.hand.add(card_to_draw)
                    elif "if_noattack" in servant.effects["aura"][1] and servant.has_attacked != 1:
                        player.pick_multi(servant.effects["aura"][2])
                elif "add_deck" in servant.effects["aura"] and "random_spell_top" in servant.effects["aura"][1]:
                    while True:
                        card_to_add = random.choice(all_spells)
                        if card_to_add["decouvrable"] == 1:
                            break
                    card_to_add = Card(**card_to_add)
                    adv.deck.cards.insert(0, card_to_add)
                elif "damage" in servant.effects["aura"]:
                    if "tous" in servant.effects["aura"][1]:
                        if not "aléatoire" in servant.effects["aura"][1]:
                            if "ennemi" in servant.effects["aura"][1]:
                                if "conditional" in servant.effects["aura"][1]:
                                    if "if_secret" in servant.effects["aura"][1] and player.secrets:
                                        for entity in [adv] + adv.servants.cards:
                                            entity.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                            else:
                                for entity in [player] + [adv] + player.servants.cards + adv.servants.cards:
                                    if entity != servant:
                                        entity.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                        elif "ennemi" in servant.effects["aura"][1]:
                            target = random.choice([adv] + adv.servants.cards)
                            target.damage(servant.effects["aura"][2], toxic=True if "toxicite" in servant.effects else False)
                    elif "heros" in servant.effects["aura"][1] and "allié" in servant.effects["aura"][1]:
                        player.damage(servant.effects["aura"][2])
                elif "attack" in servant.effects["aura"]:
                    if "serviteur" in servant.effects["aura"][1] and "ennemi" in servant.effects["aura"][1] and adv.servants.cards:
                        if "tous" in servant.effects["aura"][1]:
                            for creature in adv.servants.cards:
                                if not servant.is_dead():
                                    self.attaquer(creature, servant)
                        elif "aléatoire" in servant.effects["aura"][1]:
                            if "behemoth" in servant.effects["aura"][1] and [x for x in player.servants if x.name == "Behemoth des flots noirs"]:
                                creature = random.choice(adv.servants.cards)
                                if not servant.is_dead():
                                    self.attaquer(creature, [x for x in player.servants if x.name == "Behemoth des flots noirs"][0])
                    elif "ennemi" in servant.effects["aura"][1] and "lowest_health" in servant.effects["aura"][1]:
                        lowest_health = min([x.health for x in adv.servants.cards + [adv]])
                        target = random.choice([x for x in adv.servants.cards + [adv] if x.health == lowest_health])
                        self.attaquer(servant, target)
                elif "invocation" in servant.effects["aura"]:
                    if "until_full" in servant.effects["aura"][1]:
                        while len(player.servants) + len(player.lieux) < 7:
                            player.servants.add(get_card(servant.effects["aura"][2], all_servants))
                    elif "if_cadavre" in servant.effects["aura"][1] and player.cadavres >= servant.effects["aura"][1][-1] and len(player.servants) + len(player.lieux) < 7:
                        player.cadavres -= servant.effects["aura"][1][-1]
                        if "copy" in servant.effects["aura"][1]:
                            player.servants.add(copy_card(servant))
                        else:
                            player.servants.add(get_card(servant.effects["aura"][2], all_servants))
                    elif "copy" in servant.effects["aura"][1] and len(player.servants) + len(player.lieux) < 7 and "just_copied" not in servant.effects:
                        if "temp" in servant.effects["aura"][1]:
                            servant.effects.pop("aura")
                        to_invoke = copy_card(servant)
                        to_invoke.effects["just_copied"] = 1
                        self.invoke_servant(to_invoke, player)
                    elif "aléatoire" in servant.effects["aura"][1] and len(player.servants) + len(player.lieux) < 7:
                        if "dead_undead" in servant.effects["aura"][1] and player.dead_zombies:
                            to_invoke = get_card(random.choice(player.dead_zombies), all_servants)
                            self.invoke_servant(to_invoke, player)
                    else:
                        if len(player.servants) + len(player.lieux) < 7:
                            try:
                                self.invoke_servant(get_card(servant.effects["aura"][2], all_servants), player)
                            except:
                                print(servant, servant.effects)
                                raise TypeError
                elif "add_hand" in servant.effects["aura"]:
                    if "allié" in servant.effects["aura"][1]:
                        if "decoction" in servant.effects["aura"][1]:
                            while True:
                                card_to_draw = random.choice(all_spells)
                                if "decoction" in card_to_draw["effects"]:
                                    break
                            card_to_draw = Card(**card_to_draw)
                            player.hand.add(card_to_draw)
            if "frail" in servant.effects:
                servant.blessure = 1000
            if "temp_turn" in servant.effects:
                servant.attack -= servant.effects["temp_turn"][0]
                servant.health -= servant.effects["temp_turn"][1]
                servant.base_health -= servant.effects["temp_turn"][1]
            if "temp_turn_bonus" in servant.effects and servant.effects["temp_turn_bonus"] in servant.effects:
                servant.effects.pop(servant.effects["temp_turn_bonus"])
            if "gel" in servant.effects and not servant.has_attacked:
                servant.effects.pop("gel")
        for card in player.hand:
            if "temp_reduc" in card.effects:
                card.base_cost = card.intrinsec_cost
                card.effects.pop("temp_reduc")
            if "temp_augment" in card.effects:
                card.base_cost = min(card.base_cost - card.effects["temp_augment"], get_card(card.name, all_cards).base_cost)
                card.effects.pop("temp_augment")
            if "eclosion" in card.effects:
                card.effects["eclosion"][1] -= 1
                if card.effects["eclosion"][1] <= 0:
                    player.hand.cards = [get_card(card.effects["eclosion"][0], all_cards) if x == card else x for x in player.hand.cards]
            if "brulure" in card.effects:
                card.effects.pop("brulure")
                player.hand.remove(card)
            if "fragile" in card.effects:
                player.hand.remove(card)
        for servant in adv.servants:
            if "aura" in servant.effects and "each_turn" in servant.effects["aura"][1]:
                if "invocation" in servant.effects["aura"]:
                    if "until_full" in servant.effects["aura"][1]:
                        while len(adv.servants) + len(adv.lieux) < 7:
                            adv.servants.add(get_card(servant.effects["aura"][2], all_servants))
            if "infection" in servant.effects and "end_turn" in servant.effects["infection"]:
                if "self_damage" in servant.effects["infection"] and "vol de vie" in servant.effects["infection"]:
                    servant.damage(servant.effects["infection"][-1], toxic=True if "toxicite" in servant.effects else False)
                    player.heal(servant.effects["infection"][-1])
        if player.discount_next:
            for discount in [x for x in player.discount_next if len(x) >= 3 and x[3] == "temp_turn"]:
                player.discount_next.remove(discount)
        if "Rock en fusion" in [x.name for x in player.hand]:
            rock_en_fusion = [x for x in player.hand if x.name == "Rock en fusion"][0]
            player.hand.remove(rock_en_fusion)
            if player.mana > 0:
                player.damage(rock_en_fusion.effects["rock_en_fusion"])
            else:
                rock_en_fusion.effects["rock_en_fusion"] += 2
                adv.hand.add(rock_en_fusion)
        if adv.secrets.cards:
            if "if_zero_mana" in [x.effects["trigger"] for x in adv.secrets] and player.mana == 0:
                for secret in [x for x in adv.secrets if x.effects["trigger"] == "if_zero_mana"]:
                    secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                    secret.effects.pop("secret")
                    self.apply_effects(secret)
                    adv.secrets.remove(secret)
                    adv.secrets_declenches += 1
                    if "halkias" in secret.effects:
                        self.invoke_servant(get_card("Halkias", all_servants), adv)
            if "fin_tour_adv" in [x.effects["trigger"] for x in adv.secrets] and player.cards_this_turn:
                for secret in [x for x in adv.secrets if x.effects["trigger"] == "fin_tour_adv"]:
                    secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                    secret.effects.pop("secret")
                    self.apply_effects(secret)
                    adv.secrets.remove(secret)
                    adv.secrets_declenches += 1
                    if "halkias" in secret.effects:
                        self.invoke_servant(get_card("Halkias", all_servants), adv)
        if player.effects:
            if "end_turn" in player.effects and "damage" in player.effects["end_turn"]:
                if "heros" in player.effects["end_turn"][1] and "ennemi" in player.effects["end_turn"][1]:
                    adv.damage(player.effects["end_turn"][2])
            if "cost_armor" in player.effects:
                player.effects.pop("cost_armor")
            if "vol de vie" in player.effects:
                player.effects.pop("vol de vie")
            if [x for x in player.effects if player.effects[x] == "temp_turn"]:
                for effect in [x for x in player.effects if player.effects[x] == "temp_turn"]:
                    player.effects.pop(effect)
        if "Gardien du temps" in player.permanent_buff:
            player.permanent_buff["Gardien du temps"] -= 1
            if player.permanent_buff["Gardien du temps"] == 0:
                player.permanent_buff.pop("Gardien du temps")
        if "croise sanglant" in player.permanent_buff:
            player.permanent_buff.pop("croise sanglant")
            for serv in [x for x in player.hand if "cost_pv" in x.effects]:
                serv.effects.pop("cost_pv")
        if "eternel amour" in player.permanent_buff and player.spell_this_turn == 0:
            player.permanent_buff.pop("eternel amour")
        if "enchanteur" in player.permanent_buff:
            player.permanent_buff.pop("enchanteur")
        if [x for x in player.servants if "just_copied" in x.effects]:
            for creature in [x for x in player.servants if "just_copied" in x.effects]:
                creature.effects.pop("just_copied")
        if player.end_turn_cards:
            for card in player.end_turn_cards:
                player.hand.add(get_card(card, all_cards))
            player.end_turn_cards = []
        if player.spells_played:
            player.spell_before = True
        else:
            player.spell_before = False

    def debut_du_tour(self):
        player = self.plt.players[0]
        adv = self.plt.players[1]
        """ Effet de début de tour"""
        if player.poofed or adv.poofed:
            player.poofed[1] -= 0.5
            adv.poofed[1] -= 0.5
            if player.poofed[1] == 0:
                for serv in player.poofed[0]:
                    if player.poofed[0]:
                        player.servants.add(serv)
                player.poofed = []
            if adv.poofed[1] == 0:
                if adv.poofed[0]:
                    for serv in adv.poofed[0]:
                        adv.servants.add(serv)
                adv.poofed = []
        if [x for x in player.attached if x[-1] == 0]:
            for effect in [x for x in player.attached if x[-1] == 0]:
                player.attached.remove(effect)
                if effect[0] in ["Melodie des anciens", "Danse des geants"]:
                    self.apply_effects(get_card(effect[0], all_cards))
        if player.secrets and [x for x in player.secrets if x.effects["trigger"] == "debut_tour_j"]:
            for secret in [x for x in player.secrets if x.effects["trigger"] == "debut_tour_j"]:
                target = None
                secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                secret.effects.pop("secret")
                player.last_card = secret
                self.apply_effects(secret, target)
                player.secrets.remove(secret)
                player.secrets_declenches += 1
                if "halkias" in secret.effects:
                    self.invoke_servant(get_card("Halkias", all_servants), player)
        player.servants.reset()
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
                        self.plt.update()
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
            if "en sommeil" in servant.effects:
                if type(servant.effects["en sommeil"]) == int:
                    servant.effects["en sommeil"] -= 1
                    if servant.effects["en sommeil"] == 0:
                        servant.effects.pop("en sommeil")
                        if "insensible" in servant.effects:
                            servant.effects.pop("insensible")
                        servant.remaining_atk = 0
                        if "awaken" in servant.effects:
                            servant.effects["cri de guerre"] = servant.effects["awaken"]
                            servant.effects.pop("awaken")
                        TourEnCours(self.plt).apply_effects(servant)
            if "camouflage" in servant.effects and servant.effects["camouflage"] == 0:
                servant.effects.pop("camouflage")
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
        if [x for x in adv.attached if x[0] == "Aura de resistance"]:
            player.augment.append(["sort", "temp_fullturn", 1])
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

        """ Buffs """
        if "alibi solide" in player.permanent_buff:
            player.permanent_buff.pop("alibi solide")
        if "eternel amour" in player.permanent_buff:
            player.permanent_buff["eternel amour"] = 1
            for card in [x for x in player.hand if x.type == "Sort"]:
                card.cost = max(0, card.cost - 2)

        """ Découvertes de début de tour """
        if player.decouverte:
            self.plt.cards_chosen = self.choice_decouverte(get_card(-1, all_cards), card_group=CardGroup(player.decouverte[0]))


class Orchestrator:

    # def tour_oldia_model(self, plateau, logs, policy):
    #
    #     """ L'IA génère une action d'après son modèle, on la fait jouer par la classe Tourencours """
    #     step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
    #     reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
    #     discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')
    #
    #     """ Initialisation du vecteur d'état représentant le plateau"""
    #     action_line = plateau.get_gamestate()
    #     for classe_Players in classes_heros:
    #         if action_line[f"is_{classe_Players}"] == -99:
    #             action_line[f"is_{classe_Players}"] = 0
    #
    #     """ Le modèle choisit l'action à effectuer parmi les actions légales """
    #
    #     input_state = np.array(itemgetter(*generate_column_state_old(classes_heros_old))(action_line))
    #
    #     legal_actions = generate_legal_vector(plateau)
    #
    #     observations = old_env.observation_spec()
    #     observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
    #                                                        name='observation')
    #     observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
    #                                                          name='valid_actions')
    #     timestep = ts.TimeStep(step_type, reward, discount, observations)
    #     result = policy.action(timestep)
    #     action = int(result.action)
    #
    #     if action == 0:
    #         action_line["action"] = "passer_tour"
    #         logs.append(action_line)
    #         TourEnCours(plateau).fin_du_tour()
    #     elif action < 11:
    #         action_line["action"] = "jouer_carte"
    #         played_card = plateau.players[0].hand[action - 1]
    #         action_line["carte_jouee"] = played_card.id  # name ou id ?
    #         logs.append(action_line)
    #         TourEnCours(plateau).jouer_carte(played_card)
    #     elif 11 <= action < 75:
    #         if (action - 11) // 8 == 0:
    #             attacker = plateau.players[0]
    #         else:
    #             attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
    #         if (action - 11) % 8 == 0:
    #             target = plateau.players[1]
    #         else:
    #             target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
    #         action_line["action"] = "attaquer"
    #         action_line["attaquant"] = attacker.id if type(attacker) is Card else "Players"
    #         action_line["attaquant_atq"] = attacker.attack
    #         action_line["attaquant_pv"] = attacker.health
    #         action_line["cible"] = target.id if type(target) is Card else "Players"
    #         action_line["cible_atq"] = target.attack
    #         action_line["cible_pv"] = target.health
    #         logs.append(action_line)
    #         TourEnCours(plateau).attaquer(attacker, target)
    #     else:
    #         if action == 75:
    #             target = plateau.players[0]
    #         elif action == 83:
    #             target = plateau.players[1]
    #         elif action < 83:
    #             target = plateau.players[0].servants[action - 76]
    #         else:
    #             target = plateau.players[1].servants[action - 84]
    #         action_line["action"] = "pouvoir_Playerique"
    #         action_line["cible"] = target.id if type(target) is Card else "Players"
    #         action_line["cible_atq"] = target.attack
    #         action_line["cible_pv"] = target.health
    #         logs.append(action_line)
    #         TourEnCours(plateau).pouvoir_Playerique(plateau.players[0].classe, target)
    #
    #     plateau.update()
    #     return plateau

    # def tour_oldia_training(self, plateau, policy):
    #     """ L'IA génère une action d'après son modèle, on la fait jouer par la classe Tourencours """
    #     step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
    #     reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
    #     discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')
    #
    #     """ Initialisation du vecteur d'état représentant le plateau"""
    #     action_line = plateau.get_gamestate()
    #     for classe_Players in classes_heros:
    #         if action_line[f"is_{classe_Players}"] == -99:
    #             action_line[f"is_{classe_Players}"] = 0
    #
    #     """ Le modèle choisit l'action à effectuer parmi les actions légales """
    #
    #     input_state = np.array(itemgetter(*generate_column_state_old(classes_heros_old))(action_line))
    #
    #     legal_actions = generate_legal_vector(plateau)
    #
    #     observations = old_env.observation_spec()
    #     observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
    #                                                        name='observation')
    #     observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
    #                                                          name='valid_actions')
    #     timestep = ts.TimeStep(step_type, reward, discount, observations)
    #     result = policy.action(timestep)
    #     action = int(result.action)
    #
    #     if action == 0:
    #         TourEnCours(plateau).fin_du_tour()
    #     elif action < 11:
    #         played_card = plateau.players[0].hand[action - 1]
    #         TourEnCours(plateau).jouer_carte(played_card)
    #     elif 11 <= action < 75:
    #         if (action - 11) // 8 == 0:
    #             attacker = plateau.players[0]
    #         else:
    #             attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
    #         if (action - 11) % 8 == 0:
    #             target = plateau.players[1]
    #         else:
    #             target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
    #         TourEnCours(plateau).attaquer(attacker, target)
    #     else:
    #         if action == 75:
    #             target = plateau.players[0]
    #         elif action == 83:
    #             target = plateau.players[1]
    #         elif action < 83:
    #             target = plateau.players[0].servants[action - 76]
    #         else:
    #             target = plateau.players[1].servants[action - 84]
    #         TourEnCours(plateau).pouvoir_Playerique(plateau.players[0].classe, target)
    #
    #     plateau.update()
    #     return plateau

    # def tour_ia_model(self, plateau, logs, policy, generate_logs=True):
    #     """ L'IA génère une action d'après son modèle, on la fait jouer par la classe Tourencours """
    #     step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
    #     reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
    #     discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')
    #
    #     """ Initialisation du vecteur d'état représentant le plateau"""
    #     action_line = plateau.get_gamestate()
    #     for classe_Players in classes_heros:
    #         if action_line[f"is_{classe_Players}"] == -99:
    #             action_line[f"is_{classe_Players}"] = 0
    #
    #     """ Le modèle choisit l'action à effectuer parmi les actions légales """
    #
    #     input_state = np.array(itemgetter(*generate_column_state(classes_heros))(action_line))
    #     legal_actions = generate_legal_vector(plateau)
    #
    #     observations = new_env.observation_spec()
    #     observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
    #                                                        name='observation')
    #     observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
    #                                                          name='valid_actions')
    #     timestep = ts.TimeStep(step_type, reward, discount, observations)
    #     result = policy.action(timestep)
    #     action = int(result.action)
    #
    #     if action == 0:
    #         if generate_logs:
    #             action_line["action"] = "passer_tour"
    #             logs.append(action_line)
    #         TourEnCours(plateau).fin_du_tour()
    #     elif action < 11:
    #         played_card = plateau.players[0].hand[action - 1]
    #         if generate_logs:
    #             action_line["action"] = "jouer_carte"
    #             action_line["carte_jouee"] = played_card.id  # name ou id ?
    #             logs.append(action_line)
    #         TourEnCours(plateau).jouer_carte(played_card)
    #     elif 11 <= action < 75:
    #         if (action - 11) // 8 == 0:
    #             attacker = plateau.players[0]
    #         else:
    #             attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
    #         if (action - 11) % 8 == 0:
    #             target = plateau.players[1]
    #         else:
    #             target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
    #         if generate_logs:
    #             action_line["action"] = "attaquer"
    #             action_line["attaquant"] = attacker.id if type(attacker) is Card else "Players"
    #             action_line["attaquant_atq"] = attacker.attack
    #             action_line["attaquant_pv"] = attacker.health
    #             action_line["cible"] = target.id if type(target) is Card else "Players"
    #             action_line["cible_atq"] = target.attack
    #             action_line["cible_pv"] = target.health
    #             logs.append(action_line)
    #         TourEnCours(plateau).attaquer(attacker, target)
    #     else:
    #         if action == 75:
    #             target = plateau.players[0]
    #         elif action == 83:
    #             target = plateau.players[1]
    #         elif action < 83:
    #             target = plateau.players[0].servants[action - 76]
    #         else:
    #             target = plateau.players[1].servants[action - 84]
    #         if generate_logs:
    #             action_line["action"] = "pouvoir_Playerique"
    #             action_line["cible"] = target.id if type(target) is Card else "Players"
    #             action_line["cible_atq"] = target.attack
    #             action_line["cible_pv"] = target.health
    #             logs.append(action_line)
    #         TourEnCours(plateau).pouvoir_heroique(plateau.players[0].classe, target)
    #
    #     plateau.update()
    #     return plateau
    #
    # def tour_ia_training(self, plateau, action):
    #     """ Initialisation du vecteur d'état représentant le plateau"""
    #     action_line = plateau.get_gamestate()
    #
    #     if action == 0:
    #         TourEnCours(plateau).fin_du_tour()
    #     elif action < 161:
    #         played_card = plateau.players[0].hand[int((action - 1) // 16)]
    #         if (action - 1) % 16 == 0:
    #             target = None
    #             if "cri de guerre" in played_card.effects and "choisi" not in played_card.effects["cri de guerre"]:
    #                 if played_card.effects["cri de guerre"][1][0] == "main":
    #                     if played_card.effects["cri de guerre"][1][1] == "allié":
    #                         if played_card.effects["cri de guerre"][1][2] == "tous":
    #                             target = CardGroup(
    #                                 (x for x in plateau.players[0].hand if x.type.lower() == "serviteur"))
    #                             target.remove(played_card)
    #         elif (action - 1) % 16 == 1:
    #             target = plateau.players[0]
    #         elif (action - 1) % 16 == 8:
    #             target = plateau.players[1]
    #         elif (action - 1) % 16 < 8:
    #             target = plateau.players[0].servants[int((action - 1) % 16) - 2]
    #         else:
    #             target = plateau.players[1].servants[int((action - 1) % 16) - 9]
    #         TourEnCours(plateau).jouer_carte(played_card, target)
    #     elif 161 <= action < 225:
    #         if (action - 161) // 8 == 0:
    #             attacker = plateau.players[0]
    #         else:
    #             attacker = plateau.players[0].servants[int((action - 161) // 8 - 1)]
    #         if (action - 161) % 8 == 0:
    #             target = plateau.players[1]
    #         else:
    #             target = plateau.players[1].servants[int((action - 161) % 8 - 1)]
    #         TourEnCours(plateau).attaquer(attacker, target)
    #     else:
    #         if action == 225:
    #             target = plateau.players[0]
    #         elif action == 233:
    #             target = plateau.players[1]
    #         elif action < 233:
    #             target = plateau.players[0].servants[int(action - 226)]
    #         else:
    #             target = plateau.players[1].servants[int(action - 234)]
    #         TourEnCours(plateau).pouvoir_Playerique(plateau.players[0].classe, target)
    #
    #     dead_servants = plateau.update()
    #     for servant in dead_servants:
    #         TourEnCours(plateau).apply_effects(servant)
    #     return plateau

    def tour_ia_minmax(self, plateau, logs, action, generate_logs=True):
        player = plateau.players[0]
        adv = plateau.players[1]

        """ Jouee quand piochee """
        if player.hand.cards and "played_drawn" in player.hand.cards[-1].effects:
            while "played_drawn" in player.hand.cards[-1].effects:
                player.hand.cards[-1].cost = 0
                possible_targets = generate_targets(plateau)[17 * (len(player.hand) - 1): 17 * len(player.hand) - 1]
                possible_targets_refined = [n for n in range(len(possible_targets)) if possible_targets[n]]
                if possible_targets_refined:
                    target = random.choice(possible_targets_refined)
                    if target == 0:
                        target = None
                    elif target == 1:
                        target = player
                    elif target < 9:
                        target = player.servants[target - 2]
                    elif target == 9:
                        target = adv
                    else:
                        target = adv.servants[target - 10]
                else:
                    target = None
                try:
                    TourEnCours(plateau).jouer_carte(player.hand.cards[-1], target)
                except:
                    print(player.hand.cards[-1], target)
                    raise TypeError
                player.pick()
        """ Transformation des serviteurs concernés """
        if [x for x in player.hand if "transformation" in x.effects]:
            for serv in [x for x in player.hand if "transformation" in x.effects]:
                potential_transform = [get_card(x, all_cards) for x in serv.effects["transformation"]]
                for card in potential_transform:
                    card.cost = serv.cost
                player.hand.cards = [random.choice(potential_transform) if x == serv else x for x in player.hand]
        """ Le Geolier """
        if player.geolier:
            for servant in player.servants:
                servant.effects["bouclier divin"] = 2
                servant.effects["camouflage"] = 1
        if adv.geolier:
            for servant in adv.servants:
                servant.effects["bouclier divin"] = 2
                servant.effects["camouflage"] = 1
        """ Malédictions """
        if player.curses:
            if "Meltranix" in player.curses and len(player.hand) > 2:
                for card in player.hand.cards:
                    if card in player.hand.cards[1:-2]:
                        card.effects["entrave"] = 1
                    else:
                        if "entrave" in card.effects:
                            card.effects.pop("entrave")
            if "holotech" in player.curses and player.servants.cards:
                for creature in player.servants:
                    creature.effects["holotech"] = 1
                player.curses.pop("holotech")
            if "amitus" in player.curses and player.servants.cards:
                for creature in player.servants:
                    creature.effects["solide"] = 1
                player.curses.pop("amitus")
        if adv.curses:
            if "enchanteur" in adv.curses and adv.servants.cards:
                for creature in adv.servants:
                    creature.effects["enchanteur"] = 1
                adv.curses.pop("enchanteur")
            if "holotech" in adv.curses and adv.servants.cards:
                for creature in adv.servants:
                    creature.effects["holotech"] = 1
                adv.curses.pop("holotech")
            if "amitus" in adv.curses and adv.servants.cards:
                for creature in adv.servants:
                    creature.effects["solide"] = 1
                adv.curses.pop("amitus")
        if adv.weapon is not None and "aura" in adv.weapon.effects:
            if "modif_damage" in adv.weapon.effects["aura"]:
                if "heros" in adv.weapon.effects["aura"][1] and "ennemi" in adv.weapon.effects["aura"][1]:
                    adv.permanent_buff["micro_casse"] = 1
        """ Initialisation du vecteur d'état représentant le plateau"""
        if generate_logs:
            action_line = plateau.get_gamestate()
        if action == 0:
            if generate_logs:
                action_line["action"] = "passer_tour"
                logs.append(action_line)
            TourEnCours(plateau).fin_du_tour()
        elif action < 171:
            played_card = player.hand[(action - 1) // 17]
            if generate_logs:
                action_line["action"] = "jouer_carte"
                action_line["carte_jouee"] = played_card.id  # name ou id ?
                logs.append(action_line)
            if (action - 1) % 17 == 0:
                target = None
                if "cri de guerre" in played_card.effects and "choisi" not in played_card.effects["cri de guerre"]:
                    if "main" in played_card.effects["cri de guerre"][1]:
                        if "allié" in played_card.effects["cri de guerre"][1]:
                            if "tous" in played_card.effects["cri de guerre"][1]:
                                target = CardGroup((x for x in player.hand if x.type == "Serviteur"))
                                target.remove(played_card)
                                if "spend_cadavre" in played_card.effects["cri de guerre"][1]:
                                    if player.cadavres >= played_card.effects["cri de guerre"][1][-1]:
                                        player.cadavres -= played_card.effects["cri de guerre"][1][-1]
                                        player.cadavres_spent += played_card.effects["cri de guerre"][1][-1]
                                    else:
                                        target = None
                            elif "1" in played_card.effects["cri de guerre"][1]:
                                if "Méca" in played_card.effects["cri de guerre"][1]:
                                    target = CardGroup(
                                        (x for x in player.hand if x.type == "Serviteur" and "Méca" in x.genre))
                                    target.remove(played_card)
                                    target = random.choice(target) if len(target) > 0 else None
                            elif "chaque type" in played_card.effects["cri de guerre"][1]:
                                potential_boost = [x for x in player.hand if x.genre and x != played_card].copy()
                                target = CardGroup()
                                for genre in all_genre_servants:
                                    if [x for x in potential_boost if genre in x.genre]:
                                        boosted_servant = [x for x in potential_boost if genre in x.genre]
                                        boosted_servant = boosted_servant[
                                            np.array([len(x.genre) for x in boosted_servant]).argsort()[0]]
                                        target.add(boosted_servant)
                                        potential_boost.remove(boosted_servant)
                            elif "aléatoire" in played_card.effects["cri de guerre"][1]:
                                try:
                                    target = random.choice([x for x in player.hand if x.type == "Serviteur" and x != played_card])
                                except:
                                    pass
                    elif "deck" in played_card.effects["cri de guerre"][1]:
                        if "allié" in played_card.effects["cri de guerre"][1]:
                            if "serviteur" in played_card.effects["cri de guerre"][1] and "tous" in \
                                    played_card.effects["cri de guerre"][1]:
                                if "if_crideguerre" in played_card.effects["cri de guerre"][1]:
                                    target = CardGroup((x for x in player.deck if x.type == "Serviteur" and "cri de guerre" in x.effects))
                                else:
                                    target = CardGroup((x for x in player.deck if x.type == "Serviteur"))
            elif (action - 1) % 17 == 1:
                target = player
            elif (action - 1) % 17 == 9:
                target = adv
            elif (action - 1) % 17 < 9:
                target = player.servants[(action - 1) % 17 - 2]
                if "cri de guerre" in played_card.effects and "voisin" in played_card.effects["cri de guerre"][1] and len(player.servants) > 1:
                    try:
                        target = CardGroup([target] + [player.servants[(action) % 17 - 2]])
                    except:
                        try:
                            target = CardGroup([target] + [player.servants[(action - 2) % 17 - 2]])
                        except:
                            pass
                elif "final" in played_card.effects and "voisin" in played_card.effects["final"][1] and len(player.servants) > 1:
                    try:
                        target = CardGroup([target] + [player.servants[(action) % 17 - 2]])
                    except:
                        target = CardGroup([target] + [player.servants[(action - 2) % 17 - 2]])
            else:
                target = adv.servants[(action - 1) % 17 - 10]
                if "cri de guerre" in played_card.effects and "voisin" in played_card.effects["cri de guerre"][1] and len(adv.servants) > 1:
                    try:
                        if (action - 1) % 17 - 10 != 0:
                            target = CardGroup([target, adv.servants[action % 17 - 10], adv.servants[(action - 2) % 17 - 10]])
                    except:
                        try:
                            target = CardGroup([target] + [adv.servants[(action) % 17 - 9]])
                        except:
                            try:
                                target = CardGroup([target] + [adv.servants[(action - 2) % 17 - 9]])
                            except:
                                pass
            inter_cost = played_card.cost
            if "marginal" in played_card.effects:
                player.marginal_played += 1
            TourEnCours(plateau).jouer_carte(played_card, target)
            if len(played_card.genre) > 0 and played_card.genre[0] in all_genre_servants and len(player.genre_joues) < 10:
                to_beat_score = len(player.genre_joues)
                test_genres = player.genre_joues.copy()
                test_genres.append(played_card.genre)
                actual_score = 0
                if to_beat_score == 0:
                    player.genre_joues.append(played_card.genre)
                else:
                    for genre in all_genre_servants:
                        concerned_genre = [x for x in test_genres if genre in x]
                        if concerned_genre:
                            concerned_genre = concerned_genre[np.array([len(x) for x in concerned_genre]).argsort()[0]]
                            test_genres.remove(concerned_genre)
                            actual_score += 1
                    if actual_score > to_beat_score:
                        player.genre_joues.append(played_card.genre)
            player.last_card = played_card
            if inter_cost != played_card.base_cost:
                for discount in played_card.discount:
                    if discount in player.discount_next:
                        for card in player.hand:
                            if discount in card.discount:
                                card.discount.remove(discount)
                        player.discount_next.remove(discount)
                        try:
                            played_card.discount.remove(discount)
                        except:
                            pass
        elif 171 <= action < 235:
            if (action - 171) // 8 == 0:
                attacker = player
            else:
                try:
                    attacker = player.servants[int((action - 171) // 8 - 1)]
                except:
                    print(action, player.servants, player.last_card, player.last_card.effects)
                    raise TypeError
            if (action - 171) % 8 == 0:
                target = adv
            else:
                try:
                    target = adv.servants[int((action - 171) % 8 - 1)]
                except:
                    print(attacker, action, player.servants, adv.servants)
                    raise TypeError
            if generate_logs:
                action_line["action"] = "attaquer"
                action_line["attaquant"] = attacker.id if type(attacker) is Card else "Players"
                action_line["attaquant_atq"] = attacker.attack
                action_line["attaquant_pv"] = attacker.health
                action_line["cible"] = target.id if type(target) is Card else "Players"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).attaquer(attacker, target)
            while "aura" in attacker.effects and "boost+attack" in attacker.effects["aura"] and not attacker.is_dead():
                attacker.boost(attacker.effects["aura"][2][0], 0)
                if [x for x in adv.servants if not x.is_dead()]:
                    target = random.choice([x for x in adv.servants if not x.is_dead()])
                else:
                    break
                TourEnCours(plateau).attaquer(attacker, target)
        elif action < 251:
            if action == 235:
                target = player
            elif action == 243:
                target = adv
            elif action < 243:
                target = player.servants[action - 236]
            else:
                target = adv.servants[action - 244]
            if generate_logs:
                action_line["action"] = "pouvoir_heroique"
                action_line["cible"] = target.id if type(target) is Card else "Players"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).pouvoir_heroique(player.classe, target)
        elif action < 255:
            if generate_logs:
                action_line["action"] = "decouverte" if plateau.cards_chosen else "dragage" if plateau.cards_dragage\
                    else "entrave" if plateau.cards_entrave else "hand_to_deck" if plateau.cards_hands_to_deck else "choix_des_armes"
                logs.append(action_line)
            if plateau.cards_chosen:
                TourEnCours(plateau).decouverte(plateau.cards_chosen[0], action - 251)
                if player.copies_to_deck:
                    for _ in range(player.copies_to_deck):
                        card_to_add = get_card(player.hand.cards[-1].name, all_cards)
                        card_to_add.effects["played_drawn"] = 1
                        player.deck.add(card_to_add)
                    player.deck.shuffle()
            elif plateau.cards_dragage:
                TourEnCours(plateau).decouverte(plateau.cards_dragage[0], action - 251, type_dec="dragage")
                if "damage" in player.last_card.effects and type(player.last_card.effects["damage"]) == list and "cost_dragage" in player.last_card.effects["damage"]:
                    for serv in player.servants.cards + adv.servants.cards:
                        serv.damage(player.deck.cards[0].cost)
            elif plateau.cards_entrave:
                TourEnCours(plateau).decouverte(plateau.cards_entrave[0], action - 251, type_dec="entrave")
            elif plateau.cards_hands_to_deck:
                TourEnCours(plateau).decouverte(plateau.cards_hands_to_deck[0], action - 251, type_dec="hand_to_deck")
            elif plateau.choix_des_armes:
                TourEnCours(plateau).decouverte(plateau.choix_des_armes, action - 251, type_dec="choix_des_armes")
        elif action < 265:
            if generate_logs:
                if "echangeable" in player.hand[action - 255].effects:
                    action_line["action"] = "echange"
                elif "forge" in player.hand[action - 255].effects:
                    action_line["action"] = "forge"
                logs.append(action_line)
            if "echangeable" in player.hand[action - 255].effects:
                TourEnCours(plateau).echange(player.hand[action - 255])
            elif "forge" in player.hand[action - 255].effects:
                TourEnCours(plateau).forge(player.hand[action - 255])
        elif action < 377:
            if generate_logs:
                action_line["action"] = "lieu_utilise"
                logs.append(action_line)
            if (action - 265) % 16 == 0:
                target = player
            elif (action - 265) % 16 < 8:
                target = player.servants[(action - 266) % 16]
            elif (action - 265) % 16 == 8:
                target = adv
            else:
                target = adv.servants[(action - 274) % 16]
            TourEnCours(plateau).util_lieu(player.lieux[(action - 265) // 16], target)
        else:
            if generate_logs:
                action_line["action"] = "titan"
                logs.append(action_line)
            titans = [x for x in player.servants if "titan" in x.effects and x.effects["titan"][-1] == 1]
            titans[(action - 377) // 3].effects["titan"][-1] = 0
            TourEnCours(plateau).apply_effects(titans[(action - 377) // 3], titans[(action - 377) // 3].effects["titan"][(action - 377) % 3])
            titans[(action - 377) // 3].effects["titan"].pop((action - 377) % 3)

        """ Application des effets d'aura """
        aura_servants = [x for x in player.servants.cards + adv.servants.cards if
                         "aura" in x.effects and not x.is_dead() and "alive" in x.effects["aura"][1]]
        for creature in player.servants.cards + adv.servants.cards:
            if not ("aura" in creature.effects and "boost" in creature.effects["aura"] and "self" in creature.effects["aura"][1]):
                creature.total_temp_boost = [0, 0]
            if "enchanteur" in creature.effects and not "enchanteur" in adv.curses and not "enchanteur" in player.permanent_buff:
                creature.effects.pop("enchanteur")
            if "holotech" in creature.effects and not "holotech" in adv.curses:
                creature.effects.pop("holotech")
            if "solide" in creature.effects and not "amitus" in adv.curses:
                creature.effects.pop("solide")
        if aura_servants:
            TourEnCours(plateau).apply_effects(get_card(-1, all_cards))
        for creature in player.servants.cards + adv.servants.cards:
            try:
                creature.attack = max(0, creature.base_attack + creature.total_temp_boost[0])
            except:
                print(creature, creature.effects, creature.base_attack)
            creature.health = max(0, creature.base_health + creature.total_temp_boost[1] - creature.blessure)
            creature.surplus = 0
        if [x for x in player.servants.cards + adv.servants.cards if "infection" in x.effects and "conditional" in x.effects["infection"]]:
            for infected_creature in [x for x in player.servants.cards + adv.servants.cards if "infection" in x.effects and "conditional" in x.effects["infection"]]:
                if "if_other_destroyed" in infected_creature.effects["infection"] and "destroyed" in infected_creature.effects["infection"]:
                    if infected_creature in player.servants and [x for x in player.servants if x.is_dead() and x!= infected_creature]:
                        infected_creature.blessure = 1000
                        infected_creature.health = max(0, infected_creature.base_health - infected_creature.blessure)
                    elif infected_creature in adv.servants and [x for x in adv.servants if x.is_dead() and x!= infected_creature]:
                        infected_creature.blessure = 1000
                        infected_creature.health = max(0, infected_creature.base_health - infected_creature.blessure)
        player.has_attacked = 0.5 if player.has_attacked == 1 else 0

        """ Application des rales d'agonie """
        dead_servants, dead_servants_player = plateau.update()
        while dead_servants:
            for servant in dead_servants:
                TourEnCours(plateau).apply_effects(servant)
                if servant in adv.servants:
                    adv.servants.remove(servant)
                    if adv.secrets and "if_serv_dies" in [x.effects["trigger"] for x in adv.secrets]:
                        for secret in adv.secrets:
                            if secret.effects["trigger"] == "if_serv_dies":
                                target = None
                                if "invocation" in secret.effects["secret"]:
                                    secret.effects["secret"][1][0] = servant.name
                                if "return_hand" in secret.effects["secret"]:
                                    target = servant
                                secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                                secret.effects.pop("secret")
                                TourEnCours(plateau).apply_effects(secret, target)
                                adv.secrets.remove(secret)
                                adv.secrets_declenches += 1
                                if "halkias" in secret.effects:
                                    TourEnCours(plateau).invoke_servant(get_card("Halkias", all_servants), adv)
                elif servant in player.servants:
                    player.servants.remove(servant)
            if [x for x in dead_servants if "reinvoke" in x.effects]:
                for servant in [x for x in dead_servants if "reinvoke" in x.effects]:
                    player.servants.add(get_card(servant.name, all_servants))
            dead_servants, dead_servants_player = plateau.update()

        if player.weapon is not None:
            player.weapon.attack = max(0, player.weapon.base_attack + player.weapon.total_temp_boost[0])
            player.weapon.total_temp_boost = [0, 0]
        if player.dead_weapon and "rale d'agonie" in player.dead_weapon.effects:
            TourEnCours(plateau).apply_effects(player.dead_weapon)
        if "croise sanglant" in player.permanent_buff:
            for serv in [x for x in player.hand if x.type == "Serviteur" and x.classe == "Paladin"]:
                serv.effects["cost_pv"] = [1, 1]
        if "micro_casse" in adv.permanent_buff:
            adv.permanent_buff.pop("micro_casse")

        """ Application de secrets """
        if adv.secrets and "if_nomana_adv" in [x.effects["trigger"] for x in adv.secrets] and player.mana == 0:
            for secret in adv.secrets:
                if secret.effects["trigger"] == "if_nomana_adv":
                    if "ciblage" in secret.effects["secret"]:
                        target = player
                        secret.effects["secret"].remove("ciblage")
                    else:
                        target = None
                    secret.effects[secret.effects["secret"][0]] = secret.effects["secret"][1]
                    secret.effects.pop("secret")
                    TourEnCours(plateau).apply_effects(secret, target)
                    adv.secrets.remove(secret)
                    adv.secrets_declenches += 1
                    if "halkias" in secret.effects:
                        TourEnCours(plateau).invoke_servant(get_card("Halkias", all_servants), adv)

        player.end_action()
        adv.end_action()
        player.apply_discount()
        player.apply_weapon()
        if action == 0:
            plateau.tour_suivant()
            TourEnCours(plateau).debut_du_tour()


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

    # def generate_randomvsia_game(self, nb_games, players=()):
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
    #     for i in range(0, round(nb_games / 2)):
    #         logs_inter = []
    #         with open('plateau_init1.pickle', 'rb') as f:
    #             mon_plateau = pickle.load(f)
    #         while mon_plateau.game_on:
    #             if mon_plateau.game_turn % 2 == 0:
    #                 mon_plateau = Orchestrator().tour_au_hasard(mon_plateau, logs_inter)
    #             else:
    #                 mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, saved_policy)
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
    #     for i in range(round(nb_games / 2), nb_games):
    #         logs_inter = []
    #         with open('plateau_init2.pickle', 'rb') as f:
    #             mon_plateau2 = pickle.load(f)
    #         while mon_plateau2.game_on:
    #             if mon_plateau2.game_turn % 2 == 0:
    #                 mon_plateau2 = Orchestrator().tour_ia_model(mon_plateau2, logs_inter, saved_policy)
    #             else:
    #                 mon_plateau2 = Orchestrator().tour_au_hasard(mon_plateau2, logs_inter)
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
    #     logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis=1)
    #     os.remove('plateau_init1.pickle')
    #     os.remove('plateau_init2.pickle')
    #     return logs_hs, scores
    #
    # def generate_oldia_game(self, nb_games, new_policy=saved_policy, players=(), generate_logs=True):
    #     global logs_inter, logs_hs
    #     if generate_logs:
    #         logs_hs = []
    #     scores = {}
    #
    #     """ On simule nb_games parties """
    #     """ La moitié où le joueur 1 commence """
    #     for i in range(0, round(nb_games / 2)):
    #         if generate_logs:
    #             logs_inter = []
    #             players1 = deepcopy(players)
    #             mon_plateau = Plateau(players1)
    #             while mon_plateau.game_on:
    #                 if mon_plateau.game_turn % 2 == 0:
    #                     mon_plateau = Orchestrator().tour_oldia_model(mon_plateau, logs_inter, old_policy)
    #                 else:
    #                     mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, new_policy)
    #         else:
    #             players1 = deepcopy(players)
    #             mon_plateau = Plateau(players1)
    #             while mon_plateau.game_on:
    #                 if mon_plateau.game_turn % 2 == 0:
    #                     mon_plateau = Orchestrator().tour_oldia_training(mon_plateau, old_policy)
    #                 else:
    #                     mon_plateau = Orchestrator().tour_ia_model(mon_plateau, [], new_policy, False)
    #
    #         """Actions de fin de partie"""
    #         winner = mon_plateau.winner
    #         if generate_logs:
    #             logs_inter = pd.DataFrame(logs_inter)
    #             logs_hs.append(logs_inter)
    #         if winner.name in scores.keys():
    #             scores[winner.name] += 1
    #         else:
    #             scores[winner.name] = 1
    #         i += 1
    #         if i % 100 == 0:
    #             print(i)
    #
    #     for i in range(round(nb_games / 2), nb_games):
    #         if generate_logs:
    #             logs_inter = []
    #             players2 = deepcopy([players[1], players[0]])
    #             mon_plateau = Plateau(players2)
    #             while mon_plateau.game_on:
    #                 if mon_plateau.game_turn % 2 == 0:
    #                     mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, new_policy)
    #                 else:
    #                     mon_plateau = Orchestrator().tour_oldia_model(mon_plateau, logs_inter, old_policy)
    #         else:
    #             players2 = deepcopy([players[1], players[0]])
    #             mon_plateau = Plateau(players2)
    #             while mon_plateau.game_on:
    #                 if mon_plateau.game_turn % 2 == 0:
    #                     mon_plateau = Orchestrator().tour_ia_model(mon_plateau, [], new_policy, False)
    #                 else:
    #                     mon_plateau = Orchestrator().tour_oldia_training(mon_plateau, old_policy)
    #
    #         """Actions de fin de partie"""
    #         winner = mon_plateau.winner
    #         if generate_logs:
    #             logs_inter = pd.DataFrame(logs_inter)
    #             logs_hs.append(logs_inter)
    #         if winner.name in scores.keys():
    #             scores[winner.name] += 1
    #         else:
    #             scores[winner.name] = 1
    #         i += 1
    #         if i % 100 == 0:
    #             print(i)
    #
    #     """ Concaténation des logs + suppression des plateaux temporaires """
    #     if generate_logs:
    #         logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis=1)
    #         return logs_hs, scores
    #     else:
    #         return scores

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
