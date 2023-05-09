""" C'est ici qu'on nettoie les logs bruts pour les rendre ingérables par un modèle"""

""" Imports """
import pandas as pd
import numpy as np
import pickle

""" Lecture du fichier de logs """
with open('logs_games.pickle', 'rb') as f:
    raw_logs = pickle.load(f)

""" Sélection des colonnes nécessaires à l'entraînement """
""" Colonnes d'état """
columns_actual_state = ["mana_dispo_j", "mana_max_j",
                "mana_max_adv", "surcharge_j", "surcharge_adv", "pv_j", "pv_adv", "pv_max_j", "pv_max_adv", "nbre_cartes_j",
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
columns_actual_state.append(f"action")
columns_actual_state.append(f"victoire")

dict_actions = {
  "passer_tour": 0,
  "jouer_carte": 1,
  "attaquer": 2
}

df_state = raw_logs[columns_actual_state]
df_state = df_state.replace({"action": dict_actions})

with open('logs_refined.pickle', 'wb') as f:
    pickle.dump(df_state, f)

with open('logs_refined_light.pickle', 'wb') as f:
    pickle.dump(df_state.loc[0:100], f)
