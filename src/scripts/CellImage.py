from pygaminal import *
import math
import random

class CellImage:
    """
    Deforme olabilen jölemsi hücre görseli.
    16 noktalı yumuşak geçişli çizim.
    """

    def __init__(self, radius=32, color=(255, 180, 80), wobble_speed=2.0, wobble_amount=4.0):
        """
        Args:
            radius: Hücre yarıçapı
            color: RGB renk tuple
            wobble_speed: Deformasyon hızı
            wobble_amount: Deformasyon miktarı (piksel)
        """
        self.radius = radius
        self.color = color
        self.wobble_speed = wobble_speed
        self.wobble_amount = wobble_amount

        # 16 nokta oluştur (daire etrafında)
        self.num_points = 16
        self.base_angles = [i * (2 * math.pi / self.num_points) for i in range(self.num_points)]

        # Her nokta için rastgele offset phase
        self.phases = [random.random() * 2 * math.pi for _ in range(self.num_points)]

        # Mevcut pozisyonlar
        self.current_points = []

    def update(self, obj):
        """Her frame noktaları hafifçe kaydır"""
        app = App()

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

    def _catmull_rom_spline(self, p0, p1, p2, p3, t):
        """Catmull-Rom spline ile yumuşak eğri (4 nokta arası)"""
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

    def draw(self, obj):
        """Pixel art tarzı deformasyonlu hücre çiz"""
        screen = Screen()

        # Surface oluştur
        size = int(self.radius * 3)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        if not self.current_points:
            return

        # Yumuşak eğri ile noktaları birleştir
        points = self.current_points
        curve_points = []

        # Her nokta arası spline interpolasyon
        segments_per_edge = 8

        for i in range(len(points)):
            # Catmull-Rom için 4 nokta (wrap-around)
            p0 = points[(i - 1) % len(points)]
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            p3 = points[(i + 2) % len(points)]

            for j in range(segments_per_edge):
                t = j / segments_per_edge
                px, py = self._catmull_rom_spline(p0, p1, p2, p3, t)
                curve_points.append((px + center, py + center))

        # Doldur (daha yumuşak için anti-aliased polygon)
        if len(curve_points) > 2:
            pygame.draw.polygon(surface, self.color, curve_points)

            # Siyah çerçeve (outline)
            pygame.draw.polygon(surface, (0, 0, 0), curve_points, 3)

        # İç granüller (ilaç tanecikleri) - opsiyonel görsel detay
        num_granules = 5
        for i in range(num_granules):
            angle = (i / num_granules) * 2 * math.pi
            gr_r = self.radius * 0.4
            gx = center + math.cos(angle) * gr_r
            gy = center + math.sin(angle) * gr_r
            granule_radius = max(2, int(self.radius * 0.1))
            pygame.draw.circle(surface, (255, 220, 150), (int(gx), int(gy)), granule_radius)

        # Surface'i ekrana çiz
        screen.blit(Image(surface), obj.x - center, obj.y - center)
