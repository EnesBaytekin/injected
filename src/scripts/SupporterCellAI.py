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

        # Bullet yutma sistemi
        self.capacity = 2  # 2 bullet yutunca ölür
        self.swallowed_bullets = []
        self.is_digesting = False
        self.digestion_progress = 0.0

    def set_parent_spawner(self, spawner_obj):
        """Parent spawner'ı set et - hangi spawner'dan doğdu."""
        self.parent_spawner = spawner_obj

    def swallow_bullet(self, bullet_obj):
        """Bullet tarafından yutul (CellImage ile uyumluluk için)."""
        # Zaten _check_bullet_collision'da ekleniyor, burası boş kalabilir
        pass

    def update(self, obj):
        """Spawner'a yaklaş, bağ kur, can bas."""
        app = App()
        scene = app.get_current_scene()

        # Sindirme kontrolü
        if self.is_digesting:
            self.digestion_progress += app.dt * 0.5  # 2 saniyede tamamlanır
            if self.digestion_progress >= 1.0:
                self._explode_and_die(obj)
                return

        # Bullet collision kontrolü
        if not self.is_digesting:
            self._check_bullet_collision(obj, scene)

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

    def _check_bullet_collision(self, obj, scene):
        """Bullet çarpışması kontrolü."""
        # Tüm bullet'ları kontrol et
        for bullet_obj in scene.get_all_objects():
            if bullet_obj.dead:
                continue

            # GranuleBullet component'i var mı?
            bullet_comp = bullet_obj.get_component("GranuleBullet")
            if not bullet_comp or not hasattr(bullet_comp.instance, 'is_swallowed'):
                continue

            bullet = bullet_comp.instance

            # Yutulmuş bullet'ları atla
            if bullet.is_swallowed:
                continue

            # Supporter'ın hitbox'ı
            my_hitbox = obj.get_component("CircleHitbox")
            if not my_hitbox:
                continue

            # Çarpışma kontrolü
            dx = obj.x - bullet_obj.x
            dy = obj.y - bullet_obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < my_hitbox.radius + 4:  # Bullet radius ~4
                # Bullet'u yut
                bullet._be_swallowed(bullet_obj, obj, self)
                self.swallowed_bullets.append(bullet_obj)

                # Capacity doldu mu?
                if len(self.swallowed_bullets) >= self.capacity:
                    self.is_digesting = True

                # Bir frame'de tek bullet yut
                break

    def _explode_and_die(self, obj):
        """Supporter öldüğünde - mor particle patlaması."""
        from scripts.ParticleEffect import ParticleEffect
        from pygaminal import ScriptComponent

        scene = App().get_current_scene()

        # İçindeki bullet'ların pozisyonlarını al
        bullet_positions = []
        for bullet_obj in self.swallowed_bullets:
            if bullet_obj and not bullet_obj.dead:
                bullet_positions.append((bullet_obj.x, bullet_obj.y))
                bullet_obj.kill()

        # 1. Küçük pixel particle'lar (toz) - mor
        particle_obj1 = Object(obj.x, obj.y, depth=1000)
        effect1 = ParticleEffect(
            particle_count=200,
            shape=ParticleEffect.SHAPE_PIXEL,
            color=((180, 100, 180), (150, 80, 150)),  # Mor
            lifetime=(0.3, 0.8),
            size=(1, 3),
            velocity=(20, 150),
            acceleration=(0, 100),
            spawn_mode="burst",
            one_shot=True,
            fade_out=True,
            friction=2.0,
            spread=360
        )
        script_comp1 = ScriptComponent("scripts/ParticleEffect", [])
        script_comp1.instance = effect1
        particle_obj1.add_component(script_comp1)
        scene.add_object(particle_obj1)

        # 2. Küçülen daireler
        particle_obj2 = Object(obj.x, obj.y, depth=999)
        effect2 = ParticleEffect(
            particle_count=30,
            shape=ParticleEffect.SHAPE_SHRINKING_CIRCLE,
            color=((200, 150, 200), (180, 120, 180)),
            lifetime=(0.5, 1.0),
            size=(3, 6),
            velocity=(30, 120),
            acceleration=(0, 80),
            spawn_mode="burst",
            one_shot=True,
            fade_out=True,
            friction=1.0,
            spread=360
        )
        script_comp2 = ScriptComponent("scripts/ParticleEffect", [])
        script_comp2.instance = effect2
        particle_obj2.add_component(script_comp2)
        scene.add_object(particle_obj2)

        # 3. İçindeki bullet'ların her biri için mini patlamalar
        for bx, by in bullet_positions:
            bullet_particle = Object(bx, by, depth=1000)
            bullet_effect = ParticleEffect(
                particle_count=15,
                shape=ParticleEffect.SHAPE_SHRINKING_CIRCLE,
                color=((255, 235, 180), (200, 180, 140)),  # Sarı tonları
                lifetime=(0.2, 0.5),
                size=(2, 3),
                velocity=(15, 50),
                acceleration=(0, 50),
                spawn_mode="burst",
                one_shot=True,
                fade_out=True,
                friction=2.5,
                spread=360
            )
            bullet_script = ScriptComponent("scripts/ParticleEffect", [])
            bullet_script.instance = bullet_effect
            bullet_particle.add_component(bullet_script)
            scene.add_object(bullet_particle)

        # Supporter'ı yok et
        obj.kill()
        print("Supporter destroyed!")

    def draw(self, obj):
        """Çizim yok."""
        pass
