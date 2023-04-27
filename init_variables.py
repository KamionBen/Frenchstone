import pandas as pd

columns_logs = ["action", "carte_jouee", "attaquant", "attaquant_atq", "attaquant_pv", "cible", "cible_atq", "cible_pv",
                "classe_j", "classe_adv", "mana_dispo_j", "mana_max_j",
                "mana_max_adv", "surcharge_j", "surcharge_adv", "pv_j", "pv_adv", "pv_max_j", "pv_max_adv", "nbre_cartes_j",
                "nbre_cartes_adv", "dispo_ph_j", "cout_ph_j", "serv1_j", "atq_serv1_j", "pv_serv1_j", "serv2_j", "atq_serv2_j", "pv_serv2_j",
                "serv3_j", "atq_serv3_j", "pv_serv3_j", "serv4_j", "atq_serv4_j", "pv_serv4_j", "serv5_j", "atq_serv5_j", "pv_serv5_j",
                "serv6_j", "atq_serv6_j", "pv_serv6_j", "serv7_j", "atq_serv7_j", "pv_serv7_j",
                "serv1_adv", "atq_serv1_adv", "pv_serv1_adv", "serv2_adv", "atq_serv2_adv", "pv_serv2_adv",
                "serv3_adv", "atq_serv3_adv", "pv_serv3_adv", "serv4_adv", "atq_serv4_adv", "pv_serv4_adv", "serv5_adv", "atq_serv5_adv", "pv_serv5_adv",
                "serv6_adv", "atq_serv6_adv", "pv_serv6_adv", "serv7_adv", "atq_serv7_adv", "pv_serv7_adv",
                "arme_j", "arme_adv", "attaque_j", "attaque_adv", "durabilite_arme_j", "durabilite_arme_adv",
                "pseudo_j", "pseudo_adv", "victoire"
                ]

logs_hs = pd.DataFrame(columns = columns_logs)
