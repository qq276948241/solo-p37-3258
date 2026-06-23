import pygame
from constants import *


def draw_ui(screen, player):
    pygame.draw.rect(screen, (30, 30, 40), (0, 0, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, WHITE, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

    font = pygame.font.Font(None, 22)
    hp_label = font.render('HP:', True, WHITE)
    screen.blit(hp_label, (15, 10))

    bar_x = 50
    bar_y = 12
    bar_w = 200
    bar_h = 20
    pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
    hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 0
    hp_color = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
    pygame.draw.rect(screen, hp_color,
                     (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
    hp_text = font.render(f'{player.hp}/{player.max_hp}', True, WHITE)
    screen.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2,
                          bar_y + 2))

    gold_icon_x = bar_x + bar_w + 30
    pygame.draw.circle(screen, GOLD, (gold_icon_x + 8, bar_y + 10), 8)
    pygame.draw.circle(screen, YELLOW, (gold_icon_x + 8, bar_y + 10), 5)
    gold_text = font.render(f'{player.gold}', True, WHITE)
    screen.blit(gold_text, (gold_icon_x + 22, bar_y + 6))

    floor_text = font.render(f'第 {player.floor} 层', True, CYAN)
    screen.blit(floor_text, (gold_icon_x + 80, bar_y + 6))

    atk_text = font.render(f'ATK:{player.atk}', True, ORANGE)
    screen.blit(atk_text, (gold_icon_x + 170, bar_y + 6))

    def_text = font.render(f'DEF:{player.df}', True, BLUE)
    screen.blit(def_text, (gold_icon_x + 260, bar_y + 6))

    if player.has_bow:
        arrow_text = font.render(f'箭矢:{player.arrows}', True, ARROW_COLOR)
        screen.blit(arrow_text, (gold_icon_x + 350, bar_y + 6))

    hint_font = pygame.font.Font(None, 16)
    controls = hint_font.render('WASD/方向键移动 | J/空格 剑攻击 | K 射箭 | E 商店',
                                 True, LIGHT_GRAY)
    screen.blit(controls, (15, UI_HEIGHT - 20))


def draw_minimap(screen, game_map, player, monsters, stairs_pos):
    mm_x = SCREEN_WIDTH - MINIMAP_SIZE - 10
    mm_y = SCREEN_HEIGHT - MINIMAP_SIZE - 10

    pygame.draw.rect(screen, BLACK, (mm_x - 2, mm_y - 2,
                                      MINIMAP_SIZE + 4, MINIMAP_SIZE + 4))
    pygame.draw.rect(screen, WHITE, (mm_x - 3, mm_y - 3,
                                      MINIMAP_SIZE + 6, MINIMAP_SIZE + 6), 1)
    pygame.draw.rect(screen, (10, 10, 20), (mm_x, mm_y,
                                             MINIMAP_SIZE, MINIMAP_SIZE))

    scale_x = MINIMAP_SIZE / game_map.width
    scale_y = MINIMAP_SIZE / game_map.height

    for x in range(game_map.width):
        for y in range(game_map.height):
            if not game_map.explored[x][y]:
                continue
            tile = game_map.tiles[x][y]
            dx = int(x * scale_x)
            dy = int(y * scale_y)
            if tile == 1:
                color = (80, 60, 40)
            elif tile == 2:
                color = DOOR_COLOR
            elif tile == 3:
                color = PURPLE
            elif tile == 4:
                color = STAIRS_COLOR
            elif tile == 5:
                color = BOSS_FLOOR_COLOR
            else:
                color = FLOOR_COLOR
            if game_map.visible[x][y]:
                pass
            else:
                color = tuple(max(0, c - 60) for c in color)
            w = max(1, int(scale_x) + 1)
            h = max(1, int(scale_y) + 1)
            pygame.draw.rect(screen, color, (mm_x + dx, mm_y + dy, w, h))

    for m in monsters:
        if not m.alive:
            continue
        mx = int(m.tile_x * scale_x)
        my = int(m.tile_y * scale_y)
        if 0 <= mx < MINIMAP_SIZE and 0 <= my < MINIMAP_SIZE:
            if game_map.visible[m.tile_x][m.tile_y]:
                if m.is_boss:
                    pygame.draw.circle(screen, BOSS_COLOR,
                                       (mm_x + mx, mm_y + my), 5)
                    pygame.draw.circle(screen, YELLOW,
                                       (mm_x + mx, mm_y + my), 5, 1)
                else:
                    pygame.draw.circle(screen, RED,
                                       (mm_x + mx, mm_y + my), 2)

    if stairs_pos:
        sx = int(stairs_pos[0] * scale_x)
        sy = int(stairs_pos[1] * scale_y)
        if game_map.explored[stairs_pos[0]][stairs_pos[1]]:
            pygame.draw.circle(screen, STAIRS_COLOR,
                               (mm_x + sx, mm_y + sy), 3)

    px = int(player.tile_x * scale_x)
    py = int(player.tile_y * scale_y)
    pygame.draw.circle(screen, PLAYER_COLOR,
                       (mm_x + px, mm_y + py), 3)
    pygame.draw.circle(screen, WHITE,
                       (mm_x + px, mm_y + py), 3, 1)

    font = pygame.font.Font(None, 16)
    label = font.render('MAP', True, WHITE)
    screen.blit(label, (mm_x + 5, mm_y + 2))


def draw_floor_notice(screen, floor, timer):
    if timer <= 0:
        return
    alpha = min(255, timer * 3)
    font = pygame.font.Font(None, 60)
    text = font.render(f'第 {floor} 层', True, (255, 255, 255))
    text_surf = pygame.Surface((text.get_width() + 40, text.get_height() + 20),
                               pygame.SRCALPHA)
    text_surf.fill((0, 0, 0, min(200, alpha)))
    text_surf.blit(text, (20, 10))
    text_surf.set_alpha(alpha)
    screen.blit(text_surf,
                (SCREEN_WIDTH // 2 - text_surf.get_width() // 2,
                 SCREEN_HEIGHT // 2 - text_surf.get_height() // 2))
