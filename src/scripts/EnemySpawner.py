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

    def __init__(self, spawn_interval=10.0, max_cells=20, max_viruses=10, grace_period=20.0):
        """
        Args:
            spawn_interval: Spawn arası (saniye)
            max_cells: Maksimum aynı anda kaç passive cell olabilir
            max_viruses: Maksimum aynı anda kaç virus olabilir
            grace_period: Başlangıçta spawn yapmaz (saniye)
        """
        self.spawn_interval = spawn_interval
        self.max_cells = max_cells
        self.max_viruses = max_viruses
        self.grace_period = grace_period
        self.spawn_timer = 0.0
        self.game_time = 0.0  # Toplam oyun süresi

    def update(self, obj):
        """Her frame spawn kontrolü."""
        app = App()
        scene = app.get_current_scene()

        # Oyun süresini güncelle
        self.game_time += app.dt

        # Grace period kontrolü - ilk 20 saniye spawn yapma
        if self.game_time < self.grace_period:
            return

        # Timer güncelle
        self.spawn_timer += app.dt

        # Spawn zamanı geldi mi?
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._try_spawn(scene)

    def _try_spawn(self, scene):
        """Cell ve virus spawnlamayı dene."""
        # Mevcut sayıları kontrol et
        cell_count = len(scene.get_objects_by_tag("passive_cell"))
        virus_count = len(scene.get_objects_by_tag("enemy"))

        # Spawn kararı - cell mi virus mu?
        import random
        if cell_count < self.max_cells and (virus_count >= self.max_viruses or random.random() < 0.6):
            # %60 şansla cell, %40 şansla virus (limitlere göre)
            spawn_type = "cell"
        else:
            spawn_type = "virus"

        # Limit kontrolü
        if spawn_type == "cell" and cell_count >= self.max_cells:
            return  # Çok fazla cell var
        if spawn_type == "virus" and virus_count >= self.max_viruses:
            return  # Çok fazla virus var

        # Lenf düğümünü bul
        lymph_nodes = scene.get_objects_by_tag("lymph_node")

        if not lymph_nodes or lymph_nodes[0].dead:
            return  # Üs yok, spawn yapma

        node = lymph_nodes[0]

        # Random pozisyon - lenf düğümü etrafında geniş alanda
        angle = random.uniform(0, 360)
        radius = random.uniform(100, 500)  # 100-500 piksel uzaklık

        import math
        rad = math.radians(angle)
        spawn_x = node.x + math.cos(rad) * radius
        spawn_y = node.y + math.sin(rad) * radius

        # Spawn yap
        if spawn_type == "cell":
            self._spawn_cell(spawn_x, spawn_y, scene)
        else:
            self._spawn_virus(spawn_x, spawn_y, scene)

    def _spawn_cell(self, x, y, scene):
        """Passive cell spawnla - .obj dosyasından."""
        # Çarpışma kontrolü - başka bir şeyin içinde mi?
        if self._check_collision_at(x, y, scene, radius=20):
            return  # İçinde spawn yapma

        # .obj dosyasından yükle
        cell = Object.from_file("objects/cell.obj", x, y)
        scene.add_object(cell)
        print(f"Spawned passive cell at ({x:.1f}, {y:.1f})")

    def _spawn_virus(self, x, y, scene):
        """Virus spawnla - .obj dosyasından."""
        # Çarpışma kontrolü
        if self._check_collision_at(x, y, scene, radius=15):
            return  # İçinde spawn yapma

        # .obj dosyasından yükle
        virus = Object.from_file("objects/virus.obj", x, y)
        scene.add_object(virus)
        print(f"Spawned virus at ({x:.1f}, {y:.1f})")

    def _check_collision_at(self, x, y, scene, radius=20):
        """Belirli bir konumda çarpışma var mı kontrol et."""
        # Tüm objeleri kontrol et
        for obj in scene.get_all_objects():
            if obj.dead:
                continue

            # Hitbox'ı kontrol et
            hitbox = obj.get_component("CircleHitbox")
            if not hitbox:
                continue

            # Mesafe kontrolü
            dx = x - obj.x
            dy = y - obj.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < hitbox.radius + radius:
                return True  # Çarpışma var

        return False  # Çarpışma yok

    def draw(self, obj):
        """Çizim yok."""
        pass
