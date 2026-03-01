"""
Healer Spawn Timer - Virüs öldükten sonra healer cell spawnlamak için timer.
"""
from pygaminal import App, Object


class HealerSpawnTimer:
    """Gecikmeli healer cell spawn timer'ı."""

    def __init__(self, x, y, delay=0.5):
        """
        Args:
            x, y: Spawn pozisyonu
            delay: Gecikme süresi (saniye)
        """
        self.x = x
        self.y = y
        self.delay = delay
        self.elapsed = 0.0

    def update(self, obj):
        app = App()
        self.elapsed += app.dt

        if self.elapsed >= self.delay:
            # Healer cell spawnla
            scene = app.get_current_scene()
            healer = Object.from_file("objects/healer_cell.obj", self.x, self.y)
            scene.add_object(healer)
            print(f"Virus transformed to healer cell at ({self.x:.1f}, {self.y:.1f})")

            # Timer'ı yok et
            obj.kill()

    def draw(self, obj):
        """Çizim yok."""
        pass
