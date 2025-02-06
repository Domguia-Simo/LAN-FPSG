# game settings
import math
import os
import getpass

abs_folder_path = os.path.dirname(__file__)

RES = WIDTH, HEIGHT = 1600, 900
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60

PLAYER_POS = 1.5, 5
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004 # movement speed
PLAYER_ROT_SPEED = 0.002 # rotation speed
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100

MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

FLOOR_COLOR = (30, 30, 30)

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH + math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# Player view settings
PLAYER_MAX_PITCH = 0.5  # Maximum up angle
PLAYER_MIN_PITCH = -0.5  # Maximum down angle

# Get current user's home directory
USER_HOME = os.path.expanduser('~')
# Create a hidden directory in user's home for game data
GAME_DATA_DIR = os.path.join(USER_HOME, '.lanfpsg')
# Create user-specific database path
DB_PATH = os.path.join(GAME_DATA_DIR, 'game_stats.db')

# Create game data directory if it doesn't exist
os.makedirs(GAME_DATA_DIR, exist_ok=True)