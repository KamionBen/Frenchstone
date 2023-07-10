import time
from engine import *

players = [Player("NewIA", "Chevalier de la mort"), Player("OldIA", "Druide")]
plateau_depart = Plateau(pickle.loads(pickle.dumps(players, -1)))


def generate_legal_vector_test(state):
    """ Gestion des actions légales """
    legal_actions = [False] * 315
    player = state.players[0]
    adv = state.players[1]
    
    """ Découverte """
    if state.cards_chosen or state.cards_dragage:
        legal_actions[0] = False
        for i in range(251, 251 + len(state.cards_chosen[0]) if state.cards_chosen else 251 + len(state.cards_dragage[0])):
            legal_actions[i] = True
        if state.cards_chosen and len(state.cards_chosen[0]) == 4 and state.cards_chosen[0][3] == "choix mystere":
            legal_actions[254] = True
        return legal_actions

    if state.cards_entrave:
        for i in range(251, 251 + len(state.cards_entrave[0])):
            legal_actions[i] = True
        return legal_actions

    legal_actions[0] = True
    gamestate = state.get_gamestate()

    """ Quelles cartes peut-on jouer ? Et qur quelles cibles le cas échéant ? """
    for i in range(len(player.hand)):
        if "reduc" in player.hand[i].effects and "self" in player.hand[i].effects["reduc"]:
            if "total_serv" in player.hand[i].effects["reduc"]:
                player.hand[i].cost -= len(player.servants) + len(adv.servants)
        if player.hand[i].cost <= player.mana and "entrave" not in player.hand[i].effects:
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
                                if "if_attack_greater" in player.hand[i].effects["cri de guerre"][1] and [x for x in player.servants.cards + adv.servants.cards if x.attack >= player.hand[i].effects["cri de guerre"][1][5]]:
                                    for j in range(len(player.servants)):
                                        if player.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5] and player.servants[j] != player.hand[i]:
                                            legal_actions[17 * i + j + 3] = True
                                    for j in range(len(adv.servants)):
                                        if adv.servants[j].attack >= player.hand[i].effects["cri de guerre"][1][5]:
                                            legal_actions[17 * i + j + 11] = True
                                else:
                                    legal_actions[17 * i + 1] = True


                        else:
                            legal_actions[17 * i + 1] = True
                    elif "tous" in player.hand[i].effects["cri de guerre"][1]:
                        if "ennemi" in player.hand[i].effects["cri de guerre"][1]:
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
                                if "if_weapon" in player.hand[i].effects["cri de guerre"][1] and player.hero.weapon is not None \
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
                if "ciblage" in player.hand[i].effects:
                    if "serviteur" in player.hand[i].effects["ciblage"]:
                        if "ennemi" in player.hand[i].effects["ciblage"]:
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                    legal_actions[17 * i + j + 11] = True
                        elif "tous" in player.hand[i].effects["ciblage"]:
                            if "if_rale_agonie" in player.hand[i].effects["ciblage"]:
                                for j in range(len(player.servants)):
                                    if "rale d'agonie" in player.servants[j].effects and "inciblable" not in player.servants[j].effects:
                                        legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                        if "rale d'agonie" in adv.servants[j].effects:
                                            legal_actions[17 * i + j + 11] = True
                            elif "Mort-vivant" in player.hand[i].effects["ciblage"]:
                                for j in range(len(player.servants)):
                                    if "Mort-vivant" in player.servants[j].genre and "inciblable" not in player.servants[j].effects:
                                        legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                        if "Mort-vivant" in adv.servants[j].genre:
                                            legal_actions[17 * i + j + 11] = True
                            else:
                                for j in range(len(player.servants)):
                                    if "inciblable" not in player.servants[j].effects:
                                        legal_actions[17 * i + j + 3] = True
                                for j in range(len(adv.servants)):
                                    if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                        legal_actions[17 * i + j + 11] = True
                    elif "tous" in player.hand[i].effects["ciblage"]:
                        if "ennemi" in player.hand[i].effects["ciblage"]:
                            legal_actions[17 * i + 10] = True
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                    legal_actions[17 * i + j + 11] = True
                        else:
                            legal_actions[17 * i + 2] = True
                            legal_actions[17 * i + 10] = True
                            for j in range(len(player.servants)):
                                if "inciblable" not in player.servants[j].effects:
                                    legal_actions[17 * i + j + 3] = True
                            for j in range(len(adv.servants)):
                                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects and "inciblable" not in adv.servants[j].effects:
                                    legal_actions[17 * i + j + 11] = True
                else:
                    legal_actions[17 * i + 1] = True
            elif player.hand[i].type.lower() == "lieu" and len(player.servants) + len(player.lieux) < 7:
                legal_actions[17 * i + 1] = True
            elif player.hand[i].type.lower() == "arme":
                legal_actions[17 * i + 1] = True

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    is_provoc = False
    for j in range(len(adv.servants)):
        if "provocation" in adv.servants[j].effects:
            is_provoc = True
            break
    """ Notre héros peut attaquer """
    if player.hero.remaining_atk > 0 and player.hero.attack > 0:
        if not is_provoc:
            legal_actions[171] = True
        for j in range(len(adv.servants)):
            if not is_provoc:
                if "camouflage" not in adv.servants[j].effects and "en sommeil" not in adv.servants[j].effects:
                    legal_actions[171 + j + 1] = True
            else:
                if "provocation" in adv.servants[j].effects:
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

    """ Pouvoir héroïque """
    if player.hero.dispo_pouvoir and player.hero.cout_pouvoir_temp <= player.mana:
        targets = state.targets_hp()
        if player.hero in targets:
            legal_actions[235] = True
        if adv.hero in targets:
            legal_actions[243] = True
        if len(targets) >= 2:
            for i in range(len(player.servants)):
                if player.servants[i] in targets:
                    legal_actions[236 + i] = True
            for i in range(len(adv.servants)):
                if adv.servants[i] in targets and not list({"camouflage", "en sommeil", "inciblable"} and set(adv.servants[i].effects)):
                    legal_actions[244 + i] = True

    """ Mot-clé échangeable """
    for i in range(len(player.hand)):
        if player.mana >= 1 and "echangeable" in player.hand[i].effects:
            legal_actions[255 + i] = True

    """ Lieux """
    for i in range(len(player.lieux)):
        if player.lieux[i].attack == 1 and "choisi" in player.lieux[i].effects["use"][1]:
            if player.lieux[i].effects["use"][1][0] == "tous":
                legal_actions[265 + 15 * i] = True
                legal_actions[265 + 15 * i + 7] = True
                for m in range(len(player.servants)):
                    legal_actions[265 + 15 * i + m + 1] = True
                for n in range(len(adv.servants)):
                    if "camouflage" not in adv.servants[n].effects:
                        legal_actions[265 + 15 * i + n + 8] = True
            elif player.lieux[i].effects["use"][1][0] == "serviteur":
                if player.lieux[i].effects["use"][1][1] == "allié":
                    if "conditional" in player.lieux[i].effects["use"][1]:
                        if "if_cadavre" in player.lieux[i].effects["use"][1] and player.cadavres >= player.lieux[i].effects["use"][1][-1]:
                            for m in range(len(player.servants)):
                                legal_actions[265 + 15 * i + m + 1] = True
    return legal_actions


def calc_advantage_minmax(state):
    player = state.players[0]
    adv = state.players[1]
    advantage = (len(player.hand) - len(adv.hand)) + 0.8 * (len(player.hand) / max(1, len(adv.hand)))
    for servant in player.servants:
        advantage += 1.5 * servant.attack + 1.5 * servant.health
        if "bouclier divin" in servant.effects:
            advantage += 1.5 * servant.attack
    for servant in adv.servants:
        advantage -= 1.5 * servant.attack + 1.5 * servant.health
        if "bouclier divin" in servant.effects:
            advantage -= 1.5 * servant.attack
    advantage += 0.25 * (pow(adv.hero.base_health - adv.hero.health, 1.3) - pow(player.hero.base_health - player.hero.health, 1.3))
    advantage += player.hero.attack
    advantage += 0.02 * player.cadavres
    advantage += 3 * len(player.lieux)
    if player.hero.health <= 0:
        return -500
    elif adv.hero.health <= 0:
        return 500

    return round(advantage, 2)

total_actions = 0
def minimax(state, alpha=-1000, depth=0, best_action=-99, max_depth=3, exploration_toll=3):

    global total_actions
    base_advantage = calc_advantage_minmax(state)
    legal_actions = np.array(generate_legal_vector_test(state), dtype=bool)
    legal_actions = [i for i in range(len(legal_actions)) if legal_actions[i]]
    state_saved = pickle.dumps(state, -1)

    possible_new_states = np.array([
        (action, Orchestrator().tour_ia_minmax(pickle.loads(state_saved), [], action, False)[0]) for action
        in legal_actions
    ])

    first_estimate = [calc_advantage_minmax(possible_new_states[i][1]) for i in range(len(possible_new_states))]
    first_estimate[0] = base_advantage
    first_estimate = np.array(first_estimate)
    if depth != 0:
        possible_new_states = possible_new_states[first_estimate.argsort()[-max(round(min(30, len(possible_new_states))/(pow(exploration_toll, depth))), 1):]]
    else:
        possible_new_states = possible_new_states[first_estimate.argsort()[-min(25, len(possible_new_states)):]]

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
                break

    if depth == 0:
        print(f"Total actions : {total_actions}")
        total_actions = 0

    return alpha, best_action



logs = []
beginning = time.perf_counter()
for i in range(3):
    print(i)
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------')
    while plateau_depart.game_on:
        max_reward, best_action = minimax(plateau_depart)
        plateau_depart, logs_inter = Orchestrator().tour_ia_minmax(plateau_depart, [], best_action)
        # print(f"Meilleure action : {best_action}   ---   Avantage estimé : {max_reward}")
        # print('----------------------------------------------')
        logs.append(pd.DataFrame(logs_inter))
    plateau_depart = Plateau(pickle.loads(pickle.dumps(players, -1)))
end = time.perf_counter()
logs_hs = pd.concat(logs).reset_index().drop("index", axis=1)
print(end - beginning)

""" Sauvegarde des logs"""
os.remove('logs_games.pickle')
with open('logs_games.pickle', 'wb') as f:
    pickle.dump(logs_hs, f)

