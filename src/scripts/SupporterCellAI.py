"""
Supporter Cell AI - Spawner'a yaklaşan, can basan düşman hücresi.
Spawner'dan bölünerek doğar.
"""
from pygaminal import App, Object
import math


class SupporterCellAI:
    """
    Spawner'a can basan düşman yapay zekası.
    Spawner'a yaklaşır, bağ kurar, can basar.
    """

    def __init__(self, target_distance=30, heal_speed=40):
        """
        Args:
            target_distance: Spawner'dan ne kadar uzakta duracak (piksel)
            heal_speed: Yaklaşma hızı (piksel/saniye)
        """
        self.target_distance = target_distance
        self.heal_speed = heal_speed

        # Parent spawner (hangi spawner'dan doğdu)
        self.parent_spawner = None

        # Bağlantı durumu
        self.is_connected = False
        self.heal_timer = 0.0
        self.heal_interval = 1.0  # Her 1 saniyede bir can bas

        # Hareket
        self.vel_x = 0.0
        self.vel_y = 0.0

    def set_parent_spawner(self, spawner_obj):
        """Parent spawner'ı set et - hangi spawner'dan doğdu."""
        self.parent_spawner = spawner_obj

    def update(self, obj):
        """Spawner'a yaklaş, bağ kur, can bas."""
        app = App()
        scene = app.get_current_scene()

        # Önce parent spawner'ı kontrol et
        spawner = None
        if self.parent_spawner and not self.parent_spawner.dead:
            spawner = self.parent_spawner
        else:
            # Parent yoksa veya öldüyse, herhangi bir spawner'ı bul
            spawners = scene.get_objects_by_tag("enemy_spawner")
            if not spawners or spawners[0].dead:
                # Spawner yok, lenf düğümüne saldır
                self._attack_lymph_node(obj, scene)
                return
            spawner = spawners[0]

        # Spawner'a olan mesafeyi hesapla
        dx = spawner.x - obj.x
        dy = spawner.y - obj.y
        dist = (dx * dx + dy * dy) ** 0.5

        # Bağlantı mesafesi kontrolü
        connection_break_distance = self.target_distance * 1.5

        if dist <= self.target_distance:
            # Hedef mesafede - bağ kurabilir
            self.is_connected = True

            # Çok yaklaştıysa biraz geri çekil
            if dist < self.target_distance * 0.8:
                if dist > 0:
                    dir_x = -dx / dist
                    dir_y = -dy / dist
                    move_x = dir_x * self.heal_speed * app.dt * 0.5
                    move_y = dir_y * self.heal_speed * app.dt * 0.5
                    obj.x += move_x
                    obj.y += move_y
        elif dist > connection_break_distance:
            # Çok uzaklaştı - yaklaş
            self.is_connected = False
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                move_x = dir_x * self.heal_speed * app.dt
                move_y = dir_y * self.heal_speed * app.dt
                obj.x += move_x
                obj.y += move_y
        else:
            # Hedef mesafeye yaklaş
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                move_x = dir_x * self.heal_speed * app.dt
                move_y = dir_y * self.heal_speed * app.dt
                obj.x += move_x
                obj.y += move_y

        # Bağlıysa can bas
        if self.is_connected:
            self.heal_timer += app.dt
            if self.heal_timer >= self.heal_interval:
                self.heal_timer = 0.0
                self._heal_spawner(spawner)

    def _heal_spawner(self, spawner):
        """Spawner'a can bas."""
        spawner_comp = spawner.get_component("EnemySpawnerObject")
        if spawner_comp and hasattr(spawner_comp.instance, 'health'):
            # Spawner'ın canını artır (max 50'ye kadar)
            spawner_obj = spawner_comp.instance
            spawner_obj.health = min(spawner_obj.max_health, spawner_obj.health + 5)
            print(f"Supporter healed spawner (+5 HP)")

    def _attack_lymph_node(self, obj, scene):
        """Spawner yoksa lenf düğümüne saldır."""
        app = App()
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        if not lymph_nodes or lymph_nodes[0].dead:
            return

        node = lymph_nodes[0]

        # Lenf düğümüne yaklaş
        dx = node.x - obj.x
        dy = node.y - obj.y
        dist = (dx * dx + dy * dy) ** 0.5

        # Yakınlaştıysa hasar ver
        if dist < 100:
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                obj.x += dir_x * self.heal_speed * app.dt * 0.5
                obj.y += dir_y * self.heal_speed * app.dt * 0.5

            # Hasar ver
            node_comp = node.get_component("LymphNode")
            if node_comp:
                node_comp.instance.take_damage(0.1)

    def draw(self, obj):
        """Çizim yok."""
        pass
