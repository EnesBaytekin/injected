"""
Minimap - Küçük harita göstergesi.
Lenf düğümü, spawner'lar, player pozisyonunu gösterir.
"""
from pygaminal import App, Screen
import pygame


class Minimap:
    """
    Minimap sistemi.
    Köşede küçük harita gösterir.
    """

    def __init__(self, size=120, margin=10):
        """
        Args:
            size: Minimap kenar uzunluğu (piksel)
            margin: Ekran kenarından uzaklık (piksel)
        """
        self.size = size
        self.margin = margin

        # Dünya boyutları (harita sınırları)
        self.world_size = 1200  # -600'den +600'ye kadar
        self.world_offset = self.world_size // 2  # Merkez

        # Renkler
        self.bg_color = (20, 20, 30, 200)  # Koyu mavi, yarı saydam
        self.border_color = (100, 100, 120)

    def update(self, obj):
        """Minimap güncelle - update'de bir şey yapmıyoruz."""
        pass

    def draw(self, obj):
        """Minimap'i çiz."""
        screen = App().screen
        scene = App().get_current_scene()

        # Minimap pozisyonu (sağ üst köşe)
        map_x = screen.width - self.size - self.margin
        map_y = self.margin

        # Surface oluştur (transparan için)
        minimap_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # Arkaplan
        pygame.draw.rect(minimap_surface, self.bg_color, (0, 0, self.size, self.size))
        pygame.draw.rect(minimap_surface, self.border_color, (0, 0, self.size, self.size), 2)

        # World to minimap dönüşüm fonksiyonu
        def world_to_minimap(wx, wy):
            # World koordinatlarını minimap koordinatlarına çevir
            # World: (-600, -600)'den (600, 600)'ye
            # Minimap: (0, 0)'dan (size, size)'e
            scale = self.size / self.world_size
            mx = (wx + self.world_offset) * scale
            my = (wy + self.world_offset) * scale
            return mx, my

        # Lenf düğümünü çiz (yeşil büyük daire)
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        for node in lymph_nodes:
            if not node.dead:
                lx, ly = world_to_minimap(node.x, node.y)
                pygame.draw.circle(minimap_surface, (50, 200, 50), (int(lx), int(ly)), 6)

        # Spawner'ları çiz (mor orta daireler)
        spawners = scene.get_objects_by_tag("enemy_spawner")
        for spawner in spawners:
            if not spawner.dead:
                sx, sy = world_to_minimap(spawner.x, spawner.y)
                pygame.draw.circle(minimap_surface, (180, 100, 180), (int(sx), int(sy)), 4)

        # Player'ı çiz (sarı küçük daire)
        heroes = scene.get_objects_by_tag("hero")
        for hero in heroes:
            if not hero.dead:
                hx, hy = world_to_minimap(hero.x, hero.y)
                pygame.draw.circle(minimap_surface, (255, 255, 100), (int(hx), int(hy)), 3)

        # Healer cell'leri çiz (açık yeşil noktalar)
        healers = scene.get_objects_by_tag("healer")
        for healer in healers:
            if not healer.dead:
                hrx, hry = world_to_minimap(healer.x, healer.y)
                pygame.draw.circle(minimap_surface, (100, 255, 150), (int(hrx), int(hry)), 2)

        # Camera view rectangle (görünen alan)
        try:
            from scripts.Camera import Camera
            camera = Camera()

            # Camera sınırlarını hesapla
            screen_w = screen.width
            screen_h = screen.height

            # Camera merkezi (world koordinatlarında)
            cam_center_x = camera.x
            cam_center_y = camera.y

            # Camera rectangle'ın world koordinatları
            cam_left = cam_center_x - screen_w / 2
            cam_top = cam_center_y - screen_h / 2
            cam_right = cam_center_x + screen_w / 2
            cam_bottom = cam_center_y + screen_h / 2

            # Minimap koordinatlarına çevir
            ml, mt = world_to_minimap(cam_left, cam_top)
            mr, mb = world_to_minimap(cam_right, cam_bottom)

            # Camera rectangle'ı çiz (beyaz çerçeve)
            rect_w = mr - ml
            rect_h = mb - mt
            if rect_w > 0 and rect_h > 0:
                pygame.draw.rect(minimap_surface, (255, 255, 255, 100),
                               (ml, mt, rect_w, rect_h), 1)

        except:
            pass

        # Minimap'i ekrana blit (depth'e bakmadan, her zaman üstte)
        # Minimap depth'siz çizilir çünkü Object depth parametresi bu methodu etkilemez
        screen.surface.blit(minimap_surface, (map_x, map_y))
