import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
UI_HEIGHT = 60

MAP_COLS = 50
MAP_ROWS = 40

ROOM_MIN_SIZE = 6
ROOM_MAX_SIZE = 12
MAX_ROOMS = 8

FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 140, 0)
PURPLE = (148, 0, 211)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)

WALL_COLOR = (80, 60, 40)
FLOOR_COLOR = (45, 35, 25)
DOOR_COLOR = (180, 140, 80)
STAIRS_COLOR = (100, 100, 150)
SHOP_FLOOR_COLOR = (60, 50, 80)

PLAYER_COLOR = (100, 200, 255)
PLAYER_SIZE = 24

SLIME_COLOR = (80, 220, 80)
SKELETON_COLOR = (230, 230, 230)
BOSS_COLOR = (220, 40, 40)
BOSS_ROOM_COLOR = (70, 30, 30)
BOSS_FLOOR_COLOR = (60, 25, 25)

COIN_COLOR = (255, 215, 0)
POTION_COLOR = (255, 80, 80)
ARROW_COLOR = (200, 160, 100)
BOW_COLOR = (139, 90, 43)

PLAYER_SPEED = 3
MONSTER_SPEED = 1.5

PLAYER_MAX_HP = 100
PLAYER_BASE_ATK = 10
PLAYER_BASE_DEF = 0

MONSTER_CONFIGS = {
    'slime': {
        'hp': 30,
        'atk': 5,
        'df': 0,
        'speed': MONSTER_SPEED * 0.8,
        'size': 20,
        'color': SLIME_COLOR,
        'outline_color': DARK_GREEN,
        'gold_min': 2,
        'gold_max': 6,
        'potion_drop_chance': 0.3,
        'arrow_drop_chance': 0.2,
        'bow_drop_chance': 0.05,
        'aggro_range': 6,
        'attack_cooldown': 800,
        'patrol_speed_mult': 0.5,
        'bar_width_offset': 4,
        'bar_height': 4,
        'is_boss': False,
    },
    'skeleton': {
        'hp': 50,
        'atk': 8,
        'df': 1,
        'speed': MONSTER_SPEED,
        'size': 22,
        'color': SKELETON_COLOR,
        'outline_color': DARK_GRAY,
        'gold_min': 5,
        'gold_max': 12,
        'potion_drop_chance': 0.3,
        'arrow_drop_chance': 0.2,
        'bow_drop_chance': 0.05,
        'aggro_range': 6,
        'attack_cooldown': 800,
        'patrol_speed_mult': 0.5,
        'bar_width_offset': 4,
        'bar_height': 4,
        'is_boss': False,
    },
    'boss': {
        'hp': 300,
        'atk': 18,
        'df': 3,
        'speed': MONSTER_SPEED * 0.7,
        'size': 44,
        'color': BOSS_COLOR,
        'outline_color': YELLOW,
        'gold_min': 50,
        'gold_max': 100,
        'potion_drop_count': 2,
        'arrow_drop_chance': 0.5,
        'arrow_drop_amount': 7,
        'bow_drop_chance': 0.0,
        'aggro_range': 10,
        'attack_cooldown': 800,
        'charge_speed_mult': 2.5,
        'charge_attack_mult': 1.5,
        'charge_trigger_chance': 0.005,
        'charge_duration': 60,
        'charge_cooldown_override': 500,
        'bar_width_offset': 20,
        'bar_height': 8,
        'hp_per_floor': 80,
        'atk_per_floor': 5,
        'df_per_floor': 0.33,
        'gold_per_floor': 10,
        'is_boss': True,
    },
}

ATTACK_RANGE = 40
ARROW_SPEED = 8
ARROW_DAMAGE = 15
ATTACK_COOLDOWN = 300

POTION_HEAL = 30
STARTING_GOLD = 0
STARTING_ARROWS = 0

SHOP_ATK_COST = 30
SHOP_DEF_COST = 25
SHOP_HP_COST = 20
SHOP_POTION_COST = 15
SHOP_ARROW_COST = 10

SHOP_ATK_BONUS = 3
SHOP_DEF_BONUS = 2
SHOP_HP_BONUS = 20

MINIMAP_SIZE = 150
MINIMAP_TILE = 3

DIRECTIONS = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}
