import pygame
import sys
import random
import math
from constants import *
from game_map import GameMap
from player import Player
from monster import Monster, Boss
from items import Item, check_item_pickup
from shop import Shop
from ui import draw_ui, draw_minimap, draw_floor_notice
from game_over import GameOverScreen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('像素地下城探险')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.running = True
        self.game_over_screen = GameOverScreen()
        self.new_game()

    def new_game(self):
        self.game_map = GameMap(MAP_COLS, MAP_ROWS)
        self.floor = 1
        self.game_map.generate(self.floor)
        start_room = self.game_map.rooms[0]
        start_x, start_y = start_room.center
        self.player = Player(start_x, start_y)
        self.monsters = []
        self.items = []
        self.arrows = []
        self.damage_texts = []
        self.floor_notice_timer = 120
        self.state = 'playing'
        self.spawn_monsters()
        self.shop = Shop(self.game_map)

    def spawn_monsters(self):
        self.monsters = []
        for i, room in enumerate(self.game_map.rooms):
            if i == 0:
                continue
            if room is self.game_map.shop_room:
                continue
            if room is self.game_map.boss_room:
                continue
            num_monsters = random.randint(1, 3 + self.floor // 2)
            for _ in range(num_monsters):
                mx, my = self.game_map.get_random_floor_tile(room)
                monster_type = random.choice(['slime', 'slime', 'skeleton'])
                if self.floor >= 3:
                    monster_type = random.choice(['slime', 'skeleton', 'skeleton'])
                self.monsters.append(Monster(mx, my, monster_type))

        if self.game_map.is_boss_floor and self.game_map.boss_spawn_pos:
            bx, by = self.game_map.boss_spawn_pos
            self.monsters.append(Boss(bx, by, self.floor))

    def next_floor(self):
        self.floor += 1
        self.player.floor = self.floor
        self.game_map = GameMap(MAP_COLS, MAP_ROWS)
        self.game_map.generate(self.floor)
        start_room = self.game_map.rooms[0]
        start_x, start_y = start_room.center
        self.player.x = start_x * TILE_SIZE + TILE_SIZE // 2
        self.player.y = start_y * TILE_SIZE + TILE_SIZE // 2
        self.arrows = []
        self.items = []
        self.damage_texts = []
        self.floor_notice_timer = 120
        self.spawn_monsters()
        self.shop = Shop(self.game_map)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.state == 'game_over':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over_screen.handle_click(event.pos):
                        self.new_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.new_game()
            elif self.state == 'shop':
                self.shop.handle_input(event, self.player)
            elif self.state == 'playing':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j or event.key == pygame.K_SPACE:
                        hits = self.player.attack_melee(self.monsters)
                        for m, dmg in hits:
                            self.damage_texts.append({
                                'x': m.x, 'y': m.y - 20,
                                'text': f'-{dmg}', 'color': YELLOW, 'life': 40
                            })
                    elif event.key == pygame.K_k:
                        arrow = self.player.shoot_arrow()
                        if arrow:
                            self.arrows.append(arrow)
                    elif event.key == pygame.K_e:
                        if self.shop.is_player_in_shop(self.player):
                            self.state = 'shop'
                            self.shop.active = True
                    elif event.key == pygame.K_PERIOD:
                        if (self.game_map.stairs_pos and
                                self.game_map.stairs_active and
                                self.player.tile_x == self.game_map.stairs_pos[0] and
                                self.player.tile_y == self.game_map.stairs_pos[1]):
                            self.next_floor()

    def update(self):
        if self.state != 'playing':
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.player.move(dx, dy, self.game_map)
        self.player.update()

        self.game_map.compute_fov(self.player.tile_x, self.player.tile_y)

        for monster in self.monsters:
            if (self.game_map.visible[monster.tile_x][monster.tile_y] or
                    math.sqrt((monster.x - self.player.x) ** 2 +
                              (monster.y - self.player.y) ** 2) < TILE_SIZE * 4):
                monster.update(self.player, self.game_map, self.monsters)
                monster.try_attack(self.player)

        for arrow in self.arrows:
            if not arrow.active:
                continue
            arrow.update(self.game_map)
            for monster in self.monsters:
                if not monster.alive:
                    continue
                dist = math.sqrt((monster.x - arrow.x) ** 2 +
                                 (monster.y - arrow.y) ** 2)
                if dist < monster.size // 2 + 4:
                    damage = ARROW_DAMAGE + self.player.atk // 3
                    monster.take_damage(damage)
                    arrow.active = False
                    self.damage_texts.append({
                        'x': monster.x, 'y': monster.y - 20,
                        'text': f'-{damage}', 'color': ORANGE, 'life': 40
                    })
                    if not monster.alive:
                        self.player.total_kills += 1
                        drops = Item.create_drops(monster.tile_x,
                                                   monster.tile_y, monster)
                        self.items.extend(drops)
                    break

        self.arrows = [a for a in self.arrows if a.active]

        for monster in self.monsters:
            if not monster.alive and not hasattr(monster, '_dropped'):
                monster._dropped = True
                if hasattr(monster, 'is_boss') and monster.is_boss:
                    gold = monster.get_gold_drop()
                    self.items.append(Item(monster.tile_x, monster.tile_y,
                                            'coin', gold))
                    num_potions = monster.get_potion_drops()
                    for i in range(num_potions):
                        ox = monster.tile_x + random.randint(-2, 2)
                        oy = monster.tile_y + random.randint(-2, 2)
                        self.items.append(Item(ox, oy, 'potion'))
                    if random.random() < 0.5:
                        ox = monster.tile_x + random.randint(-1, 1)
                        oy = monster.tile_y + random.randint(-1, 1)
                        self.items.append(Item(ox, oy, 'arrow_pickup',
                                                random.randint(5, 10)))
                else:
                    drops = Item.create_drops(monster.tile_x, monster.tile_y, monster)
                    self.items.extend(drops)
        self.monsters = [m for m in self.monsters if m.alive]

        if self.game_map.is_boss_floor and not self.game_map.stairs_active:
            boss_alive = any(hasattr(m, 'is_boss') and m.is_boss for m in self.monsters)
            if not boss_alive:
                self.game_map.stairs_active = True

        for item in self.items:
            item.update()
        check_item_pickup(self.player, self.items)
        self.items = [i for i in self.items if not i.collected]

        for dt in self.damage_texts:
            dt['life'] -= 1
            dt['y'] -= 0.8
        self.damage_texts = [dt for dt in self.damage_texts if dt['life'] > 0]

        if self.floor_notice_timer > 0:
            self.floor_notice_timer -= 1

        if self.player.hp <= 0:
            self.state = 'game_over'

    def draw_map(self, camera_x, camera_y):
        start_col = max(0, int(camera_x // TILE_SIZE))
        end_col = min(self.game_map.width,
                      int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        start_row = max(0, int(camera_y // TILE_SIZE))
        end_row = min(self.game_map.height,
                      int((camera_y + SCREEN_HEIGHT - UI_HEIGHT) // TILE_SIZE) + 2)

        for col in range(start_col, end_col):
            for row in range(start_row, end_row):
                if not self.game_map.explored[col][row]:
                    continue
                tile = self.game_map.tiles[col][row]
                sx = col * TILE_SIZE - camera_x
                sy = row * TILE_SIZE - camera_y + UI_HEIGHT

                if tile == 1:
                    color = WALL_COLOR
                elif tile == 2:
                    color = DOOR_COLOR
                elif tile == 3:
                    color = SHOP_FLOOR_COLOR
                elif tile == 4:
                    color = FLOOR_COLOR
                elif tile == 5:
                    color = BOSS_FLOOR_COLOR
                else:
                    color = FLOOR_COLOR

                if not self.game_map.visible[col][row]:
                    color = tuple(max(0, c // 2) for c in color)

                pygame.draw.rect(self.screen, color,
                                 (sx, sy, TILE_SIZE, TILE_SIZE))

                if tile == 1 and self.game_map.visible[col][row]:
                    pygame.draw.rect(self.screen, (100, 80, 60),
                                     (sx, sy, TILE_SIZE, TILE_SIZE), 1)
                elif tile == 2:
                    pygame.draw.rect(self.screen, (120, 90, 50),
                                     (sx + 2, sy + 2, TILE_SIZE - 4, TILE_SIZE - 4), 1)
                    pygame.draw.circle(self.screen, YELLOW,
                                       (sx + TILE_SIZE - 8, sy + TILE_SIZE // 2), 2)
                elif tile == 4 and self.game_map.visible[col][row]:
                    pygame.draw.rect(self.screen, STAIRS_COLOR,
                                     (sx + 4, sy + 4, TILE_SIZE - 8, TILE_SIZE - 8), 2)
                    for i in range(3):
                        pygame.draw.line(self.screen, STAIRS_COLOR,
                                         (sx + 6, sy + 10 + i * 7),
                                         (sx + TILE_SIZE - 6, sy + 10 + i * 7), 2)

    def draw(self):
        self.screen.fill(BLACK)

        camera_x = self.player.x - SCREEN_WIDTH // 2
        camera_y = self.player.y - (SCREEN_HEIGHT - UI_HEIGHT) // 2
        camera_x = max(0, min(camera_x,
                               self.game_map.width * TILE_SIZE - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y,
                               self.game_map.height * TILE_SIZE -
                               (SCREEN_HEIGHT - UI_HEIGHT)))

        self.draw_map(camera_x, camera_y)

        for item in self.items:
            tx = item.x // TILE_SIZE
            ty = item.y // TILE_SIZE
            if self.game_map.visible[int(tx)][int(ty)]:
                item.draw(self.screen, camera_x, camera_y)

        for monster in self.monsters:
            if self.game_map.visible[monster.tile_x][monster.tile_y]:
                monster.draw(self.screen, camera_x, camera_y)

        for arrow in self.arrows:
            arrow.draw(self.screen, camera_x, camera_y)

        self.player.draw(self.screen, camera_x, camera_y)

        self.shop.draw_keeper(self.screen, camera_x, camera_y)

        for dt in self.damage_texts:
            sx = int(dt['x'] - camera_x)
            sy = int(dt['y'] - camera_y + UI_HEIGHT)
            font = pygame.font.Font(None, 20)
            text = font.render(dt['text'], True, dt['color'])
            text.set_alpha(min(255, dt['life'] * 8))
            self.screen.blit(text, (sx - text.get_width() // 2, sy))

        draw_ui(self.screen, self.player)
        draw_minimap(self.screen, self.game_map, self.player,
                      self.monsters, self.game_map.stairs_pos)
        draw_floor_notice(self.screen, self.floor, self.floor_notice_timer)

        if self.game_map.stairs_pos:
            sx, sy = self.game_map.stairs_pos
            if (abs(self.player.tile_x - sx) <= 1 and
                    abs(self.player.tile_y - sy) <= 1):
                if self.game_map.stairs_active:
                    hint = self.font.render('按 . 下一层', True, YELLOW)
                else:
                    hint = self.font.render('击败BOSS后楼梯激活', True, RED)
                px = self.player.x - camera_x
                py = self.player.y - camera_y + UI_HEIGHT
                self.screen.blit(hint,
                                 (px - hint.get_width() // 2, py - 50))

        if self.shop.is_player_in_shop(self.player) and self.state == 'playing':
            hint = self.font.render('按 E 打开商店', True, YELLOW)
            px = self.player.x - camera_x
            py = self.player.y - camera_y + UI_HEIGHT
            self.screen.blit(hint,
                             (px - hint.get_width() // 2, py - 50))

        if self.state == 'shop':
            self.shop.draw_panel(self.screen, self.player)
        elif self.state == 'game_over':
            self.game_over_screen.draw(self.screen, self.player)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
