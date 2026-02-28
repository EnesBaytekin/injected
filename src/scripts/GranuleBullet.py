"""
Granule Bullet - Fırlatılan ilaç taneciği.
Sıvı içinde hareket eder, sürtünme ile yavaşlar, pulse animasyonu.
"""
from pygaminal import App, Screen, Object
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
                # Particle efekti spawnla
                self._spawn_death_particles(obj)

                # Obje yok et
                obj.kill()
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

    def _spawn_death_particles(self, obj):
        """Bullet yok olurken mini particle patlaması oluştur."""
        from scripts.ParticleEffect import ParticleEffect
        from pygaminal import ScriptComponent

        # Particle objesi oluştur - yüksek depth ile (her şeyin önünde)
        particle_obj = Object(obj.x, obj.y, depth=1000)

        # Particle efekti ekle - mini pixel patlaması
        effect = ParticleEffect(
            particle_count=20,  # 20 tane mini particle
            shape=ParticleEffect.SHAPE_PIXEL,
            color=((255, 235, 180), (255, 200, 100)),  # Sarı -> altın
            lifetime=(0.3, 0.6),  # Kısa ömür
            size=1.0,  # 1 piksel
            velocity=50,  # Yavaş yayılma
            acceleration=(0, 0),
            spawn_mode="burst",
            one_shot=True,
            fade_out=True,
            friction=2.0,  # Hızlı yavaşla
            spread=360  # Tüm yönler
        )

        # ScriptComponent wrapper ile ekle
        script_comp = ScriptComponent("scripts/ParticleEffect", [])
        script_comp.instance = effect
        particle_obj.add_component(script_comp)

        # Sahneye ekle
        scene = App().get_current_scene()
        scene.add_object(particle_obj)

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
