"""
Granule Bullet - Fırlatılan ilaç taneciği.
Sıvı içinde hareket eder, sürtünme ile yavaşlar, pulse animasyonu.
Hücrelere çarpınca yutulabilir veya geri seker.
"""
from pygaminal import App, Screen, Object
import pygame
import math


class GranuleBullet:
    """
    Fırlatılan granül mermisi.
    Hareket, sürtünme, pulse, lifecycle yönetir.
    """

    def __init__(self, dir_x=1.0, dir_y=0.0, speed=400, friction=1.5):
        """
        Args:
            dir_x, dir_y: Hareket yönü (normalize edilmiş)
            speed: Başlangıç hızı (piksel/saniye)
            friction: Sürtünme katsayısı
        """
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.friction = friction

        # Hız bittiğinde bekleme süresi
        self.wait_time = 0
        self.wait_duration = 1  # 1 saniye bekle
        self.is_waiting = False

        # Pulse animasyonu için
        self.base_radius = 4
        self.pulse_speed = 3.0
        self.pulse_amount = 1.5
        self.pulse_phase = 0

        # Renk
        self.color = (255, 235, 180)  # Açık sarı

        # Yutulma durumu
        self.is_swallowed = False
        self.swallowed_by = None  # Hangi hücre yuttu?
        self.owner = None  # Hangi hücre ateşledi?

        # Hücre içinde orbital hareket
        self.orbit_angle = 0.0
        self.orbit_radius = 0.0
        self.orbit_speed = 2.0

        # Çarpışma kontrolü için
        self._processed_collision = False  # Bu frame'de çarpışma işlendi mi?

    def update(self, obj):
        """Hareket, sürtünme, pulse, lifecycle güncelle."""
        app = App()

        # Yutulduysa hücreyle hareket et
        if self.is_swallowed and self.swallowed_by:
            cell_obj = self.swallowed_by

            # Orbital hareket - merkezi etrafında dolaş
            self.orbit_angle += self.orbit_speed * app.dt

            # Hücrenin içinde orbital pozisyon
            offset_x = math.cos(self.orbit_angle) * self.orbit_radius
            offset_y = math.sin(self.orbit_angle) * self.orbit_radius

            # Mini wobble ekle
            wobble_x = math.cos(app.now * 5 + self.orbit_angle) * 2
            wobble_y = math.sin(app.now * 5 + self.orbit_angle) * 2

            obj.x = cell_obj.x + offset_x + wobble_x
            obj.y = cell_obj.y + offset_y + wobble_y

            # Pulse animasyonu devam etsin
            self.pulse_phase += self.pulse_speed * app.dt
            return  # Diğer update işlemlerini yapma

        # Hareket etmiyorsa bekle
        if self.is_waiting:
            self.wait_time += app.dt
            if self.wait_time >= self.wait_duration:
                # Particle efekti spawnla
                self._spawn_death_particles(obj)

                # Obje yok et
                obj.kill()
            return

        # Çarpışma kontrolü
        self._check_collision(obj)

        # Hareket
        # Hızı güncelle (sürtünme)
        self.speed *= (1 - self.friction * app.dt)

        # Çok düşük hızları sıfırla
        if self.speed < 5:
            self.speed = 0
            self.is_waiting = True  # Beklemeye başla
        else:
            # Pozisyon güncelle
            obj.x += self.dir_x * self.speed * app.dt
            obj.y += self.dir_y * self.speed * app.dt

        # Pulse animasyonu
        self.pulse_phase += self.pulse_speed * app.dt

    def _check_collision(self, obj):
        """Hücrelerle çarpışma kontrolü."""
        scene = App().get_current_scene()

        # Sahnedeki tüm objeleri kontrol et
        for other_obj in scene.get_all_objects():
            # Kendini atla
            if other_obj is obj:
                continue

            # Owner'ı atla (kendi ateşlediği hücre)
            if self.owner and other_obj is self.owner:
                continue

            # CellImage component'i var mı?
            cell_image = other_obj.get_component("CellImage")
            if not cell_image:
                continue

            # CircleHitbox component'i var mı?
            hitbox = other_obj.get_component("CircleHitbox")
            if not hitbox:
                continue

            # Bullet'un kendi hitbox'ı (küçük bir daire)
            bullet_radius = 2  # Bullet yaklaşık 4px çapında

            # Çarpışma kontrolü
            cell_center = hitbox.get_world_center(other_obj)
            cell_radius = hitbox.get_world_radius()

            dx = obj.x - cell_center[0]
            dy = obj.y - cell_center[1]
            distance = (dx * dx + dy * dy) ** 0.5

            # Çarpışma var mı?
            if distance < (cell_radius + bullet_radius):
                # Penetrasyon derinliği - hücre ne kadar içine girmiş?
                penetration = (cell_radius + bullet_radius) - distance

                # Merkeze doğru olan hız bileşenini hesapla
                # Bullet → Cell merkezi vektörü (normalize)
                to_center_x = cell_center[0] - obj.x
                to_center_y = cell_center[1] - obj.y
                dist_to_center = (to_center_x**2 + to_center_y**2) ** 0.5

                if dist_to_center > 0:
                    to_center_x /= dist_to_center
                    to_center_y /= dist_to_center

                # Velocity vektörü
                vel_x = self.dir_x * self.speed
                vel_y = self.dir_y * self.speed

                # Dot product = merkeze doğru olan hız bileşeni (radial velocity)
                radial_velocity = vel_x * to_center_x + vel_y * to_center_y

                # Debug
                print(f"Collision! penetration={penetration:.2f}, radial_vel={radial_velocity:.1f}")

                # Merkeze doğru olan hız bileşeni 10'dan büyükse yut
                # Teğet/kenardan geçiyorsa (radial velocity düşük) sek
                if radial_velocity > 50:
                    # YUTULMA!
                    print(f"  -> SWALLOWED!")
                    self._be_swallowed(obj, other_obj, cell_image)
                else:
                    # Geri sek - proper reflection
                    print(f"  -> BOUNCE")

                    # Normal vektör: hücre merkezinden bullet'a doğru
                    normal_x = dx / distance
                    normal_y = dy / distance

                    # Reflection: v' = v - 2(v·n)n
                    dot_product = self.dir_x * normal_x + self.dir_y * normal_y

                    # Yansıtılmış direction
                    self.dir_x = self.dir_x - 2 * dot_product * normal_x
                    self.dir_y = self.dir_y - 2 * dot_product * normal_y

                    # Biraz hız kaybet
                    self.speed *= 0.7

                    # Hücreden uzağa taşı (takılmamak için)
                    overlap = (cell_radius + bullet_radius) - distance + 1
                    obj.x += normal_x * overlap
                    obj.y += normal_y * overlap

                # Bir frame'de sadece bir çarpışma işle
                break

    def _be_swallowed(self, obj, cell_obj, cell_image):
        """Hücre tarafından yutul."""
        # Yutulma durumunu işaretle
        self.is_swallowed = True
        self.swallowed_by = cell_obj

        # Orbital hareket parametreleri - rastgele
        import random
        self.orbit_angle = random.random() * 2 * math.pi  # Rastgele açı
        self.orbit_radius = random.uniform(3, 8)  # 3-8px yarıçapta orbit
        self.orbit_speed = random.uniform(1.5, 3.0)  # Dönme hızı

        # Hücreye bildir - yutuldu!
        # cell_image ScriptComponent olabilir (instance ile erişilir)
        # veya direkt instance olabilir (SupporterCellAI gibi)
        target = cell_image.instance if hasattr(cell_image, 'instance') else cell_image

        if hasattr(target, 'swallow_bullet'):
            target.swallow_bullet(obj)

    def _spawn_death_particles(self, obj):
        """Bullet yok olurken mini particle patlaması oluştur."""
        from scripts.ParticleEffect import ParticleEffect
        from pygaminal import ScriptComponent

        # Particle objesi oluştur - yüksek depth ile (her şeyin önünde)
        particle_obj = Object(obj.x, obj.y, depth=1000)

        # Particle efekti ekle - mini pixel patlaması
        effect = ParticleEffect(
            particle_count=20,  # 20 tane mini particle
            shape=ParticleEffect.SHAPE_PIXEL,
            color=((255, 235, 180), (255, 200, 100)),  # Sarı -> altın
            lifetime=(0.3, 0.6),  # Kısa ömür
            size=1.0,  # 1 piksel
            velocity=50,  # Yavaş yayılma
            acceleration=(0, 0),
            spawn_mode="burst",
            one_shot=True,
            fade_out=True,
            friction=2.0,  # Hızlı yavaşla
            spread=360  # Tüm yönler
        )

        # ScriptComponent wrapper ile ekle
        script_comp = ScriptComponent("scripts/ParticleEffect", [])
        script_comp.instance = effect
        particle_obj.add_component(script_comp)

        # Sahneye ekle
        scene = App().get_current_scene()
        scene.add_object(particle_obj)

    def draw(self, obj):
        """Granülü çiz - pulse efekti ile."""
        screen = Screen()

        # Pulse hesapla
        pulse = math.sin(self.pulse_phase) * self.pulse_amount
        radius = self.base_radius + pulse

        # Surface oluştur (transparan için)
        surface = pygame.Surface((int(radius * 4), int(radius * 4)), pygame.SRCALPHA)
        center = int(radius * 2)

        # Granül çiz (parlak sarı)
        color_with_alpha = (*self.color, 255)
        pygame.draw.circle(surface, color_with_alpha, (center, center), int(radius))

        # Daha parlak merkez
        highlight_color = (255, 255, 220)
        highlight_radius = radius * 0.5
        pygame.draw.circle(surface, highlight_color, (center, center), int(highlight_radius))

        # Camera transform uygula
        draw_x = obj.x - center
        draw_y = obj.y - center

        try:
            from scripts.Camera import Camera
            camera = Camera()
            draw_x, draw_y = camera.world_to_screen(draw_x, draw_y)
        except Exception as e:
            raise(e)

        # Çiz
        screen.surface.blit(surface, (draw_x, draw_y))
