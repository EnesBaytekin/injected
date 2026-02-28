"""
Mouse ve Joystick ile hareket kontrolü.
Mouse sol tık basılıyken hedefe doğru çekim kuvveti uygular.
Joystick sol thumbstick ile hareket.
"""
from pygaminal import App, InputManager
import pygame
import math


class PlayerController:
    """Mouse ve Joystick ile hedefe doğru hareket."""

    def __init__(self):
        # Joystick initialization
        self.joystick = None
        self.joystick_index = None

        try:
            pygame.joystick.init()
            # İlk joysticği al
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.joystick_index = 0
                print(f"Joystick connected: {self.joystick.get_name()}")
        except:
            pass

        # Joystick aim direction (ShootingController kullanacak)
        self.joystick_aim_x = 1.0  # Varsayılan: sağa
        self.joystick_aim_y = 0.0

    def update(self, obj):
        app = App()
        im = InputManager()

        # Movement component'ini al
        movement = obj.get_component("Movement")

        if not movement:
            return

        # Joystick kontrolü
        if self.joystick:
            # Sol thumbstick (axis 0 = x, axis 1 = y)
            left_x = self.joystick.get_axis(0)
            left_y = self.joystick.get_axis(1)

            # Deadzone (ölü bölge) - çok küçük değerleri yoksay
            deadzone = 0.2

            if abs(left_x) > deadzone or abs(left_y) > deadzone:
                # Joystick ile hareket - hedefe doğru çekim yerine doğrudan hız uygula
                # Hedefi karakterin önünde uzak bir nokta olarak belirle
                target_x = obj.x + left_x * 100
                target_y = obj.y + left_y * 100
                movement.set_target(target_x, target_y)
            else:
                # Joystick serbest, mouse'a geri dön
                movement.clear_target()

            # Sağ thumbstick (axis 2 = x, axis 3 = y) - aim direction
            right_x = self.joystick.get_axis(3)
            right_y = self.joystick.get_axis(4)

            if abs(right_x) > deadzone or abs(right_y) > deadzone:
                # Aim direction'u güncelle
                self.joystick_aim_x = right_x
                self.joystick_aim_y = right_y
        else:
            # Joystick yok, mouse kontrolü
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

                # Mouse aim direction'u da güncelle
                dx = mouse_x - obj.x
                dy = mouse_y - obj.y
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > 0.1:
                    self.joystick_aim_x = dx / dist
                    self.joystick_aim_y = dy / dist
            else:
                # Tık bırakıldı, çekim kuvvetini durdur
                movement.clear_target()

    def draw(self, obj):
        pass
