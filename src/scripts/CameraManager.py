"""
Camera Manager - Camera'ı güncelleyen component.
Sahneye eklenerek her frame Camera.update() çağırır.
"""
from pygaminal import App


class CameraManager:
    """
    Camera'ı güncelleyen manager component.
    Sahnedeki herhangi bir objede olabilir.
    """

    def __init__(self, follow_tag="controllable"):
        """
        Args:
            follow_tag: Takip edilecek obje tag'i (varsayılan: "controllable")
        """
        self.follow_tag = follow_tag
        self.initialized = False

    def update(self, obj):
        """Her frame Camera'ı güncelle."""
        app = App()
        scene = app.get_current_scene()

        # Camera'ı al (singleton)
        from scripts.Camera import Camera
        camera = Camera()

        # İlk frame - camera başlangıç pozisyonu
        if not self.initialized:
            camera.x = 0
            camera.y = 0
            self.initialized = True

        # Her frame hedefi kontrol et
        # Önce split_cell tag'li objeleri kontrol et (bölünmüş hücreler)
        split_cells = scene.get_objects_by_tag("split_cell")
        if split_cells:
            # Orta noktayı hesapla
            avg_x = 0
            avg_y = 0
            count = 0
            for cell in split_cells:
                if not cell.dead:
                    avg_x += cell.x
                    avg_y += cell.y
                    count += 1

            if count > 0:
                avg_x /= count
                avg_y /= count

                # Camera'yı orta noktaya doğru hareket ettir
                # Fake bir target object oluşturmak yerine direkt pozisyon güncelle
                screen_center_x = scene.width / 2
                screen_center_y = scene.height / 2

                # Hedef kamera pozisyonu
                target_x = avg_x - screen_center_x
                target_y = avg_y - screen_center_y

                # Lerp ile yumuşak geçiş
                camera.x += (target_x - camera.x) * camera.follow_lerp * app.dt
                camera.y += (target_y - camera.y) * camera.follow_lerp * app.dt

                # Target'i temizle (manuel güncelledik)
                camera.clear_target()
                return

        # Bölünmüş hücre yoksa, hero tag'li obje takip et (birleşmiş hücre)
        heroes = scene.get_objects_by_tag("hero")
        if heroes and not heroes[0].dead:
            camera.set_target(heroes[0])

        # Camera'ı güncelle (smooth takip)
        camera.update(app.dt)

    def draw(self, obj):
        """Çizim yok."""
        pass
