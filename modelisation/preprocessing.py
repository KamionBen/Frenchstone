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

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_j")
    columns_actual_state.append(f"pv_serv{i + 1}_j")
    columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_adv")
    columns_actual_state.append(f"pv_serv{i + 1}_adv")


""" Colonne de récompense """
column_reward = ["victoire"]

""" Colonnes d'action """
columns_action = ["action"]

df_state = raw_logs[columns_actual_state]
df_action = raw_logs[columns_action]
df_reward = raw_logs[column_reward]

print(df_reward.sum().values[0])
print(df_state.shape[0])
print(df_reward.sum().values[0]/df_state.shape[0])
