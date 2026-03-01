"""
Main Menu UI - Ana menü ekranı.
OYNA ve QUIT butonları.
"""
from pygaminal import App, Screen, InputManager, Scene
import pygame
import math
import random


class MenuUI:
    """
    Ana menü.
    OYNA ve QUIT butonlarını gösterir.
    """

    def __init__(self):
        # Buton bilgisi
        self.play_button_rect = None
        self.quit_button_rect = None
        self.hovered_button = None  # 'play', 'quit', veya None

        # Animasyon
        self.time = 0.0

        # Arka plan hücreleri
        self.bg_cells = []
        for _ in range(8):
            self.bg_cells.append({
                'x': random.random() * 320,
                'y': random.random() * 180,
                'radius': 10 + random.random() * 20,
                'speed': 5 + random.random() * 10,
                'angle': random.random() * math.pi * 2
            })

    def update(self, obj):
        """Animasyonları güncelle."""
        app = App()
        self.time += app.dt

        # Arka plan hücrelerini hareket ettir
        for cell in self.bg_cells:
            cell['x'] += math.cos(cell['angle']) * cell['speed'] * app.dt
            cell['y'] += math.sin(cell['angle']) * cell['speed'] * app.dt

            # Ekran dışına çıkarsa karşıdan geri getir
            if cell['x'] < -50:
                cell['x'] = 370
            elif cell['x'] > 370:
                cell['x'] = -50
            if cell['y'] < -50:
                cell['y'] = 230
            elif cell['y'] > 230:
                cell['y'] = -50

        # Mouse hover kontrolü
        input_manager = InputManager()
        mouse_pos = input_manager.get_mouse_position()

        self.hovered_button = None
        if self.play_button_rect and self.play_button_rect.collidepoint(mouse_pos):
            self.hovered_button = 'play'
        elif self.quit_button_rect and self.quit_button_rect.collidepoint(mouse_pos):
            self.hovered_button = 'quit'

        # Click kontrolü
        if input_manager.is_mouse_just_pressed(1):
            self._handle_click()

    def _handle_click(self):
        """Buton tıklamasını kontrol et."""
        if self.hovered_button == 'play':
            # Oyun sahnesine geç
            app = App()
            app.set_scene("game")
            print("Starting game...")

        elif self.hovered_button == 'quit':
            # Oyundan çık
            app = App()
            app.stop()
            print("Quitting...")

    def draw(self, obj):
        """Ana menüyü çiz."""
        screen = Screen()

        # Arka plan (gradient)
        self._draw_background(screen)

        # Arka plan hücreleri
        self._draw_bg_cells(screen)

        # Başlık ve butonlar
        self._draw_title_and_buttons(screen)

    def _draw_background(self, screen):
        """Gradient arka plan."""
        # Koyu kırmızımsı gradient
        for y in range(screen.height):
            # Üstten alta doğru renk değişimi
            t = y / screen.height
            r = int(40 + t * 20)  # 40 → 60
            g = int(10 + t * 10)  # 10 → 20
            b = int(20 + t * 10)  # 20 → 30
            pygame.draw.line(screen.surface, (r, g, b), (0, y), (screen.width, y))

    def _draw_bg_cells(self, screen):
        """Arka planda yüzen hücreler."""
        for cell in self.bg_cells:
            # Hücre rengi (sarımsı, yarı saydam)
            color = (255, 200, 100, 50)  # RGBA
            radius = int(cell['radius'])

            # Surface oluştur (transparan için)
            cell_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(cell_surf, color, (radius, radius), radius)

            # Ekrana çiz
            screen.surface.blit(cell_surf, (int(cell['x'] - radius), int(cell['y'] - radius)))

    def _draw_title_and_buttons(self, screen):
        """Başlık ve butonları çiz."""
        # Font modülünü init et
        pygame.font.init()

        # Font'lar - küçültüldü
        try:
            title_font = pygame.font.Font(None, 36)  # 64 → 36
            button_font = pygame.font.Font(None, 24)  # 32 → 24
        except Exception as e:
            print(f"Error loading fonts: {e}")
            return

        # BAŞLIK: "INJECTED"
        title_text = "INJECTED"
        title_surf = title_font.render(title_text, True, (255, 220, 100))

        # Glow efekti
        title_glow = title_font.render(title_text, True, (255, 180, 50))
        for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            glow_rect = title_glow.get_rect(center=(screen.width / 2 + offset[0], screen.height * 0.2 + offset[1]))
            screen.surface.blit(title_glow, glow_rect)

        # Ana başlık
        title_rect = title_surf.get_rect(center=(screen.width / 2, screen.height * 0.2))
        screen.surface.blit(title_surf, title_rect)

        # OYNA butonu
        play_button_width = 120  # Küçültüldü
        play_button_height = 40  # Küçültüldü
        play_button_x = screen.width / 2 - play_button_width / 2
        play_button_y = screen.height * 0.45  # Biraz yukarı

        self.play_button_rect = pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)

        # Buton rengi (hover ile değişir)
        play_color = (120, 180, 100) if self.hovered_button == 'play' else (80, 140, 60)
        pygame.draw.rect(screen.surface, play_color, self.play_button_rect, border_radius=8)
        pygame.draw.rect(screen.surface, (180, 220, 160), self.play_button_rect, 2, border_radius=8)

        # Buton yazısı
        play_text = "OYNA"
        play_text_surf = button_font.render(play_text, True, (255, 255, 255))
        play_text_rect = play_text_surf.get_rect(center=self.play_button_rect.center)
        screen.surface.blit(play_text_surf, play_text_rect)

        # QUIT butonu
        quit_button_width = 120  # Küçültüldü
        quit_button_height = 40  # Küçültüldü
        quit_button_x = screen.width / 2 - quit_button_width / 2
        quit_button_y = screen.height * 0.45 + 50  # OYNA butonunun 50px altı

        self.quit_button_rect = pygame.Rect(quit_button_x, quit_button_y, quit_button_width, quit_button_height)

        # Buton rengi (hover ile değişir)
        quit_color = (180, 100, 100) if self.hovered_button == 'quit' else (140, 60, 60)
        pygame.draw.rect(screen.surface, quit_color, self.quit_button_rect, border_radius=8)
        pygame.draw.rect(screen.surface, (220, 140, 140), self.quit_button_rect, 2, border_radius=8)

        # Buton yazısı
        quit_text = "QUIT"
        quit_text_surf = button_font.render(quit_text, True, (255, 255, 255))
        quit_text_rect = quit_text_surf.get_rect(center=self.quit_button_rect.center)
        screen.surface.blit(quit_text_surf, quit_text_rect)
