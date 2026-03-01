"""
Healer Cell Visual - Yeşil dost hücre görseli.
Lenf düğümüne yeşil çizgi ile bağlanır, healing particle'lar gönderir.
"""
from pygaminal import App, Screen, Object, Image
import pygame
import math
import random


class HealerCellVisual:
    """
    İyileştirici hücre görsel sistemi.
    Jölemsi hücre + yeşil bağ çizgisi + healing particle'lar.
    """

    def __init__(self, radius=8, color=(100, 255, 150), wobble_speed=2.0, wobble_amount=2.0, stretch_max=2.0):
        """
        Args:
            radius: Hücre yarıçapı
            color: RGB renk tuple
            wobble_speed: Deformasyon hızı
            wobble_amount: Deformasyon miktarı
            stretch_max: Maksimum stretch faktörü
        """
        self.radius = radius
        self.color = color
        self.wobble_speed = wobble_speed
        self.wobble_amount = wobble_amount
        self.stretch_max = stretch_max

        # 12 nokta oluştur (daire etrafında)
        self.num_points = 12
        self.base_angles = [i * (2 * math.pi / self.num_points) for i in range(self.num_points)]

        # Her nokta için rastgele offset phase
        self.phases = [random.random() * 2 * math.pi for _ in range(self.num_points)]

        # Mevcut pozisyonlar
        self.current_points = []

        # Healing particle sistemi
        self.healing_particles = []  # [{"progress": 0.0, "speed": random}, ...]

    def update(self, obj):
        """Hücre deformasyonunu güncelle, healing particle'ları yönet."""
        app = App()
        scene = app.get_current_scene()

        # Hücre deformasyonunu güncelle
        new_points = []
        for i, angle in enumerate(self.base_angles):
            # Zaman bazlı wobble
            phase = self.phases[i]
            wobble = math.sin(app.now * self.wobble_speed + phase) * self.wobble_amount

            # Rastgele mikroskopik hareket
            micro_wobble = math.cos(app.now * self.wobble_speed * 1.7 + phase) * (self.wobble_amount * 0.3)

            # Yarıçapı hesapla
            r = self.radius + wobble + micro_wobble

            # Pozisyon
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            new_points.append((x, y))

        self.current_points = new_points

        # Healing particle'ları güncelle
        # HealerCellAI'dan bağlantı durumunu al
        ai_comp = obj.get_component("HealerCellAI")
        if ai_comp and hasattr(ai_comp.instance, 'is_connected') and ai_comp.instance.is_connected:
            # Bağlıysa yeni particle spawnla (her 0.3 saniyede bir)
            if not hasattr(self, '_particle_spawn_timer'):
                self._particle_spawn_timer = 0

            self._particle_spawn_timer += app.dt
            if self._particle_spawn_timer >= 0.3:
                self._particle_spawn_timer = 0
                # Yeni particle ekle
                self.healing_particles.append({
                    'progress': 0.0,
                    'speed': random.uniform(0.8, 1.2)  # Hız varyasyonu
                })

        # Mevcut particle'ları güncelle
        alive_particles = []
        for p in self.healing_particles:
            p['progress'] += p['speed'] * app.dt * 0.5  # 2 saniyede lenf düğümüne varır
            if p['progress'] < 1.0:
                alive_particles.append(p)

        self.healing_particles = alive_particles

    def draw(self, obj):
        """Hücreyi çiz, yeşil çizgi ve healing particle'ları çiz."""
        screen = Screen()
        app = App()
        scene = app.get_current_scene()

        # Lenf düğümünü bul
        lymph_nodes = scene.get_objects_by_tag("lymph_node")
        if lymph_nodes and not lymph_nodes[0].dead:
            node = lymph_nodes[0]

            # HealerCellAI'dan bağlantı durumunu al
            ai_comp = obj.get_component("HealerCellAI")
            if ai_comp and hasattr(ai_comp.instance, 'is_connected') and ai_comp.instance.is_connected:
                # YEŞİL ÇİZGİ çiz - hücreden lenf düğümüne
                try:
                    from scripts.Camera import Camera
                    camera = Camera()

                    # World to screen dönüşümü
                    start_x, start_y = camera.world_to_screen(obj.x, obj.y)
                    end_x, end_y = camera.world_to_screen(node.x, node.y)

                    # Yeşil çizgi (parlak)
                    line_color = (100, 255, 150)
                    pygame.draw.line(screen.surface, line_color, (start_x, start_y), (end_x, end_y), 2)

                    # HEALING PARTICLE'LARI çiz - yeşil çizgi üzerinde hareket eden küçük daireler
                    for p in self.healing_particles:
                        # Lerp ile pozisyon hesapla (hücreden lenf düğümüne)
                        particle_x = obj.x + (node.x - obj.x) * p['progress']
                        particle_y = obj.y + (node.y - obj.y) * p['progress']

                        # Camera transform
                        px, py = camera.world_to_screen(particle_x, particle_y)

                        # Parlayan yeşil daire
                        particle_radius = 3
                        pygame.draw.circle(screen.surface, (150, 255, 200), (int(px), int(py)), particle_radius)

                except:
                    pass  # Camera yoksa çizgi çizme

        # Hücre gövdesini çiz
        self._draw_cell_body(obj)

    def _draw_cell_body(self, obj):
        """Hücre gövdesini çiz (jölemsi deformasyonlu)."""
        screen = Screen()

        # Surface oluştur
        size = int(self.radius * (2 + self.stretch_max))
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        if not self.current_points:
            return

        # Catmull-Rom spline ile yumuşak eğri
        curve_points = []
        segments_per_edge = 6

        for i in range(len(self.current_points)):
            p0 = self.current_points[(i - 1) % len(self.current_points)]
            p1 = self.current_points[i]
            p2 = self.current_points[(i + 1) % len(self.current_points)]
            p3 = self.current_points[(i + 2) % len(self.current_points)]

            for j in range(segments_per_edge):
                t = j / segments_per_edge
                px, py = self._catmull_rom_spline(p0, p1, p2, p3, t)
                curve_points.append((px + center, py + center))

        # Doldur
        if len(curve_points) > 2:
            pygame.draw.polygon(surface, self.color, curve_points)
            # Siyah çerçeve
            pygame.draw.polygon(surface, (0, 0, 0), curve_points, 2)

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

    def _catmull_rom_spline(self, p0, p1, p2, p3, t):
        """Catmull-Rom spline ile yumuşak eğri."""
        t2 = t * t
        t3 = t2 * t

        return (
            0.5 * ((2 * p1[0]) +
                   (-p0[0] + p2[0]) * t +
                   (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                   (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
            0.5 * ((2 * p1[1]) +
                   (-p0[1] + p2[1]) * t +
                   (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                   (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
        )
