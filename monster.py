import pygame
import math
import random
from constants import *


class Monster:
    def __init__(self, x, y, monster_type):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.type = monster_type
        self.alive = True
        self.last_attack_time = 0
        self.move_timer = 0
        self.hit_flash = 0

        if monster_type == 'slime':
            self.hp = SLIME_HP
            self.max_hp = SLIME_HP
            self.atk = SLIME_ATK
            self.df = 0
            self.speed = MONSTER_SPEED * 0.8
            self.size = 20
            self.color = SLIME_COLOR
            self.gold_min = SLIME_GOLD_MIN
            self.gold_max = SLIME_GOLD_MAX
        elif monster_type == 'skeleton':
            self.hp = SKELETON_HP
            self.max_hp = SKELETON_HP
            self.atk = SKELETON_ATK
            self.df = 1
            self.speed = MONSTER_SPEED
            self.size = 22
            self.color = SKELETON_COLOR
            self.gold_min = SKELETON_GOLD_MIN
            self.gold_max = SKELETON_GOLD_MAX

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

    def update(self, player, game_map, monsters):
        if not self.alive:
            return

        if self.hit_flash > 0:
            self.hit_flash -= 16

        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)

        if dist < TILE_SIZE * 6:
            dx = player.x - self.x
            dy = player.y - self.y
            if dist > 0:
                dx /= dist
                dy /= dist
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
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
        else:
            self.move_timer -= 1
            if self.move_timer <= 0:
                self.move_timer = random.randint(30, 90)
                self._random_dx = random.choice([-1, 0, 1])
                self._random_dy = random.choice([-1, 0, 1])
                if self._random_dx != 0 and self._random_dy != 0:
                    if random.random() < 0.5:
                        self._random_dx = 0
                    else:
                        self._random_dy = 0
            if hasattr(self, '_random_dx'):
                new_x = self.x + self._random_dx * self.speed * 0.5
                new_y = self.y + self._random_dy * self.speed * 0.5
                half = self.size // 2 - 2
                test_x = new_x + (half if self._random_dx > 0 else -half)
                tx = int(test_x // TILE_SIZE)
                ty = int(self.y // TILE_SIZE)
                if not game_map.is_wall(tx, ty):
                    self.x = new_x
                test_y = new_y + (half if self._random_dy > 0 else -half)
                ty = int(test_y // TILE_SIZE)
                tx = int(self.x // TILE_SIZE)
                if not game_map.is_wall(tx, ty):
                    self.y = new_y

    def try_attack(self, player):
        if not self.alive:
            return False
        now = pygame.time.get_ticks()
        if now - self.last_attack_time < 800:
            return False
        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist < self.size + PLAYER_SIZE // 2:
            self.last_attack_time = now
            player.take_damage(self.atk)
            return True
        return False

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT)
        color = WHITE if self.hit_flash > 0 else self.color
        if self.type == 'slime':
            pygame.draw.ellipse(screen, color,
                                (sx - self.size // 2, sy - self.size // 3,
                                 self.size, self.size))
            pygame.draw.ellipse(screen, DARK_GREEN,
                                (sx - self.size // 2, sy - self.size // 3,
                                 self.size, self.size), 2)
            pygame.draw.circle(screen, BLACK, (sx - 4, sy - 2), 2)
            pygame.draw.circle(screen, BLACK, (sx + 4, sy - 2), 2)
        elif self.type == 'skeleton':
            head_r = self.size // 3
            pygame.draw.circle(screen, color, (sx, sy - self.size // 4), head_r)
            pygame.draw.rect(screen, color,
                             (sx - self.size // 3, sy - 2,
                              self.size // 1.5, self.size // 1.5))
            pygame.draw.circle(screen, BLACK, (sx - 3, sy - self.size // 4), 2)
            pygame.draw.circle(screen, BLACK, (sx + 3, sy - self.size // 4), 2)
            pygame.draw.rect(screen, DARK_GRAY,
                             (sx - 2, sy - 2, self.size // 2, 2))

        bar_w = self.size + 4
        bar_h = 4
        bar_x = sx - bar_w // 2
        bar_y = sy - self.size // 2 - 8
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))


class Boss(Monster):
    def __init__(self, x, y, floor):
        super().__init__(x, y, 'boss')
        self.floor = floor
        self.hp = BOSS_HP_BASE + (floor - 1) * 80
        self.max_hp = self.hp
        self.atk = BOSS_ATK_BASE + (floor - 1) * 5
        self.df = 3 + floor // 3
        self.speed = MONSTER_SPEED * 0.7
        self.size = int(22 * BOSS_SIZE_MULTIPLIER)
        self.color = BOSS_COLOR
        self.gold_min = BOSS_GOLD_MIN + floor * 10
        self.gold_max = BOSS_GOLD_MAX + floor * 15
        self.is_boss = True
        self.charge_timer = 0
        self.is_charging = False

    def get_gold_drop(self):
        return random.randint(self.gold_min, self.gold_max)

    def get_potion_drops(self):
        return 2 + self.floor // 2

    def update(self, player, game_map, monsters):
        if not self.alive:
            return

        if self.hit_flash > 0:
            self.hit_flash -= 16

        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)

        speed_mult = 1.0
        if self.charge_timer > 0:
            self.charge_timer -= 1
            speed_mult = 2.5
            self.is_charging = True
        else:
            self.is_charging = False
            if dist < TILE_SIZE * 8 and random.random() < 0.005:
                self.charge_timer = 60

        if dist < TILE_SIZE * 10:
            dx = player.x - self.x
            dy = player.y - self.y
            if dist > 0:
                dx /= dist
                dy /= dist
            new_x = self.x + dx * self.speed * speed_mult
            new_y = self.y + dy * self.speed * speed_mult
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

    def try_attack(self, player):
        if not self.alive:
            return False
        now = pygame.time.get_ticks()
        cooldown = 500 if self.is_charging else 800
        if now - self.last_attack_time < cooldown:
            return False
        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist < self.size + PLAYER_SIZE // 2:
            self.last_attack_time = now
            damage = self.atk
            if self.is_charging:
                damage = int(self.atk * 1.5)
            player.take_damage(damage)
            return True
        return False

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT)
        color = WHITE if self.hit_flash > 0 else self.color

        body_rect = pygame.Rect(sx - self.size // 2, sy - self.size // 2,
                           self.size, self.size)
        pygame.draw.rect(screen, color, body_rect)
        pygame.draw.rect(screen, YELLOW, body_rect, 3)

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

        if self.is_charging:
            pygame.draw.circle(screen, ORANGE,
                             (sx, sy - self.size // 2 - 15), 6)
            pygame.draw.circle(screen, YELLOW,
                             (sx, sy - self.size // 2 - 15), 3)

        bar_w = self.size + 20
        bar_h = 8
        bar_x = sx - bar_w // 2
        bar_y = sy - self.size // 2 - 18
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
        hp_ratio = self.hp / self.max_hp
        bar_color = RED if hp_ratio > 0.3 else DARK_RED
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        name_font = pygame.font.Font(None, 18)
        name = name_font.render(f'BOSS Lv.{self.floor}', True, YELLOW)
        screen.blit(name, (sx - name.get_width() // 2, bar_y - 22))
