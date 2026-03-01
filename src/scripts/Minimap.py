"""
Minimap - Küçük harita göstergesi.
Player, düşmanlar, lenf düğümü, spawner'ları gösterir.
Player merkezli takip eder.
"""
from pygaminal import App, Screen
import pygame
import math

# Global App ve Screen önbelleği (singleton sorunlarını önlemek için)
_app_cache = None
_screen_cache = None


class Minimap:
    """
    Minimap sistemi.
    Sağ altta yumuşak kenarlı kare.
    Player'ı sürekli merkeze alır.
    """

    def __init__(self, size=32, margin=5):
        """
        Args:
            size: Minimap kenar uzunluğu (piksel)
            margin: Ekran kenarından uzaklık (piksel)
        """
        global _app_cache, _screen_cache

        self.size = size
        self.margin = margin

        # Görülebilir dünya alanı (minimap kaç piksel gösterecek)
        self.visible_world_size = 400  # 400x400 piksellik alan

        # Renkler
        self.bg_color = (20, 20, 30, 220)  # Koyu mavi, yarı saydam
        self.border_color = (100, 100, 120)

        # App ve Screen'i önbelleğe al
        if _app_cache is None:
            _app_cache = App()
        if _screen_cache is None:
            _screen_cache = Screen()  # Screen ayrı singleton

    def update(self, obj):
        """Minimap güncelle - update'de bir şey yapmıyoruz."""
        pass

    def draw(self, obj):
        """Minimap'i çiz - Player merkezli, sürekli takip eden."""
        screen = _screen_cache
        scene = _app_cache.get_current_scene()

        # Player pozisyonunu al (merkez için)
        heroes = scene.get_objects_by_tag("hero")
        player_center_x = 0
        player_center_y = 0
        player_count = 0

        for hero in heroes:
            if not hero.dead:
                player_center_x += hero.x
                player_center_y += hero.y
                player_count += 1

        if player_count > 0:
            player_center_x /= player_count
            player_center_y /= player_count

        # Minimap pozisyonu (sağ alt)
        map_x = screen.width - self.size - self.margin
        map_y = screen.height - self.size - self.margin

        # Surface oluştur (transparan için)
        minimap_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # Yumuşak kenarlı arkaplan
        corner_radius = 5
        pygame.draw.rect(minimap_surface, self.bg_color, (0, 0, self.size, self.size), border_radius=corner_radius)
        pygame.draw.rect(minimap_surface, self.border_color, (0, 0, self.size, self.size), 1, border_radius=corner_radius)

        # World to minimap dönüşüm fonksiyonu (player merkezli)
        def world_to_minimap(wx, wy):
            # Player'ı merkeze al
            # World: player_center'dan visible_world_size/2 kadar her yöne
            # Minimap: (0, 0)'dan (size, size)'e
            dx = wx - player_center_x
            dy = wy - player_center_y

            # Scale minimap boyutuna göre
            scale = self.size / self.visible_world_size
            mx = self.size / 2 + dx * scale
            my = self.size / 2 + dy * scale
            return mx, my

        # LENF DÜĞÜMÜ çiz (yeşil büyük daire)
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        for node in lymph_nodes:
            if not node.dead:
                lx, ly = world_to_minimap(node.x, node.y)
                # Minimap sınırları içindeyse çiz
                if 0 <= lx <= self.size and 0 <= ly <= self.size:
                    pygame.draw.circle(minimap_surface, (50, 200, 50), (int(lx), int(ly)), 3)

        # SPAWNERLARI çiz (mor orta daireler)
        spawners = scene.get_objects_by_tag("enemy_spawner")
        for spawner in spawners:
            if not spawner.dead:
                sx, sy = world_to_minimap(spawner.x, spawner.y)
                if 0 <= sx <= self.size and 0 <= sy <= self.size:
                    pygame.draw.circle(minimap_surface, (180, 100, 180), (int(sx), int(sy)), 2)

        # HEALER CELL'LERİ çiz (açık yeşil küçük daireler)
        healers = scene.get_objects_by_tag("healer")
        for healer in healers:
            if not healer.dead:
                hx, hy = world_to_minimap(healer.x, healer.y)
                if 0 <= hx <= self.size and 0 <= hy <= self.size:
                    pygame.draw.circle(minimap_surface, (100, 255, 150), (int(hx), int(hy)), 1)

        # DÜŞMANLARI çiz
        for enemy in scene.get_all_objects():
            if enemy.dead:
                continue

            ex, ey = world_to_minimap(enemy.x, enemy.y)

            # Minimap sınırları dışındaysa atla
            if not (0 <= ex <= self.size and 0 <= ey <= self.size):
                continue

            # VirusAI = mavi
            if enemy.get_component("VirusAI"):
                pygame.draw.circle(minimap_surface, (150, 150, 200), (int(ex), int(ey)), 1)
            # InfectedCellAI = kahverengi
            elif enemy.get_component("InfectedCellAI"):
                pygame.draw.circle(minimap_surface, (150, 100, 80), (int(ex), int(ey)), 1)
            # BacteriaAI = kırmızı
            elif enemy.get_component("BacteriaAI"):
                pygame.draw.circle(minimap_surface, (200, 50, 50), (int(ex), int(ey)), 1)
            # SupporterCellAI = mor
            elif enemy.get_component("SupporterCellAI"):
                pygame.draw.circle(minimap_surface, (180, 100, 180), (int(ex), int(ey)), 1)

        # PLAYER'I çiz (sarı nokta - merkezde)
        if player_count > 0:
            center_x = self.size / 2
            center_y = self.size / 2
            pygame.draw.circle(minimap_surface, (255, 255, 100), (int(center_x), int(center_y)), 2)

        # Minimap'i ekrana blit (sağ alt)
        screen.surface.blit(minimap_surface, (map_x, map_y))
