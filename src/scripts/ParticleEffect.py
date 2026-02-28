"""
Particle Effect - Görsel particle sistemi.
Patlamalar, izler, tozlar vb. efektler için kullanılır.
"""
from pygaminal import App, Screen
import pygame
import random
import math


class ParticleEffect:
    """
    Particle efekti yöneticisi.
    Tek bir objeden yüzlerce particle çizer ve günceller.
    """

    # Şekil tipleri
    SHAPE_PIXEL = "pixel"
    SHAPE_SQUARE = "square"
    SHAPE_CIRCLE = "circle"
    SHAPE_SHRINKING_CIRCLE = "shrinking_circle"

    def __init__(self,
                 particle_count=50,
                 shape=SHAPE_CIRCLE,
                 color=(255, 255, 255),
                 lifetime=1.0,
                 size=3.0,
                 velocity=(0, 0),
                 acceleration=(0, 0),
                 spawn_mode="burst",
                 one_shot=True,
                 fade_out=True,
                 friction=0.0,
                 gravity=0.0,
                 spread=360):
        """
        Args:
            particle_count: Kaç tane particle oluştur
            shape: Şekil tipi (pixel, square, circle, shrinking_circle)
            color: Renk (R,G,B) veya ((R,G,B), (R,G,B)) için min-max range
            lifetime: Yaşam süresi (saniye) veya (min, max) için range
            size: Boyut veya (min, max) için range
            velocity: Başlangıç hızı (vx, vy) veya ((vx_min, vx_max), (vy_min, vy_max))
            acceleration: İvme (ax, ay)
            spawn_mode: "burst" (hepsi aynı anda) veya "stream" (sürekli)
            one_shot: True ise particle'lar bitince objeyi de yok et
            fade_out: True ise alpha zamanla azalır
            friction: Hava sürtünmesi (0-1)
            gravity: Yerçekimi kuvveti
            spread: Hız yayılma açısı (derece), 360 = tüm yönler
        """
        self.particle_count = particle_count
        self.shape = shape
        self.color = color
        self.lifetime = lifetime
        self.size = size
        self.velocity = velocity
        self.acceleration = acceleration
        self.spawn_mode = spawn_mode
        self.one_shot = one_shot
        self.fade_out = fade_out
        self.friction = friction
        self.gravity = gravity
        self.spread = spread

        # Particle listesi
        self.particles = []
        self._spawned_count = 0
        self._spawn_timer = 0

        # Stream mode için spawn rate
        self._stream_spawn_rate = None
        if spawn_mode == "stream":
            # Particle' lifetime boyunca yayınla
            self._stream_spawn_rate = lifetime / particle_count if lifetime > 0 else 0.1

    def _parse_range(self, value):
        """Tek değer veya (min, max) tuple'ından rastgele değer al."""
        if isinstance(value, tuple) and len(value) == 2:
            return random.uniform(value[0], value[1])
        return value

    def _parse_range_int(self, value):
        """Integer range için."""
        if isinstance(value, tuple) and len(value) == 2:
            return random.randint(value[0], value[1])
        return int(value)

    def _get_color(self):
        """Renk range'inden rastgele renk al."""
        if isinstance(self.color, tuple) and len(self.color) == 2:
            # İki renk arası interpolate
            c1, c2 = self.color
            t = random.random()
            return (
                int(c1[0] + (c2[0] - c1[0]) * t),
                int(c1[1] + (c2[1] - c1[1]) * t),
                int(c1[2] + (c2[2] - c1[2]) * t)
            )
        return self.color

    def _get_velocity(self):
        """
        Hız range'inden rastgele hız al.
        Polar koordinatla (açı + hız) - doğal dairesel dağılım.
        Küçük hızlar daha fazla, büyükler daha az (merkezde yoğunlaşmak için).
        """
        if isinstance(self.velocity, tuple) and len(self.velocity) == 2:
            # Speed range
            speed_min, speed_max = self.velocity

            # Küçük hızların daha fazla olması için random()^2 kullan
            # Bu 0-1 arası verir ama 0'a yakın değerleri daha fazla üretir
            t = random.random()
            biased_t = t * t  # Küçük değerleri daha fazla

            speed = speed_min + (speed_max - speed_min) * biased_t

            # Rastgele açı (0-360) - dairesel uniform dağılım
            angle = random.uniform(0, 360)

            rad = math.radians(angle)
            vx = math.cos(rad) * speed
            vy = math.sin(rad) * speed
        else:
            speed = self.velocity
            angle = random.uniform(0, 360)

            # Spread uygula
            if self.spread < 360:
                angle = random.uniform(-self.spread/2, self.spread/2)

            rad = math.radians(angle)
            vx = math.cos(rad) * speed
            vy = math.sin(rad) * speed

        return vx, vy

    def _spawn_particle(self, obj_x, obj_y):
        """Yeni particle oluştur."""
        # lifetime
        lifetime = self._parse_range(self.lifetime)

        # Renk
        color = self._get_color()

        # Boyut
        size = self._parse_range(self.size)

        # Hız
        vx, vy = self._get_velocity()

        # Particle dict
        particle = {
            'x': obj_x,
            'y': obj_y,
            'vx': vx,
            'vy': vy,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'color': color,
            'size': size,
            'initial_size': size
        }

        self.particles.append(particle)
        self._spawned_count += 1

    def update(self, obj):
        """Particle'ları güncelle."""
        app = App()
        scene = app.get_current_scene()

        # Spawn
        if self.spawn_mode == "burst" and self._spawned_count == 0:
            # Hepsini aynı anda spawnla
            for _ in range(self.particle_count):
                self._spawn_particle(obj.x, obj.y)
        elif self.spawn_mode == "stream":
            # Sürekli spawnla
            if self._spawned_count < self.particle_count:
                self._spawn_timer += app.dt
                if self._spawn_timer >= self._stream_spawn_rate:
                    self._spawn_particle(obj.x, obj.y)
                    self._spawn_timer = 0

        # Update particle'lar
        alive_particles = []

        for p in self.particles:
            # Lifetime azalt
            p['lifetime'] -= app.dt

            if p['lifetime'] > 0:
                # Fizik
                p['vx'] += self.acceleration[0] * app.dt
                p['vy'] += (self.acceleration[1] + self.gravity) * app.dt

                # Friction
                if self.friction > 0:
                    p['vx'] *= (1 - self.friction * app.dt)
                    p['vy'] *= (1 - self.friction * app.dt)

                # Pozisyon güncelle
                p['x'] += p['vx'] * app.dt
                p['y'] += p['vy'] * app.dt

                # Shrinking circle için boyut güncelle
                if self.shape == self.SHAPE_SHRINKING_CIRCLE:
                    progress = 1 - (p['lifetime'] / p['max_lifetime'])
                    p['size'] = p['initial_size'] * (1 - progress)

                alive_particles.append(p)

        self.particles = alive_particles

        # One shot ve bitince objeyi yok et
        if self.one_shot and len(self.particles) == 0 and self._spawned_count >= self.particle_count:
            scene.remove_object(obj)

    def draw(self, obj):
        """Particle'ları çiz - her şeyin önünde."""
        screen = Screen()
        app = App()

        # Tüm particle'ları çiz
        for p in self.particles:
            # Alpha hesapla
            alpha = 255
            if self.fade_out:
                progress = 1 - (p['lifetime'] / p['max_lifetime'])
                alpha = int(255 * (1 - progress))

            if alpha <= 0:
                continue

            # Screen pozisyonu - camera transform uygula
            screen_x = p['x']
            screen_y = p['y']
            try:
                from scripts.Camera import Camera
                camera = Camera()
                screen_x, screen_y = camera.world_to_screen(screen_x, screen_y)
            except:
                pass

            size = p['size']

            # Şekil tipine göre çiz
            if self.shape == self.SHAPE_PIXEL:
                # Tek pixel
                color_with_alpha = (*p['color'], alpha)
                screen.surface.set_at((int(screen_x), int(screen_y)), color_with_alpha)

            elif self.shape == self.SHAPE_SQUARE:
                # Kare
                surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
                color_with_alpha = (*p['color'], alpha)
                surface.fill(color_with_alpha)
                screen.surface.blit(surface, (int(screen_x - size), int(screen_y - size)))

            elif self.shape == self.SHAPE_CIRCLE:
                # Daire
                radius = int(size)
                surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                color_with_alpha = (*p['color'], alpha)
                pygame.draw.circle(surface, color_with_alpha, (radius, radius), radius)
                screen.surface.blit(surface, (int(screen_x - radius), int(screen_y - radius)))

            elif self.shape == self.SHAPE_SHRINKING_CIRCLE:
                # Küçülen daire
                radius = max(1, int(size))
                surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                color_with_alpha = (*p['color'], alpha)
                pygame.draw.circle(surface, color_with_alpha, (radius, radius), radius)
                screen.surface.blit(surface, (int(screen_x - radius), int(screen_y - radius)))
