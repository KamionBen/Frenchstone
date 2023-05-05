from Entities import *
from random import shuffle
from init_variables import *
from copy import deepcopy


""" TO DO """
# Le mana n'est pas mis à jour après avoir joué une carte
# Les dégâts de fatigue ne sont pas loggés

class Plateau:
    def __init__(self, players=()):
        """ Décrit exhaustivement le plateau de jeu """
        class_files = {'Chasseur': 'test_deck.csv',
                       'Mage': 'test_deck.csv'}
        if players == ():
            self.players = [Player("Smaguy", 'Chasseur'), Player("Rupert", 'Mage')]

        else:
            self.players = list(players)

        for player in self.players:
            player.set_deck(class_files[player.classe])

        shuffle(self.players)

        """ Mélange des decks et tirage de la main de départ """
        for player in self.players:
            player.start_game()

        """ Gestion du mana """
        """ Le premier joueur démarre son tour à l'initialisation """
        self.players[0].start_turn()

        """ Tour de jeu """
        self.game_turn = 0  # Décompte des tours
        self.game_on = True
        self.winner = None

    def tour_suivant(self):
        """ Met à jour le plateau à la fin du tour d'un joueur """
        self.game_turn += 1
        self.players.reverse()

        self.players[0].start_turn()

    def update(self):
        """ Vérifie les serviteurs morts et les pdv des joueurs """
        for player in self.players:
            if player.hero.is_dead():
                self.game_on = False
                for winner in self.players:
                    if winner != player:
                        self.winner = winner
            for servant in player.servants:
                if servant.is_dead():
                    player.servants.remove(servant)

    def get_targets(self, serviteur):
        if serviteur not in self.players[0].servants:
            raise KeyError("Le serviteur choisi n'est pas sur le plateau du joueur actif")
        else:
            adv = self.players[1]
            targets = []
            if "Ruée" in serviteur.get_effects():
                if serviteur.effects["Ruée"].active is False:
                    targets.append(adv.hero)
            else:
                targets.append(adv.hero)
            for carte in adv.servants:
                targets.append(carte)
        return targets

    def get_gamestate(self) -> dict:
        player = self.players[0]
        adv = self.players[1]

        # On assigne les actions de base avant les actions spécifiques au choix
        """ BOARD """
        action_line = {"action": "",
                       "carte_jouee": "",
                       "attaquant": "", "attaquant_atq": "", "attaquant_pv": "",
                       "cible": "", "cible_atq": "", "cible_pv": "",
                       "classe_j": player.classe, "classe_adv": adv.classe,
                       "mana_dispo_j": player.mana, "mana_max_j": player.mana_max,
                       "mana_max_adv": adv.mana_max,
                       "surcharge_j": player.surcharge, "surcharge_adv": adv.surcharge,
                       "pv_j": player.hero.health, "pv_adv": adv.hero.health,
                       "pv_max_j": player.hero.base_health, "pv_max_adv": adv.hero.base_health,
                       "nbre_cartes_j": len(player.hand),
                       "nbre_cartes_adv": len(adv.hand),
                       "dispo_ph_j": player.hero.dispo_pouvoir,
                       "cout_ph_j": player.hero.cout_pouvoir,
                       "arme_j": player.hero.weapon,
                       "arme_adv": adv.hero.weapon,
                       "attaque_j": player.hero.attack,
                       "attaque_adv": adv.hero.attack,
                       "durabilite_arme_j": player.hero.weapon.durability if player.hero.weapon is not None else 0,
                       "durabilite_arme_adv": adv.hero.weapon.durability if player.hero.weapon is not None else 0,
                       "pseudo_j": player.name,
                       "pseudo_adv": adv.name,
                       "victoire": 0}
        """ HAND """
        cartes_en_main = {i: carte.id for i, carte in enumerate(player.hand)}
        for i in range(10):
            if i in cartes_en_main.keys():
                action_line[f"carte_en_main{i + 1}"] = cartes_en_main[i]
            else:
                action_line[f"carte_en_main{i + 1}"] = -99

        """ SERVANTS """
        player_servants = {i: carte.id for i, carte in enumerate(player.servants)}
        player_servants_atk = {i: carte.attack for i, carte in enumerate(player.servants)}
        player_servants_pv = {i: carte.health for i, carte in enumerate(player.servants)}
        for i in range(7):
            if i in player_servants.keys():
                action_line[f"serv{i + 1}_j"] = player_servants[i]
                action_line[f"atq_serv{i + 1}_j"] = player_servants_atk[i]
                action_line[f"pv_serv{i + 1}_j"] = player_servants_pv[i]
            else:
                action_line[f"serv{i + 1}_j"] = -99
                action_line[f"atq_serv{i + 1}_j"] = -99
                action_line[f"pv_serv{i + 1}_j"] = -99

        adv_servants = {i: carte.id for i, carte in enumerate(adv.servants)}
        adv_servants_atk = {i: carte.attack for i, carte in enumerate(adv.servants)}
        adv_servants_pv = {i: carte.health for i, carte in enumerate(adv.servants)}
        for i in range(7):
            if i in adv_servants.keys():
                action_line[f"serv{i + 1}_adv"] = adv_servants[i]
                action_line[f"atq_serv{i + 1}_adv"] = adv_servants_atk[i]
                action_line[f"pv_serv{i + 1}_adv"] = adv_servants_pv[i]
            else:
                action_line[f"serv{i + 1}_adv"] = -99
                action_line[f"atq_serv{i + 1}_adv"] = -99
                action_line[f"pv_serv{i + 1}_adv"] = -99

        return action_line


class TourEnCours:
    """Classe prenant en entrée un plateau de jeu et permettant d'effectuer toutes les actions possibles dessus."""
    def __init__(self, plateau):
        self.plt = plateau

    def jouer_carte(self, carte):
        """ Action de poser une carte depuis la main du joueur dont c'est le tour.
        Le plateau est mis à jour en conséquence """
        player = self.plt.players[0]
        if carte.cost <= player.mana:
            if carte.type.lower() == "sort":
                player.hand.remove(carte)
                player.mana_spend(carte.cost)
            elif carte.type.lower() == "serviteur":
                if len(player.servants) < 7:
                    player.hand.remove(carte)
                    player.servants.add(carte)
                    player.mana_spend(carte.cost)
                else:
                    raise PermissionError("Nombre maximum de serviteurs atteint")
        else:
            raise PermissionError("Carte plus chère que la mana du joueur")

    def attaquer(self, attaquant, cible):
        """ Action d'attaquer avec un serviteur ou son héros une cible adverse (serviteur ou héros aussi) """
        if type(attaquant) in (Hero, Card) and type(cible) in (Hero, Card):
            cible.damage(attaquant.attack)
            attaquant.damage(cible.attack)
            self.plt.update()
            attaquant.remaining_atk -= 1
        else:
            raise TypeError

    def fin_du_tour(self):
        self.plt.tour_suivant()


class RandomOrchestrator:
    def tour_au_hasard(self, plateau, logs):
        """ On génère une action aléatoire et on la fait jouer par la classe Tourencours """
        player = plateau.players[0]
        adv = plateau.players[1]
        tour_en_cours = TourEnCours(plateau)

        action_line = plateau.get_gamestate()

        """ ON CHOISIT L'ACTION """
        action_possible = ["Passer_tour"]
        for carte in player.servants:
            if carte.attack > 0 and carte.remaining_atk > 0:
                if len(tour_en_cours.plt.get_targets(carte)) > 0:
                    action_possible.append(carte)
        for carte in player.hand:
            if carte.cost <= player.mana and not (carte.type.lower() == "serviteur" and len(player.servants) == 7):
                action_possible.append(carte)
        if player.hero.attack > 0:
            action_possible.append(player.hero)

        action = choice(action_possible)
        if action == "Passer_tour":
            action_line["action"] = "passer_tour"
            logs.loc[len(logs)] = action_line
            tour_en_cours.fin_du_tour()

        elif action in player.hand:
            """ La carte est jouée depuis la main """
            action_line["action"] = "jouer_carte"
            action_line["carte_jouee"] = action.id  # name ou id ?
            logs.loc[len(logs)] = action_line
            # player.hand.remove(action)
            # player.servants.add(action)
            tour_en_cours.jouer_carte(action)

        elif action in player.servants or type(action) == Hero:
            provocation = False
            for carte in adv.servants:
                if "provocation" in carte.get_effects():
                    provocation = True

            targets = []
            if provocation:
                for carte in adv.servants:
                    if "provocation" in carte.get_effects():
                        targets.append(carte)
            else:
                if "Ruée" in action.get_effects():
                    if action.effects["Ruée"].active is False:
                        targets.append(adv.hero)
                else:
                    targets.append(adv.hero)
                for carte in adv.servants:
                    targets.append(carte)



            target = choice(targets)

            action_line["action"] = "attaquer"
            action_line["attaquant"] = action.id if type(action) is Card else "heros"
            action_line["attaquant_atq"] = action.attack
            action_line["attaquant_pv"] = action.health
            action_line["cible"] = target.id if type(target) is Card else "heros"
            action_line["cible_atq"] = target.attack
            action_line["cible_pv"] = target.health

            logs.loc[len(logs)] = action_line

            tour_en_cours.attaquer(action, target)
        plateau.update()
        return plateau

    """ Génère un nombre donné de parties et créé les logs associés"""
    def generate_game(self, nb_games, players=()):
        logs_hs = pd.DataFrame(columns=columns_logs)
        i = 0
        scores = {}
        """ On simule nb_games parties """
        while i < nb_games:
            logs_inter = pd.DataFrame(columns=columns_logs)
            mon_plateau = Plateau(players)
            while mon_plateau.game_on:
                mon_plateau = RandomOrchestrator().tour_au_hasard(mon_plateau, logs_inter)

            # Actions de fin de partie
            winner = mon_plateau.winner
            logs_inter["victoire"] = np.where(logs_inter['pseudo_j'] == winner.name, 1, -1)
            logs_hs = pd.concat([logs_hs, logs_inter]).reset_index().drop('index', axis=1)
            if winner.name in scores.keys():
                scores[winner.name] += 1
            else:
                scores[winner.name] = 1
            i += 1
        return logs_hs, list(scores.values())


if __name__ == '__main__':
    logs_hs, scores = RandomOrchestrator().generate_game(10)
    print(scores)

