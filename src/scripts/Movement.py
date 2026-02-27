"""
Yumuşak fizik tabanlı hareket sistemi.
İvme, sürtünme, mouse takibi ve yay benzeri çarpışma.
"""
import pygame
from pygaminal import App


class Movement:
    """
    Yumuşak fizik hareket sistemi.
    Mouse ile hedefe doğru çekim, çarpışmalarda yay gibi itme.
    """

    def __init__(self, acceleration=800, friction=3.0, repulsion_force=600):
        """
        Args:
            acceleration: İvme gücü (piksel/saniye²)
            friction: Sürtünme katsayısı (hız azalma oranı)
            repulsion_force: Çarpışma itme kuvveti
        """
        self.acceleration = acceleration
        self.friction = friction
        self.repulsion_force = repulsion_force

        # Fizik durumu
        self.vel_x = 0.0
        self.vel_y = 0.0

        # Mouse hedefi
        self.target_x = None
        self.target_y = None

    def set_target(self, x, y):
        """Hedef nokta belirle (mouse pozisyonu)."""
        self.target_x = x
        self.target_y = y

    def clear_target(self):
        """Hedefi temizle (çekim kuvvetini durdur)."""
        self.target_x = None
        self.target_y = None

    def update(self, obj):
        """
        Her frame çağrılır - fizik simülasyonunu günceller.
        Çekim kuvveti, sürtünme, çarpışma itmesi uygular.
        """
        app = App()

        # 1. Mouse hedefine doğru çekim kuvveti
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - obj.x
            dy = self.target_y - obj.y
            distance = (dx * dx + dy * dy) ** 0.5

            # Hedefe henüz varmadıysa kuvvet uygula
            if distance > 1:
                # Normalize yön
                dir_x = dx / distance
                dir_y = dy / distance

                # İvme uygula
                self.vel_x += dir_x * self.acceleration * app.dt
                self.vel_y += dir_y * self.acceleration * app.dt

        # 2. Çarpışma itme kuvvetleri (yay gibi)
        self._apply_repulsion(obj)

        # 3. Sürtünme uygula (hız azaltma)
        self.vel_x *= (1 - self.friction * app.dt)
        self.vel_y *= (1 - self.friction * app.dt)

        # Çok düşük hızları sıfırla
        if abs(self.vel_x) < 1:
            self.vel_x = 0
        if abs(self.vel_y) < 1:
            self.vel_y = 0

        # 4. Pozisyon güncelle
        obj.x += self.vel_x * app.dt
        obj.y += self.vel_y * app.dt

        # 5. Ekran sınırları (opsiyonel, çıkmasın)
        scene = app.get_current_scene()
        if obj.x < 0:
            obj.x = 0
            self.vel_x = 0
        if obj.x > scene.width:
            obj.x = scene.width
            self.vel_x = 0
        if obj.y < 0:
            obj.y = 0
            self.vel_y = 0
        if obj.y > scene.height:
            obj.y = scene.height
            self.vel_y = 0

    def _apply_repulsion(self, obj):
        """
        Çarpışan objelere yay benzeri itme kuvveti uygular.
        İç içe geçme miktarına göre itme gücü değişir.
        """
        scene = App().get_current_scene()
        hitbox_comp = obj.get_component("CircleHitbox")

        if not hitbox_comp:
            return

        for other_obj in scene.get_all_objects():
            if other_obj is obj:
                continue

            other_hitbox = other_obj.get_component("CircleHitbox")
            if not other_hitbox:
                continue

            # Çarpışma kontrolü
            if hitbox_comp.collides_with_circle(other_hitbox, obj, other_obj):
                # Merkezler arası mesafe ve yön
                c1 = hitbox_comp.get_world_center(obj)
                c2 = other_hitbox.get_world_center(other_obj)

                dx = c1[0] - c2[0]
                dy = c1[1] - c2[1]
                distance = (dx * dx + dy * dy) ** 0.5

                if distance == 0:
                    continue

                # Yarıçaplar toplamı
                r1 = hitbox_comp.get_world_radius()
                r2 = other_hitbox.get_world_radius()
                total_radius = r1 + r2

                # İç içe geçme miktarı
                overlap = total_radius - distance

                if overlap > 0:
                    # Normalize yön (diğerinden uzaklaş)
                    dir_x = dx / distance
                    dir_y = dy / distance

                    # İtme kuvveti (overlap ile orantılı)
                    # Ne kadar iç içe geçmişse o kadar kuvvetli it
                    push_strength = overlap * self.repulsion_force

                    # İvmeye ekle
                    self.vel_x += dir_x * push_strength * App().dt
                    self.vel_y += dir_y * push_strength * App().dt

    def get_speed(self):
        """Mevcut hızın büyüklüğünü döndür."""
        return (self.vel_x ** 2 + self.vel_y ** 2) ** 0.5

    def set_velocity(self, vx, vy):
        """Hızı manuel ayarla (dış kuvvetler için)."""
        self.vel_x = vx
        self.vel_y = vy

    def draw(self, obj):
        """Çizim yok."""
        pass
