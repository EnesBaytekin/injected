from pygaminal import *
import math
import random

class CellImage:
    """
    Deforme olabilen jölemsi hücre görseli.
    16 noktalı yumuşak geçişli çizim.
    """

    def __init__(self, radius=32, color=(255, 180, 80), wobble_speed=2.0, wobble_amount=4.0, stretch_max=2.5):
        """
        Args:
            radius: Hücre yarıçapı
            color: RGB renk tuple
            wobble_speed: Deformasyon hızı
            wobble_amount: Deformasyon miktarı (piksel)
            stretch_max: Maksimum stretch faktörü (1.0 = yok, 2.0 = 2x uzama)
        """
        self.radius = radius
        self.color = color
        self.wobble_speed = wobble_speed
        self.wobble_amount = wobble_amount
        self.stretch_max = stretch_max

        # 16 nokta oluştur (daire etrafında)
        self.num_points = 16
        self.base_angles = [i * (2 * math.pi / self.num_points) for i in range(self.num_points)]

        # Her nokta için rastgele offset phase
        self.phases = [random.random() * 2 * math.pi for _ in range(self.num_points)]

        # Mevcut pozisyonlar
        self.current_points = []

        # Granül sistemi
        self.num_granules = 6
        self.granules = []
        for _ in range(self.num_granules):
            self.granules.append({
                'angle': random.random() * 2 * math.pi,
                'distance': random.uniform(0.2, 0.5) * self.radius,  # Merkezden uzaklık
                'rotation_speed': random.uniform(-2, 2),  # Dönme hızı
                'pulse_phase': random.random() * 2 * math.pi,  # Boyat pulse phase
                'pulse_speed': random.uniform(2, 4),  # Boyat pulse hızı
                'wobble_offset': random.random() * 2 * math.pi,
                'orbit_radius': random.uniform(0.05, 0.15) * self.radius,  # Mini orbit yarıçapı
                'orbit_speed': random.uniform(1, 3),  # Orbit hızı
                'orbit_phase': random.random() * 2 * math.pi,
            })
        self.granule_states = []  # Her frame için güncel durumlar

        # Yutulma mekaniiği
        self.swallowed_bullets = []  # Yutulan bullet objeleri
        self.capacity = 3  # Kaç bullet yutunca sindirilmeye başlayacak
        self.is_digesting = False  # Sindiriliyor mu?
        self.digestion_progress = 0.0  # Sindirme ilerlemesi (0.0 - 1.0)
        self.tremor_intensity = 0.0  # Titreme şiddeti
        self.inner_color_progress = 0.0  # İç renk beyazlaşma ilerlemesi

    def update(self, obj):
        """Her frame noktaları hafifçe kaydır, granülleri güncelle"""
        app = App()

        # Sindirme animasyonu
        if self.is_digesting:
            self.digestion_progress += app.dt * 0.5  # 2 saniyede tamamlanır

            # Titreme şiddeti artar
            self.tremor_intensity = self.digestion_progress * 5.0  # Maksimum 5px titreme

            # İç renk beyazlaşma ilerlemesi
            self.inner_color_progress = min(1.0, self.digestion_progress * 1.5)

            # Sindirme bitti mi?
            if self.digestion_progress >= 1.0:
                self._explode_and_die(obj)
                return

        # Hücre deformasyonunu güncelle
        new_points = []
        for i, angle in enumerate(self.base_angles):
            # Zaman bazlı wobble
            phase = self.phases[i]
            wobble = math.sin(app.now * self.wobble_speed + phase) * self.wobble_amount

            # Rastgele mikroskopik hareket
            micro_wobble = math.cos(app.now * self.wobble_speed * 1.7 + phase) * (self.wobble_amount * 0.3)

            # Sindirme titremesi ekle
            tremor = 0
            if self.is_digesting:
                tremor = math.sin(app.now * 20 + phase) * self.tremor_intensity

            # Yarıçapı hesapla
            r = self.radius + wobble + micro_wobble + tremor

            # Pozisyon
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            new_points.append((x, y))

        self.current_points = new_points

        # Granülleri güncelle
        self.granule_states = []
        for g in self.granules:
            # Ana rotasyon (merkez etrafında dönme)
            current_angle = g['angle'] + app.now * g['rotation_speed'] * 0.5

            # Mini orbit (merkez etrafında küçük dairesel hareket)
            orbit_offset_x = math.cos(app.now * g['orbit_speed'] + g['orbit_phase']) * g['orbit_radius']
            orbit_offset_y = math.sin(app.now * g['orbit_speed'] + g['orbit_phase']) * g['orbit_radius']

            # Hafif rastgele wobble
            wobble_x = math.cos(app.now * 2 + g['wobble_offset']) * 2
            wobble_y = math.sin(app.now * 2.3 + g['wobble_offset']) * 2

            # Sindirme titremesi
            tremor_x = tremor_y = 0
            if self.is_digesting:
                tremor_x = math.sin(app.now * 15 + g['wobble_offset']) * self.tremor_intensity * 0.5
                tremor_y = math.cos(app.now * 15 + g['wobble_offset']) * self.tremor_intensity * 0.5

            # Ana pozisyon
            base_x = math.cos(current_angle) * g['distance']
            base_y = math.sin(current_angle) * g['distance']

            # Final pozisyon (tüm offset'ler eklenir)
            final_x = base_x + orbit_offset_x + wobble_x + tremor_x
            final_y = base_y + orbit_offset_y + wobble_y + tremor_y

            # Boyat pulse (büyüyüp küçülme)
            base_radius = max(2, int(self.radius * 0.08))
            pulse_amount = math.sin(app.now * g['pulse_speed'] + g['pulse_phase']) * 0.4 + 1  # 0.6x - 1.4x
            final_radius = base_radius * pulse_amount

            self.granule_states.append({
                'x': final_x,
                'y': final_y,
                'radius': final_radius
            })

    def swallow_bullet(self, bullet_obj):
        """Bullet tarafından yutul."""
        # Bullet'u listeye ekle
        self.swallowed_bullets.append(bullet_obj)

        # Her bullet yutulduğunda iç renk biraz bozulur
        self.inner_color_progress += 0.15

        # Capacity doldu mu?
        if len(self.swallowed_bullets) >= self.capacity and not self.is_digesting:
            # Sindirmeye başla!
            self.is_digesting = True

    def _explode_and_die(self, obj):
        """Sindirme tamamlandı - hücre particle patlamasıyla yok olur."""
        from pygaminal import App, Object
        from scripts.ParticleEffect import ParticleEffect

        # İçindeki bullet'ları da yok et
        for bullet_obj in self.swallowed_bullets:
            if bullet_obj and not bullet_obj.dead:
                bullet_obj.kill()

        # Tonla beyaz particle patlaması
        particle_count = 100
        particle_obj = Object(obj.x, obj.y, depth=1000)

        effect = ParticleEffect(
            particle_count=particle_count,
            shape=ParticleEffect.SHAPE_PIXEL,
            color=((255, 255, 255), (200, 200, 200)),  # Beyaz -> gri
            lifetime=(0.5, 1.5),
            size=(1, 2),
            velocity=150,
            acceleration=(0, 0),
            spawn_mode="burst",
            one_shot=True,
            fade_out=True,
            friction=0.5,
            spread=360
        )

        from pygaminal import ScriptComponent
        script_comp = ScriptComponent("scripts/ParticleEffect", [])
        script_comp.instance = effect
        particle_obj.add_component(script_comp)

        # Sahneye ekle
        scene = App().get_current_scene()
        scene.add_object(particle_obj)

        # Hücreyi yok et
        obj.kill()

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
        """Pixel art tarzı deformasyonlu hücre çiz - hıza göre eliptik deformasyon"""
        screen = Screen()

        # Surface oluştur - stretch_max'a göre büyüt
        size = int(self.radius * (2 + self.stretch_max))  # Yeterince büyük
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        if not self.current_points:
            return

        # Hıza göre deformasyon parametrelerini hesapla
        movement = obj.get_component("Movement")
        stretch_factor = 1.0  # Varsayılan: deformasyon yok

        if movement:
            # Hız vektörünü al
            vel_x = movement.vel_x
            vel_y = movement.vel_y
            speed = (vel_x ** 2 + vel_y ** 2) ** 0.5

            # Hıza göre stretch faktörü (maksimum stretch_max'a kadar)
            # speed = 200 ise stretch_factor = stretch_max
            max_expected_speed = 200.0
            speed_ratio = min(speed / max_expected_speed, 1.0)
            stretch_factor = 1.0 + speed_ratio * (self.stretch_max - 1.0)  # 1.0 ile stretch_max arası

        # Hız yönünü normalize et
        velocity_dir = (1.0, 0.0)  # Varsayılan (sağ)
        if movement:
            vel_x = movement.vel_x
            vel_y = movement.vel_y
            speed = (vel_x ** 2 + vel_y ** 2) ** 0.5
            if speed > 0.1:
                velocity_dir = (vel_x / speed, vel_y / speed)

        # Hız yönüne dik vektör (perpendicular)
        perp_dir = (-velocity_dir[1], velocity_dir[0])

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

                # Hıza göre eliptik deformasyon uygula
                if stretch_factor > 1.001:
                    # Nokta pozisyonunu hız yönü ve dik yönüne decompose et
                    # velocity yönündeki bileşen
                    vel_dot = px * velocity_dir[0] + py * velocity_dir[1]
                    # perpendicular yönündeki bileşen
                    perp_dot = px * perp_dir[0] + py * perp_dir[1]

                    # Hız yönünde: stretch_factor kadar uzat
                    vel_dot *= stretch_factor
                    # Dik yönde: 1/stretch_factor kadar kısalt (sıkıştır)
                    perp_dot /= stretch_factor

                    # Tekrar birleştir
                    px = vel_dot * velocity_dir[0] + perp_dot * perp_dir[0]
                    py = vel_dot * velocity_dir[1] + perp_dot * perp_dir[1]

                curve_points.append((px + center, py + center))

        # Doldur (daha yumuşak için anti-aliased polygon)
        if len(curve_points) > 2:
            # İç renk beyazlaşma efekti
            if self.inner_color_progress > 0:
                # Original color'dan beyaz'a interpolasyon
                r = int(self.color[0] + (255 - self.color[0]) * self.inner_color_progress)
                g = int(self.color[1] + (255 - self.color[1]) * self.inner_color_progress)
                b = int(self.color[2] + (255 - self.color[2]) * self.inner_color_progress)
                fill_color = (r, g, b)
            else:
                fill_color = self.color

            pygame.draw.polygon(surface, fill_color, curve_points)

            # Siyah çerçeve (outline) - her zaman siyah kalır
            pygame.draw.polygon(surface, (0, 0, 0), curve_points, 3)

        # İç granüller (ilaç tanecikleri) - hareketli, dönen, boyut değiştiren
        for state in self.granule_states:
            gx = center + state['x']
            gy = center + state['y']

            # Granüllere de eliptik deformasyon uygula
            if stretch_factor > 1.001:
                # Merkezden relative pozisyon (center'a göre)
                rel_x = state['x']
                rel_y = state['y']

                # Hız yönü ve dik yönüne decompose et
                vel_dot = rel_x * velocity_dir[0] + rel_y * velocity_dir[1]
                perp_dot = rel_x * perp_dir[0] + rel_y * perp_dir[1]

                # Hız yönünde: stretch_factor kadar uzat
                vel_dot *= stretch_factor
                # Dik yönde: 1/stretch_factor kadar kısalt
                perp_dot /= stretch_factor

                # Tekrar birleştir
                rel_x = vel_dot * velocity_dir[0] + perp_dot * perp_dir[0]
                rel_y = vel_dot * velocity_dir[1] + perp_dot * perp_dir[1]

                # Center'ı ekle
                gx = center + rel_x
                gy = center + rel_y

            granule_radius = max(1, int(state['radius']))
            # Daha parlak sarı renk
            pygame.draw.circle(surface, (255, 235, 180), (int(gx), int(gy)), granule_radius)

        # Camera transform uygula ve çiz
        draw_x = obj.x - center
        draw_y = obj.y - center

        # Camera varsa world to screen dönüşümü yap
        try:
            from scripts.Camera import Camera
            camera = Camera()
            draw_x, draw_y = camera.world_to_screen(draw_x, draw_y)
        except:
            pass  # Camera yoksa düz çiz

        screen.blit(Image(surface), draw_x, draw_y)
