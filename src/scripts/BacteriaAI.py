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

        # Hero'ları bul (bölünmüş olabilir)
        heroes = scene.get_objects_by_tag("hero")

        # En yakın hero'yu bul
        closest_hero = None
        min_dist = float('inf')

        for hero in heroes:
            if hero.dead:
                continue

            dx = hero.x - obj.x
            dy = hero.y - obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < min_dist:
                min_dist = dist
                closest_hero = hero

        if closest_hero and min_dist < self.detection_radius:
            # Detection radius içindeyse takip et
            self._chase(obj, closest_hero)
        else:
            # Uzakta veya hero yok, rastgele dolaş
            self._wander(obj)

        # Pozisyon güncelle
        obj.x += self.vel_x * app.dt
        obj.y += self.vel_y * app.dt

        # Çarpışma kontrolü - diğer düşmanlarla it
        self._check_enemy_collisions(obj, scene)

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

    def _check_enemy_collisions(self, obj, scene):
        """Diğer düşmanlarla çarpışma kontrolü ve itme."""
        # Tüm düşmanları bul (infected ve enemy tag'li)
        for other in scene.get_all_objects():
            if other is obj or other.dead:
                continue

            # Sadece düşmanlarla çarpış (infected veya enemy tag)
            if "infected" not in other.tags and "enemy" not in other.tags:
                continue

            # Hitbox'ları al
            my_hitbox = obj.get_component("CircleHitbox")
            other_hitbox = other.get_component("CircleHitbox")

            if not my_hitbox or not other_hitbox:
                continue

            # Mesafe hesapla
            dx = obj.x - other.x
            dy = obj.y - other.y
            dist = (dx * dx + dy * dy) ** 0.5

            # Minimum mesafe (yarıçaplar toplamı)
            min_dist = my_hitbox.radius + other_hitbox.radius

            # İç içe geçmişse it
            if 0 < dist < min_dist:
                overlap = min_dist - dist

                # Normalize yön (diğerinden uzaklaş)
                dir_x = dx / dist
                dir_y = dy / dist

                # İtme kuvveti
                push_strength = 400

                # Hıza ekle
                self.vel_x += dir_x * push_strength * App().dt
                self.vel_y += dir_y * push_strength * App().dt

    def draw(self, obj):
        """Çizim yok."""
        pass
