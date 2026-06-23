import pygame
import math
import random
from constants import *


class Item:
    def __init__(self, x, y, item_type, value=0):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.type = item_type
        self.value = value
        self.collected = False
        self.bob_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.bob_offset += 0.08

    def draw(self, screen, camera_x, camera_y):
        if self.collected:
            return
        bob = math.sin(self.bob_offset) * 3
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT + bob)

        if self.type == 'coin':
            pygame.draw.circle(screen, GOLD, (sx, sy), 7)
            pygame.draw.circle(screen, YELLOW, (sx, sy), 4)
            pygame.draw.circle(screen, (255, 255, 150), (sx - 2, sy - 2), 1)
        elif self.type == 'potion':
            pygame.draw.rect(screen, DARK_RED, (sx - 5, sy - 6, 10, 12), 2)
            pygame.draw.rect(screen, POTION_COLOR, (sx - 4, sy - 4, 8, 9))
            pygame.draw.rect(screen, BROWN, (sx - 3, sy - 8, 6, 3))
            pygame.draw.circle(screen, (255, 150, 150), (sx - 1, sy - 1), 1)
        elif self.type == 'arrow_pickup':
            for i in range(3):
                offset = (i - 1) * 3
                pygame.draw.line(screen, ARROW_COLOR,
                                 (sx - 6 + offset, sy + 4),
                                 (sx + 6 + offset, sy - 4), 2)
                pygame.draw.polygon(screen, DARK_GRAY, [
                    (sx + 6 + offset, sy - 4),
                    (sx + 9 + offset, sy - 6),
                    (sx + 6 + offset, sy - 1)
                ])
        elif self.type == 'bow':
            pygame.draw.arc(screen, BOW_COLOR,
                            (sx - 10, sy - 8, 20, 16),
                            math.radians(-60), math.radians(60), 3)
            pygame.draw.line(screen, LIGHT_GRAY,
                             (sx - 8, sy - 7), (sx - 8, sy + 7), 1)


def create_drops(monster):
    drops = []
    tx, ty = monster.tile_x, monster.tile_y

    gold = monster.get_gold_drop()
    drops.append(Item(tx, ty, 'coin', gold))

    if monster.is_boss:
        potion_count = monster.get_potion_drops()
        for _ in range(potion_count):
            ox = tx + random.randint(-2, 2)
            oy = ty + random.randint(-2, 2)
            drops.append(Item(ox, oy, 'potion'))
        if random.random() < monster._arrow_drop_chance:
            drops.append(Item(tx + random.randint(-1, 1),
                              ty + random.randint(-1, 1),
                              'arrow_pickup', monster.get_arrow_drops()))
    else:
        if random.random() < monster._potion_drop_chance:
            drops.append(Item(tx + random.randint(-1, 1),
                              ty + random.randint(-1, 1), 'potion'))
        if random.random() < monster._arrow_drop_chance:
            drops.append(Item(tx + random.randint(-1, 1),
                              ty + random.randint(-1, 1),
                              'arrow_pickup', random.randint(2, 5)))
        if random.random() < monster._bow_drop_chance:
            drops.append(Item(tx + random.randint(-1, 1),
                              ty + random.randint(-1, 1), 'bow'))
    return drops


def check_item_pickup(player, items):
    picked = []
    for item in items:
        if item.collected:
            continue
        dist = math.sqrt((player.x - item.x) ** 2 + (player.y - item.y) ** 2)
        if dist < TILE_SIZE:
            if item.type == 'coin':
                player.gold += item.value
                player.total_gold += item.value
            elif item.type == 'potion':
                player.heal(POTION_HEAL)
            elif item.type == 'arrow_pickup':
                player.arrows += item.value
            elif item.type == 'bow':
                player.has_bow = True
                player.arrows += 5
            item.collected = True
            picked.append(item)
    return picked
