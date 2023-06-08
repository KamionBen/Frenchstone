import pandas as pd
import numpy as np
from Entities import *
import random
import os
from operator import itemgetter
from copy import deepcopy
from tf_agents.trajectories import time_step as ts
import tensorflow as tf
from tf_agents.specs import array_spec
from tf_agents.environments import py_environment, tf_py_environment


def generate_column_state_old(classes_hero):
    columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                            "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]

    """ HERO """
    for classe_heros in classes_hero:
        columns_actual_state.append(f"is_{classe_heros}")

    """ HAND """
    for i in range(10):
        columns_actual_state.append(f"carte_en_main{i + 1}_cost")
        columns_actual_state.append(f"carte_en_main{i + 1}_atk")
        columns_actual_state.append(f"carte_en_main{i + 1}_pv")

    """ SERVANTS """
    for i in range(7):
        columns_actual_state.append(f"atq_serv{i + 1}_j")
        columns_actual_state.append(f"pv_serv{i + 1}_j")
        columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

    for i in range(7):
        columns_actual_state.append(f"atq_serv{i + 1}_adv")
        columns_actual_state.append(f"pv_serv{i + 1}_adv")

    return columns_actual_state


def generate_column_state(classes_hero):
    columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                            "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]

    """ HERO """
    for classe_heros in classes_hero:
        columns_actual_state.append(f"is_{classe_heros}")

    """ HAND """
    for i in range(10):
        for j in range(len(all_cards)):
            columns_actual_state.append(f"is_carte{i + 1}_{all_cards[j]['name']}")

    """ SERVANTS """
    for i in range(7):
        columns_actual_state.append(f"atq_serv{i + 1}_j")
        columns_actual_state.append(f"pv_serv{i + 1}_j")
        columns_actual_state.append(f"atq_remain_serv{i + 1}_j")
        for j in range(len(all_servants)):
            columns_actual_state.append(f"is_servant{i + 1}_{all_servants[j]['name']}_j")
            columns_actual_state.append(f"is_servant{i + 1}_{all_servants[j]['name']}_adv")

    for i in range(7):
        columns_actual_state.append(f"atq_serv{i + 1}_adv")
        columns_actual_state.append(f"pv_serv{i + 1}_adv")

    return columns_actual_state


def generate_legal_vector_old(state):
    """ Gestion des actions légales """
    legal_actions = [True]
    gamestate = state.get_gamestate()
    for i in range(90):
        legal_actions.append(False)

    """ Quelles cartes peut-on jouer ? """
    for i in range(int(gamestate["nbre_cartes_j"])):
        for j in range(len(all_cards)):
            if gamestate[f"is_carte{i + 1}_{all_cards[j]['name']}"] != -99 \
            and get_card(all_cards[j]['name'], all_cards).cost <= gamestate["mana_dispo_j"] \
            and gamestate[f"pv_serv7_j"] == -99:
                legal_actions[i + 1] = True


    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    """ Notre héros peut attaquer """
    if gamestate["remaining_atk_j"] > 0 and gamestate["attaque_j"] > 0:
        legal_actions[11] = True
        for j in range(1, 8):
            if gamestate[f"atq_serv{j}_adv"] != -99:
                legal_actions[11 + j] = True

    """ Nos serviteurs peuvent attaquer """
    is_provoc = False
    for j in range(1, 8):
        if gamestate[f"atq_serv{j}_adv"] != -99 and "provocation" in state.players[1].servants[j - 1].effects:
            is_provoc = True
            break
    for i in range(1, 8):
        if gamestate[f"atq_remain_serv{i}_j"] > 0:
            if not is_provoc:
                legal_actions[11 + 8 * i] = True
            if "ruée" in state.players[0].servants[i-1].effects:
                if state.players[0].servants[i-1].effects["ruée"] == 1:
                    legal_actions[11 + 8 * i] = False
            for j in range(1, 8):
                if not is_provoc:
                    if gamestate[f"atq_serv{j}_adv"] != -99:
                        legal_actions[11 + 8 * i + j] = True
                else:
                    if "provocation" in state.players[1].servants[j - 1].effects:
                        legal_actions[11 + 8 * i + j] = True

    if gamestate["dispo_ph_j"] and gamestate["cout_ph_j"] <= gamestate["mana_dispo_j"]:
        targets = state.targets_hp()
        if state.players[0].hero in targets:
            legal_actions[75] = True
        if state.players[1].hero in targets:
            legal_actions[83] = True
        for i in range(1, 8):
            if gamestate[f"atq_serv{i}_j"] != -99:
                if gamestate[f"serv{i}_j"] in targets:
                    legal_actions[75 + i] = True
            if gamestate[f"atq_serv{i}_adv"] != -99:
                if gamestate[f"serv{i}_adv"] in targets:
                    legal_actions[83 + i] = True

    return legal_actions


def generate_legal_vector(state):
    """ Gestion des actions légales """
    legal_actions = [False] * 241
    legal_actions[0] = True
    gamestate = state.get_gamestate()

    """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
    for i in range(len(state.players[0].hand)):
        if state.players[0].hand[i].cost <= state.players[0].mana:
            if len(state.players[0].servants) != 7 and state.players[0].hand[i].type.lower() == "serviteur":

                """ Serviteurs avec cris de guerre ciblés """
                if "cri de guerre" in state.players[0].hand[i].effects and "choisi" in state.players[0].hand[i].effects["cri de guerre"][1]:
                    if state.players[0].hand[i].effects["cri de guerre"][1][0] == "serviteur":
                        if state.players[0].hand[i].effects["cri de guerre"][1][1] == "allié" and gamestate[f"serv1_j"] != -99:
                            for j in range(len(state.players[0].servants)):
                                legal_actions[16 * i + j + 3] = True
                        elif state.players[0].hand[i].effects["cri de guerre"][1][1] == "tous" and (gamestate[f"serv1_j"] != -99 or gamestate[f"serv1_adv"] != -99):
                            for j in range(len(state.players[0].servants)):
                                legal_actions[16 * i + j + 3] = True
                            for j in range(len(state.players[1].servants)):
                                legal_actions[16 * i + j + 10] = True
                        else:
                            legal_actions[16 * i + 1] = True
                    elif state.players[0].hand[i].effects["cri de guerre"][1][0] == "tous":
                        if state.players[0].hand[i].effects["cri de guerre"][1][1] == "tous":
                            legal_actions[16 * i + 2] = True
                            legal_actions[16 * i + 9] = True
                            for j in range(len(state.players[0].servants)):
                                legal_actions[16 * i + j + 3] = True
                            for j in range(len(state.players[1].servants)):
                                legal_actions[16 * i + j + 10] = True
                else:
                    legal_actions[16 * i + 1] = True
            elif state.players[0].hand[i].type.lower() == "sort":
                legal_actions[16 * i + 1] = True


    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    is_provoc = False
    for j in range(len(state.players[1].servants)):
        if "provocation" in state.players[1].servants[j].effects:
            is_provoc = True
            break
    """ Notre héros peut attaquer """
    if state.players[0].hero.remaining_atk > 0 and state.players[0].hero.attack > 0:
        if not is_provoc:
            legal_actions[161] = True
        for j in range(len(state.players[1].servants)):
            if not is_provoc:
                legal_actions[161 + j + 1] = True
            else:
                if "provocation" in state.players[1].servants[j].effects:
                    legal_actions[161 + j + 1] = True

    """ Nos serviteurs peuvent attaquer """

    for i in range(len(state.players[0].servants)):
        if gamestate[f"atq_remain_serv{i + 1}_j"] > 0:
            if not is_provoc:
                legal_actions[161 + 8 * (i + 1)] = True
            if "ruée" in state.players[0].servants[i].effects:
                if state.players[0].servants[i].effects["ruée"] == 1:
                    legal_actions[161 + 8 * (i + 1)] = False
            for j in range(len(state.players[1].servants)):
                if not is_provoc:
                    legal_actions[161 + 8 * (i + 1) + (j + 1)] = True
                else:
                    if "provocation" in state.players[1].servants[j].effects:
                        legal_actions[161 + 8 * (i + 1) + (j + 1)] = True

    if state.players[0].hero.dispo_pouvoir and state.players[0].hero.cout_pouvoir_temp <= state.players[0].mana:
        targets = state.targets_hp()
        if state.players[0].hero in targets:
            legal_actions[225] = True
        if state.players[1].hero in targets:
            legal_actions[233] = True
        if len(targets) >= 2:
            for i in range(len(state.players[0].servants)):
                if state.players[0].servants[i] in targets:
                    legal_actions[226 + i] = True
            for i in range(len(state.players[1].servants)):
                if state.players[1].servants[i] in targets:
                    legal_actions[234 + i] = True

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

    def calc_advantage(state):
        advantage = (state["nbre_cartes_j"] - state["nbre_cartes_adv"]) + 0.8 * (state["nbre_cartes_j"] / max(1, state["nbre_cartes_adv"]))
        for i in range(1, 8):
            if state[f"serv{i}_j"] != -99:
                advantage += 2 * state[f"atq_serv{i}_j"] + 2 * state[f"pv_serv{i}_j"]
            if state[f"serv{i}_adv"] != -99:
                advantage -= 2 * state[f"atq_serv{i}_adv"] + 2 * state[f"pv_serv{i}_adv"]
        advantage += 0.22 * (pow(30 - state["pv_adv"], 1.3) - pow(30 - state["pv_j"], 1.3))
        advantage += state["attaque_j"]
        return advantage

    actual_advantage = calc_advantage(actual_state.get_gamestate())
    predicted_advantage = calc_advantage(next_state.get_gamestate())


    # print(actual_state.get_gamestate())
    # print(f"Avantage en cours : {actual_advantage}")
    # print(action)
    # print(next_state.get_gamestate())
    # print(f"Avantage prévu : {predicted_advantage}")
    # print('-------------------------------------------')

    return round(predicted_advantage - actual_advantage, 2)

""" Initialisation de l'environnement et chagrement du modèle """

old_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')
saved_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')


class Frenchstone_old(py_environment.PyEnvironment):
    def __init__(self):
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

        obs['observation'] = np.array(itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate()))
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
        obs['observation'] = np.array(itemgetter(*generate_column_state_old(classes_heros_old))(self._state.get_gamestate()),
                                      dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        if reward in [-500, 500]:
            self._episode_ended = True
            return ts.termination(obs, reward)
        return ts.transition(obs, reward)


old_env = Frenchstone_old()
old_env = tf_py_environment.TFPyEnvironment(old_env)


class Frenchstone(py_environment.PyEnvironment):
    def __init__(self):
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
        if "charge" in carte.effects or "ruée" in carte.effects:
            carte.remaining_atk = 1
        if "add_mana" in carte.effects:
            player.mana += carte.effects["add_mana"]
        if "cri de guerre" in carte.effects and not carte.is_dead():
            if "boost" in carte.effects["cri de guerre"] and target is not None:
                if type(target) == Card:
                    target.attack += carte.effects["cri de guerre"][2][0]
                    target.base_attack += carte.effects["cri de guerre"][2][0]
                    target.health += carte.effects["cri de guerre"][2][1]
                    target.base_health += carte.effects["cri de guerre"][2][1]
                elif type(target) == CardGroup:
                    for card in target:
                        card.attack += carte.effects["cri de guerre"][2][0]
                        card.base_attack += carte.effects["cri de guerre"][2][0]
                        card.health += carte.effects["cri de guerre"][2][1]
                        card.base_health += carte.effects["cri de guerre"][2][1]
            if "add_durability" in carte.effects["cri de guerre"] and player.hero.weapon is not None:
                player.hero.weapon.durability += carte.effects["cri de guerre"]
            if "cout_hp" in carte.effects["cri de guerre"]:
                player.hero.cout_pouvoir_temp = 0
            if "damage" in carte.effects["cri de guerre"] and target is not None:
                target.damage(carte.effects["cri de guerre"][2])
            if "heal" in carte.effects["cri de guerre"] and target is not None:
                target.heal(carte.effects["cri de guerre"][2])
            if "ne peut pas attaquer" in carte.effects["cri de guerre"] and target is not None:
                target.effects["ne peut pas attaquer"] = 1
                target.remaining_atk = 0
                carte.effects["liberation"] = target.id
        if "liberation" in carte.effects and carte.is_dead():
            if carte.effects["liberation"] in [x.id for x in player.servants]:
                [x for x in player.servants if x.id == carte.effects["liberation"]][0].effects.pop("ne peut pas attaquer", None)
            elif carte.effects["liberation"] in [x.id for x in adv.servants]:
                [x for x in adv.servants if x.id == carte.effects["liberation"]][0].effects.pop("ne peut pas attaquer", None)
        if "rale d'agonie" in carte.effects and carte.is_dead():
            if carte.effects["rale d'agonie"][1][0] == "serviteur":
                if carte.effects["rale d'agonie"][1][1] == "allié":
                    if carte.effects["rale d'agonie"][1][3] == "Mort-vivant":
                        target = random.choice([x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre]) \
                            if len([x for x in self.plt.players[0].servants if "Mort-vivant" in x.genre]) != 0 else None
                elif carte.effects["rale d'agonie"][1][1] == "ennemi":
                    if carte.effects["rale d'agonie"][1][3] == "Mort-vivant":
                        target = random.choice([x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre]) \
                            if len([x for x in self.plt.players[1].servants if "Mort-vivant" in x.genre]) != 0 else None
            if "boost" in carte.effects["rale d'agonie"] and target is not None:
                target.attack += carte.effects["rale d'agonie"][2][0]
                target.base_attack += carte.effects["rale d'agonie"][2][0]
                target.health += carte.effects["rale d'agonie"][2][1]
                target.base_health += carte.effects["rale d'agonie"][2][1]
        aura_servants = [x for x in player.servants if "aura" in x.effects]
        for servant in aura_servants:
            if servant.effects["aura"][0] == "boost":
                if servant.effects["aura"][1][0] == "serviteur":
                    if servant.effects["aura"][1][1] == "allié":
                        if servant.effects["aura"][1][3] == "Mort-vivant" and "Mort-vivant" in carte.genre and servant != carte:
                            carte.attack += servant.effects["aura"][2][0]
                            carte.base_attack += servant.effects["aura"][2][0]
                            carte.health += servant.effects["aura"][2][1]
                            carte.base_health += servant.effects["aura"][2][1]

    def jouer_carte(self, carte, target=None):
        """ Action de poser une carte depuis la main du joueur dont c'est le tour.
        Le plateau est mis à jour en conséquence """
        player = self.plt.players[0]
        if carte.cost <= player.mana:
            if carte.type.lower() == "sort":
                player.hand.remove(carte)
                player.mana_spend(carte.cost)
                self.apply_effects(carte)
            elif carte.type.lower() == "serviteur":
                if len(player.servants) < 7:
                    player.hand.remove(carte)
                    player.servants.add(carte)
                    player.mana_spend(carte.cost)
                    self.apply_effects(carte, target)
                else:
                    raise PermissionError("Nombre maximum de serviteurs atteint")
        else:
            raise PermissionError("Carte plus chère que la mana du joueur")

    def attaquer(self, attaquant, cible, target=None):
        """ Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi) """
        if type(attaquant) in (Hero, Card) and type(cible) in (Hero, Card):
            cible.damage(attaquant.attack)
            attaquant.damage(cible.attack)
            attaquant.remaining_atk -= 1
            if type(attaquant) == Hero and attaquant.weapon is not None:
                attaquant.weapon.durability -= 1
                if attaquant.weapon.durability == 0:
                    attaquant.weapon = None
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

    def fin_du_tour(self):
        self.plt.tour_suivant()


class Orchestrator:
    # def tour_au_hasard(self, plateau, logs):
    #     """ On génère une action aléatoire et on la fait jouer par la classe Tourencours """
    #     player = plateau.players[0]
    #     adv = plateau.players[1]
    #     tour_en_cours = TourEnCours(plateau)
    #
    #     action_line = plateau.get_gamestate()
    #
    #     """ ON CHOISIT L'ACTION """
    #     action_possible = ["Passer_tour"]
    #     for carte in player.servants:
    #         if carte.attack > 0 and carte.remaining_atk > 0:
    #             if len(tour_en_cours.plt.get_targets(carte)) > 0:
    #                 action_possible.append(carte)
    #     for carte in player.hand:
    #         if carte.cost <= player.mana and not (carte.type.lower() == "serviteur" and len(player.servants) == 7):
    #             action_possible.append(carte)
    #     if player.hero.attack > 0 and player.hero.remaining_atk > 0:
    #         action_possible.append(player.hero)
    #     if player.hero.cout_pouvoir <= player.mana and player.hero.dispo_pouvoir:
    #         if not (player.classe in ["Paladin", "Chevalier de la mort"] and len(player.servants) == 7):
    #             action_possible.append("Pouvoir_heroique")
    #
    #     action = choice(action_possible) # Choix aléatoire de l'action à effectuer
    #
    #     if action == "Passer_tour":
    #         action_line["action"] = "passer_tour"
    #         logs.append(action_line)
    #         tour_en_cours.fin_du_tour()
    #
    #     elif action == "Pouvoir_heroique":
    #         target = random.choice(plateau.targets_hp())
    #         action_line["action"] = "pouvoir_heroique"
    #         action_line["cible"] = target.id if type(target) is Card else "heros"
    #         action_line["cible_atq"] = target.attack
    #         action_line["cible_pv"] = target.health
    #         logs.append(action_line)
    #
    #         tour_en_cours.pouvoir_heroique(player.classe, target)
    #
    #     elif (action in player.hand) and (action.cost <= player.mana):
    #         """ La carte est jouée depuis la main """
    #         action_line["action"] = "jouer_carte"
    #         action_line["carte_jouee"] = action.id  # name ou id ?
    #         logs.append(action_line)
    #         tour_en_cours.jouer_carte(action)
    #
    #     elif action in player.servants or type(action) == Hero:
    #         provocation = False
    #         for carte in adv.servants:
    #             if "provocation" in carte.get_effects():
    #                 provocation = True
    #
    #         targets = []
    #         if provocation:
    #             for carte in adv.servants:
    #                 if "provocation" in carte.get_effects():
    #                     targets.append(carte)
    #         else:
    #             if type(action) == Card:
    #                 if "Ruée" in action.get_effects():
    #                     if action.effects["Ruée"].active is False:
    #                         targets.append(adv.hero)
    #                 else:
    #                     targets.append(adv.hero)
    #             else:
    #                 targets.append(adv.hero)
    #             for carte in adv.servants:
    #                 targets.append(carte)
    #
    #         target = choice(targets)
    #
    #         action_line["action"] = "attaquer"
    #         action_line["attaquant"] = action.id if type(action) is Card else "heros"
    #         action_line["attaquant_atq"] = action.attack
    #         action_line["attaquant_pv"] = action.health
    #         action_line["cible"] = target.id if type(target) is Card else "heros"
    #         action_line["cible_atq"] = target.attack
    #         action_line["cible_pv"] = target.health
    #
    #         logs.append(action_line)
    #
    #         tour_en_cours.attaquer(action, target)
    #     plateau.update()
    #     return plateau

    def tour_oldia_model(self, plateau, logs, policy):

        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
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
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32, name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool, name='valid_actions')
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
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
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
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32, name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool, name='valid_actions')
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
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
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
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32, name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool, name='valid_actions')
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
        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()

        if action == 0:
            if generate_logs:
                action_line["action"] = "passer_tour"
                logs.append(action_line)
            TourEnCours(plateau).fin_du_tour()
        elif action < 161:
            played_card = plateau.players[0].hand[(action - 1) // 16]
            if generate_logs:
                action_line["action"] = "jouer_carte"
                action_line["carte_jouee"] = played_card.id  # name ou id ?
                logs.append(action_line)
            if (action - 1) % 16 == 0:
                target = None
                if "cri de guerre" in played_card.effects and "choisi" not in played_card.effects["cri de guerre"]:
                    if played_card.effects["cri de guerre"][1][0] == "main":
                        if played_card.effects["cri de guerre"][1][1] == "allié":
                            if played_card.effects["cri de guerre"][1][2] == "tous":
                                target = CardGroup((x for x in plateau.players[0].hand if x.type.lower() == "serviteur"))
                                target.remove(played_card)
            elif (action - 1) % 16 == 1:
                target = plateau.players[0].hero
            elif (action - 1) % 16 == 8:
                target = plateau.players[1].hero
            elif (action - 1) % 16 < 8:
                target = plateau.players[0].servants[(action - 1) % 16 - 2]
            else:
                target = plateau.players[1].servants[(action - 1) % 16 - 9]
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
            if action == 225:
                target = plateau.players[0].hero
            elif action == 233:
                target = plateau.players[1].hero
            elif action < 233:
                target = plateau.players[0].servants[action - 226]
            else:
                target = plateau.players[1].servants[action - 234]
            if generate_logs:
                action_line["action"] = "pouvoir_heroique"
                action_line["cible"] = target.id if type(target) is Card else "heros"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
            TourEnCours(plateau).pouvoir_heroique(plateau.players[0].classe, target)

        dead_servants = plateau.update()
        for servant in dead_servants:
            TourEnCours(plateau).apply_effects(servant)
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
        for i in range(0, round(nb_games/2)):
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
        for i in range(round(nb_games/2), nb_games):
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
        logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis = 1)
        os.remove('plateau_init1.pickle')
        os.remove('plateau_init2.pickle')
        return logs_hs, scores

    def generate_oldia_game(self, nb_games, new_policy=saved_policy, players=(), generate_logs=True):
        if generate_logs:
            logs_hs = []
        scores = {}

        """ On simule nb_games parties """
        """ La moitié où le joueur 1 commence """
        for i in range(0, round(nb_games/2)):
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

        for i in range(round(nb_games/2), nb_games):
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