import pygame
from pygame.locals import *
from modelisation.Entities import *

CARD_POOL = get_cards_data("cards.json")


class ScrollLog(pygame.sprite.Sprite):
    def __init__(self, gamelog: dict, player_colors: dict):
        pygame.sprite.Sprite.__init__(self)
        self.gamelog = gamelog
        self.player_colors = player_colors
        self.length = len(gamelog)

        self.image = pygame.Surface((160, 720))
        self.rect = self.image.get_rect()
        self.rect.x = 0

    def update(self, current_turn):
        # Fill the background
        self.image.fill('grey')
        pygame.draw.rect(self.image, (20, 20, 20), (1, 1, self.rect.width - 2, self.rect.height - 2))

        pos_y = current_turn * 16 - 256

        for i, logline in self.gamelog.items():
            if i == current_turn:
                str_line = f"{i} : {logline['action']} - {get_card(logline['carte_jouee'], CARD_POOL) if logline['carte_jouee'] else ''}"
            else:
                str_line = str(i)

            if i in range(current_turn-40, current_turn+40):
                txt = default_font[18].render(str_line, True, 'white')
                self.image.blit(txt, (10, i * 16 + 2 - pos_y))
                pygame.draw.line(self.image, self.player_colors[logline['pseudo_j']], (2, i*16 - pos_y), (2, (i+1)*16 - pos_y), 2)
            try:
                if logline['cible'] == 'heros' and logline['cible_pv'] - logline['attaquant_atq'] <= 0:
                    pygame.draw.line(self.image, 'red', (0, (i + 1) * 16 - pos_y), (120, (i + 1) * 16 - pos_y), 1)
            except TypeError:
                pass


        self.rect.y = -current_turn*16


class CardSprite(pygame.sprite.Sprite):
    def __init__(self, cid=None):
        pygame.sprite.Sprite.__init__(self)
        self.cid = cid
        if cid is not None:
            obj = get_card(cid, CARD_POOL)
            self.name = obj.name
            self.pv_max = obj.base_health
            self.attaque_max = obj.base_attack
            self.description = []

        self.attaque = None
        self.pv = None
        self.atq_remain = None
        self.cost = None

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
            try:
                if on_board_id.split('_')[-1] == 'j':
                    self.atq_remain = logline['atq_remain_'+on_board_id]
                if logline['divineshield_'+on_board_id] >= 1:
                    self.description += [" Bouclier divin"]
                if logline['provocation_'+on_board_id] == 1:
                    self.description += [" Provocation"]
                if logline['cant_attack_'+on_board_id] == 1:
                    self.description += [" Ne peut pas attaquer"]
                if logline['ruee_'+on_board_id] == 1:
                    self.description += [" Ruée"]
                if logline['charge_'+on_board_id] == 1:
                    self.description += [" Charge"]
                if logline['camouflage_'+on_board_id] >= 0:
                    self.description += [" Camouflage"]
                if logline['reincarnation_'+on_board_id] >= 0:
                    self.description += [" Réincarnation"]
                if logline['en_sommeil_'+on_board_id] != -99:
                    self.description += [" En sommeil"]
                if logline['gel_'+on_board_id] == 1:
                    self.description += [" Gelé"]
                if logline['inciblable_'+on_board_id] == 1:
                    self.description += [" Inciblable"]
                if logline['voldevie_'+on_board_id] == 1:
                    self.description += [" Vol de vie"]
                if logline['toxicite_'+on_board_id] == 1:
                    self.description += [" Toxicité"]
                if logline['spelldamage_'+on_board_id] != -99:
                    self.description += [f" Dégats des sorts : {logline['spelldamage_'+on_board_id]}"]
                if logline['furiedesvents_'+on_board_id] == 1:
                    self.description += [" Furie des vents"]
                if logline['titan_'+on_board_id] >= 0:
                    self.description += [" Titan"]
            except:
                try:
                    if logline['impregnation_'+on_board_id] != -99:
                        self.description += [" Imprégnation" + str(logline['impregnation_'+on_board_id])]
                    if logline['eclosion_'+on_board_id] != -99:
                        self.description += [" Éclosion" + str(logline['eclosion_'+on_board_id])]
                    self.cost = logline['cost_'+on_board_id]
                except:
                    pass
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
            if self.attaque is not None:
                atq = default_font[32].render(str(self.attaque), True, 'white')
                self.image.blit(atq, (10, 120))
            for i in range(len(self.description)):
                descr = default_font[16].render(self.description[i], True, 'white')
                self.image.blit(descr, (10, 50 + 10 * i))

            try:
                if self.pv < self.pv_max:
                    color = 'red'
                else:
                    color = 'white'
            except:
                color = "white"
            if self.pv is not None:
                pv = default_font[32].render(str(self.pv), True, color)
                self.image.blit(pv, (80, 120))
            if self.cost is not None:
                cost = default_font[16].render(str(self.cost), True, color)
                self.image.blit(cost, (5, 30))


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
        self.attaque, self.durabilite = 0, 0
        self.surcharge = 0
        self.armor = 0
        self.cadavres = 0
        self.pv, self.pv_max = 30, 30

        """ Cards """
        self.hand = pygame.sprite.Group()
        self.servant = pygame.sprite.Group()
        self.lieux = pygame.sprite.Group()
        self.secrets = []

        """ State """
        self.is_playing = False
        self.is_attacking = False
        self.gets_attacked = False

        """ Pygame variables """
        self.image = pygame.Surface([1080, 330])
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
        self.classe = logline['classe_'+role]

        self.mana_max = logline['mana_max_'+role]
        self.surcharge = logline['surcharge_'+role]
        self.pv, self.pv_max = logline['pv_'+role], logline['pv_max_'+role]
        self.cost = 0
        self.armor = logline['armor_'+role]
        self.cadavres = logline['cadavres_' + role]
        self.attaque = logline['attaque_'+role]
        self.durabilite = logline['durabilite_arme_' + role]

        """ Cards """
        if role == "j":
            hand = [logline[f"carte_en_main{i + 1}_{role}"] for i in range(10)]
            self.hand = pygame.sprite.Group(*[CardSprite(e) for e in hand if e != -99])
            self.hand.update(logline)
        else:
            self.hand = pygame.sprite.Group(*[CardSprite() for x in range(logline['nbre_cartes_' + role])])
            self.hand.update()
        servant = [logline[f"serv{i+1}_{role}"] for i in range(7)]
        self.servant = pygame.sprite.Group(*[CardSprite(e) for e in servant if e != -99])
        self.servant.update(logline)
        lieux = [logline[f"lieu{i+1}_{role}"] for i in range(7)]
        self.lieux = pygame.sprite.Group(*[CardSprite(e) for e in lieux if e != -99])
        self.lieux.update(logline)
        self.secrets = [logline[f"secret{i + 1}_{role}"] for i in range(7)]

        """ Update sprite """
        self.image.fill(self.color)
        border = 1
        pygame.draw.rect(self.image, (20, 20, 20), (border, border, 1080 - border * 2, 330 - border * 2))

        """ Hand """
        height = {'top': 0, 'bottom': 180}
        hand = pygame.Surface((100*len(self.hand), 150))
        for x, card in enumerate(self.hand):
            hand.blit(card.image, (100 * x, 0))
        self.image.blit(hand, (450-hand.get_width()/2, height[self.position]))

        """ Player """

        if logline['cible'] == 'heros' and not self.is_playing:
            color = 'red'
        elif logline['attaquant'] == 'heros' and self.is_playing:
            color = 'blue'
        else:
            color = 'white'

        pseudo = default_font[32].render(f"{self.pseudo} ({self.classe})", True, color)
        mana = default_font[24].render(f"Mana : {self.mana}/{self.mana_max}", True, 'white')
        atq = default_font[32].render(str(self.attaque), True, 'white')
        durabilite = default_font[20].render("dur : " + str(self.durabilite), True, 'white')
        armor = default_font[32].render(str(self.armor), True, 'white')
        cadavres = default_font[20].render("cad : " + str(self.cadavres), True, 'white')
        secrets = [default_font[20].render("secrets : " + str(x), True, 'white') for x in self.secrets if x != -99]
        if self.pv < self.pv_max:
            color = 'red'
        else:
            color = 'white'
        pv = default_font[32].render(str(self.pv), True, color)

        height = {'top': (10, 40, 70, 100), 'bottom': (300, 270, 240, 160)}

        self.image.blit(pseudo, (950 - pseudo.get_width()/2, height[self.position][0]))
        self.image.blit(mana, (950 - mana.get_width() / 2, height[self.position][1]))
        self.image.blit(atq, (850 - atq.get_width() / 2, height[self.position][2]))
        self.image.blit(durabilite, (830 - atq.get_width() / 2, height[self.position][1]))
        self.image.blit(pv, (950 - pv.get_width() / 2, height[self.position][2]))
        self.image.blit(armor, (1050 - armor.get_width() / 2, height[self.position][2]))
        self.image.blit(cadavres, (1030 - atq.get_width() / 2, height[self.position][1]))
        for i in range(len(secrets)):
            self.image.blit(secrets[i], (830, height[self.position][3] - 15 * i * (self.position == "top") + 15 * i * (self.position == "bottom")))

        """ Servants """
        gap = 5
        pos_x = 450 - ((100 + gap) * len(self.servant))/2
        height = {'top': 170, 'bottom': 10}
        for x, card in enumerate(self.servant):
            self.image.blit(card.image, (pos_x + (card.width + gap) * x, height[self.position]))

        """ Lieux """
        gap = 5
        pos_x = 900 - ((100 + gap) * len(self.lieux))/2
        height = {'top': 170, 'bottom': 10}
        for x, card in enumerate(self.lieux):
            self.image.blit(card.image, (pos_x + (card.width + gap) * x, height[self.position]))


class FancyInterface:
    def __init__(self, log_filename, debug=False, resolution=(1280, 720)):
        """ Show the gamelog with a graphic interface """
        """ PYGAME INIT """
        pygame.init()
        self.screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption('FrenchStone')
        pygame.display.set_icon(pygame.image.load('../images/icon.png'))
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

        self.scrolllog = ScrollLog(self.gamelog, {p1.pseudo: colors[0], p2.pseudo: colors[1]})

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
                else:
                    try:
                        if current['cible'] == 'heros' and current['cible_pv'] - current['attaquant_atq'] <= 0:
                            color = 'red'
                        else:
                            color = 'white'
                    except TypeError:
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

            #self.screen.blit(turns, (0, -t_range*14))
            #self.screen.blit(self.scrolllog.image, (0, 128-self.current_turn*16))
            self.screen.blit(self.scrolllog.image, (0, 0))
            pygame.display.flip()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEWHEEL:
                self.change_current_turn(event.y)

    def update(self):
        self.players.update(self.get_currentline())
        self.scrolllog.update(self.current_turn)

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
    fi = FancyInterface('logs_games.pickle', debug=False)
    fi.run()



