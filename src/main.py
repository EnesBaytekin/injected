#!/usr/bin/env python3

from pygaminal import *

if __name__ == "__main__":
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

