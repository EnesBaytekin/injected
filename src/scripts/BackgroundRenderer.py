"""
Parallax Background - Sonsuz chunk sistemi.
Her layer kendi chunk genişliğine sahip, parallax efekti ile derinlik.
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
        # parallax 0.0 = sabit, 1.0 = kamera ile aynı hız
        # chunk_w = screen_w * chunk_width_mult (küçük mult = daha büyük chunk = uzak)
        self.parallax_layers = [
            {"factor": 0.15, "chunk_mult": 2.0, "name": "back"},      # En uzak - büyük chunk
            {"factor": 0.35, "chunk_mult": 1.0, "name": "middle"},    # Orta - normal chunk
            {"factor": 0.65, "chunk_mult": 0.5, "name": "front"}      # En yakın - küçük chunk
        ]

        # Her layer için chunk yüzeylerini oluştur
        # layer_surfaces[layer_index][seed] = surface
        self.layer_surfaces = []

        for layer in self.parallax_layers:
            chunk_w = int(self.screen_w * layer["chunk_mult"])
            chunk_h = int(self.screen_h * layer["chunk_mult"])

            surfaces = {}
            for seed in range(4):  # 4 farklı chunk varyasyonu
                surfaces[seed] = self._generate_chunk_surface(chunk_w, chunk_h, seed, layer["factor"])

            self.layer_surfaces.append({
                "surfaces": surfaces,
                "chunk_w": chunk_w,
                "chunk_h": chunk_h,
                "factor": layer["factor"]
            })

    def _generate_chunk_surface(self, chunk_w, chunk_h, seed, parallax_factor):
        """
        Chunk yüzeyi oluştur - transparan, sadece bu layer'a ait objeler.
        """
        surface = pygame.Surface((chunk_w, chunk_h), pygame.SRCALPHA)

        # Random seed ile tutarlılık (parallax faktörünü de kat)
        random.seed(seed + int(parallax_factor * 1000))

        # Organik hücre detayları
        num_cells = 6 + random.randint(0, 4)

        for _ in range(num_cells):
            # Rastgele pozisyon
            cx = random.randint(0, chunk_w)
            cy = random.randint(0, chunk_h)
            radius = random.randint(20, 60)

            # Parallax faktörüne göre hücre boyutu filtrele
            # Küçük parallax (uzak) = büyük hücreler
            # Büyük parallax (yakın) = küçük hücreler
            if parallax_factor <= 0.2:  # Back layer - büyük hücreler
                if radius < 40:
                    continue
            elif parallax_factor >= 0.6:  # Front layer - küçük hücreler
                if radius >= 35:
                    continue
            # Middle layer - tüm hücreler

            # Renk varyasyonu (katmana göre parlaklık)
            base_brightness = 40 + int((1.0 - parallax_factor) * 30)  # Uzak = koyu
            color_variation = random.randint(-10, 10)
            cell_color = (
                max(0, min(255, base_brightness + color_variation)),
                max(0, min(255, 15 + color_variation // 2)),
                max(0, min(255, 20 + color_variation // 2))
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
                max(0, min(255, cell_color[0] + 12)),
                max(0, min(255, cell_color[1] + 4)),
                max(0, min(255, cell_color[2] + 4))
            )
            detail_r = radius * 0.3
            pygame.draw.circle(surface, detail_color, (cx, cy), int(detail_r))

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

        # Reset random seed
        random.seed()

        return surface

    def update(self, obj):
        """Güncelleme gerek yok."""
        pass

    def draw(self, obj):
        """
        Her parallax layer'ı çiz.
        Her layer kendi chunk boyutunda, ekranı dolduracak kadar chunk çizer.
        """
        screen = Screen()

        # Camera pozisyonunu al
        try:
            from scripts.Camera import Camera
            camera = Camera()
            cam_x, cam_y = camera.get_offset()
        except:
            cam_x, cam_y = 0, 0

        # Her layer'ı çiz (arkadan öne)
        for layer_data in self.layer_surfaces:
            surfaces = layer_data["surfaces"]
            chunk_w = layer_data["chunk_w"]
            chunk_h = layer_data["chunk_h"]
            parallax_factor = layer_data["factor"]

            # Parallax world offset
            # Kamera sağa gittikçe, layer parallax factor kadar "geride" kalır
            world_offset_x = cam_x * parallax_factor
            world_offset_y = cam_y * parallax_factor

            # Ekranı kaplayacak chunk aralığını hesapla
            # Ekranın sol üst ve sağ alt köşelerinin dünya koordinatları
            screen_tl_world_x = world_offset_x
            screen_tl_world_y = world_offset_y
            screen_br_world_x = world_offset_x + self.screen_w
            screen_br_world_y = world_offset_y + self.screen_h

            # Hangi chunk'ların görüneceğini hesapla
            start_chunk_x = int(screen_tl_world_x / chunk_w)
            end_chunk_x = int(screen_br_world_x / chunk_w) + 1
            start_chunk_y = int(screen_tl_world_y / chunk_h)
            end_chunk_y = int(screen_br_world_y / chunk_h) + 1

            # Chunk'ları çiz
            for chunk_x in range(start_chunk_x, end_chunk_x + 1):
                for chunk_y in range(start_chunk_y, end_chunk_y + 1):
                    # Chunk seed
                    chunk_seed = (chunk_x + chunk_y) % 4

                    # Chunk yüzeyini al
                    chunk_surface = surfaces[chunk_seed]

                    # Chunk'ın dünya pozisyonu
                    world_px = chunk_x * chunk_w
                    world_py = chunk_y * chunk_h

                    # Screen koordinatına çevir (world offset'ten çıkar)
                    screen_x = world_px - world_offset_x
                    screen_y = world_py - world_offset_y

                    # Çiz (transparan blit)
                    screen.blit(Image(chunk_surface), screen_x, screen_y)
