"""
Lenf Düğümü - Bağışıklık üssü.
Enfekte hücrelerden korunması gerekir.
"""
from pygaminal import App, Screen
import pygame
import math


class LymphNode:
    """
    Lenf düğümü üssü.
    Enfekte hücreler tarafından saldırıya uğrar.
    Oyuncu tarafından korunmalıdır.
    """

    def __init__(self, radius=80, max_health=1000):
        """
        Args:
            radius: Üs yarıçapı (görsel ve collision)
            max_health: Maksimum can
        """
        self.radius = radius
        self.max_health = max_health
        self.health = max_health

        # Game over kontrolü
        self.is_dead = False

        # Nabız animasyonu
        self.pulse_phase = 0.0
        self.pulse_speed = 2.0

        # Spawn radius - enfekte hücreler buradan spawn olur
        self.spawn_radius = 300

    def update(self, obj):
        """Her frame sağlık kontrolü ve animasyon."""
        app = App()

        # Nabız animasyonu güncelle
        self.pulse_phase += self.pulse_speed * app.dt

        # Enfekte hücrelerden hasar almayı kontrol et
        self._check_infection_damage(obj)

    def _check_infection_damage(self, obj):
        """Enfekte hücrelerin temasını kontrol et."""
        scene = App().get_current_scene()

        # "infected" tag'li tüm objeleri bul
        infected_cells = scene.get_objects_by_tag("infected")

        for enemy in infected_cells:
            if enemy.dead:
                continue

            # Mesafeyi hesapla
            dx = enemy.x - obj.x
            dy = enemy.y - obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            # Enfekte hücre üs'e değdiyse hasar ver
            # Yüzeye yapışması için: tam içinde değilse ama yakınsa hasar ver
            if dist < self.radius + enemy.get_component("CircleHitbox").radius:
                # Düşman yüzeye yapışık, çok yavaş can al
                self.take_damage(0.05)  # Yarı hasar

    def take_damage(self, amount):
        """Hasar al."""
        if self.is_dead:
            return

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self._on_death()

    def _on_death(self):
        """Lenf düğümü öldüğünde - game over'ı tetikle."""
        print("LYMPH NODE DESTROYED! GAME OVER!")

        # Game over UI'sini bul ve tetikle
        scene = App().get_current_scene()
        game_over_objs = scene.get_objects_by_tag("ui")
        for obj in game_over_objs:
            game_over_comp = obj.get_component("GameOverUI")
            if game_over_comp and hasattr(game_over_comp, 'instance'):
                game_over_comp.instance.trigger_game_over()
                break

    def heal(self, amount):
        """Can al."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def get_health_percentage(self):
        """Can yüzdesini döndür (0.0 - 1.0)."""
        return self.health / self.max_health

    def _lerp_color(self, color1, color2, t):
        """İki renk arası linear interpolation."""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )

    def draw(self, obj):
        """Lenf düğümünü çiz - nabız atan yeşil daire."""
        screen = Screen()
        app = App()

        # Nabız hesapla
        pulse = math.sin(self.pulse_phase) * 0.1 + 1.0  # 0.9 - 1.1 arası
        current_radius = int(self.radius * pulse)

        # Can yüzdesine göre renk belirle - smooth geçiş
        health_pct = self.get_health_percentage()

        # Renkler
        healthy_color = (50, 200, 50)
        healthy_glow = (100, 255, 100)

        damaged_color = (200, 150, 50)
        damaged_glow = (255, 200, 100)

        critical_color = (200, 50, 50)
        critical_glow = (255, 100, 100)

        if health_pct > 0.6:
            # Sağlıklı - Yeşil (sabit)
            color = healthy_color
            glow_color = healthy_glow
        elif health_pct > 0.3:
            # Hasarlı - Yeşil'den Sarı'ya smooth geçiş
            # 0.6 -> 0.0 (yeşil), 0.3 -> 1.0 (sarı)
            t = (0.6 - health_pct) / 0.3
            color = self._lerp_color(healthy_color, damaged_color, t)
            glow_color = self._lerp_color(healthy_glow, damaged_glow, t)
        else:
            # Kritik - Sarı'dan Kırmızı'ya smooth geçiş
            # 0.3 -> 0.0 (sarı), 0.0 -> 1.0 (kırmızı)
            t = (0.3 - health_pct) / 0.3
            color = self._lerp_color(damaged_color, critical_color, t)
            glow_color = self._lerp_color(damaged_glow, critical_glow, t)

        # Camera transform
        draw_x = obj.x
        draw_y = obj.y
        try:
            from scripts.Camera import Camera
            camera = Camera()
            draw_x, draw_y = camera.world_to_screen(draw_x, draw_y)
        except:
            pass

        # Glow efekti (dış hale)
        glow_radius = current_radius + 8
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*glow_color, 50), (glow_radius, glow_radius), glow_radius)
        screen.surface.blit(glow_surface, (int(draw_x - glow_radius), int(draw_y - glow_radius)))

        # Ana daire
        pygame.draw.circle(screen.surface, color, (int(draw_x), int(draw_y)), current_radius)

        # İç kısım (daha parlak)
        inner_radius = int(current_radius * 0.6)
        pygame.draw.circle(screen.surface, glow_color, (int(draw_x), int(draw_y)), inner_radius)

        # Can barı (üzerinde)
        bar_width = 60
        bar_height = 6
        bar_x = int(draw_x - bar_width / 2)
        bar_y = int(draw_y - current_radius - 15)

        # Arkaplan
        pygame.draw.rect(screen.surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Doluluk
        fill_width = int(bar_width * health_pct)
        if fill_width > 0:
            pygame.draw.rect(screen.surface, color, (bar_x, bar_y, fill_width, bar_height))

        # Kenarlık
        pygame.draw.rect(screen.surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)
