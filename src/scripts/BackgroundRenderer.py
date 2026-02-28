"""
Parallax Background - Sonsuz chunk sistemi.
Her layer kendi chunk genişliğine sahip, parallax efekti ile derinlik.
Seamless geçiş - wrap-around ile chunk kenarları birbirini tamamlar.
"""
import pygame
import math
import random

from pygaminal import Screen, Image


class BackgroundRenderer:
    """
    Parallax arkaplan - sonsuz chunk sistemi.
    Her layer farklı chunk boyutunda, kamera hareketine göre farklı hızda kayar.
    """

    def __init__(self, screen_w, screen_h):
        """
        Args:
            screen_w: Ekran genişliği
            screen_h: Ekran yüksekliği
        """
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Parallax katmanları: (parallax_factor, chunk_width_multiplier)
        self.parallax_layers = [
            {"factor": 0.15, "chunk_mult": 2.0, "name": "back"},
            {"factor": 0.35, "chunk_mult": 1.0, "name": "middle"},
            {"factor": 0.60, "chunk_mult": 0.5, "name": "front"}
        ]

        # Her layer için chunk yüzeyini oluştur
        self.layer_surfaces = []

        for layer in self.parallax_layers:
            chunk_w = int(self.screen_w * layer["chunk_mult"])
            chunk_h = int(self.screen_h * layer["chunk_mult"])

            # Tek chunk surface - seamless wrap-around ile
            surface = self._generate_chunk_surface(chunk_w, chunk_h, layer["factor"])

            self.layer_surfaces.append({
                "surface": surface,
                "chunk_w": chunk_w,
                "chunk_h": chunk_h,
                "factor": layer["factor"]
            })

    def _draw_wrapped_polygon(self, surface, color, points, chunk_w, chunk_h):
        """
        Polygon çiz - chunk sınırlarından taşarsa wrap-around yap.
        Bir polygon chunk'tan çıkarsa diğer taraftan devam eder.
        """
        # Bounding box hesapla
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        # Chunk sınırlarından taşıyor mu?
        wraps_x = max_x >= chunk_w or min_x < 0
        wraps_y = max_y >= chunk_h or min_y < 0

        if not wraps_x and not wraps_y:
            # Taşma yok, normal çiz
            pygame.draw.polygon(surface, color, points)
            return

        # Wrap-around var - chunk'ı 3x3 grid gibi düşün, her tile'a çiz
        # Sadece görünebilecek tile'ları çiz (optimizasyon)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                # Ötelenmiş noktalar
                offset_points = [(px + dx * chunk_w, py + dy * chunk_h) for px, py in points]

                # Bu ötelemenin görünüp görünmeyeceğini kontrol et
                offset_min_x = min_x + dx * chunk_w
                offset_max_x = max_x + dx * chunk_w
                offset_min_y = min_y + dy * chunk_h
                offset_max_y = max_y + dy * chunk_h

                # Chunk ile kesişiyor mu?
                if (offset_max_x > 0 and offset_min_x < chunk_w and
                    offset_max_y > 0 and offset_min_y < chunk_h):
                    pygame.draw.polygon(surface, color, offset_points)

        # Orijinali de çiz
        pygame.draw.polygon(surface, color, points)

    def _draw_wrapped_circle(self, surface, color, center, radius, chunk_w, chunk_h):
        """
        Circle çiz - chunk sınırlarından taşarsa wrap-around yap.
        """
        cx, cy = center

        # Bounding box
        min_x = cx - radius
        max_x = cx + radius
        min_y = cy - radius
        max_y = cy + radius

        # Taşıyor mu?
        wraps_x = max_x >= chunk_w or min_x < 0
        wraps_y = max_y >= chunk_h or min_y < 0

        pygame.draw.circle(surface, color, (int(cx), int(cy)), int(radius))

        if wraps_x or wraps_y:
            # Wrap-around - komşu tile'lara da çiz
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                offset_cx = cx + dx * chunk_w
                offset_cy = cy + dy * chunk_h

                # Görünüyor mu?
                if (offset_cx + radius > 0 and offset_cx - radius < chunk_w and
                    offset_cy + radius > 0 and offset_cy - radius < chunk_h):
                    pygame.draw.circle(surface, color, (int(offset_cx), int(offset_cy)), int(radius))

    def _generate_chunk_surface(self, chunk_w, chunk_h, parallax_factor):
        """
        Chunk yüzeyi oluştur - wrap-around ile seamless.
        """
        surface = pygame.Surface((chunk_w, chunk_h), pygame.SRCALPHA)

        random.seed(int(parallax_factor * 1000)*123)

        # Grid tabanlı uniform dağılım
        grid_size = 80  # Her grid hücresi 80x80
        grid_cols = chunk_w // grid_size + 1
        grid_rows = chunk_h // grid_size + 1

        for grid_x in range(grid_cols):
            for grid_y in range(grid_rows):
                # Her grid hücresinde %60 ihtimalle hücre var
                if random.random() > 0.6:
                    continue

                # Grid hücresi sınırları
                cell_start_x = grid_x * grid_size
                cell_start_y = grid_y * grid_size
                cell_end_x = min(cell_start_x + grid_size, chunk_w)
                cell_end_y = min(cell_start_y + grid_size, chunk_h)

                # Grid hücresi chunk dışına taşıyorsa skip
                if cell_start_x >= chunk_w or cell_start_y >= chunk_h:
                    continue

                # Grid hücresi içinde rastgele pozisyon (padding ile)
                padding = 15
                cx_min = cell_start_x + padding
                cx_max = cell_end_x - padding
                cy_min = cell_start_y + padding
                cy_max = cell_end_y - padding

                # Geçerli aralık kontrolü
                if cx_min >= cx_max or cy_min >= cy_max:
                    continue

                cx = random.randint(cx_min, cx_max)
                cy = random.randint(cy_min, cy_max)

                radius = random.randint(20, 60)

                # Parallax faktörüne göre hücre boyutu filtrele
                if parallax_factor <= 0.2:
                    if radius < 40:
                        continue
                elif parallax_factor >= 0.6:
                    if radius >= 35:
                        continue

                base_brightness = 55 + int(parallax_factor * 40)  # Yakın = açık, uzak = koyu
                color_variation = random.randint(-10, 10)
                cell_color = (
                    max(0, min(255, base_brightness + color_variation)),
                    max(0, min(255, 15 + color_variation // 2)),
                    max(0, min(255, 20 + color_variation // 2))
                )

                # Polygon noktaları
                points = []
                num_points = 8
                for i in range(num_points):
                    angle = (i / num_points) * 2 * math.pi
                    r_var = random.randint(-5, 5)
                    r = radius + r_var
                    px = cx + math.cos(angle) * r
                    py = cy + math.sin(angle) * r
                    points.append((px, py))

                # Wrap-around polygon çiz
                self._draw_wrapped_polygon(surface, cell_color, points, chunk_w, chunk_h)

                # İç detay
                detail_color = (
                    max(0, min(255, cell_color[0] + 12)),
                    max(0, min(255, cell_color[1] + 4)),
                    max(0, min(255, cell_color[2] + 4))
                )
                detail_r = radius * 0.3
                self._draw_wrapped_circle(surface, detail_color, (cx, cy), detail_r, chunk_w, chunk_h)

        # Damar çizgileri (sadece middle layer)
        if 0.3 < parallax_factor < 0.4:
            for _ in range(4):
                x1 = random.randint(0, chunk_w)
                y1 = random.randint(0, chunk_h)
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(30, 80)

                x2 = x1 + math.cos(angle) * length
                y2 = y1 + math.sin(angle) * length

                vein_color = (30, 12, 18)
                pygame.draw.line(surface, vein_color, (x1, y1), (x2, y2), 2)

        random.seed()

        return surface

    def update(self, obj):
        """Güncelleme gerek yok."""
        pass

    def draw(self, obj):
        """
        Her parallax layer'ı çiz.
        """
        screen = Screen()

        try:
            from scripts.Camera import Camera
            camera = Camera()
            cam_x, cam_y = camera.get_offset()
        except:
            cam_x, cam_y = 0, 0

        for layer_data in self.layer_surfaces:
            surface = layer_data["surface"]
            chunk_w = layer_data["chunk_w"]
            chunk_h = layer_data["chunk_h"]
            parallax_factor = layer_data["factor"]

            world_offset_x = cam_x * parallax_factor
            world_offset_y = cam_y * parallax_factor

            screen_tl_world_x = world_offset_x
            screen_tl_world_y = world_offset_y
            screen_br_world_x = world_offset_x + self.screen_w
            screen_br_world_y = world_offset_y + self.screen_h

            start_chunk_x = int(screen_tl_world_x / chunk_w) - 1
            end_chunk_x = int(screen_br_world_x / chunk_w) + 1
            start_chunk_y = int(screen_tl_world_y / chunk_h) - 1
            end_chunk_y = int(screen_br_world_y / chunk_h) + 1

            for chunk_x in range(start_chunk_x, end_chunk_x + 1):
                for chunk_y in range(start_chunk_y, end_chunk_y + 1):
                    world_px = chunk_x * chunk_w
                    world_py = chunk_y * chunk_h

                    screen_x = world_px - world_offset_x
                    screen_y = world_py - world_offset_y

                    screen.blit(Image(surface), screen_x, screen_y)
