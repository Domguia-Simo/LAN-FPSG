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
import json

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

        self.health = self.player.health
        self.__messages = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        self.socket.send(json.dumps({
            "user": {
                # "id": 1,
                "name": platform.node()
            },
            "message": "SYN"
        }).encode('utf-8'))
        self._private = 1

        self.on_message_receive = None

        self.running = True

        server_listener = threading.Thread(target=self.listen_to_server)
        server_listener.start()

        
    def send_message_as_dict(self):
        message = {
            "user": {
                # "id": self.id,
                "name": platform.node()
            },
            "message": self.player.health
        }

        self.send_message(message)
    
    def send_message(self, message):
        print(f"In client socket, sending message: {message}")
        self.socket.send(json.dumps(message).encode('utf-8'))
    
    def listen_to_server(self):
        while self.running:
            try:
                data_bytes = self.socket.recv(1024)
                print(f"Message received: ")
                message = data_bytes.decode()
                print(message)

                self.__messages.append(message)

                if self.on_message_receive and callable(self.on_message_receive):
                    message = json.loads(message)
                    self.on_message_receive(message)
            # exit loop if there is an error
            except ConnectionAbortedError:
                break



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
        
        if(self.health != self.player.health):
            self.send_message_as_dict()

        self.health = self.player.health
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() : .1f}')


    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        # self.map.draw()
        # self.player.draw()


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
            self.draw()
            self.update()


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
    # elif 'create' in args:
    #     print("create LAN game")
    #     game = Game(host ,'create')
    else:
        print("Playing a solo game")
        game = Game()

    game.run()

    # game = Game()
    # game.run()