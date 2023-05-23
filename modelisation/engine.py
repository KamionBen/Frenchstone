import pandas as pd
import numpy as np
from Entities import *
import random
import pickle
import os
from operator import itemgetter
from copy import deepcopy
from tf_agents.trajectories import time_step as ts
import tensorflow as tf
from tf_agents.specs import array_spec
from tf_agents.environments import py_environment, tf_py_environment
from tf_agents.policies import greedy_policy

""" Chargement des données d'entraînement et de données d'init """
with open('logs_refined_light.pickle', 'rb') as f:
    df_state = pickle.load(f)

dict_actions = {
            0: "passer_tour",
            1: "jouer_carte",
            2: "attaquer"
        }


def generate_legal_vector_old(state):
    """ Gestion des actions légales """
    legal_actions = [True]
    for i in range(74):
        legal_actions.append(False)

    """ Peut-on jouer une carte ? """
    for i in range(int(state["nbre_cartes_j"])):
        if state[f"carte_en_main{i + 1}_cost"] <= state["mana_dispo_j"] and state[f"carte_en_main{i + 1}_cost"] != -99\
                and state[f"pv_serv7_j"] == -99:
            legal_actions[i+1] = True
            break

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    for i in range(1, 8):
        if state[f"atq_remain_serv{i}_j"] > 0:
            legal_actions[11 + 8 * i] = True
            for j in range(1, 8):
                if state[f"atq_serv{j}_adv"] != -99:
                    legal_actions[11 + 8 * i + j] = True
    return legal_actions


def generate_legal_vector(state):
    """ Gestion des actions légales """
    legal_actions = [True]
    gamestate = state.get_gamestate()
    for i in range(90):
        legal_actions.append(False)

    """ Quelles cartes peut-on jouer ? """
    for i in range(int(gamestate["nbre_cartes_j"])):
        if gamestate[f"carte_en_main{i + 1}_cost"] <= gamestate["mana_dispo_j"] and gamestate[f"carte_en_main{i + 1}_cost"] != -99\
                and gamestate[f"pv_serv7_j"] == -99:
            legal_actions[i+1] = True
            break

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    for i in range(1, 8):
        if gamestate[f"atq_remain_serv{i}_j"] > 0:
            legal_actions[11 + 8 * i] = True
            for j in range(1, 8):
                if gamestate[f"atq_serv{j}_adv"] != -99:
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


class Frenchstone_old(py_environment.PyEnvironment):
    def __init__(self, data):
        self.data = data
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=65, name='action')
        self._observation_spec = {
            'observation': array_spec.BoundedArraySpec(shape=(self.data.shape[1],), dtype=np.int32, minimum=-100, maximum=100, name='observation'),
            'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(66,), dtype=np.bool_)
        }
        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]
        self._episode_ended = False
        obs = self.observation_spec()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state)

        obs['observation'] = np.array(self._state, dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.restart(obs)

    def _step(self, action):

        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]

        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state)

        if not(legal_actions[1] or legal_actions[2]):
            reward = 0
            self._episode_ended = True
            obs = self.observation_spec()
            obs['observation'] = np.array(self._state, dtype=np.int32)
            obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
            return ts.termination(obs, reward)
        else:
            if int(action) == self._state['action']:
                if self._state['victoire'] == 1:
                    reward = 1
                else:
                    reward = -1
                obs = self.observation_spec()
                obs['observation'] = np.array(self._state, dtype=np.int32)
                obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
                if int(action) == 0:
                    self._episode_ended = True
                    return ts.termination(obs, reward)
                else:
                    return ts.transition(obs, reward)
            else:
                if self._state['victoire'] == 1:
                    reward = -0.05
                else:
                    reward = 0.02
                obs = self.observation_spec()
                obs['observation'] = np.array(self._state, dtype=np.int32)
                obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
                if int(action) == 0:
                    self._episode_ended = True
                    return ts.termination(obs, reward)
                else:
                    return ts.transition(obs, reward)


columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j", "nbre_cartes_adv"]

for i in range(10):
    columns_actual_state.append(f"carte_en_main{i + 1}_cost")
    columns_actual_state.append(f"carte_en_main{i + 1}_atk")
    columns_actual_state.append(f"carte_en_main{i + 1}_pv")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_j")
    columns_actual_state.append(f"pv_serv{i + 1}_j")
    columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_adv")
    columns_actual_state.append(f"pv_serv{i + 1}_adv")


class Frenchstone(py_environment.PyEnvironment):
    def __init__(self):
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=90, name='action')
        self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
        self._observation_spec = {
            'observation': array_spec.BoundedArraySpec(shape=(len(itemgetter(*columns_actual_state)(self._state.get_gamestate())),), dtype=np.int32, minimum=-100, maximum=100, name='observation'),
            'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(91,), dtype=np.bool_)
        }
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        if bool(random.getrandbits(1)):
            self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
        else:
            self._state = Plateau([Player("OldIA", "Chasseur"), Player("NewIA", "Mage")])
            while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
                self._state = Orchestrator().tour_oldia_training(self._state, old_policy, oldpolicy_state)
        self._episode_ended = False
        obs = self.observation_spec()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state)

        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()))
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.restart(obs)

    def _step(self, action):

        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        """ Estimation de la récompense """
        # reward = estimated_advantage(action, self._state.get_gamestate())

        """ Gestion des actions légales """
        self._state = Orchestrator().tour_ia_training(self._state, action)

        legal_actions = generate_legal_vector(self._state)
        obs = self.observation_spec()
        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()), dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)

        if not self._state.game_on:
            reward = 100
            self._episode_ended = True
            return ts.termination(obs, reward)

        while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
            self._state = Orchestrator().tour_oldia_training(self._state, old_policy, oldpolicy_state)
            if not self._state.game_on:
                reward = -100
                self._episode_ended = True
                return ts.termination(obs, reward)

        legal_actions = generate_legal_vector(self._state)
        obs = self.observation_spec()
        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()), dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        reward = 0
        return ts.transition(obs, reward)


""" Initialisation de l'environnement et chagrement du modèle """
old_env = Frenchstone_old(df_state.reset_index().drop('index', axis=1))
old_env = tf_py_environment.TFPyEnvironment(old_env)
env = Frenchstone()
env = tf_py_environment.TFPyEnvironment(env)

old_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02')
oldpolicy_state = old_policy.get_initial_state(batch_size=512)
saved_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02-a')
policy_state = saved_policy.get_initial_state(batch_size=128)




class TourEnCours:
    """Classe prenant en entrée un plateau de jeu et permettant d'effectuer toutes les actions possibles dessus."""
    def __init__(self, plateau):
        self.plt = plateau

    def jouer_carte(self, carte):
        """ Action de poser une carte depuis la main du joueur dont c'est le tour.
        Le plateau est mis à jour en conséquence """
        player = self.plt.players[0]
        if carte.cost <= player.mana:
            if carte.type.lower() == "sort":
                player.hand.remove(carte)
                player.mana_spend(carte.cost)
            elif carte.type.lower() == "serviteur":
                if len(player.servants) < 7:
                    player.hand.remove(carte)
                    player.servants.add(carte)
                    player.mana_spend(carte.cost)
                else:
                    raise PermissionError("Nombre maximum de serviteurs atteint")
        else:
            raise PermissionError("Carte plus chère que la mana du joueur")

    def attaquer(self, attaquant, cible):
        """ Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi) """
        if type(attaquant) in (Hero, Card) and type(cible) in (Hero, Card):
            cible.damage(attaquant.attack)
            attaquant.damage(cible.attack)
            self.plt.update()
            if type(attaquant) == Card:
                attaquant.remaining_atk -= 1
        else:
            raise TypeError

    def pouvoir_heroique(self, classe, cible):
        player = self.plt.players[0]
        if type(cible) in (Hero, Card):
            if classe == "Mage":
                cible.damage(1)
            elif classe == "Chasseur":
                cible.damage(2)
            player.mana_spend(player.hero.cout_pouvoir)
            player.hero.dispo_pouvoir = False
            self.plt.update()
        else:
            raise TypeError

    def fin_du_tour(self):
        self.plt.tour_suivant()


class Orchestrator:
    def tour_au_hasard(self, plateau, logs):
        """ On génère une action aléatoire et on la fait jouer par la classe Tourencours """
        player = plateau.players[0]
        adv = plateau.players[1]
        tour_en_cours = TourEnCours(plateau)

        action_line = plateau.get_gamestate()

        """ ON CHOISIT L'ACTION """
        action_possible = ["Passer_tour"]
        for carte in player.servants:
            if carte.attack > 0 and carte.remaining_atk > 0:
                if len(tour_en_cours.plt.get_targets(carte)) > 0:
                    action_possible.append(carte)
        for carte in player.hand:
            if carte.cost <= player.mana and not (carte.type.lower() == "serviteur" and len(player.servants) == 7):
                action_possible.append(carte)
        if player.hero.attack > 0:
            action_possible.append(player.hero)
        if player.hero.cout_pouvoir <= player.mana and player.hero.dispo_pouvoir:
            action_possible.append("Pouvoir_heroique")

        action = choice(action_possible)
        if action == "Passer_tour":
            action_line["action"] = "passer_tour"
            logs.append(action_line)
            tour_en_cours.fin_du_tour()

        elif action == "Pouvoir_heroique":
            target = random.choice(plateau.targets_hp())
            action_line["action"] = "pouvoir_heroique"
            action_line["cible"] = target.id if type(target) is Card else "heros"
            action_line["cible_atq"] = target.attack
            action_line["cible_pv"] = target.health
            logs.append(action_line)

            tour_en_cours.pouvoir_heroique(player.classe, target)

        elif (action in player.hand) and (action.cost <= player.mana):
            """ La carte est jouée depuis la main """
            action_line["action"] = "jouer_carte"
            action_line["carte_jouee"] = action.id  # name ou id ?
            logs.append(action_line)
            tour_en_cours.jouer_carte(action)

        elif action in player.servants or type(action) == Hero:
            provocation = False
            for carte in adv.servants:
                if "provocation" in carte.get_effects():
                    provocation = True

            targets = []
            if provocation:
                for carte in adv.servants:
                    if "provocation" in carte.get_effects():
                        targets.append(carte)
            else:
                if "Ruée" in action.get_effects():
                    if action.effects["Ruée"].active is False:
                        targets.append(adv.hero)
                else:
                    targets.append(adv.hero)
                for carte in adv.servants:
                    targets.append(carte)

            target = choice(targets)

            action_line["action"] = "attaquer"
            action_line["attaquant"] = action.id if type(action) is Card else "heros"
            action_line["attaquant_atq"] = action.attack
            action_line["attaquant_pv"] = action.health
            action_line["cible"] = target.id if type(target) is Card else "heros"
            action_line["cible_atq"] = target.attack
            action_line["cible_pv"] = target.health

            logs.append(action_line)

            tour_en_cours.attaquer(action, target)
        plateau.update()
        return plateau

    def tour_oldia_model(self, plateau, logs, policy, state):
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')

        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()

        """ Sélection des colonnes nécessaires à la prédiction """
        columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                                "nbre_cartes_adv"]

        for i in range(10):
            columns_actual_state.append(f"carte_en_main{i + 1}_cost")
            columns_actual_state.append(f"carte_en_main{i + 1}_atk")
            columns_actual_state.append(f"carte_en_main{i + 1}_pv")

        for i in range(7):
            columns_actual_state.append(f"atq_serv{i + 1}_j")
            columns_actual_state.append(f"pv_serv{i + 1}_j")
            columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

        for i in range(7):
            columns_actual_state.append(f"atq_serv{i + 1}_adv")
            columns_actual_state.append(f"pv_serv{i + 1}_adv")

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        input_state = np.array(itemgetter(*columns_actual_state)(action_line))

        legal_actions = generate_legal_vector_old(action_line)

        observations = env.observation_spec()
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
                                                           name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
                                                             name='valid_actions')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = policy.action(timestep, state)
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
        elif action >= 11:
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

        plateau.update()
        return plateau

    def tour_oldia_training(self, plateau, policy, state):
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')

        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()

        """ Sélection des colonnes nécessaires à la prédiction """
        columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                                "nbre_cartes_adv"]

        for i in range(10):
            columns_actual_state.append(f"carte_en_main{i + 1}_cost")
            columns_actual_state.append(f"carte_en_main{i + 1}_atk")
            columns_actual_state.append(f"carte_en_main{i + 1}_pv")

        for i in range(7):
            columns_actual_state.append(f"atq_serv{i + 1}_j")
            columns_actual_state.append(f"pv_serv{i + 1}_j")
            columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

        for i in range(7):
            columns_actual_state.append(f"atq_serv{i + 1}_adv")
            columns_actual_state.append(f"pv_serv{i + 1}_adv")

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        input_state = np.array(itemgetter(*columns_actual_state)(action_line))

        legal_actions = generate_legal_vector_old(action_line)

        observations = env.observation_spec()
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32,
                                                           name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool,
                                                             name='valid_actions')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = policy.action(timestep, state)
        action = int(result.action)

        if action == 0:
            TourEnCours(plateau).fin_du_tour()
        elif action < 11:
            played_card = plateau.players[0].hand[action - 1]
            TourEnCours(plateau).jouer_carte(played_card)
        elif action >= 11:
            attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
            if (action - 11) % 8 == 0:
                target = plateau.players[1].hero
            else:
                target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
            TourEnCours(plateau).attaquer(attacker, target)

        plateau.update()
        return plateau

    def tour_ia_model(self, plateau, logs, policy, state):
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')


        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        input_state = np.array(itemgetter(*columns_actual_state)(action_line))
        legal_actions = generate_legal_vector(plateau)


        observations = env.observation_spec()
        observations['observation'] = tf.convert_to_tensor(input_state.reshape(1, -1), dtype=tf.int32, name='observation')
        observations['valid_actions'] = tf.convert_to_tensor(np.array(legal_actions).reshape(1, -1), dtype=tf.bool, name='valid_actions')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = policy.action(timestep, state)
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


    def tour_ia_training(self, plateau, action):
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """

        """ Le modèle choisit l'action à effectuer parmi les actions légales """

        action = int(action)

        if action == 0:
            TourEnCours(plateau).fin_du_tour()
        elif action < 11:
            TourEnCours(plateau).jouer_carte(plateau.players[0].hand[action - 1])
        elif 11 <= action < 75:
            attacker = plateau.players[0].servants[int((action - 11) // 8 - 1)]
            if (action - 11) % 8 == 0:
                target = plateau.players[1].hero
            else:
                target = plateau.players[1].servants[int((action - 11) % 8 - 1)]
            TourEnCours(plateau).attaquer(attacker, target)
        elif action >= 75:
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


    """ Génère un nombre donné de parties et créé les logs associés"""
    def generate_random_game(self, nb_games, players=()):
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
                mon_plateau = Orchestrator().tour_au_hasard(mon_plateau, logs_inter)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
            logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            print(i)

        """ L'autre moitié où le joueur 2 commence """
        for i in range(round(nb_games/2), nb_games):
            logs_inter = []
            with open('plateau_init2.pickle', 'rb') as f:
                mon_plateau2 = pickle.load(f)
            while mon_plateau2.game_on:
                mon_plateau2 = Orchestrator().tour_au_hasard(mon_plateau2, logs_inter)

            """Actions de fin de partie"""
            winner = mon_plateau2.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
            logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            print(i)

        """ Concaténation des logs + suppression des plateaux temporaires """
        logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis = 1)
        os.remove('plateau_init1.pickle')
        os.remove('plateau_init2.pickle')
        return logs_hs, scores

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
                    mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, saved_policy, policy_state)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
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
                    mon_plateau2 = Orchestrator().tour_ia_model(mon_plateau2, logs_inter, saved_policy, policy_state)
                else:
                    mon_plateau2 = Orchestrator().tour_au_hasard(mon_plateau2, logs_inter)

            """Actions de fin de partie"""
            winner = mon_plateau2.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
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

    def generate_oldia_game(selfself, nb_games, players=()):
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
                    mon_plateau = Orchestrator().tour_oldia_model(mon_plateau, logs_inter, old_policy, oldpolicy_state)
                else:
                    mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, saved_policy, policy_state)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
            logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            if i % 100 == 0:
                print(i)

        for i in range(round(nb_games/2), nb_games):
            logs_inter = []
            with open('plateau_init2.pickle', 'rb') as f:
                mon_plateau = pickle.load(f)
            while mon_plateau.game_on:
                if mon_plateau.game_turn % 2 == 0:
                    mon_plateau = Orchestrator().tour_ia_model(mon_plateau, logs_inter, saved_policy, policy_state)
                else:
                    mmon_plateau = Orchestrator().tour_oldia_model(mon_plateau, logs_inter, old_policy, oldpolicy_state)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
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

    def generate_ia_game(self, nb_games, players=()):
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
                mon_plateau = Orchestrator().tour_ia(mon_plateau, logs_inter, saved_policy, policy_state)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
            logs_hs.append(logs_inter)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
            if i % 100 == 0:
                print(i)

        for i in range(round(nb_games/2), nb_games):
            logs_inter = []
            with open('plateau_init2.pickle', 'rb') as f:
                mon_plateau = pickle.load(f)
            while mon_plateau.game_on:
                mon_plateau = Orchestrator().tour_ia(mon_plateau, logs_inter, saved_policy, policy_state)

            """Actions de fin de partie"""
            winner = mon_plateau.winner
            logs_inter = pd.DataFrame(logs_inter)
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
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


if __name__ == '__main__':
    logs_hs, scores = Orchestrator().generate_random_game(10)
    print(scores)