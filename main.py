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

# Add this import at the top with other imports
from database_handler import DatabaseHandler
from server import GameServer  # Add this import

class Menu:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(True)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 64)
        self.small_font = pg.font.Font(None, 36)
        
        # Mode selection buttons
        self.mode_buttons = {
            'single': pg.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 50),
            'multiplayer': pg.Rect(WIDTH//2 - 150, HEIGHT//2 + 50, 300, 50)
        }
        
        # Server buttons (for multiplayer)
        self.server_buttons = {
            'create': pg.Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50),
            'join': pg.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
        }
        
        self.input_active = False
        self.input_text = ''
        self.input_rect = pg.Rect(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 40)
        self.show_mode_selection = True  # Start with mode selection
        
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Title
        title = self.font.render('FIRST PERSON SHOOTER GAME', True, (255, 0, 0))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))

        if self.show_mode_selection:
            # Single Player button
            pg.draw.rect(self.screen, (100, 100, 100), self.mode_buttons['single'])
            single_text = self.small_font.render('Single Player', True, (255, 255, 255))
            self.screen.blit(single_text, (self.mode_buttons['single'].centerx - single_text.get_width()//2,
                                         self.mode_buttons['single'].centery - single_text.get_height()//2))

            # Multiplayer button
            pg.draw.rect(self.screen, (100, 100, 100), self.mode_buttons['multiplayer'])
            multi_text = self.small_font.render('LAN Multiplayer', True, (255, 255, 255))
            self.screen.blit(multi_text, (self.mode_buttons['multiplayer'].centerx - multi_text.get_width()//2,
                                        self.mode_buttons['multiplayer'].centery - multi_text.get_height()//2))
        else:
            # Create Server button
            pg.draw.rect(self.screen, (100, 100, 100), self.server_buttons['create'])
            create_text = self.small_font.render('Create Server', True, (255, 255, 255))
            self.screen.blit(create_text, (self.server_buttons['create'].centerx - create_text.get_width()//2,
                                         self.server_buttons['create'].centery - create_text.get_height()//2))

            # Join Server button
            pg.draw.rect(self.screen, (100, 100, 100), self.server_buttons['join'])
            join_text = self.small_font.render('Join Server', True, (255, 255, 255))
            self.screen.blit(join_text, (self.server_buttons['join'].centerx - join_text.get_width()//2,
                                       self.server_buttons['join'].centery - join_text.get_height()//2))

            # IP input box
            if self.input_active:
                pg.draw.rect(self.screen, (100, 100, 100), self.input_rect)
                text_surface = self.small_font.render(self.input_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
                helper_text = self.small_font.render('Enter IP address and press Enter', True, (200, 200, 200))
                self.screen.blit(helper_text, (WIDTH//2 - helper_text.get_width()//2, self.input_rect.bottom + 10))

        pg.display.flip()

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    if self.show_mode_selection:
                        if self.mode_buttons['single'].collidepoint(mouse_pos):
                            return Game()  # Start single player game
                        elif self.mode_buttons['multiplayer'].collidepoint(mouse_pos):
                            self.show_mode_selection = False  # Show multiplayer options
                    else:
                        if self.server_buttons['create'].collidepoint(mouse_pos):
                            server = GameServer()
                            server_thread = threading.Thread(target=server.start)
                            server_thread.daemon = True
                            server_thread.start()
                            return Game(host='localhost', game_type='create')
                        elif self.server_buttons['join'].collidepoint(mouse_pos):
                            self.input_active = True
                
                if event.type == pg.KEYDOWN and self.input_active:
                    if event.key == pg.K_RETURN:
                        if self.input_text:
                            return Game(host=self.input_text, game_type='join')
                    elif event.key == pg.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode

            self.draw()
            self.clock.tick(60)

from typing import Optional

class Game:
    def __init__(self, host: Optional[str] = None, game_type: Optional[str] = None) -> None:
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()

        # Network game initialization
        self.is_network_game = host is not None and game_type is not None
        if self.is_network_game and host and game_type:  # Add explicit checks
            self.port = 9000
            self.host = str(host)  # Ensure string type
            self.type = str(game_type)  # Ensure string type
            self.is_host = game_type == 'create'
            self.health = self.player.health
            self.__messages = []

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            # Send initial connection message with role info
            self.socket.send(json.dumps({
                "user": {
                    "name": platform.node(),
                    "role": "host" if self.is_host else "client"
                },
                "type": "connection",
                "message": "SYN"
            }).encode('utf-8'))

            print(f"Connected as {'HOST' if self.is_host else 'CLIENT'}")
            self._private = 1

            self.on_message_receive = None
            self.running = True

            server_listener = threading.Thread(target=self.listen_to_server)
            server_listener.start()

        # Change font size to be more readable
        self.font = pg.font.Font(None, 36)  # Smaller font size
        self.stats_font = pg.font.Font(None, 72)  # Larger font for stats screen

        self.db = DatabaseHandler()
        self.player_name = platform.node()
        self.kills = 0
        self.last_saved_kills = 0  # Initialize this
        # Start new session
        self.db.start_new_session(self.player_name)

        self.frame_time = 0
        self.target_fps = 60
        self.frame_interval = 1.0 / self.target_fps

        
    def send_message_as_dict(self):
        message = {
            "user": {
                "name": platform.node(),
                "role": "host" if self.is_host else "client"
            },
            "type": "update",
            "message": {
                "health": self.player.health,
                "kills": self.kills,
                "position": list(self.player.pos)  # Send player position
            }
        }
        self.send_message(message)
    
    def send_message(self, message):
        print(f"In client socket, sending message: {message}")
        self.socket.send(json.dumps(message).encode('utf-8'))
    
    def listen_to_server(self):
        while self.running:
            try:
                data_bytes = self.socket.recv(1024)
                message = json.loads(data_bytes.decode())
                print(f"Received message from {'Host' if message['user'].get('role') == 'host' else 'Client'}: {message}")

                # Handle different message types
                if message.get('type') == 'update':
                    if message['user']['name'] != platform.node():  # Don't process own messages
                        self.handle_player_update(message)

            except ConnectionAbortedError:
                print("Disconnected from server")
                break
            except json.JSONDecodeError:
                print("Received invalid message format")
            except Exception as e:
                print(f"Error in listener: {e}")

    def handle_player_update(self, message):
        """Handle updates from other players"""
        if 'message' in message:
            data = message['message']
            # Update other player data here
            print(f"Player {message['user']['name']} health: {data.get('health')}")

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
        frame_start = pg.time.get_ticks() / 1000.0  # Convert to seconds

        # Update game state
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        
        # Network updates in a separate thread
        if self.is_network_game and self.health != self.player.health:
            network_thread = threading.Thread(target=self.send_message_as_dict)
            network_thread.daemon = True
            network_thread.start()
            self.health = self.player.health

        # Stats saving in a separate thread
        if self.global_trigger and self.kills != self.last_saved_kills:
            stats_thread = threading.Thread(target=self.save_stats)
            stats_thread.daemon = True
            stats_thread.start()

        # Frame timing and limiting
        self.frame_time = (pg.time.get_ticks() / 1000.0) - frame_start
        if self.frame_time < self.frame_interval:
            pg.time.delay(int((self.frame_interval - self.frame_time) * 1000))

        # Update display
        pg.display.flip()
        self.delta_time = self.clock.tick_busy_loop(self.target_fps)
        fps = self.clock.get_fps()
        pg.display.set_caption(f'FPS: {fps:.1f}')

    def save_stats(self):
        """Separate thread for saving stats"""
        self.db.save_player_stats(self.player_name, self.player.health, self.kills)
        self.last_saved_kills = self.kills
        print(f"Saved kills to database: {self.kills}")

    def draw(self):
        # Only redraw what's necessary
        # Draw main game elements
        self.object_renderer.draw()
        self.weapon.draw()
        
        # Draw crosshair last so it's always on top
        self.draw_crosshair()
        
        # Draw UI elements
        stats_rect = self.draw_stats()
        
        pg.display.flip()

    def draw_crosshair(self):
        # Make crosshair more visible
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        color = (255, 0, 0)  # Changed to red
        line_length = 15     # Made longer
        thickness = 2
        
        # Draw with black outline for better visibility
        pg.draw.line(self.screen, (0, 0, 0), (center_x - line_length - 1, center_y),
                     (center_x + line_length + 1, center_y), thickness + 2)
        pg.draw.line(self.screen, (0, 0, 0), (center_x, center_y - line_length - 1),
                     (center_x, center_y + line_length + 1), thickness + 2)
                     
        # Draw red crosshair
        pg.draw.line(self.screen, color, (center_x - line_length, center_y),
                     (center_x + line_length, center_y), thickness)
        pg.draw.line(self.screen, color, (center_x, center_y - line_length),
                     (center_x, center_y + line_length), thickness)

    def draw_stats(self):
        kills_text = f'Kills: {self.kills}'
        kills_surface = self.font.render(kills_text, True, (255, 0, 0))
        x = WIDTH - kills_surface.get_width() - 100  # Match health padding
        y = 50  # Slightly lower than health
        # Add outline
        outline = self.font.render(kills_text, True, (0, 0, 0))
        self.screen.blit(outline, (x + 1, y + 1))
        self.screen.blit(kills_surface, (x, y))
        rect = pg.Rect(x, y, kills_surface.get_width() + 2, kills_surface.get_height() + 2)
        return rect

    def draw_stats_screen(self):
        """Draw a stats screen overlay"""
        # Create semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0,0))

        # Get stats data
        high_scores = self.db.get_high_scores(5)
        all_time_kills = self.db.get_all_time_kills(self.player_name)
        best_session = self.db.get_total_kills(self.player_name)
        sessions, _ = self.db.get_session_stats(self.player_name)

        # Render stats
        y_pos = 100
        # Use stats_font for the stats screen
        title = self.stats_font.render("STATS", True, (255, 255, 255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, y_pos))

        # Current session
        y_pos += 80
        current = self.font.render(f"Current Session: {self.kills} kills", True, (255, 0, 0))
        self.screen.blit(current, (WIDTH//2 - current.get_width()//2, y_pos))

        # Best session
        y_pos += 50
        best = self.font.render(f"Best Session: {best_session} kills", True, (255, 200, 0))
        self.screen.blit(best, (WIDTH//2 - best.get_width()//2, y_pos))

        # All-time kills
        y_pos += 50
        total = self.font.render(f"All-time Kills: {all_time_kills}", True, (0, 255, 0))
        self.screen.blit(total, (WIDTH//2 - total.get_width()//2, y_pos))

        # Total sessions
        y_pos += 50
        sessions_text = self.font.render(f"Total Sessions: {sessions}", True, (100, 200, 255))
        self.screen.blit(sessions_text, (WIDTH//2 - sessions_text.get_width()//2, y_pos))

        # High scores
        y_pos += 80
        for player, score in high_scores:
            text = self.font.render(f"{player}: {score} kills", True, (255, 200, 0))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 50

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.cleanup()
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)
            # Add this to your existing event handling
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.draw_stats_screen()
                pg.display.flip()
                pg.time.wait(2000)  # Show stats for 2 seconds

    def run(self):
        try:
            while True:
                self.check_events()
                self.draw()
                self.update()
        except Exception as e:
            print(f"Game error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'db'):
            self.db.close()
        if hasattr(self, 'socket'):
            self.socket.close()
        if hasattr(self, 'running'):
            self.running = False

    def increment_kills(self):
        self.kills += 1
        print(f"Kills updated: {self.kills}")
        # Save immediately when kills increase
        self.db.save_player_stats(self.player_name, self.player.health, self.kills)
        self.last_saved_kills = self.kills


if __name__ == '__main__':
    try:
        pg.init()
        menu = Menu()
        game = menu.run()
        if game:  # Only run the game if menu returns a game instance
            game.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pg.quit()