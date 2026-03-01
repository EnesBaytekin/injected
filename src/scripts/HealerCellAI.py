"""
Healer Cell AI - Lenf düğümüne yaklaşan, bağ kuran, can basan dost hücre.
Virüslerden dönüşür.
"""
from pygaminal import App, Object
import math


class HealerCellAI:
    """
    İyileştirici hücre yapay zekası.
    Lenf düğümüne yaklaşır, bağ kurar, can basar.
    """

    def __init__(self, target_distance=80, approach_speed=60):
        """
        Args:
            target_distance: Lenf düğümünden ne kadar uzakta duracak (piksel)
            approach_speed: Yaklaşma hızı (piksel/saniye)
        """
        print(f"HealerCellAI.__init__() called - target_dist={target_distance}, speed={approach_speed}")

        self.target_distance = target_distance
        self.approach_speed = approach_speed

        # Bağlantı durumu
        self.is_connected = False
        self.heal_timer = 0.0
        self.heal_interval = 0.5  # Her 0.5 saniyede bir can bas

        # Hareket
        self.vel_x = 0.0
        self.vel_y = 0.0

    def update(self, obj):
        """Lenf düğümüne yaklaş, bağ kur, can bas."""
        app = App()
        scene = app.get_current_scene()

        # DEBUG
        print(f"HealerCellAI.update() - pos: ({obj.x:.1f}, {obj.y:.1f})")

        # Lenf düğümünü bul
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        print(f"  Lymph nodes: {len(lymph_nodes)}")

        if not lymph_nodes or lymph_nodes[0].dead:
            print("  No lymph node!")
            return  # Lenf düğümü yok, bekle

        node = lymph_nodes[0]
        print(f"  Node pos: ({node.x:.1f}, {node.y:.1f})")

        # Lenf düğümüne olan mesafeyi hesapla
        dx = node.x - obj.x
        dy = node.y - obj.y
        dist = (dx * dx + dy * dy) ** 0.5
        print(f"  Distance: {dist:.1f}, target: {self.target_distance}")

        # Bağlantı mesafı kontrolü
        connection_break_distance = self.target_distance * 1.5  # %50 uzaklaşınca kopar

        if dist <= self.target_distance:
            # Hedef mesafede - bağ kurabilir
            self.is_connected = True
            print("  Connected!")

            # Çok yaklaştıysa biraz geri çekil
            if dist < self.target_distance * 0.8:
                print("  Too close, backing up...")
                if dist > 0:
                    dir_x = -dx / dist
                    dir_y = -dy / dist
                    move_x = dir_x * self.approach_speed * app.dt * 0.5
                    move_y = dir_y * self.approach_speed * app.dt * 0.5
                    obj.x += move_x
                    obj.y += move_y
        elif dist > connection_break_distance:
            # Çok uzaklaştı - bağ koparıldı, yaklaş!
            self.is_connected = False
            print("  Too far, disconnected - APPROACHING!")
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                move_x = dir_x * self.approach_speed * app.dt
                move_y = dir_y * self.approach_speed * app.dt
                obj.x += move_x
                obj.y += move_y
        else:
            # Hedef mesafeye yaklaş
            print("  Approaching...")
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                move_x = dir_x * self.approach_speed * app.dt
                move_y = dir_y * self.approach_speed * app.dt
                obj.x += move_x
                obj.y += move_y

        # Bağlıysa can bas
        if self.is_connected:
            self.heal_timer += app.dt
            if self.heal_timer >= self.heal_interval:
                self.heal_timer = 0.0
                self._heal_lymph_node(node)

    def _heal_lymph_node(self, node):
        """Lenf düğümüne can bas."""
        from scripts.LymphNode import LymphNode

        lymph_node_comp = node.get_component("LymphNode")
        if lymph_node_comp and hasattr(lymph_node_comp.instance, 'heal'):
            # Her seferinde 5 can bas
            lymph_node_comp.instance.heal(5)
            print(f"Healer cell healed lymph node (+5 HP)")

    def draw(self, obj):
        """Çizim yok."""
        pass
