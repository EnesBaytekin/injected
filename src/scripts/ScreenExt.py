"""
Screen uzantısı - Camera desteği ile.
Framework'ün Screen sınıfını wrap eder.
"""
from pygaminal import Screen as BaseScreen


class ScreenExt:
    """Camera destekli Screen wrapper."""

    def __init__(self):
        self.base = BaseScreen()
        self.camera = None

    def set_camera(self, camera):
        """Camera ata."""
        self.camera = camera

    def blit(self, image, x, y):
        """
        Image çiz - camera offset'i uygula.
        """
        if self.camera:
            # Camera offset'i düş
            offset_x, offset_y = self.camera.get_offset()
            x = x - offset_x
            y = y - offset_y

        self.base.blit(image, x, y)

    def paste(self, image, x=0, y=0):
        """Blit alias."""
        self.blit(image, x, y)

    # Diğer metodları base'e forward et
    def init(self, width, height):
        self.base.init(width, height)

    def set_background_color(self, color):
        self.base.set_background_color(color)

    def set_background_image(self, image_path):
        self.base.set_background_image(image_path)

    def clear(self):
        self.base.clear()

    def refresh(self):
        self.base.refresh()

    @property
    def surface(self):
        return self.base.surface

    @property
    def width(self):
        return self.base.width

    @property
    def height(self):
        return self.base.height
