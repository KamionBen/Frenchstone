""" C'est ici qu'on nettoie les logs bruts pour les rendre ingérables par un modèle"""

""" Imports """
import pandas as pd
import numpy as np
import pickle

""" Lecture du fichier de logs """
with open('logs_games.pickle', 'rb') as f:
    raw_logs = pickle.load(f)

dict_actions = {
  "passer_tour": 0,
  "jouer_carte": 1,
  "attaquer": 2
}

""" Modification de la colonne 'cible' qui retourne un entier en fonction de la cible : """
# 0 --> héros          1-7 --> serviteur correspondant
conditions = [
              raw_logs.cible == "heros", raw_logs.cible == raw_logs.serv1_adv, raw_logs.cible == raw_logs.serv2_adv,
              raw_logs.cible == raw_logs.serv3_adv, raw_logs.cible == raw_logs.serv4_adv, raw_logs.cible == raw_logs.serv5_adv,
              raw_logs.cible == raw_logs.serv6_adv, raw_logs.cible == raw_logs.serv7_adv
              ]
choices = [0, 1, 2, 3, 4, 5, 6, 7]
raw_logs['cible'] = np.select(conditions, choices, default=-99)

"""Modification de la colonne 'actions' pour être un entier """
raw_logs = raw_logs.replace({"action": dict_actions})
## Si l'action est une attaque, on incrémente l'action de la cible visée
raw_logs['action'] = np.where(raw_logs['action'] == 2, raw_logs['action'] + raw_logs['cible'], raw_logs['action'])


""" Sélection des colonnes nécessaires à l'entraînement """
""" Colonnes d'état """
columns_actual_state = ["mana_dispo_j", "mana_max_j",
                "mana_max_adv", "surcharge_j", "surcharge_adv", "pv_j", "pv_adv", "pv_max_j", "pv_max_adv", "nbre_cartes_j",
                "nbre_cartes_adv", "action", "victoire"]

for i in range(10):
    columns_actual_state.append(f"carte_en_main{i + 1}_cost")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_j")
    columns_actual_state.append(f"pv_serv{i + 1}_j")
    columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_adv")
    columns_actual_state.append(f"pv_serv{i + 1}_adv")


df_state = raw_logs[columns_actual_state]

# print(df_state.loc[0:100].to_string())

with open('logs_refined.pickle', 'wb') as f:
    pickle.dump(df_state, f)

with open('logs_refined_light.pickle', 'wb') as f:
    pickle.dump(df_state.loc[0:100], f)
