"""
Bakteri AI - Oyuncuyu takip eden agresif düşman.
Hero'ya doğru koşar, saldırır.
"""
from pygaminal import App
import math


class BacteriaAI:
    """
    Bakteri yapay zekası.
    Oyuncuyu takip eder ve saldırır.
    """

    def __init__(self, speed=80, detection_radius=200):
        """
        Args:
            speed: Hız (piksel/saniye)
            detection_radius: Oyuncuyu algılama mesafesi
        """
        self.speed = speed
        self.detection_radius = detection_radius

        # Hareket durumu
        self.vel_x = 0.0
        self.vel_y = 0.0

    def update(self, obj):
        """Her frame oyuncuyu takip et."""
        # Chunk kontrolü - performans için
        if hasattr(obj, '_chunk_active') and not obj._chunk_active:
            return  # Uzakta, update yapma

        app = App()
        scene = app.get_current_scene()

        # Hero'yu bul
        heroes = scene.get_objects_by_tag("hero")

        if not heroes or heroes[0].dead:
            # Hero yoksa rastgele dolaş
            self._wander(obj)
        else:
            hero = heroes[0]

            # Mesafeyi hesapla
            dx = hero.x - obj.x
            dy = hero.y - obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            # Detection radius içindeyse takip et
            if dist < self.detection_radius:
                self._chase(obj, hero)
            else:
                # Uzakta, rastgele dolaş
                self._wander(obj)

        # Pozisyon güncelle
        obj.x += self.vel_x * app.dt
        obj.y += self.vel_y * app.dt

    def _chase(self, obj, target):
        """Hedefe doğru kovala."""
        dx = target.x - obj.x
        dy = target.y - obj.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > 1:
            # Normalize yön
            dir_x = dx / distance
            dir_y = dy / distance

            # Hız uygula
            self.vel_x = dir_x * self.speed
            self.vel_y = dir_y * self.speed
        else:
            # Hedefe çok yakın, dur
            self.vel_x = 0
            self.vel_y = 0

    def _wander(self, obj):
        """Uzakta iken rastgele dolaş."""
        import random
        if not hasattr(self, '_wander_timer'):
            self._wander_timer = 0
            self._wander_dir_x = random.uniform(-1, 1)
            self._wander_dir_y = random.uniform(-1, 1)

        self._wander_timer += App().dt

        # Her 3 saniyede yeni yön
        if self._wander_timer > 3.0:
            self._wander_timer = 0
            self._wander_dir_x = random.uniform(-1, 1)
            self._wander_dir_y = random.uniform(-1, 1)

        # Normalize
        mag = (self._wander_dir_x**2 + self._wander_dir_y**2) ** 0.5
        if mag > 0:
            self._wander_dir_x /= mag
            self._wander_dir_y /= mag

        self.vel_x = self._wander_dir_x * self.speed * 0.3  # Yavaş dolaş
        self.vel_y = self._wander_dir_y * self.speed * 0.3

    def draw(self, obj):
        """Çizim yok."""
        pass
