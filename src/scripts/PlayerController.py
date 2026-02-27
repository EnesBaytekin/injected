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
        if im.is_mouse_pressed(1):
            # Mouse pozisyonunu al
            mouse_x, mouse_y = im.get_mouse_position()
            movement.set_target(mouse_x, mouse_y)
        else:
            # Tık bırakıldı, çekim kuvvetini durdur
            movement.clear_target()

    def draw(self, obj):
        pass
