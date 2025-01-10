import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import * 
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
import platform

import socket
import threading

class Game:
    def __init__(self ,host:str=None ,game_type:str=None) -> None:
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()

        self.port = 9000
        self.host = host
        self.type = game_type
        self.scores = {}
        self.running = True
        if game_type == 'join':
            self.join_thread = threading.Thread(target=self.join_session)
            self.join_thread.start()
            # self.join_session()
        elif game_type == 'create':
            self.create_thread = threading.Thread(target=self.create_session)
            self.create_thread.start()
            # self.create_session()

        

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
 
    def update(self): 
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        print("The player: ")
        print(self.player.health)
        if self.type == 'create' or self.type == 'join':
            score_message = f"{platform.node()}:{self.player.health}"
            self.send_data(score_message)

        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() : .1f}')


    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        # self.map.draw()
        # self.player.draw()

        print("\n Current scores:")
        for player_name ,score in self.scores.items():
            print(f"{player_name}:{score}")

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

    def create_session(self):
        try:
            with socket.socket(socket.AF_INET ,socket.SOCK_STREAM) as s:
                s.bind((self.host ,self.port))
                s.listen(1)
                conn ,addr =s.accept()
                print("A player connected: ",addr)
                self.conn = conn
                while self.running:
                    data = conn.recv(1024)
                    if(data):
                        data_str = data.decode()
                        if ":" in data_str:
                            player_name ,score = data_str.split(':')
                            self.scores[player_name] = int(score)
                    # score_message = 
                        # print(data.decode())
        except:
            print("An error occured while creating a sesion")
            self.running = False
            # sys.exit()

    def join_session(self):
        try:
            with socket.socket(socket.AF_INET ,socket.SOCK_STREAM) as s:
                s.connect((self.host ,self.port))
                self.s = s
                while self.running:
                    data = s.recv(1024)
                    if data:
                        data_str = data.decode()
                        if ":" in data_str:
                            player_name ,score = data_str.split(':')
                            self.scores[player_name] = int(score)
                        # print("Received: ",data.decode())
        except:
            print('An error occured while trying to join the session')
            self.running
            # sys.exit()

    def send_data(self ,message):
        if self.type == 'create':
            try:
                self.conn.sendall(message.encode())
            except:
                pass
        elif self.type == 'join':
            try:
                self.s.sendall(message.encode())
            except:
                pass


if __name__ == '__main__':
    args = sys.argv
    if(len(args) == 3 ):
        host=args[2]
        print(f' host:post | {host}:9000')
    elif len(args) > 1 or len(args) >3:
        print('Invalid option')
        sys.exit()

    if 'join' in args:
        print("Join LAN game")
        game = Game(host ,'join')
    elif 'create' in args:
        print("create LAN game")
        game = Game(host ,'create')
    else:
        print("Playing a solo game")
        game = Game()

    game.run()

    # game = Game()
    # game.run()