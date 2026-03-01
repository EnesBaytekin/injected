"""
Enemy Spawner Object - Fiziksel spawner hücresi.
Biyolojik bölünme animasyonu ile düşman üretir.
"""
from pygaminal import App, Screen, Object, Image
import pygame
import math
import random


class EnemySpawnerObject:
    """
    Fiziksel düşman spawnerı.
    Hücresel bölünme ile düşman üretir.
    """

    def __init__(self, radius=35, max_health=100):
        """
        Args:
            radius: Spawner yarıçapı
            max_health: Maksimum can (kaç vuruşta öleceği)
        """
        self.radius = radius
        self.max_health = max_health
        self.health = max_health

        # Spawn timer'lar
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 25.0  # Her 25 saniyede bir düşman
        self.supporter_spawn_timer = 0.0
        self.supporter_spawn_interval = 50.0  # Her 50 saniyede bir supporter

        # Bölünme animasyonu
        self.division_progress = 0.0  # 0.0 - 1.0 arası
        self.is_dividing = False
        self.division_angle = 0.0
        self.division_spawn_type = None  # "enemy" veya "supporter"

        # Görsel wobble
        self.wobble_phases = [random.random() * 2 * math.pi for _ in range(12)]

        # Renk (koyu mor/kırmızı - enfekte görünüm)
        self.color = (120, 40, 80)
        self.core_color = (80, 20, 50)

    def update(self, obj):
        """Spawn timer'larını güncelle, bölünme animasyonunu yönet."""
        app = App()
        scene = app.get_current_scene()

        # Bullet collision kontrolü
        self.check_bullet_collision(obj)

        # Zaten bölünüyorsa, animasyon bitmesini bekle
        if self.is_dividing:
            self.division_progress += app.dt * 0.8  # 1.25 saniyede tamamlanır
            if self.division_progress >= 1.0:
                # Bölünme tamamlandı - düşman spawnla
                self._spawn_from_division(obj, scene)
                self.is_dividing = False
                self.division_progress = 0.0
            return

        # Lenf düğümü hayatta mı kontrol et
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        if not lymph_nodes or lymph_nodes[0].dead:
            return  # Lenf düğümü öldü, spawn yapma

        # Düşman spawn timer
        self.enemy_spawn_timer += app.dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0.0
            # Bölünmeyi başlat
            self.is_dividing = True
            self.division_angle = random.uniform(0, 360)
            self.division_spawn_type = "enemy"

        # Supporter spawn timer
        self.supporter_spawn_timer += app.dt
        if self.supporter_spawn_timer >= self.supporter_spawn_interval:
            self.supporter_spawn_timer = 0.0
            # Bölünmeyi başlat
            self.is_dividing = True
            self.division_angle = random.uniform(0, 360)
            self.division_spawn_type = "supporter"

    def _spawn_from_division(self, obj, scene):
        """Bölünme animasyonu tamamlandığında düşman spawnla."""
        import math

        # Spawn pozisyonu - spawner'dan biraz uzakta
        rad = math.radians(self.division_angle)
        spawn_distance = self.radius + 20
        spawn_x = obj.x + math.cos(rad) * spawn_distance
        spawn_y = obj.y + math.sin(rad) * spawn_distance

        if self.division_spawn_type == "enemy":
            # Random düşman tipi seç
            enemy_type = random.choice([
                "infected_cell", "infected_cell", "infected_cell",
                "bacteria", "bacteria",
                "virus"
            ])
            enemy = Object.from_file(f"objects/{enemy_type}.obj", spawn_x, spawn_y)
            scene.add_object(enemy)
            print(f"Spawner spawned {enemy_type} at ({spawn_x:.1f}, {spawn_y:.1f})")
        else:
            # Supporter spawnla - parent spawner'ı set et
            supporter = Object.from_file("objects/supporter_cell.obj", spawn_x, spawn_y)

            # Supporter AI'ına parent spawner'ı set et
            supporter_ai = supporter.get_component("SupporterCellAI")
            if supporter_ai and hasattr(supporter_ai.instance, 'set_parent_spawner'):
                supporter_ai.instance.set_parent_spawner(obj)

            scene.add_object(supporter)
            print(f"Spawner spawned supporter at ({spawn_x:.1f}, {spawn_y:.1f})")

    def take_damage(self, amount):
        """Hasar al."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Öldü
        return False  # Hayatta

    def check_bullet_collision(self, obj):
        """Mermi çarpışması kontrolü - GranuleBullet tarafından çağrılır."""
        from pygaminal import App
        scene = App().get_current_scene()

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

            # Spawner'ın hitbox'ı
            my_hitbox = obj.get_component("CircleHitbox")
            if not my_hitbox:
                continue

            # Çarpışma kontrolü
            dx = obj.x - bullet_obj.x
            dy = obj.y - bullet_obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < my_hitbox.radius + 4:  # Bullet radius ~4
                # Hasar ver
                died = self.take_damage(5)  # Her mermi 5 hasar

                # Bullet'u yok et
                bullet_obj.kill()

                if died:
                    # Spawner öldü - particle patlaması
                    self._explode_and_die(obj)

                return True  # Çarpışma işlendi

        return False

    def _explode_and_die(self, obj):
        """Spawner öldüğünde - büyük particle patlaması."""
        from scripts.ParticleEffect import ParticleEffect
        from pygaminal import ScriptComponent

        scene = App().get_current_scene()

        # 1. Büyük particle patlaması - mor/kırmızı
        particle_obj1 = Object(obj.x, obj.y, depth=1000)
        effect1 = ParticleEffect(
            particle_count=100,
            shape=ParticleEffect.SHAPE_PIXEL,
            color=((120, 40, 80), (80, 20, 50)),
            lifetime=(0.5, 1.2),
            size=(2, 5),
            velocity=(50, 200),
            acceleration=(0, 100),
            spawn_mode="burst",
            one_shot=True,
            fade_out=True,
            friction=1.5,
            spread=360
        )
        script_comp1 = ScriptComponent("scripts/ParticleEffect", [])
        script_comp1.instance = effect1
        particle_obj1.add_component(script_comp1)
        scene.add_object(particle_obj1)

        # 2. Daha büyük parçalar
        particle_obj2 = Object(obj.x, obj.y, depth=999)
        effect2 = ParticleEffect(
            particle_count=30,
            shape=ParticleEffect.SHAPE_SHRINKING_CIRCLE,
            color=((150, 60, 100), (100, 40, 70)),
            lifetime=(0.7, 1.5),
            size=(4, 8),
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

        # Spawner'ı yok et
        obj.kill()
        print("Spawner destroyed!")

    def draw(self, obj):
        """Spawner'ı çiz - biyolojik hücre + bölünme animasyonu."""
        screen = Screen()
        app = App()

        # Surface oluştur
        size = int(self.radius * 3)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Wobble hesapla
        points = []
        num_points = 12
        for i in range(num_points):
            angle = i * (2 * math.pi / num_points)
            phase = self.wobble_phases[i]
            wobble = math.sin(app.now * 2 + phase) * 2

            r = self.radius + wobble
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            points.append((x + center, y + center))

        # Ana hücre gövdesini çiz
        if len(points) > 2:
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, (50, 20, 30), points, 3)

        # Çekirdek (nucleus)
        pygame.draw.circle(surface, self.core_color, (center, center), int(self.radius * 0.4))

        # Bölünme animasyonu
        if self.is_dividing:
            # Animasyon ilerlemesine göre "buds" çiz
            rad = math.radians(self.division_angle)
            bud_distance = self.division_progress * (self.radius * 0.8)

            # Bud pozisyonu
            bud_x = center + math.cos(rad) * bud_distance
            bud_y = center + math.sin(rad) * bud_distance

            # Bud radius - zamanla büyür
            bud_radius = self.division_progress * self.radius * 0.5

            # Bud çiz (yeni hücre parçası)
            pygame.draw.circle(surface, self.color, (int(bud_x), int(bud_y)), int(bud_radius))

            # Bağlantı "neck"
            if self.division_progress < 0.8:
                neck_width = int(self.radius * 0.3 * (1 - self.division_progress))
                if neck_width > 0:
                    pygame.draw.line(surface, self.color,
                                    (center, center),
                                    (bud_x, bud_y), neck_width)

        # Can barı
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 4
            bar_x = center - bar_width // 2
            bar_y = center - self.radius - 10

            health_pct = self.health / self.max_health

            # Arkaplan
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

            # Doluluk
            fill_width = int(bar_width * health_pct)
            if fill_width > 0:
                color = (255, 100, 100)  # Kırmızımsı
                pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))

        # Camera transform
        draw_x = obj.x - center
        draw_y = obj.y - center

        try:
            from scripts.Camera import Camera
            camera = Camera()
            draw_x, draw_y = camera.world_to_screen(draw_x, draw_y)
        except:
            pass

        screen.blit(Image(surface), draw_x, draw_y)
