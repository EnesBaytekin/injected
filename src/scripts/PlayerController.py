"""
Mouse ile hareket kontrolü.
Mouse sol tık basılıyken hedefe doğru çekim kuvveti uygular.
"""
from pygaminal import App, InputManager


class PlayerController:
    """Mouse ile hedefe doğru hareket."""

    def __init__(self):
        pass

    def update(self, obj):
        app = App()
        im = InputManager()

        # Movement component'ini al
        movement = obj.get_component("Movement")

        if not movement:
            return

        # Mouse sol tık (button 1) basılı mı?
        if im.is_mouse_pressed(3):
            # Mouse pozisyonunu al (ekran koordinatları)
            mouse_x, mouse_y = im.get_mouse_position()

            # Camera varsa dünya koordinatlarına çevir
            try:
                from scripts.Camera import Camera
                camera = Camera()
                mouse_x, mouse_y = camera.screen_to_world(mouse_x, mouse_y)
            except:
                pass  # Camera yoksa ekran koordinatlarını kullan

            movement.set_target(mouse_x, mouse_y)
        else:
            # Tık bırakıldı, çekim kuvvetini durdur
            movement.clear_target()

    def draw(self, obj):
        pass
