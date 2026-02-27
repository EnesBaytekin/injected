"""
Dairesel hitbox component'i.
Hücre oyunu için radius bazlı çarpışma kontrolü.
"""
import pygame
from pygaminal import Screen

class CircleHitbox:
    """Dairesel hitbox - radius bazlı çarpışma kontrolü."""

    def __init__(self, radius, offset_x=0, offset_y=0):
        """
        Args:
            radius: Daire yarıçapı
            offset_x: X offset (obje merkezinden)
            offset_y: Y offset (obje merkezinden)
        """
        self.radius = radius
        self.offset_x = offset_x
        self.offset_y = offset_y

    def get_world_center(self, obj):
        """
        Dünyadaki merkez noktasını al.

        Returns:
            tuple: (center_x, center_y)
        """
        return (obj.x + self.offset_x, obj.y + self.offset_y)

    def get_world_radius(self):
        """Dünyadaki yarıçap."""
        return self.radius

    def collides_with_circle(self, other_circle_hitbox, obj1, obj2):
        """
        Başka bir CircleHitbox ile çarpışma kontrolü.

        Args:
            other_circle_hitbox: Diğer CircleHitbox instance
            obj1: Bu obje
            obj2: Diğer obje

        Returns:
            bool: Çarpışma varsa True
        """
        c1 = self.get_world_center(obj1)
        r1 = self.get_world_radius()

        c2 = other_circle_hitbox.get_world_center(obj2)
        r2 = other_circle_hitbox.get_world_radius()

        # İki daire arası mesafe
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        distance = (dx * dx + dy * dy) ** 0.5

        # Çarpışma: mesafe < yarıçaplar toplamı
        return distance < (r1 + r2)

    def collides_with_point(self, point_x, point_y, obj):
        """
        Bir nokta ile çarpışma kontrolü.

        Args:
            point_x, point_y: Nokta koordinatları
            obj: Bu obje

        Returns:
            bool: Nokta daire içindeyse True
        """
        center = self.get_world_center(obj)
        dx = center[0] - point_x
        dy = center[1] - point_y
        distance = (dx * dx + dy * dy) ** 0.5

        return distance < self.radius

    def draw_debug(self, obj):
        """
        Debug çizim (opsiyonel).
        Çağırmak için draw() içinde kullanılabilir.
        """

        screen = Screen()
        center = self.get_world_center(obj)

        # Yeşil çember çiz (debug için)
        pygame.draw.circle(
            screen.surface,
            (0, 255, 0),
            (int(center[0]), int(center[1])),
            int(self.radius),
            1
        )

    def update(self, obj):
        """Hitbox güncellemesi gereksiz."""
        pass

    def draw(self, obj):
        """Çizim yok (debug için draw_debug kullanılabilir)."""
