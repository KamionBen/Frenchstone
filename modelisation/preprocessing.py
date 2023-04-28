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
                "nbre_cartes_adv", "dispo_ph_j", "cout_ph_j", "atq_serv1_j", "pv_serv1_j", "atq_serv2_j", "pv_serv2_j",
                "atq_serv3_j", "pv_serv3_j", "atq_serv4_j", "pv_serv4_j", "atq_serv5_j", "pv_serv5_j",
                "atq_serv6_j", "pv_serv6_j", "atq_serv7_j", "pv_serv7_j",
                "atq_serv1_adv", "pv_serv1_adv", "atq_serv2_adv", "pv_serv2_adv",
                "atq_serv3_adv", "pv_serv3_adv", "atq_serv4_adv", "pv_serv4_adv", "atq_serv5_adv", "pv_serv5_adv",
                "atq_serv6_adv", "pv_serv6_adv", "atq_serv7_adv", "pv_serv7_adv",
                "arme_j", "arme_adv", "attaque_j", "attaque_adv", "durabilite_arme_j", "durabilite_arme_adv"
                ]

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
