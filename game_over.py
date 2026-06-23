import pygame
from constants import *


class GameOverScreen:
    def __init__(self):
        self.restart_rect = None

    def draw(self, screen, player):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        panel_w = 420
        panel_h = 380
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2

        pygame.draw.rect(screen, (40, 20, 20), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, RED, (panel_x, panel_y, panel_w, panel_h), 3)
        pygame.draw.rect(screen, BLACK, (panel_x + 5, panel_y + 5,
                                          panel_w - 10, panel_h - 10))

        font_big = pygame.font.Font(None, 52)
        title = font_big.render('你死了', True, RED)
        screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2,
                            panel_y + 25))

        font = pygame.font.Font(None, 30)

        stats = [
            ('到达层数', f'第 {player.floor} 层', CYAN),
            ('总击杀数', str(player.total_kills), ORANGE),
            ('获得金币', str(player.total_gold), GOLD),
        ]

        for i, (label, value, color) in enumerate(stats):
            y = panel_y + 110 + i * 50
            label_text = font.render(f'{label}:', True, WHITE)
            value_text = font.render(value, True, color)
            screen.blit(label_text, (panel_x + 50, y))
            screen.blit(value_text, (panel_x + panel_w - 60 - value_text.get_width(), y))
            pygame.draw.line(screen, DARK_GRAY,
                             (panel_x + 40, y + 35),
                             (panel_x + panel_w - 40, y + 35), 1)

        button_w = 200
        button_h = 50
        button_x = panel_x + panel_w // 2 - button_w // 2
        button_y = panel_y + panel_h - 80
        self.restart_rect = pygame.Rect(button_x, button_y, button_w, button_h)

        mouse = pygame.mouse.get_pos()
        hovered = self.restart_rect.collidepoint(mouse)
        btn_color = (80, 160, 80) if hovered else DARK_GREEN
        pygame.draw.rect(screen, btn_color, self.restart_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.restart_rect, 2, border_radius=8)

        btn_font = pygame.font.Font(None, 28)
        btn_text = btn_font.render('重新开始', True, WHITE)
        screen.blit(btn_text,
                    (button_x + button_w // 2 - btn_text.get_width() // 2,
                     button_y + button_h // 2 - btn_text.get_height() // 2))

        hint_font = pygame.font.Font(None, 18)
        hint = hint_font.render('点击按钮或按 R 键重新开始', True, LIGHT_GRAY)
        screen.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2,
                           panel_y + panel_h - 20))

    def handle_click(self, pos):
        if self.restart_rect and self.restart_rect.collidepoint(pos):
            return True
        return False
