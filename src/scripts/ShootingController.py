"""
Shooting Controller - Mouse ve Joystick ile granül fırlatma.
Mouse sol tık veya Joystick A tuşu ile ateş eder.
"""
from pygaminal import App, Screen, InputManager, Object
import pygame
import math


class ShootingController:
    """
    Mouse sol tık ve Joystick A tuşu ile ateş eder.
    Mouse yönüne veya Joystick sağ thumbstick yönüne granül mermisi spawnlar.
    """

    def __init__(self, bullet_speed=400, cooldown=0.3):
        """
        Args:
            bullet_speed: Mermi hızı (piksel/saniye)
            cooldown: Ateş arası bekleme süresi (saniye)
        """
        self.bullet_speed = bullet_speed
        self.cooldown = cooldown
        self.last_shot_time = 0

        # Joystick initialization
        self.joystick = None
        self.last_trigger_state = False  # Trigger "just pressed" için
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
        except:
            pass

    def update(self, obj):
        """Her frame ateş kontrolü yap."""
        app = App()
        scene = app.get_current_scene()

        # Cooldown kontrolü
        if app.now - self.last_shot_time < self.cooldown:
            return

        # Ateş yönü
        dir_x = None
        dir_y = None

        # Joystick kontrolü
        if self.joystick:
            # Right trigger (button 5) - "just pressed" mantığı
            trigger_pressed = self.joystick.get_button(5)
            trigger_just_pressed = trigger_pressed and not self.last_trigger_state
            self.last_trigger_state = trigger_pressed

            if trigger_just_pressed:
                # PlayerController'dan aim direction al
                player_controller = obj.get_component("PlayerController")
                if player_controller:
                    dir_x = player_controller.joystick_aim_x
                    dir_y = player_controller.joystick_aim_y

        # Mouse kontrolü (fallback)
        if dir_x is None:
            im = InputManager()
            # Sol tık kontrolü - just pressed ile tek seferlik
            if im.is_mouse_just_pressed(1):
                # Mouse pozisyonunu al
                mouse_x, mouse_y = im.get_mouse_position()

                # World koordinatına çevir
                try:
                    from scripts.Camera import Camera
                    camera = Camera()
                    target_x, target_y = camera.screen_to_world(mouse_x, mouse_y)
                except:
                    target_x, target_y = mouse_x, mouse_y

                # Yön hesapla (objeden mouse'a)
                dx = target_x - obj.x
                dy = target_y - obj.y
                distance = (dx * dx + dy * dy) ** 0.5

                if distance > 0.1:
                    # Normalize yön
                    dir_x = dx / distance
                    dir_y = dy / distance

        # Ateş et
        if dir_x is not None and dir_y is not None:
            # Mermi spawnla (obj = owner)
            self._spawn_bullet(scene, obj.x, obj.y, dir_x, dir_y, obj)

            # Cooldown başlat
            self.last_shot_time = app.now

    def _spawn_bullet(self, scene, x, y, dir_x, dir_y, owner_obj):
        """Yeni mermi objesi spawnla - .obj dosyasından yükler."""
        # Spawn pozisyonu - karakter merkezinden biraz ötele
        spawn_offset = 10  # 10 piksel önde
        spawn_x = x + dir_x * spawn_offset
        spawn_y = y + dir_y * spawn_offset

        # .obj dosyasından obje yükle
        bullet = Object.from_file("objects/granule_bullet.obj", spawn_x, spawn_y)

        # Component'i al ve değerlerini güncelle - instance'a direkt set et!
        bullet_comp = bullet.get_component("GranuleBullet")
        bullet_comp.instance.dir_x = dir_x
        bullet_comp.instance.dir_y = dir_y
        bullet_comp.instance.speed = self.bullet_speed
        bullet_comp.instance.owner = owner_obj  # Owner'ı set et

        # Sahneye ekle
        scene.add_object(bullet)

    def draw(self, obj):
        """Çizim yok."""
        pass
