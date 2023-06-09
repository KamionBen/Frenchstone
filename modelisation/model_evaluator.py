## Lanceur de la simulation Hearthstone

# Import & Utils
from engine import *
from Entities import *
import matplotlib.pyplot as plt
from timeit import default_timer as timer


def generate_perf_plot(nb_games, nb_models):
    score_new_ia = {}
    classes_heros = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                     "Chevalier de la mort", "Prêtre"]
    for classe in classes_heros:
        score_new_ia[classe] = []
    for i in range(60, nb_models + 60):
        for classe in classes_heros:
            players = [Player("OldIA", "Mage"), Player("NewIA", classe)]
            score_oldia = Orchestrator().generate_oldia_game(nb_games, tf.compat.v2.saved_model.load(
                f"frenchstone_agent_v0.04-a-{i * 1000}"), players, False)
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
    plt.plot(steps, moyenne_model, label='moyenne')
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
players = [Player("OldIA", "Druide"), Player("NewIA", "Chasseur")]
score_oldia = Orchestrator().generate_oldia_game(100, tf.compat.v2.saved_model.load("frenchstone_agent_v0.04-a-14000"), players, False)
""" Affichage des résultats """
# print(logs_hs_oldia.to_string())
print(score_oldia)
""" Sauvegarde des logs"""
# os.remove('logs_games.pickle')
# with open('logs_games.pickle', 'wb') as f:
#     pickle.dump(logs_hs_oldia, f)
# generate_perf_plot(10, 5)


# """ Générateur de parties avec le modèle contre lui-même """
# players = [Player("Pascal", "Mage"), Player("Joseph", "Chasseur")]
# logs_hs_ia, score_ia = Orchestrator().generate_ia_game(10000, players, random_toll=0.2)




if __name__ == "__main__":
    start = timer()
    generate_perf_plot(10, 5)
    print("with GPU:", timer() - start)



