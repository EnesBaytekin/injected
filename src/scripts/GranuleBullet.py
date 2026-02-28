"""
Granule Bullet - Fırlatılan ilaç taneciği.
Sıvı içinde hareket eder, sürtünme ile yavaşlar, pulse animasyonu.
"""
from pygaminal import App, Screen
import pygame
import math


class GranuleBullet:
    """
    Fırlatılan granül mermisi.
    Hareket, sürtünme, pulse, lifecycle yönetir.
    """

    def __init__(self, dir_x=1.0, dir_y=0.0, speed=400, friction=1.5):
        """
        Args:
            dir_x, dir_y: Hareket yönü (normalize edilmiş)
            speed: Başlangıç hızı (piksel/saniye)
            friction: Sürtünme katsayısı
        """
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.friction = friction

        # Hız bittiğinde bekleme süresi
        self.wait_time = 0
        self.wait_duration = 1  # 1 saniye bekle
        self.is_waiting = False

        # Pulse animasyonu için
        self.base_radius = 4
        self.pulse_speed = 3.0
        self.pulse_amount = 1.5
        self.pulse_phase = 0

        # Renk
        self.color = (255, 235, 180)  # Açık sarı

    def update(self, obj):
        """Hareket, sürtünme, pulse, lifecycle güncelle."""
        app = App()

        # Hareket etmiyorsa bekle
        if self.is_waiting:
            self.wait_time += app.dt
            if self.wait_time >= self.wait_duration:
                # Obje yok et
                scene = app.get_current_scene()
                scene.remove_object(obj)
            return

        # Hareket
        # Hızı güncelle (sürtünme)
        self.speed *= (1 - self.friction * app.dt)

        # Çok düşük hızları sıfırla
        if self.speed < 5:
            self.speed = 0
            self.is_waiting = True  # Beklemeye başla
        else:
            # Pozisyon güncelle
            obj.x += self.dir_x * self.speed * app.dt
            obj.y += self.dir_y * self.speed * app.dt

        # Pulse animasyonu
        self.pulse_phase += self.pulse_speed * app.dt

    def draw(self, obj):
        """Granülü çiz - pulse efekti ile."""
        screen = Screen()

        # Pulse hesapla
        pulse = math.sin(self.pulse_phase) * self.pulse_amount
        radius = self.base_radius + pulse

        # Surface oluştur (transparan için)
        surface = pygame.Surface((int(radius * 4), int(radius * 4)), pygame.SRCALPHA)
        center = int(radius * 2)

        # Granül çiz (parlak sarı)
        color_with_alpha = (*self.color, 255)
        pygame.draw.circle(surface, color_with_alpha, (center, center), int(radius))

        # Daha parlak merkez
        highlight_color = (255, 255, 220)
        highlight_radius = radius * 0.5
        pygame.draw.circle(surface, highlight_color, (center, center), int(highlight_radius))

        # Camera transform uygula
        draw_x = obj.x - center
        draw_y = obj.y - center

        try:
            from scripts.Camera import Camera
            camera = Camera()
            draw_x, draw_y = camera.world_to_screen(draw_x, draw_y)
        except Exception as e:
            raise(e)

        # Çiz
        screen.surface.blit(surface, (draw_x, draw_y))
