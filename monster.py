import pygame
import math
import random
from constants import *


class BaseMonster:
    def __init__(self, x, y, config_key, floor=1):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.type = config_key
        self.alive = True
        self.last_attack_time = 0
        self.move_timer = 0
        self.hit_flash = 0
        self.floor = floor

        cfg = MONSTER_CONFIGS[config_key]
        self._apply_config(cfg, floor)

    def _apply_config(self, cfg, floor):
        self.hp = cfg['hp']
        self.max_hp = cfg['hp']
        self.atk = cfg['atk']
        self.df = cfg['df']
        self.speed = cfg['speed']
        self.size = cfg['size']
        self.color = cfg['color']
        self.outline_color = cfg['outline_color']
        self.gold_min = cfg['gold_min']
        self.gold_max = cfg['gold_max']
        self.aggro_range = cfg['aggro_range']
        self.attack_cooldown = cfg['attack_cooldown']
        self.patrol_speed_mult = cfg.get('patrol_speed_mult', 0.5)
        self.bar_width_offset = cfg.get('bar_width_offset', 4)
        self.bar_height = cfg.get('bar_height', 4)
        self.is_boss = cfg.get('is_boss', False)
        self._potion_drop_chance = cfg.get('potion_drop_chance', 0.0)
        self._arrow_drop_chance = cfg.get('arrow_drop_chance', 0.0)
        self._bow_drop_chance = cfg.get('bow_drop_chance', 0.0)

    @property
    def tile_x(self):
        return int(self.x // TILE_SIZE)

    @property
    def tile_y(self):
        return int(self.y // TILE_SIZE)

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 200
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def get_gold_drop(self):
        return random.randint(self.gold_min, self.gold_max)

    def get_attack_damage(self):
        return self.atk

    def get_attack_cooldown(self):
        return self.attack_cooldown

    def get_speed_multiplier(self):
        return 1.0

    def update_special(self, player, game_map):
        pass

    def update(self, player, game_map, monsters):
        if not self.alive:
            return

        if self.hit_flash > 0:
            self.hit_flash -= 16

        self.update_special(player, game_map)

        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        speed_mult = self.get_speed_multiplier()

        if dist < TILE_SIZE * self.aggro_range:
            dx = player.x - self.x
            dy = player.y - self.y
            if dist > 0:
                dx /= dist
                dy /= dist
            new_x = self.x + dx * self.speed * speed_mult
            new_y = self.y + dy * self.speed * speed_mult
            self._try_move(new_x, new_y, dx, dy, game_map)
        else:
            self._patrol(game_map)

    def _try_move(self, new_x, new_y, dx, dy, game_map):
        half = self.size // 2 - 2
        can_move_x = True
        can_move_y = True
        test_x = new_x + (half if dx > 0 else -half)
        tx = int(test_x // TILE_SIZE)
        ty1 = int((self.y - half) // TILE_SIZE)
        ty2 = int((self.y + half) // TILE_SIZE)
        if game_map.is_wall(tx, ty1) or game_map.is_wall(tx, ty2):
            can_move_x = False
        test_y = new_y + (half if dy > 0 else -half)
        ty = int(test_y // TILE_SIZE)
        tx1 = int((self.x - half) // TILE_SIZE)
        tx2 = int((self.x + half) // TILE_SIZE)
        if game_map.is_wall(tx1, ty) or game_map.is_wall(tx2, ty):
            can_move_y = False
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y

    def _patrol(self, game_map):
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.move_timer = random.randint(30, 90)
            self._patrol_dx = random.choice([-1, 0, 1])
            self._patrol_dy = random.choice([-1, 0, 1])
            if self._patrol_dx != 0 and self._patrol_dy != 0:
                if random.random() < 0.5:
                    self._patrol_dx = 0
                else:
                    self._patrol_dy = 0
        if hasattr(self, '_patrol_dx'):
            new_x = self.x + self._patrol_dx * self.speed * self.patrol_speed_mult
            new_y = self.y + self._patrol_dy * self.speed * self.patrol_speed_mult
            self._try_move(new_x, new_y, self._patrol_dx, self._patrol_dy, game_map)

    def try_attack(self, player):
        if not self.alive:
            return False
        now = pygame.time.get_ticks()
        cooldown = self.get_attack_cooldown()
        if now - self.last_attack_time < cooldown:
            return False
        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist < self.size + PLAYER_SIZE // 2:
            self.last_attack_time = now
            player.take_damage(self.get_attack_damage())
            return True
        return False

    def draw_body(self, screen, sx, sy, color):
        raise NotImplementedError

    def draw_health_bar(self, screen, sx, sy):
        bar_w = self.size + self.bar_width_offset
        bar_h = self.bar_height
        bar_x = sx - bar_w // 2
        bar_y = sy - self.size // 2 - 8 - self.bar_height
        if self.is_boss:
            bar_y -= 8
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
        if self.is_boss:
            pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
        hp_ratio = self.hp / self.max_hp
        bar_color = RED
        if self.is_boss and hp_ratio <= 0.3:
            bar_color = DARK_RED
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT)
        color = WHITE if self.hit_flash > 0 else self.color
        self.draw_body(screen, sx, sy, color)
        self.draw_health_bar(screen, sx, sy)


class Slime(BaseMonster):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, 'slime', floor)

    def draw_body(self, screen, sx, sy, color):
        pygame.draw.ellipse(screen, color,
                            (sx - self.size // 2, sy - self.size // 3,
                             self.size, self.size))
        pygame.draw.ellipse(screen, self.outline_color,
                            (sx - self.size // 2, sy - self.size // 3,
                             self.size, self.size), 2)
        pygame.draw.circle(screen, BLACK, (sx - 4, sy - 2), 2)
        pygame.draw.circle(screen, BLACK, (sx + 4, sy - 2), 2)


class Skeleton(BaseMonster):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, 'skeleton', floor)

    def draw_body(self, screen, sx, sy, color):
        head_r = self.size // 3
        pygame.draw.circle(screen, color, (sx, sy - self.size // 4), head_r)
        pygame.draw.rect(screen, color,
                         (sx - self.size // 3, sy - 2,
                          self.size // 1.5, self.size // 1.5))
        pygame.draw.circle(screen, BLACK, (sx - 3, sy - self.size // 4), 2)
        pygame.draw.circle(screen, BLACK, (sx + 3, sy - self.size // 4), 2)
        pygame.draw.rect(screen, self.outline_color,
                         (sx - 2, sy - 2, self.size // 2, 2))


class Boss(BaseMonster):
    def __init__(self, x, y, floor=1):
        super().__init__(x, y, 'boss', floor)
        cfg = MONSTER_CONFIGS['boss']
        self.hp = cfg['hp'] + (floor - 1) * cfg['hp_per_floor']
        self.max_hp = self.hp
        self.atk = cfg['atk'] + (floor - 1) * cfg['atk_per_floor']
        self.df = cfg['df'] + int(floor * cfg['df_per_floor'])
        self.gold_min = cfg['gold_min'] + floor * cfg['gold_per_floor']
        self.gold_max = cfg['gold_max'] + floor * cfg['gold_per_floor']
        self._charge_timer = 0
        self._is_charging = False
        self._potion_drop_count = cfg.get('potion_drop_count', 2) + floor // 2
        self._arrow_drop_amount = cfg.get('arrow_drop_amount', 7)

    def get_speed_multiplier(self):
        if self._charge_timer > 0:
            return MONSTER_CONFIGS['boss']['charge_speed_mult']
        return 1.0

    def get_attack_damage(self):
        if self._is_charging:
            return int(self.atk * MONSTER_CONFIGS['boss']['charge_attack_mult'])
        return self.atk

    def get_attack_cooldown(self):
        if self._is_charging:
            return MONSTER_CONFIGS['boss']['charge_cooldown_override']
        return self.attack_cooldown

    def update_special(self, player, game_map):
        cfg = MONSTER_CONFIGS['boss']
        if self._charge_timer > 0:
            self._charge_timer -= 1
            self._is_charging = True
        else:
            self._is_charging = False
            dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
            if dist < TILE_SIZE * 8 and random.random() < cfg['charge_trigger_chance']:
                self._charge_timer = cfg['charge_duration']

    def get_potion_drops(self):
        return self._potion_drop_count

    def get_arrow_drops(self):
        return self._arrow_drop_amount

    def draw_body(self, screen, sx, sy, color):
        body_rect = pygame.Rect(sx - self.size // 2, sy - self.size // 2,
                                self.size, self.size)
        pygame.draw.rect(screen, color, body_rect)
        pygame.draw.rect(screen, self.outline_color, body_rect, 3)

        eye_y = sy - self.size // 6
        pygame.draw.circle(screen, YELLOW, (sx - self.size // 4, eye_y), 4)
        pygame.draw.circle(screen, YELLOW, (sx + self.size // 4, eye_y), 4)
        pygame.draw.circle(screen, BLACK, (sx - self.size // 4, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (sx + self.size // 4, eye_y), 2)

        mouth_y = sy + self.size // 6
        pygame.draw.rect(screen, BLACK,
                         (sx - self.size // 4, mouth_y, self.size // 2, self.size // 8))
        for i in range(3):
            tx = sx - self.size // 4 + i * (self.size // 8)
            pygame.draw.polygon(screen, WHITE, [
                (tx, mouth_y),
                (tx + self.size // 16, mouth_y + self.size // 10),
                (tx + self.size // 8, mouth_y)
            ])

        if self._is_charging:
            pygame.draw.circle(screen, ORANGE,
                               (sx, sy - self.size // 2 - 15), 6)
            pygame.draw.circle(screen, YELLOW,
                               (sx, sy - self.size // 2 - 15), 3)

    def draw_health_bar(self, screen, sx, sy):
        super().draw_health_bar(screen, sx, sy)
        name_font = pygame.font.Font(None, 18)
        name = name_font.render(f'BOSS Lv.{self.floor}', True, YELLOW)
        bar_w = self.size + self.bar_width_offset
        bar_y = sy - self.size // 2 - 8 - self.bar_height - 8
        screen.blit(name, (sx - name.get_width() // 2, bar_y - 18))
