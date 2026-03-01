"""
Enemy Spawner - Lenf düğümü etrafında procedural düşman spawn.
Zamanla yeni düşmanlar oluşturur.
"""
from pygaminal import App, Object
import random


class EnemySpawner:
    """
    Düşman spawn sistemi.
    Lenf düğümü etrafında procedural olarak düşman oluşturur.
    """

    def __init__(self, spawn_interval=5.0, max_enemies=10):
        """
        Args:
            spawn_interval: Spawn arası (saniye)
            max_enemies: Maksimum aynı anda kaç düşman olabilir
        """
        self.spawn_interval = spawn_interval
        self.max_enemies = max_enemies
        self.spawn_timer = 0.0

    def update(self, obj):
        """Her frame spawn kontrolü."""
        app = App()
        scene = app.get_current_scene()

        # Timer güncelle
        self.spawn_timer += app.dt

        # Spawn zamanı geldi mi?
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._try_spawn(scene)

    def _try_spawn(self, scene):
        """Düşman spawnlamayı dene."""
        # Mevcut düşman sayısını kontrol et
        enemy_count = len(scene.get_objects_by_tag("enemy"))
        infected_count = len(scene.get_objects_by_tag("infected"))

        total_enemies = enemy_count + infected_count

        if total_enemies >= self.max_enemies:
            return  # Çok fazla düşman var

        # Lenf düğümünü bul
        lymph_nodes = scene.get_objects_by_tag("lymph_node")

        if not lymph_nodes or lymph_nodes[0].dead:
            return  # Üs yok, spawn yapma

        node = lymph_nodes[0]

        # Üs etrafında random pozisyon hesapla (spawn_radius içinde)
        angle = random.uniform(0, 360)
        radius = random.uniform(200, 400)  # 200-400 piksel uzaklık

        import math
        rad = math.radians(angle)
        spawn_x = node.x + math.cos(rad) * radius
        spawn_y = node.y + math.sin(rad) * radius

        # Random düşman tipi seç
        enemy_type = random.choice([
            "infected_cell",  # %40 şans
            "infected_cell",
            "infected_cell",
            "infected_cell",
            "bacteria",       # %30 şans
            "bacteria",
            "bacteria",
            "virus"           # %30 şans
        ])

        # Düşman oluştur
        self._spawn_enemy(enemy_type, spawn_x, spawn_y, scene)

    def _spawn_enemy(self, enemy_type, x, y, scene):
        """Belirtilen tipte düşman spawnla - .obj dosyasından."""
        # .obj dosya yolu
        obj_file = f"objects/{enemy_type}.obj"

        # Objeyi dosyadan yükle
        enemy = Object.from_file(obj_file, x, y)

        # Sahneye ekle
        scene.add_object(enemy)
        print(f"Spawned {enemy_type} at ({x:.1f}, {y:.1f})")

    def draw(self, obj):
        """Çizim yok."""
        pass
