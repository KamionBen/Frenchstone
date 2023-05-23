from pandas.core.frame import DataFrame
import pygame
from pygame.locals import *

from modelisation.Entities import *
from time import sleep
import pickle


CARD_POOL = get_cards_data("modelisation/cards.json")


def import_log(file: str) -> DataFrame:
    with open(file, 'rb') as f:
        return pickle.load(f)


def get_players_fromlog(log: DataFrame, index: int) -> dict:
    """ Return (current_player, other_player) from a log line """
    logline = log.to_dict(orient="index")[index]
    cleaned = {k: v for k, v in logline.items() if v not in ('',-99)}  # Just for visibility
    print(cleaned)

    """ CREATE THE INSTANCES """
    current_player = Player(logline['pseudo_j'], logline['classe_j'])
    other_player = Player(logline['pseudo_adv'], logline['classe_adv'])

    """ SET THE MANA """
    other_player.mana_max = logline['mana_max_adv']
    other_player.mana_reset()
    current_player.mana_max = logline['mana_max_j']
    current_player.mana = logline['mana_dispo_j']

    return {current_player.name: current_player, other_player.name: other_player}


def MainScreen(logfile: str):
    game_log = import_log(logfile)

    total_turn = len(game_log)

    first_pass = game_log.to_dict(orient='index')[0]
    p1, p2 = first_pass['pseudo_j'], first_pass['pseudo_adv']

    pygame.init()
    RES = 1280, 720
    screen = pygame.display.set_mode(RES)
    clock = pygame.time.Clock()

    default_font = {i: pygame.font.Font(None, i) for i in range(16, 72, 2)}

    current_turn = 0
    players_inst = get_players_fromlog(game_log, current_turn)
    debug = game_log.to_dict(orient='index')[current_turn]
    debug = {k: v for k, v in debug.items() if v not in ('', -99)}

    game_on = True
    while game_on:
        """ EVENT LOOP """
        for event in pygame.event.get():
            if event.type == QUIT:
                game_on = False
            if event.type == MOUSEWHEEL:
                current_turn -= event.y
                if current_turn < 0:
                    current_turn = 0
                if current_turn > total_turn:
                    current_turn = total_turn
                players_inst = get_players_fromlog(game_log, current_turn)
                debug = game_log.to_dict(orient='index')[current_turn]
                debug = {k: v for k, v in debug.items() if v not in ('', -99)}

        """ DISPLAY LOOP """
        clock.tick(60)
        screen.fill('black')

        p1_inst = players_inst[p1]
        p2_inst = players_inst[p2]

        p1_name = default_font[24].render(p1_inst.name, True, 'white')
        screen.blit(p1_name, (600, 700))

        p2_name = default_font[24].render(p2_inst.name, True, 'white')
        screen.blit(p2_name, (600, 60))

        # TURNS
        margin, span, size = 70, 12, 16
        for t in range(total_turn):
            if t == current_turn:
                screen.blit(default_font[size].render(str(t), True, 'green'), (5, margin + t * span))
            else:
                screen.blit(default_font[size].render(str(t), True, 'white'), (5, margin + t * span))

        # DEBUG
        debug_str = [str(debug)]
        while len(debug_str[-1]) > 230:
            temp = debug_str[-1][230:]
            debug_str[-1] = debug_str[-1][:230]
            debug_str.append(temp)

        for y, elt in enumerate(debug_str):
            debug_txt = default_font[16].render(elt, True, 'white')
            screen.blit(debug_txt, (10, 5+y*15))

        pygame.display.flip()


if __name__ == '__main__':
    MainScreen('modelisation/logs_games.pickle')
