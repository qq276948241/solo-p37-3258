import pygame
import math
from constants import *


class Arrow:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.active = True

    def update(self, game_map):
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(self.y // TILE_SIZE)
        if game_map.is_wall(tile_x, tile_y):
            self.active = False
            return
        self.x += self.dx * ARROW_SPEED
        self.y += self.dy * ARROW_SPEED

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT)
        angle = math.atan2(self.dy, self.dx)
        length = 12
        end_x = sx + math.cos(angle) * length
        end_y = sy + math.sin(angle) * length
        pygame.draw.line(screen, ARROW_COLOR, (sx, sy), (int(end_x), int(end_y)), 3)
        tip_x = sx + math.cos(angle) * (length + 4)
        tip_y = sy + math.sin(angle) * (length + 4)
        pygame.draw.circle(screen, DARK_GRAY, (int(tip_x), int(tip_y)), 2)


class Player:
    def __init__(self, x, y):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.atk = PLAYER_BASE_ATK
        self.df = PLAYER_BASE_DEF
        self.gold = STARTING_GOLD
        self.arrows = STARTING_ARROWS
        self.has_bow = False
        self.facing = 'down'
        self.last_attack_time = 0
        self.attacking = False
        self.attack_timer = 0
        self.invincible = 0
        self.total_kills = 0
        self.total_gold = 0
        self.floor = 1

    @property
    def tile_x(self):
        return int(self.x // TILE_SIZE)

    @property
    def tile_y(self):
        return int(self.y // TILE_SIZE)

    def move(self, dx, dy, game_map):
        new_x = self.x + dx * PLAYER_SPEED
        new_y = self.y + dy * PLAYER_SPEED
        if dx < 0:
            self.facing = 'left'
        elif dx > 0:
            self.facing = 'right'
        elif dy < 0:
            self.facing = 'up'
        elif dy > 0:
            self.facing = 'down'

        half_size = PLAYER_SIZE // 2 - 2
        if dx != 0:
            check_x = new_x + (half_size if dx > 0 else -half_size)
            tile_x = int(check_x // TILE_SIZE)
            tile_y1 = int((self.y - half_size) // TILE_SIZE)
            tile_y2 = int((self.y + half_size) // TILE_SIZE)
            if not (game_map.is_wall(tile_x, tile_y1) or game_map.is_wall(tile_x, tile_y2)):
                self.x = new_x

        if dy != 0:
            check_y = new_y + (half_size if dy > 0 else -half_size)
            tile_y = int(check_y // TILE_SIZE)
            tile_x1 = int((self.x - half_size) // TILE_SIZE)
            tile_x2 = int((self.x + half_size) // TILE_SIZE)
            if not (game_map.is_wall(tile_x1, tile_y) or game_map.is_wall(tile_x2, tile_y)):
                self.y = new_y

    def attack_melee(self, monsters):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time < ATTACK_COOLDOWN:
            return []
        self.last_attack_time = now
        self.attacking = True
        self.attack_timer = 200
        hits = []
        dir_dx, dir_dy = DIRECTIONS[self.facing]
        attack_cx = self.x + dir_dx * ATTACK_RANGE * 0.6
        attack_cy = self.y + dir_dy * ATTACK_RANGE * 0.6
        for monster in monsters:
            if not monster.alive:
                continue
            dist = math.sqrt((monster.x - attack_cx) ** 2 + (monster.y - attack_cy) ** 2)
            if dist < ATTACK_RANGE:
                damage = max(1, self.atk - monster.df)
                monster.take_damage(damage)
                hits.append((monster, damage))
                if not monster.alive:
                    self.total_kills += 1
        return hits

    def shoot_arrow(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time < ATTACK_COOLDOWN:
            return None
        if not self.has_bow or self.arrows <= 0:
            return None
        self.last_attack_time = now
        self.arrows -= 1
        dir_dx, dir_dy = DIRECTIONS[self.facing]
        return Arrow(self.x, self.y, dir_dx, dir_dy)

    def take_damage(self, amount):
        if self.invincible > 0:
            return
        actual_damage = max(1, amount - self.df)
        self.hp -= actual_damage
        self.invincible = 500
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def update(self):
        if self.attack_timer > 0:
            self.attack_timer -= 16
            if self.attack_timer <= 0:
                self.attacking = False
        if self.invincible > 0:
            self.invincible -= 16

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT)
        if self.invincible > 0 and (self.invincible // 100) % 2 == 0:
            return
        body_rect = pygame.Rect(sx - PLAYER_SIZE // 2, sy - PLAYER_SIZE // 2,
                                 PLAYER_SIZE, PLAYER_SIZE)
        pygame.draw.rect(screen, PLAYER_COLOR, body_rect)
        pygame.draw.rect(screen, WHITE, body_rect, 2)
        eye_offset = 4
        if self.facing == 'left':
            pygame.draw.circle(screen, BLACK, (sx - eye_offset, sy - 3), 2)
        elif self.facing == 'right':
            pygame.draw.circle(screen, BLACK, (sx + eye_offset, sy - 3), 2)
        elif self.facing == 'up':
            pygame.draw.circle(screen, BLACK, (sx - 4, sy - eye_offset), 2)
            pygame.draw.circle(screen, BLACK, (sx + 4, sy - eye_offset), 2)
        else:
            pygame.draw.circle(screen, BLACK, (sx - 4, sy + eye_offset), 2)
            pygame.draw.circle(screen, BLACK, (sx + 4, sy + eye_offset), 2)

        if self.attacking:
            dir_dx, dir_dy = DIRECTIONS[self.facing]
            sw_x = sx + dir_dx * 25
            sw_y = sy + dir_dy * 25
            if dir_dx != 0:
                pygame.draw.rect(screen, LIGHT_GRAY,
                                 (sw_x - 2, sw_y - 12, 4, 24))
            else:
                pygame.draw.rect(screen, LIGHT_GRAY,
                                 (sw_x - 12, sw_y - 2, 24, 4))
