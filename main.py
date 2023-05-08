## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *

# total_games = 50000

# """ Générateur de parties aléatoires """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs, score = Orchestrator().generate_random_game(15000, players)
#
# """ Générateur de partie random vs ia """
# players = [Player("Random", "Mage"), Player("IA", "Chasseur")]
# logs_hs_randomia, score_randomia = Orchestrator().generate_randomvsia_game(35000, players)

""" Générateur de parties avec le modèle """
players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
logs_hs_ia, score_ia = Orchestrator().generate_ia_game(1, players)

# # """ Concaténation des différentes sources """
# logs_hs = pd.concat([logs_hs, logs_hs_randomia, logs_hs_ia]).reset_index().drop('index', axis=1)

""" Affichage des résultats """
print(logs_hs_ia.to_string())
# print(score_randomia)



""" Sauvegarde des logs """
# os.remove('modelisation/logs_games.pickle')
# with open('modelisation/logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs, f)



""" Tests de chargement de l'agent """

#
# step_type = tf.convert_to_tensor([0], dtype=tf.int32, name='step_type')
# reward = tf.convert_to_tensor([0], dtype=tf.float32, name='reward')
# discount = tf.convert_to_tensor([1], dtype=tf.float32, name='discount')
# for i in range(0, 200):
#     vecteur_test = df_state.drop(['victoire', 'action'], axis=1).loc[i]
#     observations = tf.convert_to_tensor(vecteur_test.values.reshape(1, 1, -1), dtype=tf.int32, name='observations')
#     timestep3 = ts.TimeStep(step_type, reward, discount, observations)
#     result = saved_policy.action(timestep3, policy_state)
#     action = dict_actions[int(result.action)]
#     if action == "jouer_carte":
#         compteur = 0
#         for j in range(10):
#             if vecteur_test[f"carte_en_main{j+1}_cost"] > vecteur_test["mana_dispo_j"] or vecteur_test[f"carte_en_main{j+1}_cost"] == -99:
#                 compteur += 1
#         if compteur == 10:
#             print(i)
#             print(action)
#             print(vecteur_test)
#     print('--------------------------------------------------------------------------------------------------')
