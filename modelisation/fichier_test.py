import time
from engine import *
from statistics import mean

players = [Player("NewIA", "Druide"), Player("OldIA", "Druide")]
plateau_depart = Plateau(deepcopy(players))


def generate_legal_vector_test(state):
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


def calc_advantage_minmax(state):
    gamestate = state.get_gamestate()
    advantage = (len(state.players[0].hand) - len(state.players[1].hand)) + 0.8 * (
                len(state.players[0].hand) / max(1, len(state.players[1].hand)))
    for servant in state.players[0].servants:
        advantage += 1.5 * servant.attack + 1.5 * servant.health
        if "bouclier divin" in servant.effects:
            advantage += 1.5 * servant.attack
    for servant in state.players[1].servants:
        advantage -= 1.5 * servant.attack + 1.5 * servant.health
        if "bouclier divin" in servant.effects:
            advantage -= 1.5 * servant.attack
    advantage += 0.25 * (pow(30 - state.players[1].hero.health, 1.3) - pow(30 - state.players[0].hero.health, 1.3))
    advantage += state.players[0].hero.attack
    if state.players[0].hero.health <= 0:
        return -500
    elif state.players[1].hero.health <= 0:
        return 500

    return round(advantage, 2)


def minimax(state, alpha=-1000, depth=0, best_action=-99, max_depth=4, exploration_toll=2):

    base_advantage = calc_advantage_minmax(state)
    legal_actions = np.array(generate_legal_vector_test(state), dtype=bool)
    legal_actions = [i for i in range(len(legal_actions)) if legal_actions[i]]

    possible_new_states = np.array([
        (action, Orchestrator().tour_ia_minmax(deepcopy(state), [], action, False)[0]) for action in legal_actions
    ])

    first_estimate = [calc_advantage_minmax(possible_new_states[i][1]) for i in range(len(possible_new_states))]
    first_estimate[0] = base_advantage
    first_estimate = np.array(first_estimate)
    possible_new_states = possible_new_states[first_estimate.argsort()[-max(round(len(possible_new_states)/(pow(exploration_toll, depth))), 1):]]

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



logs = []
beginning = time.perf_counter()
for i in range(10):
    print(i)
    while plateau_depart.game_on:
        max_reward, best_action = minimax(plateau_depart)
        plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], best_action)
        print(f"Meilleure action : {best_action}   ---   Avantage estimé : {max_reward}")
        print(plateau_depart.get_gamestate())
        print('----------------------------------------------')
        logs.append(pd.DataFrame(logs_inter))
    plateau_depart = Plateau(deepcopy(players))
end = time.perf_counter()
logs_hs = pd.concat(logs).reset_index().drop("index", axis=1)
print(end - beginning)

""" Sauvegarde des logs"""
os.remove('logs_games.pickle')
with open('logs_games.pickle', 'wb') as f:
    pickle.dump(logs_hs, f)

