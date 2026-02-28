"""
Arkaplan renderer - Chunk tabanlı sistem.
Ekranın 4 köşesini hesaplar, o 4 chunk'ı 4 farklı yere çizer.
"""
import pygame
import math
import random

from pygaminal import App, Screen, Image


class BackgroundRenderer:
    """
    Arkaplan chunk sistemi - tek objeden 4 chunk çizimi.
    Ekranın 4 köşesini hesaplar, her biri için doğru chunk'ı çizer.
    """

    def __init__(self, chunk_w, chunk_h):
        """
        Args:
            chunk_w: Chunk genişliği (ekran genişliği)
            chunk_h: Chunk yüksekliği (ekran yüksekliği)
        """
        self.chunk_w = chunk_w
        self.chunk_h = chunk_h

        # Chunk görsellerini oluştur (cache)
        # 4 farklı chunk için sabit görseller
        self.chunk_surfaces = {}
        for seed in range(4):
            self.chunk_surfaces[seed] = self._generate_chunk_surface(seed)

    def _generate_chunk_surface(self, seed):
        """Chunk görselini oluştur (kan damarı teması)."""
        surface = pygame.Surface((self.chunk_w, self.chunk_h))

        # Ana arkaplan rengi - koyu kırmızı/kan tonu
        bg_color = (45, 18, 25)
        surface.fill(bg_color)

        # Random seed ile tutarlılık
        random.seed(seed)

        # Organik hücre detayları (kan damarı hücreleri)
        num_cells = 8 + random.randint(0, 5)

        for _ in range(num_cells):
            # Rastgele pozisyon
            cx = random.randint(0, self.chunk_w)
            cy = random.randint(0, self.chunk_h)
            radius = random.randint(30, 80)

            # Renk varyasyonu
            color_variation = random.randint(-10, 10)
            cell_color = (
                max(0, min(255, 50 + color_variation)),
                max(0, min(255, 18 + color_variation // 2)),
                max(0, min(255, 25 + color_variation // 2))
            )

            # Hücre çiz (organik şekil)
            points = []
            num_points = 8
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                r_var = random.randint(-5, 5)
                r = radius + r_var
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                points.append((px, py))

            pygame.draw.polygon(surface, cell_color, points)

            # İç detay
            detail_color = (
                max(0, min(255, cell_color[0] + 15)),
                max(0, min(255, cell_color[1] + 5)),
                max(0, min(255, cell_color[2] + 5))
            )
            detail_r = radius * 0.3
            pygame.draw.circle(surface, detail_color, (cx, cy), int(detail_r))

        # Damar çizgileri
        for _ in range(5):
            x1 = random.randint(0, self.chunk_w)
            y1 = random.randint(0, self.chunk_h)
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(40, 100)

            x2 = x1 + math.cos(angle) * length
            y2 = y1 + math.sin(angle) * length

            vein_color = (35, 14, 20)
            pygame.draw.line(surface, vein_color, (x1, y1), (x2, y2), 3)

        # Reset random seed
        random.seed()

        return surface

    def update(self, obj):
        """Objenin kendini güncellemeye gerek yok."""
        pass

    def draw(self, obj):
        """
        Ekranın 4 köşesini hesapla, her biri için doğru chunk'ı çiz.
        Camera transform UYGULAMADAN doğrudan çiz.
        """
        screen = Screen()

        # Camera pozisyonunu al
        try:
            from scripts.Camera import Camera
            camera = Camera()
            cam_x, cam_y = camera.get_offset()
        except:
            cam_x, cam_y = 0, 0

        # Ekranın 4 köşesinin dünya koordinatlarını hesapla
        # Ekranın sol üst köşesinin dünya koordinatı = camera pozisyonu
        screen_tl_world_x = cam_x
        screen_tl_world_y = cam_y

        # Ekranın 4 köşesi (dünya koordinatlarında)
        corners = [
            (screen_tl_world_x, screen_tl_world_y),                           # Sol üst
            (screen_tl_world_x + self.chunk_w, screen_tl_world_y),           # Sağ üst
            (screen_tl_world_x, screen_tl_world_y + self.chunk_h),           # Sol alt
            (screen_tl_world_x + self.chunk_w, screen_tl_world_y + self.chunk_h)  # Sağ alt
        ]

        # Her köşe için chunk'ı hesapla ve çiz
        # Ancak ÇİZİM ekran koordinatlarında olacak (0, 0) sol üstten başlayarak
        for i, (corner_x, corner_y) in enumerate(corners):
            # Bu köşe hangi chunk'a ait? (grid indeksi)
            chunk_index_x = int(corner_x / self.chunk_w)
            chunk_index_y = int(corner_y / self.chunk_h)

            # Chunk seed'ini hesapla (chunk pozisyonuna göre)
            # (chunk_x + chunk_y) % 4 döngüsel olarak 0,1,2,3 verir
            chunk_seed = (chunk_index_x + chunk_index_y) % 4

            # Chunk görselini al
            chunk_surface = self.chunk_surfaces[chunk_seed]

            # Çizim pozisyonu - ekranın 4 köşesinde sabit
            # 0: Sol üst (0, 0)
            # 1: Sağ üst (chunk_w, 0)
            # 2: Sol alt (0, chunk_h)
            # 3: Sağ alt (chunk_w, chunk_h)
            draw_positions = [
                (0, 0),
                (self.chunk_w, 0),
                (0, self.chunk_h),
                (self.chunk_w, self.chunk_h)
            ]

            draw_x, draw_y = draw_positions[i]

            # Camera transform UYGULAMA - doğrudan ekrana çiz
            screen.blit(Image(chunk_surface), draw_x, draw_y)
