import time
from engine import *
import gc
import functools


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
            if alpha == 10000:
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
    class_j1 = "Paladin"
    class_j2 = random.choice(all_classes)
    deck_j1 = random.choice(class_files[class_j1])
    deck_j2 = random.choice(class_files[class_j2])
    players = [Player("NewIA", class_j1, import_deck(deck_j1[0]), style_deck=deck_j1[1]), Player("OldIA", class_j2,import_deck(deck_j2[0]), style_deck=deck_j2[1])].copy()
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

