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

        # Camera'ı al (singleton)
        from scripts.Camera import Camera
        camera = Camera()

        # İlk frame - hedefi belirle
        if not self.initialized:
            scene = app.get_current_scene()

            # Belirtilen tag'e sahip objeyi bul
            targets = scene.get_objects_by_tag(self.follow_tag)
            if targets:
                camera.set_target(targets[0])  # İlk bulduğunu takip et

            # Camera başlangıç pozisyonu
            camera.x = 0
            camera.y = 0

            self.initialized = True

        # Camera'ı güncelle (smooth takip)
        camera.update(app.dt)

    def draw(self, obj):
        """Çizim yok."""
        pass
