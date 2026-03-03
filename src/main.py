#!/usr/bin/env python3

from pygaminal import *
import sys
import os

if __name__ == "__main__":
    # PyInstaller için çalışma dizinini ayarla
    # PyInstaller veri dosyalarını sys._MEIPASS'a çıkarır
    if getattr(sys, 'frozen', False):
        # PyInstaller ile çalışıyoruz
        base_path = sys._MEIPASS
        # src dizinine git (JSON dosyaları orada)
        src_path = os.path.join(base_path, "src")
        os.chdir(src_path)
        # sys.path'e src dizinini ekle (scripts modülü için)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    else:
        # Geliştirme modundayız, src dizinine git
        base_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_path)
        # sys.path'e src dizinini ekle
        if base_path not in sys.path:
            sys.path.insert(0, base_path)

    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")

    # Önce menu sahnesini yükle
    app = App()
    app.init(320, 180, "INJECTED")

    # Menu sahnesini yükle
    menu_scene = Scene.get_scene_from_json("menu_scene.json")
    app.add_scene("menu", menu_scene)

    # Oyun sahnesini yükle (arkada hazır dursun)
    game_scene = Scene.get_scene_from_json("main_scene.json")
    app.add_scene("game", game_scene)

    # Menu sahnesinin background color'unu set et (başlangıç)
    if menu_scene.background_color:
        Screen().set_background_color(menu_scene.background_color)

    # Menu'den başla
    app.set_scene("menu")

    app.run()

