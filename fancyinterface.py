from pandas.core.frame import DataFrame
import pygame
from pygame.locals import *

from modelisation.Entities import *
import pickle
from random import shuffle

CARD_POOL = get_cards_data("modelisation/cards.json")




class CardSprite(pygame.sprite.Sprite):
    def __init__(self, cid=None):
        pygame.sprite.Sprite.__init__(self)
        self.cid = cid
        if cid is not None:
            obj = get_card(cid, CARD_POOL)
            self.name = obj.name
            self.pv_max = obj.health
            self.attaque_max = obj.base_attack
            self.description = obj.description

        self.attaque = None
        self.pv = None
        self.atq_remain = None

        self.color = (128,128,128)

        """ Card infos """
        self.width, self.height = 100, 150
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

    def update(self, logline=None):
        """ Update """
        """ Infos """
        on_board_id = None
        if logline is not None:
            for k, v in logline.items():
                if v == self.cid:
                    on_board_id = k

        if on_board_id is not None:
            self.attaque = logline['atq_'+on_board_id]
            self.pv = logline['pv_'+on_board_id]
            if on_board_id.split('_')[-1] == 'j':
                self.atq_remain = logline['atq_remain_'+on_board_id]

        border = 1
        self.image.fill(self.color)
        if logline is not None:
            if logline['carte_jouee'] == self.cid:
                self.image.fill('blue')  # TODO : Regarder la ligne de log précédente ...
            if logline['attaquant'] == self.cid:
                self.image.fill('red')

        pygame.draw.rect(self.image, (40, 40, 40), (border, border, self.width - border * 2, self.height - border * 2))
        if self.cid is not None:
            cid = default_font[16].render(f"{self.cid} | {on_board_id}", True, 'white')
            self.image.blit(cid, (5, 0))
            if logline['cible'] == self.cid:
                color = 'red'
            else:
                color = 'white'
            name = default_font[16].render(self.name, True, color)
            self.image.blit(name, (5,15))
            atq = default_font[32].render(str(self.attaque), True, 'white')
            self.image.blit(atq, (10, 120))
            descr = default_font[16].render(self.description, True, 'white')
            self.image.blit(descr, (10, 60))

            if self.pv < self.pv_max:
                color = 'red'
            else:
                color = 'white'
            pv = default_font[32].render(str(self.pv), True, color)
            self.image.blit(pv, (80, 120))


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, pseudo: str, color=None):
        pygame.sprite.Sprite.__init__(self)
        """ Player name """
        self.pseudo = pseudo
        self.position = None  # top or bottom

        """ Player infos """
        self.classe = None
        self.mana, self.mana_max = 0, 0
        self.color = color

        """ Hero """
        self.attaque = 0
        self.surcharge = 0
        self.pv, self.pv_max = 30, 30

        """ Cards """
        self.hand = pygame.sprite.Group()
        self.servant = pygame.sprite.Group()

        """ State """
        self.is_playing = False
        self.is_attacking = False
        self.gets_attacked = False

        """ Pygame variables """
        self.image = pygame.Surface([900, 330])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def set_position(self, pos: str):
        if pos not in ('top', 'bottom'):
            raise ValueError("Position must must be 'top' or 'bottom' ! (hehe)")
        else:
            self.position = pos
            self.rect.x = 180
        if pos == "top":
            self.rect.y = 20
        else:
            self.rect.y = 370

    def update(self, logline: dict):
        """ Update """
        """ Update infos """
        if self.pseudo == logline['pseudo_j']:
            role = 'j'
        else:
            role = 'adv'
        if role == 'j':
            self.mana = logline['mana_dispo_'+role]

        if logline['pseudo_j'] == self.pseudo:
            self.is_playing = True
        else:
            self.is_playing = False

        """ Infos """
        if self.classe is None:
            self.classe = logline['classe_'+role]

        self.mana_max = logline['mana_max_'+role]
        self.surcharge = logline['surcharge_'+role]
        self.pv, self.pv_max = logline['pv_'+role], logline['pv_max_'+role]
        self.attaque = logline['attaque_'+role]

        """ Cards """
        self.hand = pygame.sprite.Group(*[CardSprite() for x in range(logline['nbre_cartes_'+role])])
        self.hand.update()

        servant = [logline[f"serv{i+1}_{role}"] for i in range(7)]
        self.servant = pygame.sprite.Group(*[CardSprite(e) for e in servant if e != -99])
        self.servant.update(logline)

        """ Update sprite """
        self.image.fill(self.color)
        if logline['cible'] == 'heros' and not self.is_playing:
            color = 'red'
        elif logline['attaquant'] == 'heros' and self.is_playing:
            color = 'blue'
        else:
            color = 'white'

        pseudo = default_font[32].render(f"{self.pseudo} ({self.classe})", True, color)
        mana = default_font[24].render(f"Mana : {self.mana}/{self.mana_max}", True, 'white')
        pv = default_font[32].render(f"{self.attaque}      {self.pv}", True, 'white')

        border = 1
        pygame.draw.rect(self.image, (20, 20, 20), (border, border, 900-border*2, 330-border*2))
        if self.position == 'top':
            self.image.blit(pseudo, (450 - pseudo.get_width()/2, 10))
            self.image.blit(mana, (450 - mana.get_width() / 2, 40))
            self.image.blit(pv, (450 - pv.get_width() / 2, 70))
        else:
            self.image.blit(pseudo, (450 - pseudo.get_width() / 2, 300))
            self.image.blit(mana, (450 - mana.get_width() / 2, 270))
            self.image.blit(pv, (450 - pv.get_width() / 2, 240))

        """ Hand """
        height = {'top': 5, 'bottom': 250}
        for x, card in enumerate(self.hand):
            self.image.blit(card.image, (55 * x + 5, height[self.position]))

        """ Servants """
        gap = 5
        pos_x = 450 - ((100 + gap) * len(self.servant))/2
        height = {'top': 170, 'bottom': 10}
        for x, card in enumerate(self.servant):
            self.image.blit(card.image, (pos_x + (card.width + gap) * x, height[self.position]))


class FancyInterface:
    def __init__(self, log_filename, debug=False, resolution=(1280, 720)):
        """ Show the gamelog with a graphic interface """
        """ PYGAME INIT """
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption('FrenchStone')
        pygame.display.set_icon(pygame.image.load('images/icon.png'))
        self.clock = pygame.time.Clock()

        global default_font
        default_font = {i: pygame.font.Font(None, i) for i in range(16, 72, 2)}  # Default font

        """ GAMELOG INIT """
        self.gamelog = None
        self.debug = debug
        with open(log_filename, 'rb') as f:
            self.gamelog = pickle.load(f).to_dict(orient='index')



        colors = ['green', 'blue', 'yellow', 'red', 'orange', 'purple']
        shuffle(colors)
        p1 = PlayerSprite(self.gamelog[0]['pseudo_j'], colors[0])
        p2 = PlayerSprite(self.gamelog[0]['pseudo_adv'], colors[1])
        p1.set_position('bottom')
        p2.set_position('top')
        self.players = pygame.sprite.Group(*[p1, p2])

        self.current_turn = 0
        self.update()

        self.running = True

    def run(self):
        while self.running:
            self.event_loop()
            self.clock.tick(30)
            self.screen.fill('black')
            self.players.draw(self.screen)

            # TURNS
            turns = pygame.Surface((120, 6800))
            margin, span, size = 10, 14, 18

            if self.current_turn < 30:
                t_range = 0
            else:
                t_range = self.current_turn - 30
            for t in range(t_range, t_range+50):
                current = self.gamelog[t]
                if current['action'] == "passer_tour":
                    color = 'yellow'
                elif current['cible'] == 'heros' and current['cible_pv'] - current['attaquant_atq'] <= 0:
                    color = 'red'
                else:
                    color = 'white'

                if t == self.current_turn:
                    txt = f"{t} : {self.get_currentline()['action'].capitalize().replace('_', ' ')}"
                    turns.blit(default_font[size].render(txt, True, color),
                                (10, 10 + margin + t * span))
                else:
                    turns.blit(default_font[size].render(str(t), True, color), (10,10 + margin + t * span))
                for player in self.players:
                    if player.pseudo == current['pseudo_j']:
                        pygame.draw.rect(turns, player.color, (2, 10 + margin + t * span, 2, 14))

            self.screen.blit(turns, (0, -t_range*14))
            pygame.display.flip()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEWHEEL:
                self.change_current_turn(event.y)

    def update(self):
        self.players.update(self.get_currentline())

    def get_currentline(self):
        return self.gamelog[self.current_turn]

    def change_current_turn(self, nb):
        self.current_turn -= nb
        if self.current_turn < 0:
            self.current_turn = 0
        elif self.current_turn > len(self.gamelog):
            self.current_turn = len(self.gamelog)
        else:
            self.update()
            if self.debug:
                debug_str = {k: v for k, v in self.get_currentline().items() if v not in (-99, "")}
                print(debug_str)







if __name__ == '__main__':
    fi = FancyInterface('modelisation/logs_games.pickle', debug=False)
    fi.run()


