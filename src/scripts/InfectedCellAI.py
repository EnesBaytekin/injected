"""
Enfekte Hücre AI - Lenf düğümüne saldıran düşman.
Üs'e doğru yavaşça yaklaşır.
"""
from pygaminal import App, Object
import pygame
import math


class InfectedCellAI:
    """
    Enfekte hücre yapay zekası.
    Lenf düğümüne doğru saldırır.
    """

    def __init__(self, speed=50):
        """
        Args:
            speed: Hız (piksel/saniye)
        """
        self.speed = speed

        # Joystick değil, otomatik hareket
        self.vel_x = 0.0
        self.vel_y = 0.0

    def update(self, obj):
        """Her frame üs'e doğru hareket."""
        # Chunk kontrolü - performans için
        if hasattr(obj, '_chunk_active') and not obj._chunk_active:
            return  # Uzakta, update yapma

        app = App()
        scene = app.get_current_scene()

        # Lenf düğümünü bul
        lymph_nodes = scene.get_objects_by_tag("lymph_node")

        if not lymph_nodes or lymph_nodes[0].dead:
            # Üs yoksa rastgele dolaş
            self._wander(obj)
        else:
            # En yakın lenf düğümünü bul
            target = self._find_closest_lymph_node(obj, lymph_nodes)

            if target:
                # Üs'e doğru hareket et
                self._move_towards(obj, target)
            else:
                self._wander(obj)

        # Pozisyon güncelle
        obj.x += self.vel_x * app.dt
        obj.y += self.vel_y * app.dt

        # Çarpışma kontrolü - diğer düşmanlarla it
        self._check_enemy_collisions(obj, scene)

    def _find_closest_lymph_node(self, obj, nodes):
        """En yakın lenf düğümünü bul."""
        closest = None
        min_dist = float('inf')

        for node in nodes:
            if node.dead:
                continue

            dx = node.x - obj.x
            dy = node.y - obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < min_dist:
                min_dist = dist
                closest = node

        return closest

    def _move_towards(self, obj, target):
        """Hedefe doğru hareket et - yüzeyinde dur."""
        dx = target.x - obj.x
        dy = target.y - obj.y
        distance = (dx * dx + dy * dy) ** 0.5

        # Lenf düğümünün ve düşmanın yarıçapını al
        target_lymph = target.get_component("LymphNode")
        my_hitbox = obj.get_component("CircleHitbox")

        if target_lymph and my_hitbox:
            # Yüzeyde durma mesafesi
            stop_distance = target_lymph.radius - my_hitbox.radius
        else:
            stop_distance = 1

        if distance > stop_distance:
            # Normalize yön
            dir_x = dx / distance
            dir_y = dy / distance

            # Hız uygula
            self.vel_x = dir_x * self.speed
            self.vel_y = dir_y * self.speed
        else:
            # Yüzeye vardı, dur
            self.vel_x = 0
            self.vel_y = 0

    def _wander(self, obj):
        """Üs yoksa rastgele dolaş."""
        # Basit rastgele hareket
        # Her X saniyede yeni yön seç
        import random
        if not hasattr(self, '_wander_timer'):
            self._wander_timer = 0
            self._wander_dir_x = random.uniform(-1, 1)
            self._wander_dir_y = random.uniform(-1, 1)

        self._wander_timer += App().dt

        # Her 2 saniyede yeni yön
        if self._wander_timer > 2.0:
            self._wander_timer = 0
            self._wander_dir_x = random.uniform(-1, 1)
            self._wander_dir_y = random.uniform(-1, 1)

        # Normalize
        mag = (self._wander_dir_x**2 + self._wander_dir_y**2) ** 0.5
        if mag > 0:
            self._wander_dir_x /= mag
            self._wander_dir_y /= mag

        self.vel_x = self._wander_dir_x * self.speed * 0.5  # Yavaşça dolaş
        self.vel_y = self._wander_dir_y * self.speed * 0.5

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

                # İtme kuvveti (ne kadar iç içe, o kadar kuvvetli)
                push_strength = 400

                # Hıza ekle
                self.vel_x += dir_x * push_strength * App().dt
                self.vel_y += dir_y * push_strength * App().dt

    def draw(self, obj):
        """Çizim yok."""
        pass
