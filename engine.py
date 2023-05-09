import pandas as pd

from Entities import *
import random
from init_variables import *
import pickle
import os
from operator import itemgetter
from copy import deepcopy
from tf_agents.trajectories import time_step as ts
import tensorflow as tf
from tf_agents.specs import array_spec
from tf_agents.environments import py_environment, tf_py_environment

""" Chargement des données d'entraînement et de données d'init """
with open('modelisation/logs_refined.pickle', 'rb') as f:
    df_state = pickle.load(f)

dict_actions = {
            0: "passer_tour",
            1: "jouer_carte",
            2: "attaquer"
        }

class Frenchstone(py_environment.PyEnvironment):
    def __init__(self, data):
        self.data = data
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(shape=(1, self.data.shape[1]), dtype=np.int32, minimum=-100, maximum=100, name='observation')
        # self._observation_spec = {
        #     'observations': array_spec.BoundedArraySpec(shape=(1, self.data_train.shape[1]), dtype=np.int32, minimum=-100, maximum=100, name='observation'),
        #     'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(3,), dtype=np.bool_)
        # }
        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]
        self.actual_step = 0
        self._episode_ended = False
        return ts.restart(np.array([self._state], dtype=np.int32))

    def _step(self, action):

        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        legal_actions = [0]
        """ Calcul de la récompense """
        """ Ici, on doit déterminer les actions légales en fonction de l'état tiré au hasard """
        """ Peut-on jouer une carte ? """
        for i in range(int(self._state["nbre_cartes_j"])):
            if self._state[f"carte_en_main{i + 1}_cost"] <= self._state["mana_dispo_j"] and self._state[f"carte_en_main{i + 1}_cost"] != 99:
                legal_actions.append(1)
                break
        """ Peut-on attaquer ? """
        for i in range(7):
            if self._state[f"atq_remain_serv{i + 1}_j"] > 0:
                legal_actions.append(2)
                break


        if action not in legal_actions:
            reward = -100
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        else:
            if len(legal_actions) == 1:
                reward = 0
                self._episode_ended = True
                return ts.termination(np.array([self._state], dtype=np.int32), reward)
            else:
                if int(action) == self._state['action']:
                    if self._state['victoire'] == 1:
                        reward = 1
                    else:
                        reward = -1
                    self._episode_ended = True
                    return ts.termination(np.array([self._state], dtype=np.int32), reward)
                else:
                    reward = 0
                    self._episode_ended = True
                    return ts.termination(np.array([self._state], dtype=np.int32), reward)



""" Initialisation de l'environnement et chagrement du modèle """
env = Frenchstone(df_state.reset_index().drop('index', axis=1))
env = tf_py_environment.TFPyEnvironment(env)

saved_policy = tf.compat.v2.saved_model.load('modelisation/frenchstone_agent')
policy_state = saved_policy.get_initial_state(batch_size=512)

class Plateau:
    def __init__(self, players=()):
        """ Décrit exhaustivement le plateau de jeu """
        class_files = {'Chasseur': 'test_deck.csv',
                       'Mage': 'test_deck.csv'}
        if players == ():
            self.players = [Player("Smaguy", 'Chasseur'), Player("Rupert", 'Mage')]

        else:
            self.players = list(players)

        for player in self.players:
            player.set_deck(class_files[player.classe])

        # shuffle(self.players)  ## Il ne faut probablement pas shuffle les joueurs, mais plutôt les faire alterner dans le main

        """ Mélange des decks et tirage de la main de départ """
        for player in self.players:
            player.start_game()

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

        self.players[0].start_turn()

    def update(self):
        """ Vérifie les serviteurs morts et les pdv des joueurs """
        for player in self.players:
            if player.hero.is_dead():
                self.game_on = False
                for winner in self.players:
                    if winner != player:
                        self.winner = winner
            for servant in player.servants:
                if servant.is_dead():
                    player.servants.remove(servant)

    def get_targets(self, serviteur):
        if serviteur not in self.players[0].servants:
            raise KeyError("Le serviteur choisi n'est pas sur le plateau du joueur actif")
        else:
            adv = self.players[1]
            targets = []
            if "Ruée" in serviteur.get_effects():
                if serviteur.effects["Ruée"].active is False:
                    targets.append(adv.hero)
            else:
                targets.append(adv.hero)
            for carte in adv.servants:
                targets.append(carte)
        return targets

    def get_gamestate(self) -> dict:
        player = self.players[0]
        adv = self.players[1]

        # On assigne les actions de base avant les actions spécifiques au choix
        """ BOARD """
        action_line = {"action": 0,
                       "carte_jouee": "",
                       "attaquant": "", "attaquant_atq": "", "attaquant_pv": "",
                       "cible": "", "cible_atq": "", "cible_pv": "",
                       "classe_j": player.classe, "classe_adv": adv.classe,
                       "mana_dispo_j": player.mana, "mana_max_j": player.mana_max,
                       "mana_max_adv": adv.mana_max,
                       "surcharge_j": player.surcharge, "surcharge_adv": adv.surcharge,
                       "pv_j": player.hero.health, "pv_adv": adv.hero.health,
                       "pv_max_j": player.hero.base_health, "pv_max_adv": adv.hero.base_health,
                       "nbre_cartes_j": len(player.hand),
                       "nbre_cartes_adv": len(adv.hand),
                       "dispo_ph_j": player.hero.dispo_pouvoir,
                       "cout_ph_j": player.hero.cout_pouvoir,
                       "arme_j": player.hero.weapon,
                       "arme_adv": adv.hero.weapon,
                       "attaque_j": player.hero.attack,
                       "attaque_adv": adv.hero.attack,
                       "durabilite_arme_j": player.hero.weapon.durability if player.hero.weapon is not None else 0,
                       "durabilite_arme_adv": adv.hero.weapon.durability if player.hero.weapon is not None else 0,
                       "pseudo_j": player.name,
                       "pseudo_adv": adv.name,
                       "victoire": 0}
        """ HAND """
        cartes_en_main = {i: carte for i, carte in enumerate(player.hand)}
        for i in range(10):
            if i in cartes_en_main.keys():
                action_line[f"carte_en_main{i + 1}"] = cartes_en_main[i].id
                action_line[f"carte_en_main{i + 1}_cost"] = cartes_en_main[i].cost
            else:
                action_line[f"carte_en_main{i + 1}"] = -99
                action_line[f"carte_en_main{i + 1}_cost"] = -99

        """ SERVANTS """
        player_servants = {i: carte.id for i, carte in enumerate(player.servants)}
        player_servants_atk = {i: carte.attack for i, carte in enumerate(player.servants)}
        player_servants_pv = {i: carte.health for i, carte in enumerate(player.servants)}
        player_servants_atk_remain = {i: carte.remaining_atk for i, carte in enumerate(player.servants)}
        for i in range(7):
            if i in player_servants.keys():
                action_line[f"serv{i + 1}_j"] = player_servants[i]
                action_line[f"atq_serv{i + 1}_j"] = player_servants_atk[i]
                action_line[f"pv_serv{i + 1}_j"] = player_servants_pv[i]
                action_line[f"atq_remain_serv{i + 1}_j"] = player_servants_atk_remain[i]
            else:
                action_line[f"serv{i + 1}_j"] = -99
                action_line[f"atq_serv{i + 1}_j"] = -99
                action_line[f"pv_serv{i + 1}_j"] = -99
                action_line[f"atq_remain_serv{i + 1}_j"] = -99

        adv_servants = {i: carte.id for i, carte in enumerate(adv.servants)}
        adv_servants_atk = {i: carte.attack for i, carte in enumerate(adv.servants)}
        adv_servants_pv = {i: carte.health for i, carte in enumerate(adv.servants)}
        for i in range(7):
            if i in adv_servants.keys():
                action_line[f"serv{i + 1}_adv"] = adv_servants[i]
                action_line[f"atq_serv{i + 1}_adv"] = adv_servants_atk[i]
                action_line[f"pv_serv{i + 1}_adv"] = adv_servants_pv[i]
            else:
                action_line[f"serv{i + 1}_adv"] = -99
                action_line[f"atq_serv{i + 1}_adv"] = -99
                action_line[f"pv_serv{i + 1}_adv"] = -99

        return action_line


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
            attaquant.remaining_atk -= 1
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

        action = choice(action_possible)
        if action == "Passer_tour":
            action_line["action"] = "passer_tour"
            logs.append(action_line)
            tour_en_cours.fin_du_tour()

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

    def tour_ia(self, plateau, logs, policy, state):
        """ L'IA génère une action d'après son modèle on la fait jouer par la classe Tourencours """
        player = plateau.players[0]
        adv = plateau.players[1]

        tour_en_cours = TourEnCours(plateau)
        step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
        reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
        discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')


        """ Initialisation du vecteur d'état représentant le plateau"""
        action_line = plateau.get_gamestate()

        """ Sélection des colonnes nécessaires à la prédiction """
        columns_actual_state = ["mana_dispo_j", "mana_max_j",
                                "mana_max_adv", "surcharge_j", "surcharge_adv", "pv_j", "pv_adv", "pv_max_j",
                                "pv_max_adv", "nbre_cartes_j",
                                "nbre_cartes_adv"]

        for i in range(10):
            columns_actual_state.append(f"carte_en_main{i + 1}_cost")

        for i in range(7):
            columns_actual_state.append(f"atq_serv{i + 1}_j")
            columns_actual_state.append(f"pv_serv{i + 1}_j")
            columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

        for i in range(7):
            columns_actual_state.append(f"atq_serv{i + 1}_adv")
            columns_actual_state.append(f"pv_serv{i + 1}_adv")
        columns_actual_state.append("action")
        columns_actual_state.append("victoire")

        """ Le modèle choisit l'action à effectuer """
        input_state = np.array(itemgetter(*columns_actual_state)(action_line))
        observations = tf.convert_to_tensor(input_state.reshape(1, 1, -1), dtype=tf.int32, name='observations')
        timestep = ts.TimeStep(step_type, reward, discount, observations)
        result = saved_policy.action(timestep, policy_state)
        action = dict_actions[int(result.action)]

        if action == "passer_tour":
            action_line["action"] = "passer_tour"
            logs.append(action_line)
            tour_en_cours.fin_du_tour()

        elif action == "jouer_carte":
            try:
                """ La carte est jouée depuis la main """
                action_line["action"] = "jouer_carte"
                playable_cards = [x for x in player.hand if x.cost <= player.mana]
                played_card = choice(playable_cards)
                action_line["carte_jouee"] = played_card.id  # name ou id ?
                logs.append(action_line)
                tour_en_cours.jouer_carte(played_card)
            except:
                action_line["action"] = "passer_tour"
                logs.append(action_line)
                tour_en_cours.fin_du_tour()

        elif action == "attaquer":
            try:
                potential_attackers = []
                for carte in player.servants:
                    if carte.attack > 0 and carte.remaining_atk > 0:
                        if len(tour_en_cours.plt.get_targets(carte)) > 0:
                            potential_attackers.append(carte)
                if player.hero.attack > 0:
                    potential_attackers.append(player.hero)

                attacker = choice(potential_attackers)

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
                    if "Ruée" in attacker.get_effects():
                        if attacker.effects["Ruée"].active is False:
                            targets.append(adv.hero)
                    else:
                        targets.append(adv.hero)
                    for carte in adv.servants:
                        targets.append(carte)

                target = choice(targets)

                action_line["action"] = "attaquer"
                action_line["attaquant"] = attacker.id if type(attacker) is Card else "heros"
                action_line["attaquant_atq"] = attacker.attack
                action_line["attaquant_pv"] = attacker.health
                action_line["cible"] = target.id if type(target) is Card else "heros"
                action_line["cible_atq"] = target.attack
                action_line["cible_pv"] = target.health
                logs.append(action_line)
                tour_en_cours.attaquer(attacker, target)
            except:
                action_line["action"] = "passer_tour"
                logs.append(action_line)
                tour_en_cours.fin_du_tour()

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
            print(i)

        """ L'autre moitié où le joueur 2 commence """
        for i in range(round(nb_games/2), nb_games):
            logs_inter = []
            with open('plateau_init2.pickle', 'rb') as f:
                mon_plateau2 = pickle.load(f)
            while mon_plateau2.game_on:
                if mon_plateau2.game_turn % 2 == 0:
                    mon_plateau2 = Orchestrator().tour_ia(mon_plateau2, logs_inter, saved_policy, policy_state)
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
            print(i)

        """ Concaténation des logs + suppression des plateaux temporaires """
        logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis = 1)
        os.remove('plateau_init1.pickle')
        os.remove('plateau_init2.pickle')
        return logs_hs, scores

    def generate_ia_game(selfself, nb_games, players=()):
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
            print(i)

        """ Concaténation des logs + suppression des plateaux temporaires """
        logs_hs = pd.concat(logs_hs).reset_index().drop("index", axis=1)
        os.remove('plateau_init1.pickle')
        os.remove('plateau_init2.pickle')
        return logs_hs, scores


if __name__ == '__main__':
    logs_hs, scores = Orchestrator().generate_random_game(10)
    print(scores)

