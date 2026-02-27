"""
Camera sistemi - karakteri smooth takip eder.
Singleton pattern ile global camera yönetimi.
"""
from pygaminal import App


class Camera:
    """Global kamera - smooth takip ile."""

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Kamera pozisyonu (dünya koordinatlarında)
        self.x = 0.0
        self.y = 0.0

        # Takip edilecek obje
        self.target = None

        # Smooth takip parametreleri
        self.follow_lerp = 3.0  # Takip hızı (saniye)
        self.enabled = True

    def set_target(self, obj):
        """Takip edilecek objeyi belirle."""
        self.target = obj

    def clear_target(self):
        """Takibi bırak."""
        self.target = None

    def set_position(self, x, y):
        """Kamerayı direkt belirli bir yere koy."""
        self.x = x
        self.y = y
        self.clear_target()

    def update(self, dt):
        """
        Her frame çağrılır - kamerayı günceller.
        Hedef objeyi ekranın ortasında smooth takip eder.
        """
        if not self.enabled or self.target is None:
            return

        # Ekran boyutlarını al
        app = App()
        scene = app.get_current_scene()
        screen_center_x = scene.width / 2
        screen_center_y = scene.height / 2

        # Hedef kamera pozisyonu (karakter ekranın ortasında olmalı)
        target_x = self.target.x - screen_center_x
        target_y = self.target.y - screen_center_y

        # Lerp ile yumuşak geçiş
        # new_pos = current + (target - current) * lerp_factor * dt
        self.x += (target_x - self.x) * self.follow_lerp * dt
        self.y += (target_y - self.y) * self.follow_lerp * dt

    def get_offset(self):
        """
        Çizim için offset döndür.
        Obje pozisyonundan camera pozisyonunu çıkar.
        """
        return (self.x, self.y)

    def world_to_screen(self, world_x, world_y):
        """
        Dünya koordinatlarını ekran koordinatlarına çevir.
        """
        offset_x, offset_y = self.get_offset()
        return (world_x - offset_x, world_y - offset_y)

    def screen_to_world(self, screen_x, screen_y):
        """
        Ekran koordinatlarını dünya koordinatlarına çevir.
        Mouse tıklaması için önemli.
        """
        offset_x, offset_y = self.get_offset()
        return (screen_x + offset_x, screen_y + offset_y)

    def shake(self, intensity=5.0, duration=0.3):
        """
        Ekran sarsma efekti (opsiyonel).
        """
        # İlerde implement edilebilir
        pass
