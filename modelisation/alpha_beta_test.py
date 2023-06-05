import time
from engine import *
from statistics import mean

players = [Player("NewIA", "Mage"), Player("OldIA", "Chasseur")]
plateau_depart = Plateau(deepcopy(players))

def calc_advantage_minmax(state):
    advantage = (state["nbre_cartes_j"] - state["nbre_cartes_adv"]) + 0.8 * (
                state["nbre_cartes_j"] / max(1, state["nbre_cartes_adv"]))
    for i in range(1, 8):
        if state[f"serv{i}_j"] != -99:
            advantage += 1.5 * state[f"atq_serv{i}_j"] + 1.5 * state[f"pv_serv{i}_j"]
        if state[f"serv{i}_adv"] != -99:
            advantage -= 1.5 * state[f"atq_serv{i}_adv"] + 1.5 * state[f"pv_serv{i}_adv"]
    advantage += 0.25 * (pow(30 - state["pv_adv"], 1.3) - pow(30 - state["pv_j"], 1.3))
    advantage += state["attaque_j"]
    if state["pv_j"] <= 0:
        return -500
    elif state["pv_adv"] <= 0:
        return 500

    return round(advantage, 2)


def minimax(state, alpha=-1000, depth=0, best_action=-99, max_depth=2):

    base_advantage = calc_advantage_minmax(state.get_gamestate())
    legal_actions = np.array(generate_legal_vector(state), dtype=bool)
    legal_actions = [i for i in range(len(legal_actions)) if legal_actions[i]]

    possible_new_states = np.array([
        (action, Orchestrator().tour_ia_training(deepcopy(state), action)) for action in legal_actions
    ])

    first_estimate = [calc_advantage_minmax(possible_new_states[i][1].get_gamestate()) for i in range(len(possible_new_states))]
    first_estimate[0] = base_advantage
    first_estimate = np.array(first_estimate)
    possible_new_states = possible_new_states[first_estimate.argsort()[-max(round(len(possible_new_states)/(depth + 2)), 1):]]

    for new_state in possible_new_states:
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
                break

    return alpha, best_action



# logs = []
# beginning = time.perf_counter()
# for i in range(10):
#     print(i)
#     while plateau_depart.game_on:
#         max_reward, best_action = minimax(plateau_depart)
#         plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], best_action)
#         print(f"Meilleure action : {best_action}   ---   Avantage estimé : {max_reward}")
#         print(plateau_depart.get_gamestate())
#         print('----------------------------------------------')
#         logs.append(pd.DataFrame(logs_inter))
#     plateau_depart = Plateau(deepcopy(players))
# end = time.perf_counter()
# logs_hs = pd.concat(logs).reset_index().drop("index", axis=1)
# print(end - beginning)
#
# """ Sauvegarde des logs"""
# os.remove('logs_games.pickle')
# with open('logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs, f)

