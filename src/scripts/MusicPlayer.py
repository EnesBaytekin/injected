"""
Music Player - Background music çalar.
Sahne başladığında müziği başlatır ve sürekli çalar.
"""
from pygaminal import App
import pygame
import os


class MusicPlayer:
    """
    Background music çalar.
    Sürekli dönen tema müziği.
    """

    def __init__(self, music_file="main_theme.ogg", volume=0.25):
        """
        Args:
            music_file: Müzik dosyası (sounds dizininde)
            volume: Ses seviyesi (0.0 - 1.0)
        """
        self.music_file = music_file
        self.volume = volume
        self.is_playing = False

    def update(self, obj):
        """Müzik başlat - bir kere çalışır."""
        if not self.is_playing:
            try:
                # Mixer başlat
                pygame.mixer.init()

                # Ses seviyesi ayarla
                pygame.mixer.music.set_volume(self.volume)

                # Müzik dosyasını yükle ve çal
                music_path = os.path.join("sounds", self.music_file)

                if os.path.exists(music_path):
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)  # -1 = sonsuz döngü
                    self.is_playing = True
                    print(f"Music started: {self.music_file}")
                else:
                    print(f"Music file not found: {music_path}")
            except Exception as e:
                print(f"Error loading music: {e}")

    def draw(self, obj):
        """Çizim yok."""
        pass
