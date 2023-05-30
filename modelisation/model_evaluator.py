## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *
from Entities import *
import matplotlib.pyplot as plt

def generate_perf_plot(nb_games, nb_models):
    score_new_ia = {}
    classes_heros = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                     "Chevalier de la mort"]
    for classe in classes_heros:
        score_new_ia[classe] = []
    for i in range(1, nb_models + 1):
        for classe in classes_heros:
            players = [Player("OldIA", "Mage"), Player("NewIA", classe)]
            logs_hs_oldia, score_oldia = Orchestrator().generate_oldia_game(nb_games, tf.compat.v2.saved_model.load(
                f"frenchstone_agent_v0.02-a-{i * 1000}"), players)
            try:
                score_new_ia[classe].append(score_oldia['NewIA'])
            except:
                score_new_ia[classe].append(0)
        print(i)
    moyenne_model = []
    for i in range(nb_models):
        moyenne_model.append(0)
        for classe in classes_heros:
            moyenne_model[i] += score_new_ia[classe][i]/len(classes_heros)

    steps = range(1, nb_models + 1, 1)
    for classe in classes_heros:
        plt.plot(steps, score_new_ia[classe], label=classe)
    plt.plot(steps, moyenne_model, label = 'moyenne')
    plt.legend(loc='upper left')
    plt.ylabel('Games won')
    plt.xlabel('Iteration of model')
    plt.ylim(bottom=0)
    plt.ylim(top=nb_games)
    plt.show()


""" Générateur de parties aléatoires """
# players = [Player("Pascal", "Paladin"), Player("Joseph", "Voleur")]
# logs_hs, score = Orchestrator().generate_random_game(10, players)

""" Générateur de partie random vs ia """
# players = [Player("Random", "Mage"), Player("IA", "Chasseur")]
# logs_hs_randomia, score_randomia = Orchestrator().generate_randomvsia_game(1, players)
# logs_hs_randomia['id_partie'] = logs_hs_randomia['id_partie'] + 10000

""" Générateur de parties avec le modèle contre son prédecesseur """
# players = [Player("OldIA", "Mage"), Player("NewIA", "Paladin")]
# logs_hs_oldia, score_oldia = Orchestrator().generate_oldia_game(100, tf.compat.v2.saved_model.load("frenchstone_agent_v0.02-a-15000"), players)
generate_perf_plot(100, 16)


# """ Générateur de parties avec le modèle contre lui-même """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs_ia, score_ia = Orchestrator().generate_ia_game(10000, players, random_toll=0.2)

# """ Affichage des résultats """
# print(logs_hs_oldia.to_string())
# print(score_randomia)
# print(score_oldia)

""" Sauvegarde des logs"""
# os.remove('logs_games.pickle')
# with open('logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs_oldia, f)


