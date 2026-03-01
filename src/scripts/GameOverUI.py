"""
GameOver UI - Lenf düğümü enfekte olduğunda gösterilen ekran.
Player kontrollerini kapatır, kamerayı lenf düğümüne odaklar.
"""
from pygaminal import App, Screen, InputManager
import pygame
import math


class GameOverUI:
    """
    Game Over ekranı.
    Lenf düğümü enfekte olduğunda aktif olur.
    """

    def __init__(self):
        self.is_game_over = False
        self.fade_alpha = 0.0
        self.fade_speed = 150.0  # Çok hızlı fade-in (~1 saniye)

        # Buton bilgisi
        self.button_rect = None
        self.button_hovered = False

        # Lenf düğümü pozisyonu
        self.lymph_node_pos = (0, 0)

    def trigger_game_over(self):
        """Game over'ı tetikle."""
        if self.is_game_over:
            return  # Zaten game over

        self.is_game_over = True
        self.fade_alpha = 0.0

        # Lenf düğümü pozisyonunu al
        scene = App().get_current_scene()
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        if lymph_nodes and not lymph_nodes[0].dead:
            self.lymph_node_pos = (lymph_nodes[0].x, lymph_nodes[0].y)

        # Player kontrollerini devre dışı bırak
        heroes = scene.get_objects_by_tag("hero")
        for hero in heroes:
            if not hero.dead:
                # PlayerController component'ini bul
                controller = hero.get_component("PlayerController")
                if controller:
                    controller.instance.enabled = False

                # ShootingController'ı da devre dışı bırak
                shooting = hero.get_component("ShootingController")
                if shooting:
                    shooting.instance.enabled = False

                # SplitController'ı da devre dışı bırak
                split = hero.get_component("SplitController")
                if split:
                    split.instance.enabled = False

        print("GAME OVER: Lymph node infected!")

    def update(self, obj):
        """Fade-in animasyonunu güncelle ve mouse click'i kontrol et."""
        if not self.is_game_over:
            return

        app = App()
        screen = Screen()

        # Fade alpha'yı artır (hızlı)
        self.fade_alpha += self.fade_speed * app.dt
        if self.fade_alpha > 180:  # Max 180/255 = ~70% opacity
            self.fade_alpha = 180

        # Kamerayı her zaman lenf düğümüne odakla (fade boyunca)
        from scripts.Camera import Camera
        camera = Camera()

        # Lenf düğümünü ekranın tam ortasına al
        target_cam_x = self.lymph_node_pos[0] - screen.width / 2
        target_cam_y = self.lymph_node_pos[1] - screen.height / 2

        # Daha hızlı kamera hareketi
        camera.x += (target_cam_x - camera.x) * 3.0 * app.dt
        camera.y += (target_cam_y - camera.y) * 3.0 * app.dt

        # Target'i temizle (manuel güncelliyoruz)
        camera.clear_target()

        # Mouse click kontrolü (fade bitince)
        if self.fade_alpha >= 180:
            input_manager = InputManager()
            if input_manager.is_mouse_just_pressed(1):  # Sol click
                self.handle_click()

    def draw(self, obj):
        """Game over ekranını çiz."""
        if not self.is_game_over:
            return

        screen = Screen()

        # DEBUG
        print(f"Drawing game over screen, alpha: {self.fade_alpha}")

        # Transparent siyah overlay
        if self.fade_alpha > 0:
            overlay = pygame.Surface((screen.width, screen.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.fade_alpha)))
            screen.surface.blit(overlay, (0, 0))
            print("  Overlay drawn")

        # Fade bittiyse yazıları çiz
        if self.fade_alpha >= 180:
            print("Drawing text...")
            self._draw_text(screen)

    def _draw_text(self, screen):
        """Game over yazılarını çiz."""
        # DEBUG
        print("  _draw_text called")

        # Font'ları yükle (ekran boyutuna göre scale)
        try:
            title_font = pygame.font.Font(None, 36)  # 72 → 36
            subtitle_font = pygame.font.Font(None, 20)  # 36 → 20
            button_font = pygame.font.Font(None, 24)  # 32 → 24
            print("  Fonts loaded")
        except Exception as e:
            print(f"Error loading fonts: {e}")
            return

        # Başlık (üste yakın ama ortada)
        title_text = "LYMPH NODE INFECTED"
        title_surf = title_font.render(title_text, True, (200, 50, 50))
        title_rect = title_surf.get_rect(center=(screen.width / 2, screen.height * 0.25))
        screen.surface.blit(title_surf, title_rect)

        # Alt başlık (başlığın altında)
        subtitle_text = "The infection has overwhelmed"
        subtitle_surf = subtitle_font.render(subtitle_text, True, (150, 150, 150))
        subtitle_rect = subtitle_surf.get_rect(center=(screen.width / 2, screen.height * 0.35))
        screen.surface.blit(subtitle_surf, subtitle_rect)

        # İkinci alt başlık
        subtitle_text2 = "your defenses"
        subtitle_surf2 = subtitle_font.render(subtitle_text2, True, (150, 150, 150))
        subtitle_rect2 = subtitle_surf2.get_rect(center=(screen.width / 2, screen.height * 0.40))
        screen.surface.blit(subtitle_surf2, subtitle_rect2)

        # Main Menu butonu (ortada biraz aşağıda)
        button_width = 140  # 200 → 140
        button_height = 40  # 50 → 40
        button_x = screen.width / 2 - button_width / 2
        button_y = screen.height * 0.6  # Ekranın %60'ı

        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Buton rengi (hover ile değişir)
        mouse_pos = pygame.mouse.get_pos()
        self.button_hovered = self.button_rect.collidepoint(mouse_pos)

        button_color = (100, 100, 120) if self.button_hovered else (70, 70, 90)
        pygame.draw.rect(screen.surface, button_color, self.button_rect, border_radius=6)
        pygame.draw.rect(screen.surface, (150, 150, 170), self.button_rect, 2, border_radius=6)

        # Buton yazısı
        button_text = "MAIN MENU"
        button_text_surf = button_font.render(button_text, True, (255, 255, 255))
        button_text_rect = button_text_surf.get_rect(center=self.button_rect.center)
        screen.surface.blit(button_text_surf, button_text_rect)

    def handle_click(self):
        """Buton tıklamasını kontrol et."""
        if self.is_game_over and self.fade_alpha >= 180 and self.button_hovered:
            # Menu sahnesine dön
            app = App()
            app.set_scene("menu")

            # Game over'ı resetle
            self.is_game_over = False
            self.fade_alpha = 0.0

            print("Returning to main menu...")
