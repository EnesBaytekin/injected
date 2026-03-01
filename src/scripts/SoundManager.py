"""
Sound Manager - Sound effects (SFX) çalar.
Olaylara göre ses efektlerini oynatır.
"""
import pygame
import os


class SoundManager:
    """
    Sound effects yöneticisi.
    Farklı sesleri yükler ve oynatır.
    """

    def __init__(self):
        """Sound manager başlat."""
        # Mixer'ı başlat (zaten MusicPlayer'da başlatılmış olabilir)
        try:
            pygame.mixer.init()
        except:
            pass

        # Sesleri yükle
        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        """Ses dosyalarını yükle."""
        sound_files = {
            "throw_bullet": "throw_bullet.mp3",
            "spawner_explosion": "spawner_explosion.mp3",
            "cell_explosion": "cell_explosion.mp3"
        }

        for name, filename in sound_files.items():
            sound_path = os.path.join("sounds", filename)
            if os.path.exists(sound_path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(sound_path)
                    print(f"Loaded sound: {name}")
                except Exception as e:
                    print(f"Error loading sound {name}: {e}")
            else:
                print(f"Sound file not found: {sound_path}")

    def play(self, sound_name, volume=1.0):
        """Ses çal.

        Args:
            sound_name: Ses adı (throw_bullet, spawner_explosion, cell_explosion)
            volume: Ses seviyesi (0.0 - 1.0)
        """
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].set_volume(volume)
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
        else:
            print(f"Sound not found: {sound_name}")

    def update(self, obj):
        """Update - bir şey yapmıyoruz."""
        pass

    def draw(self, obj):
        """Çizim yok."""
        pass
