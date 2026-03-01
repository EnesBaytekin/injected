"""
Split Controller - Hücre bölünme ve birleşme mekanizması.
X tuşu ile bölünür, B tuşu ile partner ile birleşir.
"""
from pygaminal import App, Object, Screen, ScriptComponent
import pygame
import math


class SplitController:
    """
    Hücreyi ikiye böler ve tekrar birleştirir.
    Sol/sağ thumbstick ile bağımsız kontrol.
    """

    def __init__(self):
        # Joystick
        self.joystick = None
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
        except:
            pass

        # Enabled flag (Game over'da devre dışı bırakmak için)
        self.enabled = True

        # Split durumu
        self.is_split = False
        self.partner = None  # Partner hücre (birleşmek için)

        # Merge kontrolü
        self.merge_distance = 20  # Birleşme mesafesi (piksel)

        # Elastik bağ kuvveti (uzaklaştıkça birbirini çeker)
        self.elastic_max_distance = 180  # Maksimum mesafe (bundan sonra kuvvet başlar)
        self.elastic_strength = 50  # Çekme kuvveti gücü (doğrudan pozisyon için düşük)

    def update(self, obj):
        """Bölünme/birleşme kontrolü."""
        # Game over'da çalışma
        if not self.enabled:
            return

        # Bölünmüş hücrelerde elastik kuvvet uygula
        if self.is_split:
            self._apply_elastic_force(obj)

        # Sadece bölünmemiş hücrelerde X tuşuna tepki ver
        if not self.is_split and self.joystick:
            # X button (button 2) - Bölünme
            if self.joystick.get_button(2):
                self._split(obj)

        # Bölünmüş hücrelerde birleşme kontrolü
        if self.is_split and self.joystick:
            # B button (button 1) - Birleşme
            if self.joystick.get_button(1):
                print(f"B button pressed! is_split={self.is_split}, partner={self.partner}")
                self._try_merge(obj)

    def _split(self, obj):
        """Hücreyi ikiye böl."""
        print("SPLIT!")
        app = App()

        # Mevcut özellikleri al
        cell_image = obj.get_component("CellImage")
        if not cell_image:
            return

        original_radius = cell_image.radius
        original_color = cell_image.color

        # Yeni radius = biraz daha küçük
        new_radius = original_radius * 0.8

        # İki yeni hücre oluştur
        offset = new_radius * 0.8  # Birbirinden biraz uzakta

        # Sol hücre
        left_obj = Object(obj.x - offset, obj.y)
        self._setup_split_cell(left_obj, new_radius, original_color, "left")

        # Sağ hücre
        right_obj = Object(obj.x + offset, obj.y)
        self._setup_split_cell(right_obj, new_radius, original_color, "right")

        # Partner'ları bağla
        left_controller = left_obj.get_component("SplitController")
        right_controller = right_obj.get_component("SplitController")
        left_controller.instance.partner = right_obj
        right_controller.instance.partner = left_obj

        # Sahneye ekle
        scene = app.get_current_scene()
        scene.add_object(left_obj)
        scene.add_object(right_obj)

        # Eski objeyi yok et
        obj.kill()

    def _setup_split_cell(self, new_obj, radius, color, side):
        """Bölünmüş hücreyi kur."""
        # CellImage (daha küçük radius)
        cell_image_comp = ScriptComponent("scripts/CellImage", [radius, color, 2.0, 4.0, 2.5])
        new_obj.add_component(cell_image_comp)

        # CircleHitbox
        hitbox_comp = ScriptComponent("scripts/CircleHitbox", [radius])
        new_obj.add_component(hitbox_comp)

        # Movement - hangi thumbstick?
        joystick_thumb = "left" if side == "left" else "right"
        movement_comp = ScriptComponent("scripts/Movement", [200, 2.0, 50, joystick_thumb])
        new_obj.add_component(movement_comp)

        # SplitController - is_split = True
        split_comp = ScriptComponent("scripts/SplitController", [])
        new_obj.add_component(split_comp)
        split_comp.instance.is_split = True

        # ShootingController - hangi shoulder?
        shoulder_button = 4 if side == "left" else 5  # Sol=4, Sağ=5
        shooting = ScriptComponent("scripts/ShootingController", [200, 0.3, shoulder_button])
        new_obj.add_component(shooting)

        # Tag'leri ekle
        new_obj.tags.add("controllable")
        new_obj.tags.add("hero")
        new_obj.tags.add("split_cell")

    def _try_merge(self, obj):
        """Partner ile birleşmeyi dene."""
        print(f"_try_merge called! partner={self.partner}")

        if not self.partner:
            print("No partner, returning")
            return

        partner_obj = self._get_partner_object()
        print(f"Partner object: {partner_obj}, dead={partner_obj.dead if partner_obj else 'N/A'}")

        if not partner_obj or partner_obj.dead:
            print("Partner invalid or dead, returning")
            return

        # Radiusları al
        cell_image = obj.get_component("CellImage")
        partner_image = partner_obj.get_component("CellImage")

        if not cell_image or not partner_image:
            print("Missing CellImage components")
            return

        # Radius toplamı + biraz tolerans
        total_radius = cell_image.radius + partner_image.radius
        merge_threshold = total_radius + 5  # 5 piksel tolerans

        dx = obj.x - partner_obj.x
        dy = obj.y - partner_obj.y
        dist = (dx * dx + dy * dy) ** 0.5

        print(f"Distance: {dist:.1f}, threshold: {merge_threshold:.1f}")
        print(f"obj id: {id(obj)}, partner id: {id(partner_obj)}, id(obj) < id(partner): {id(obj) < id(partner_obj)}")

        if dist < merge_threshold:
            # Sadece bir hücre birleştirmeyi yapsın (ID'si daha küçük olan)
            # Böylece iki hücre aynı anda B tuşuna basınca çakışma olmaz
            if id(obj) < id(partner_obj):
                print("MERGE!")
                self._merge(obj, partner_obj)
            else:
                print("Partner has lower ID, letting partner handle merge")
        else:
            print("Too far to merge")

    def _merge(self, obj, partner_obj):
        """İki hücreyi birleştir, ana hücreye dön."""
        app = App()

        # Ana radius'u hesapla (bölünme tersi: split'te 0.8 kullandık, burada 1/0.8 = 1.25)
        cell_image = obj.get_component("CellImage")
        original_radius = cell_image.radius / 0.8  # 0.8'in tersi

        # Ana hücreyi orta noktada oluştur
        merged_obj = Object(obj.x, obj.y)
        self._setup_merged_cell(merged_obj, original_radius, cell_image.color)

        # Sahneye ekle
        scene = app.get_current_scene()
        scene.add_object(merged_obj)

        # Eski objeleri yok et
        obj.kill()
        partner_obj.kill()

    def _setup_merged_cell(self, new_obj, radius, color):
        """Birleşmiş hücreyi kur."""
        # CellImage (orijinal radius)
        cell_image_comp = ScriptComponent("scripts/CellImage", [radius, color, 2.0, 4.0, 2.5])
        new_obj.add_component(cell_image_comp)

        # CircleHitbox
        hitbox_comp = ScriptComponent("scripts/CircleHitbox", [radius])
        new_obj.add_component(hitbox_comp)

        # Movement - joystick_thumb None = mouse kontrolü
        movement_comp = ScriptComponent("scripts/Movement", [200, 2.0, 50])
        new_obj.add_component(movement_comp)

        # PlayerController - mouse ile kontrol
        player_controller = ScriptComponent("scripts/PlayerController", [])
        new_obj.add_component(player_controller)

        # ShootingController - trigger/mouse ile ateş
        shooting = ScriptComponent("scripts/ShootingController", [200, 0.3])
        new_obj.add_component(shooting)

        # SplitController - is_split = False
        split_comp = ScriptComponent("scripts/SplitController", [])
        new_obj.add_component(split_comp)

        # Tag'leri ekle
        new_obj.tags.add("controllable")
        new_obj.tags.add("hero")  # Camera için hero tag'i

    def _apply_elastic_force(self, obj):
        """Bölünmüş hücreler çok uzaklaştığında birbirini çeken elastik kuvvet."""
        partner_obj = self._get_partner_object()
        if not partner_obj or partner_obj.dead:
            return

        # Mesafe hesapla
        dx = partner_obj.x - obj.x
        dy = partner_obj.y - obj.y
        dist = (dx * dx + dy * dy) ** 0.5

        # Maksimum mesafeyi geçtiyse kuvvet uygula
        if dist > self.elastic_max_distance:
            # Normalize yön (partner'a doğru)
            dir_x = dx / dist
            dir_y = dy / dist

            # Mesafeye göre kuvvet hesapla (ne kadar uzak, o kadar güçlü)
            excess_distance = dist - self.elastic_max_distance

            # Sadece mesafeye bağlı kademeli kuvvet
            force = excess_distance * self.elastic_strength

            # Doğrudan pozisyona uygula (sürtünme yok, çarpışma mantığı gibi)
            app = App()
            obj.x += dir_x * force * app.dt
            obj.y += dir_y * force * app.dt

    def _get_partner_object(self):
        """Partner objesini sahneden bul."""
        if not self.partner:
            return None

        # Partner bir obje, sahneden ara
        scene = App().get_current_scene()
        for scene_obj in scene.get_all_objects():
            if scene_obj is self.partner:
                return scene_obj

        return None

    def draw(self, obj):
        """Çizim - birleşme göstergesi."""
        if not self.is_split or not self.partner:
            return

        partner_obj = self._get_partner_object()
        if not partner_obj or partner_obj.dead:
            return

        dx = obj.x - partner_obj.x
        dy = obj.y - partner_obj.y
        dist = (dx * dx + dy * dy) ** 0.5

        # Birleşme mesafesinden yakınsa yeşil çizgi çiz
        if dist < self.merge_distance * 3:
            # Debug line kaldırıldı
            pass
