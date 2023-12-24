import time
from engine import *
import gc
import functools


total_actions, estimated_actions = 0, 1

def minimax(state, alpha=-10000, depth=0, best_action=-99, max_depth=4, exploration_toll=2.3, estimate=False):
    gc.disable()
    global total_actions, estimated_actions
    if total_actions > 8000:
        return alpha, best_action

    base_advantage = calc_advantage_minmax(state)
    legal_actions = np.array(generate_legal_vector_test(state), dtype=bool)
    legal_actions = [i for i in range(len(legal_actions)) if legal_actions[i]]
    if len(legal_actions) == 0:
        player = state.players[0]
        adv = state.players[1]
        print(player.health, adv.health)
        print(player.servants, adv.servants)
        print(player.mana)
        print(player.hand)

    state_saved = pickle.dumps(state, -1)

    possible_new_states = np.array([
         (action, Orchestrator().tour_ia_minmax(pickle.loads(state_saved), [], action, False)[0], 0) for action in legal_actions
    ])

    first_estimate = [calc_advantage_minmax(possible_new_states[i][1]) for i in range(len(possible_new_states))]

    if len(possible_new_states) != 0 and possible_new_states[0][0] == 0:
        first_estimate[0] = base_advantage
    first_estimate_sorted_values = sorted(first_estimate, reverse=True)
    first_estimate_sorted = np.array(first_estimate).argsort()[::-1]
    if depth != 0 and max_depth != 10:
        baseline = [x[2] for x in possible_new_states if x[0] == 0][0]
        possible_new_states = [x for x in possible_new_states if x[2] > baseline]
    to_simulate = max(round(min(30, len(possible_new_states)) / (pow(exploration_toll, depth))), 1)

    if not (251 <= min(legal_actions) and max(legal_actions) <= 254):
        if depth != 0:
            possible_new_states = possible_new_states[first_estimate_sorted[:to_simulate]]
        else:
            possible_new_states = possible_new_states[first_estimate_sorted[:min(25, len(possible_new_states))]]

    for i in range(len(possible_new_states)):
        if possible_new_states[i][0]:
            possible_new_states[i][2] = first_estimate_sorted_values[i]
        else:
            possible_new_states[i][2] = base_advantage

    ### Dédoublonnage
    possible_new_states = list(dict((x[2], x) for x in possible_new_states).values())
    # print(depth, to_simulate, alpha, base_advantage, [(x[0], x[2]) for x in possible_new_states])
    # print('------------------------------------')

    if estimate:
        estimated_actions *= len(possible_new_states)
        if possible_new_states[0][0] != 0:
            try:
                minimax(possible_new_states[0][1], alpha, depth + 1, estimate=True)[0]
            except:
                return estimated_actions
        else:
            return estimated_actions


    gc.enable()

    for new_state in possible_new_states:
        total_actions += 1
        previous_reward = alpha

        """ On va chercher les feuilles de l'arbre pour en récuperer la valeur """
        if new_state[0] == 0 or depth == max_depth:
            alpha = max(alpha, new_state[2])
        else:
            alpha = minimax(new_state[1], alpha, depth+1, max_depth=max_depth, exploration_toll=exploration_toll)[0]

        """ On met à jour alpha si nécessaire """
        if alpha > previous_reward and depth == 0:
            best_action = new_state[0]
            if alpha == 10000:
                break
    return alpha, best_action


def return_best_action(plateau=None):
    player = plateau.players[0]
    adv = plateau.players[1]
    global total_actions, estimated_actions
    total_actions, estimated_actions = 0, 1
    potential_actions = minimax(plateau, estimate=True)
    if potential_actions <= 2000:
        max_reward, best_action = minimax(plateau, max_depth=10, exploration_toll=1, estimate=False)
    else:
        ratio_actions = potential_actions/2000
        depth_max = 3 if ratio_actions > 3 else 4 if ratio_actions > 2 else 5
        exp_toll = 1.75 + 0.5 * ratio_actions
        max_reward, best_action = minimax(plateau, max_depth=depth_max, exploration_toll=exp_toll, estimate=False)
    print("Total actions", total_actions)
    cible, attaquant, choix = None, None, None
    output_action = ""
    if best_action == 0:
        output_action = "Passer le tour"
    elif best_action < 171:
        output_action = f"Jouer carte - {player.hand[(best_action - 1) // 17]}"
        if (best_action - 1) % 17 == 0:
            pass
        elif (best_action - 1) % 17 == 1:
            cible = "Joueur"
        elif (best_action - 1) % 17 == 9:
            cible = "Adversaire"
        elif (best_action - 1) % 17 < 9:
            cible = player.servants[(best_action - 1) % 17 - 2].name
        else:
            cible = adv.servants[(best_action - 1) % 17 - 10].name
    elif 171 <= best_action < 235:
        output_action = "Attaquer"
        if (best_action - 171) // 8 == 0:
            attaquant = "Joueur"
        else:
            attaquant = player.servants[int((best_action - 171) // 8 - 1)]
        if (best_action - 171) % 8 == 0:
            cible = "Adversaire"
        else:
            cible = adv.servants[int((best_action - 171) % 8 - 1)]
    elif best_action < 251:
        output_action = "Pouvoir héroïque"
        if best_action == 235:
            cible = "Joueur"
        elif best_action == 243:
            cible = "Adversaire"
        elif best_action < 243:
            cible = player.servants[best_action - 236].name
        else:
            cible = adv.servants[best_action - 244].name
    elif best_action < 255:
        output_action = "Choix carte"
        if plateau.cards_chosen:
            choix = plateau.cards_chosen[0][best_action - 251].name
        elif plateau.cards_dragage:
            choix = plateau.cards_dragage[0][best_action - 251].name
        elif plateau.cards_entrave:
            choix = plateau.cards_entrave[0][best_action - 251].name
        elif plateau.cards_hands_to_deck:
            choix = plateau.cards_hands_to_deck[0][best_action - 251].name
        elif plateau.choix_des_armes:
            choix = plateau.choix_des_armes[0][best_action - 251].name
    elif best_action < 265:
        if "echangeable" in player.hand[best_action - 255].effects:
            output_action = "Echange"
        elif "forge" in player.hand[best_action - 255].effects:
            output_action = "Forge"
        cible = player.hand[best_action - 255].name
    elif best_action < 377:
        output_action = f"Lieu utilisé : {player.lieux[(best_action - 265) // 16].name}"
        if (best_action - 265) % 16 == 0:
            cible = "Joueur"
        elif (best_action - 265) % 16 < 8:
            cible = player.servants[(best_action - 266) % 16].name
        elif (best_action - 265) % 16 == 8:
            cible = "Adversaire"
        else:
            cible = adv.servants[(best_action - 274) % 16].name
    else:
        titans = [x for x in player.servants if "titan" in x.effects and x.effects["titan"][-1] == 1]
        output_action = f"Titan utilisé : {titans[(best_action - 377) // 3].name}"
        choix = str((best_action - 377) % 3)
    print('                                       ')
    print(f"Joueur : {player.name}")
    print(f"Avantage estimé : {max_reward}")
    print(f"Meilleure action : {output_action}")
    if choix is not None:
        print(f"Choix : {choix}")
    if attaquant is not None:
        if type(attaquant) == str:
            print(f"Attaquant : {attaquant}")
        else:
            print(f"Attaquant : {attaquant.name} ({attaquant.attack, attaquant.health})")
    if cible is not None:
        if type(cible) == str:
            print(f"Attaquant : {cible}")
        else:
            print(f"Attaquant : {cible.name} ({cible.attack, cible.health})")
    return max_reward, best_action
