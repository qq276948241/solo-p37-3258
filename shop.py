import pygame
from constants import *


class Shop:
    def __init__(self, game_map):
        self.active = False
        self.items = [
            {'name': '攻击力+3', 'cost': SHOP_ATK_COST, 'type': 'atk',
             'desc': '永久提升攻击力'},
            {'name': '防御力+2', 'cost': SHOP_DEF_COST, 'type': 'df',
             'desc': '永久提升防御力'},
            {'name': '最大生命+20', 'cost': SHOP_HP_COST, 'type': 'maxhp',
             'desc': '提升最大生命并回满'},
            {'name': '生命药水', 'cost': SHOP_POTION_COST, 'type': 'heal',
             'desc': '立刻恢复30点生命'},
            {'name': '箭矢x5', 'cost': SHOP_ARROW_COST, 'type': 'arrow',
             'desc': '获得5支箭矢'},
        ]
        self.selected = 0
        self.shop_room = game_map.shop_room
        if self.shop_room:
            cx, cy = self.shop_room.center
            self.x = cx * TILE_SIZE + TILE_SIZE // 2
            self.y = cy * TILE_SIZE + TILE_SIZE // 2
        else:
            self.x = 0
            self.y = 0

    def is_player_in_shop(self, player):
        if not self.shop_room:
            return False
        return (self.shop_room.left <= player.tile_x < self.shop_room.right and
                self.shop_room.top <= player.tile_y < self.shop_room.bottom)

    def draw_keeper(self, screen, camera_x, camera_y):
        if not self.shop_room:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + UI_HEIGHT)
        body_rect = pygame.Rect(sx - 12, sy - 16, 24, 32)
        pygame.draw.rect(screen, PURPLE, body_rect)
        pygame.draw.rect(screen, WHITE, body_rect, 2)
        pygame.draw.circle(screen, (255, 200, 150), (sx, sy - 18), 8)
        pygame.draw.circle(screen, BLACK, (sx - 3, sy - 19), 1)
        pygame.draw.circle(screen, BLACK, (sx + 3, sy - 19), 1)
        pygame.draw.rect(screen, CYAN, (sx - 14, sy + 14, 28, 4))
        font = pygame.font.Font(None, 18)
        text = font.render('SHOP', True, YELLOW)
        screen.blit(text, (sx - text.get_width() // 2, sy + 20))

    def draw_panel(self, screen, player):
        panel_w = 360
        panel_h = 320
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2

        pygame.draw.rect(screen, DARK_GRAY, (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), 3)
        pygame.draw.rect(screen, BLACK, (panel_x + 4, panel_y + 4,
                                          panel_w - 8, panel_h - 8))

        font_big = pygame.font.Font(None, 32)
        title = font_big.render('=== 商店 ===', True, YELLOW)
        screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2,
                            panel_y + 15))

        font = pygame.font.Font(None, 22)
        gold_text = font.render(f'金币: {player.gold}', True, GOLD)
        screen.blit(gold_text, (panel_x + 20, panel_y + 55))

        for i, item in enumerate(self.items):
            item_y = panel_y + 90 + i * 40
            bg_color = (60, 60, 80) if i == self.selected else (30, 30, 40)
            pygame.draw.rect(screen, bg_color,
                             (panel_x + 15, item_y, panel_w - 30, 35))
            if i == self.selected:
                pygame.draw.rect(screen, YELLOW,
                                 (panel_x + 15, item_y, panel_w - 30, 35), 2)

            name_text = font.render(item['name'], True, WHITE)
            screen.blit(name_text, (panel_x + 25, item_y + 7))

            cost_color = GREEN if player.gold >= item['cost'] else RED
            cost_text = font.render(f'{item["cost"]}G', True, cost_color)
            screen.blit(cost_text, (panel_x + panel_w - 80, item_y + 7))

        hint_font = pygame.font.Font(None, 18)
        hint = hint_font.render('上下键选择 | 空格购买 | ESC离开', True, LIGHT_GRAY)
        screen.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2,
                           panel_y + panel_h - 30))

    def handle_input(self, event, player):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key == pygame.K_SPACE:
                self.buy(player)
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_e:
                self.active = False

    def buy(self, player):
        item = self.items[self.selected]
        if player.gold < item['cost']:
            return
        player.gold -= item['cost']
        if item['type'] == 'atk':
            player.atk += SHOP_ATK_BONUS
        elif item['type'] == 'df':
            player.df += SHOP_DEF_BONUS
        elif item['type'] == 'maxhp':
            player.max_hp += SHOP_HP_BONUS
            player.hp = player.max_hp
        elif item['type'] == 'heal':
            player.heal(POTION_HEAL)
        elif item['type'] == 'arrow':
            player.arrows += 5
