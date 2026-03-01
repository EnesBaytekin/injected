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

    def __init__(self, bullet_speed=400, cooldown=0.3, shoulder_button=None):
        """
        Args:
            bullet_speed: Mermi hızı (piksel/saniye)
            cooldown: Ateş arası bekleme süresi (saniye)
            shoulder_button: 4 (sol) veya 5 (sağ) - None ise trigger/mouse kullan
        """
        self.bullet_speed = bullet_speed
        self.cooldown = cooldown
        self.last_shot_time = 0
        self.shoulder_button = shoulder_button

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

        # Ateş yönü - input yönü (hareket yönü DEĞİL)
        dir_x = None
        dir_y = None

        # Joystick kontrolü (shoulder button veya right trigger)
        should_fire = False
        if self.joystick:
            if self.shoulder_button is not None:
                # Bölünmüş hücre - shoulder button kullan
                trigger_pressed = self.joystick.get_button(self.shoulder_button)
                trigger_just_pressed = trigger_pressed and not self.last_trigger_state
                self.last_trigger_state = trigger_pressed

                if trigger_just_pressed:
                    should_fire = True
                    # Ateş yönü = thumbstick input yönü (hareket yönü DEĞİL)
                    movement = obj.get_component("Movement")
                    if movement and movement.joystick_thumb:
                        # Joystick inputunu oku
                        deadzone = 0.2
                        if movement.joystick_thumb == "left":
                            thumb_x = self.joystick.get_axis(0)
                            thumb_y = self.joystick.get_axis(1)
                        else:  # right
                            thumb_x = self.joystick.get_axis(3)
                            thumb_y = self.joystick.get_axis(4)

                        # Deadzone kontrolü ve normalize
                        if abs(thumb_x) > deadzone or abs(thumb_y) > deadzone:
                            dir_x = thumb_x
                            dir_y = thumb_y
                            # Normalize et (magnitude önemli değil, yön önemli)
                            mag = (dir_x ** 2 + dir_y ** 2) ** 0.5
                            if mag > 0:
                                dir_x /= mag
                                dir_y /= mag

                    # Input yoksa varsayılan yön (sağ)
                    if dir_x is None:
                        dir_x = 1.0
                        dir_y = 0.0
            else:
                # Ana hücre - right trigger (button 5) kullan
                trigger_pressed = self.joystick.get_button(5)
                trigger_just_pressed = trigger_pressed and not self.last_trigger_state
                self.last_trigger_state = trigger_pressed

                if trigger_just_pressed:
                    should_fire = True
                    # Ateş yönü = PlayerController'dan aim direction (right thumbstick)
                    player_controller = obj.get_component("PlayerController")
                    if player_controller and hasattr(player_controller, 'joystick_aim_x'):
                        aim_x = player_controller.joystick_aim_x
                        aim_y = player_controller.joystick_aim_y
                        # Aim direction varsa kullan
                        if aim_x != 0 or aim_y != 0:
                            dir_x = aim_x
                            dir_y = aim_y
                    # Yoksa varsayılan yön (sağ)
                    if dir_x is None:
                        dir_x = 1.0
                        dir_y = 0.0

        # Mouse kontrolü (fallback - shoulder button yoksa)
        if not should_fire and self.shoulder_button is None:
            im = InputManager()
            # Sol tık kontrolü - just pressed ile tek seferlik
            if im.is_mouse_just_pressed(1):
                should_fire = True
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
                else:
                    # Mouse üstündeyse varsayılan yön
                    dir_x = 1.0
                    dir_y = 0.0

        # Ateş et
        if should_fire and dir_x is not None and dir_y is not None:
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

        # SES: Bullet fırlatma
        self._play_sound("throw_bullet", scene)

    def _play_sound(self, sound_name, scene):
        """Sound efektini çal."""
        # SoundManager objesini bul
        sound_managers = scene.get_objects_by_tag("sound")
        if sound_managers and not sound_managers[0].dead:
            sound_manager = sound_managers[0]
            sound_comp = sound_manager.get_component("SoundManager")
            if sound_comp and hasattr(sound_comp, 'instance'):
                sound_comp.instance.play(sound_name, volume=0.7)

    def draw(self, obj):
        """Çizim yok."""
        pass
