# PyGamer Framework Documentation

Pygame tabanlı 2D oyun yapma framework'ü. JSON + assetler ile oyun geliştirme.

## Proje Yapısı

```
pygamer/
├── pygaminal/                     # Core engine
│   ├── __init__.py               # run_app() fonksiyonu
│   ├── app.py                    # Singleton: Ana oyun döngüsü
│   ├── scene.py                  # Sahne yönetimi
│   ├── object.py                 # Entity-Component System
│   ├── component.py              # Base Component
│   ├── script_component.py       # Universal component loader
│   ├── components/               # Built-in component script'leri
│   │   ├── ImageComponent.py    # Sprite çizim
│   │   ├── AnimationComponent.py # Animasyon çizim
│   │   └── YSortComponent.py    # Y eksenine göre depth sorting
│   ├── image.py                  # PNG/JPG yükleme
│   ├── animation.py              # Animasyon sistemi
│   ├── screen.py                 # Singleton: Pygame Surface yönetimi
│   ├── input_manager.py          # Singleton: Input handling
│   └── util.py                   # Yardımcı fonksiyonlar
└── sample-game/                  # Örnek oyun
    ├── scene_data.json           # Sahne tanımı
    ├── main.py                   # Entry point
    ├── MovementScript.py         # Custom script
    └── images/                   # Assetler (PNG)
```

## Core Sınıflar

### App (Singleton)
Ana uygulama yöneticisi.

```python
from pygaminal import App
app = App()
app.init(width=800, height=600, title="My Game")
app.run()
```

**Özellikler:**
- `width`, `height`, `title` - Pencere ayarları
- `now` - Şu anki zaman (saniye)
- `dt` - Delta time (frame arası geçen süre)
- `target_fps` - FPS limiti (default: 60)

**Metodlar:**
- `add_scene(name, scene)` - Sahne ekle
- `set_scene(name)` - Aktif sahneyi değiştir
- `get_current_scene()` - Aktif sahne
- `stop()` - Oyunu durdur

### Screen (Singleton)
Render yüzeyi.

```python
from pygaminal import Screen
screen = Screen()
screen.init(800, 600)
screen.set_background_color("#3366ff")
screen.set_background_image("bg.png")
screen.clear()  # Arka planı çiz
screen.blit(image, x, y)  # Image çiz
screen.refresh()  # Display güncelle
```

### InputManager (Singleton)
Input yönetimi.

```python
from pygaminal import InputManager
import pygame

im = InputManager()
im.update()  # Frame başı çağır

# Key kontrolü
if im.is_pressed(pygame.K_w):  # Basılı mı
if im.is_just_pressed(pygame.K_SPACE):  # Just basıldı mı
if im.is_released(pygame.K_a):  # Bırakıldı mı
```

### Scene
Objeleri tutan konteyner. **Performans için dict-based storage.**

```python
from pygaminal import Scene

scene = Scene()
scene.add_object(obj)  # Obje ekle (next frame'de aktif)
scene.update()  # Tüm objeleri update et
scene.draw()  # Tüm objeleri çiz
```

**Storage:**
- `scene.objects = {name: Object}` - Dict storage, O(1) lookup
- `scene._tags = {tag: [Object]}` - Tag index, O(1) lookup

**Property'ler:**
- `width`, `height` - Sahne boyutu
- `background_color` - Hex color string
- `background_image` - Dosya yolu

**Metodlar:**
- `add_object(obj)` - Obje ekle (next frame'de aktif olur)
- `remove_object(obj)` - Obje sil (next frame'de silinir)
- `get_object(name)` - İsmi verilen objeyi al - **O(1)**
- `get_objects_by_tag(tag)` - Tag'e göre tüm objeleri al - **O(1)**
- `get_all_objects()` - Tüm objeleri al

### Object
Entity-Component mimarisi. **Her obje unique isme sahiptir.**

```python
from pygaminal import Object

obj = Object(x, y, name="player", tags=["hero", "main"])
obj.kill()  # Objeyi yok et (next frame'de silinir)
```

**Property'ler:**
- `name` - Unique isim (auto-generated veya explicit)
- `tags` - Tag set'i (set of strings)
- `x`, `y` - Pozisyon
- `dead` - Öldü mü?
- `depth` - Çizim derinliği (otomatik Y-sort)

**Metodlar:**
- `add_tag(tag)` - Tag ekle (obj.tags'de hemen, scene._tags'de next frame)
- `remove_tag(tag)` - Tag sil (obj.tags'te hemen, scene._tags'den next frame)
- `has_tag(tag)` - Tag kontrolü ✅ - Works immediately
- `kill()` - Next frame'de sil
- `add_component(component, explicit_name=None)` - Component ekle
- `get_component(name)` - Component al (unique name ile)
- `get_components(file_name)` - Aynı türdeki tüm component'leri al

## Objeleri Yönetme

### Name Sistemi
Her objenin unique bir ismi vardır:

```python
# Explicit name
obj = Object(100, 100, name="player")

# Auto-generated name (ad conflicts için)
obj = Object(100, 100)  // name = "object_0"
obj = Object(200, 200)  // name = "object_1"

# Name conflicts → auto-numbering
obj1 = Object(100, 100, name="box")
obj2 = Object(200, 200, name="box")  // → "box_2"
obj3 = Object(300, 300, name="box")  // → "box_3"
```

### Tag Sistemi
Objeleri gruplamak için tags kullanın:

```python
# Create with tags
player = Object(100, 100, name="player", tags=["hero", "controllable"])
enemy = Object(200, 200, tags=["enemy", "flying"])

# Add/remove tags
enemy.add_tag("poisoned")
enemy.remove_tag("flying")

// Check tag (immediate - works same-frame)
if enemy.has_tag("poisoned"):
    take_damage()
```

### Objeleri Erişme

**ByName - Tek obje:**
```python
player = scene.get_object("player")
player.x += 100
```

**By Tag - Liste:**
```python
# Tüm düşmanları al
enemies = scene.get_objects_by_tag("enemy")
for enemy in enemies:
    enemy.x -= 50

# Tüm mermileri al
bullets = scene.get_objects_by_tag("bullet")
for bullet in bullets:
    bullet.x += 200 * app.dt
```

### Runtime Objeler Oluşturma

**Bullet spawn:**
```python
# Script'te
def shoot(self, obj):
    bullet = Object(obj.x, obj.y, tags=["bullet", "player_owned"])
    scene.add_object(bullet)
    # Next frame'de sahnede aktif olur
```

**Particle effect:**
```python
def create_explosion(self, x, y):
    particle = Object(x, y, tags=["effect", "explosion"])
    scene.add_object(particle)
    # Tag ile yönetilebilir, name gereksiz
```

### Pending Updates Sistemi

Değişiklikler **frame sonunda** uygulanır:

```python
// Tag ekle
obj.add_tag("flying")
// - obj.tags'de: ✅ HEMEN var
// - scene._tags'de: ❌ Next frame'de var

// Objeye erişim (immediate)
if obj.has_tag("flying"):  // ✅ Works same-frame
    fly()

// Scene-wide query (next frame)
enemies = scene.get_objects_by_tag("enemy")
// Eğer aynı frame'de tag eklendiyse, bu objenin listede OLMAMASI normal
```

**Neden?**
- **Performans:** Frame ortasında index update yapmıyoruz
- **Tutarlılık:** Tüm değişiklikler bir sonraki frame'den itibaren aktif
- **O(1) Lookup:** Index her zaman güncel ve fast

**Kullanım ipucu:** Genelde next frame'de query yaparsınız, sorun değil.

### Obje Silme

```python
// Mark for removal
obj.kill()

// Veya
scene.remove_object(obj)

// Next frame'de silinir:
// - scene.objects'dan
// - scene._tags'den
// - Cleanup tam
```

## Component Sistemi

### Uniform Component Yapısı

Tüm component'ler **aynı format**ta script dosyalarıdır. Built-in component'ler ve user script'ler arasında fark yoktur.

#### Built-in Component'ler
Framework ile birlikte gelen component'ler. `@` prefix'i ile kullanılır:

```json
{"file": "@ImageComponent", "args": [...]}
{"file": "@AnimationComponent", "args": [...]}
{"file": "@YSortComponent", "args": []}
```

#### User-Defined Component'ler
Kullanıcının yazdığı script'ler. Dosya adı ile kullanılır:

```json
{"file": "MovementScript", "args": [200]}
{"file": "MyScript", "args": []}
```

### Component Script Formatı

Her component script'i aynı yapıdadır - **inheritance gerekmez**:

```python
# MyComponent.py
class MyComponent:
    def __init__(self, arg1, arg2=None):
        # Constructor
        self.value = arg1

    def update(self, obj):
        # Her frame çağrılır
        obj.x += 100 * app.dt

    def draw(self, obj):
        # Çizim anında çağrılır (opsiyonel)
        pass
```

### Built-in Component'ler

#### ImageComponent
Tek frame çizim.

```python
# JSON
{
  "file": "@ImageComponent",
  "name": "body",  // Optional
  "args": ["player.png", "center", "end"]
}
```

**Args:**
1. `image_or_path` - Image objesi veya dosya yolu
2. `pivot_x` - "center", "end", veya pixel değeri
3. `pivot_y` - "center", "end", veya pixel değeri

#### AnimationComponent
Animasyon çizim.

```python
# JSON
{
  "file": "@AnimationComponent",
  "args": [{
    "file": "walk.png",
    "frame_width": 32,
    "frame_height": 32,
    "frames": [0, 1, 2, 3],
    "speed": 10,
    "loop": true
  }]
}
```

**Args:**
- Animasyon data dict'i:
  - `file` - Sprite sheet dosya yolu
  - `frame_width` - Frame genişliği
  - `frame_height` - Frame yüksekliği
  - `frames` - Frame listesi (opsiyonel)
  - `speed` - Animasyon hızı
  - `loop` - Döngü mü?

#### YSortComponent
Y pozisyonuna göre depth ayarlama (derinlik sıralaması için).

```python
{
  "file": "@YSortComponent",
  "args": []
}
```

### Component Yönetimi

**Tek Component (Name ile):**
```python
// JSON
{
  "file": "@ImageComponent",
  "name": "shadow",
  "args": ["shadow.png"]
}

// Python
comp = obj.get_component("shadow")
```

**Aynı Türden Çoklu Component:**
```python
// JSON - Auto-naming
{
  "components": [
    {"file": "@ImageComponent", "args": ["layer1.png"]},
    {"file": "@ImageComponent", "args": ["layer2.png"]},
    {"file": "@ImageComponent", "args": ["layer3.png"]}
  ]
}
// Sonuç: ImageComponent, ImageComponent2, ImageComponent3

// JSON - Explicit naming
{
  "components": [
    {"file": "@ImageComponent", "name": "shadow", "args": ["shadow.png"]},
    {"file": "@ImageComponent", "name": "body", "args": ["body.png"]},
    {"file": "@ImageComponent", "name": "glow", "args": ["glow.png"]}
  ]
}

// Python - Tüm aynı türdekileri al
images = obj.get_components("@ImageComponent")  // [comp1, comp2, comp3]
```

## JSON Formatı

### Uniform Component Formatı

Tüm component'ler aynı formattadır:

```json
{
  "file": "ComponentName",      // Zorunlu: Component dosyası
  "name": "my_component",       // Opsiyonel: Unique isim
  "args": [arg1, arg2, ...]     // Opsiyonel: Constructor argümanları
}
```

### Component Kuralları

1. **`file`** - Zorunlu
   - `@` ile başlarsa → Built-in component (`@ImageComponent`)
   - `@` yoksa → User script (`MovementScript`)

2. **`name`** - Opsiyonel
   - Verilirse → Bu isimle eklenir
   - Verilmezse → Otomatik isim (`ImageComponent`, `ImageComponent2`, ...)

3. **`args`** - Opsiyonel
   - Component constructor'ına geçilecek parametreler

### Sahne Dosyası (scene_data.json)

```json
{
  "width": 800,
  "height": 600,
  "background_color": "#222222",
  "background_image": "bg.png",
  "objects": [
    {
      "x": 100,
      "y": 200,
      "name": "player",        // Optional unique name
      "tags": ["hero", "main"], // Optional tags
      "components": [
        {
          "file": "@ImageComponent",
          "name": "body",
          "args": ["images/player.png", "center", "end"]
        },
        {
          "file": "MovementScript",
          "args": [200]
        },
        {
          "file": "@YSortComponent",
          "args": []
        }
      ]
    },
    {
      "x": 300,
      "y": 150,
      "tags": ["enemy"],
      "components": [
        {
          "file": "@AnimationComponent",
          "args": [{
            "file": "images/explosion.png",
            "frame_width": 32,
            "frame_height": 32,
            "frames": [0, 1, 2, 3],
            "speed": 10,
            "loop": false
          }]
        }
      ]
    }
  ]
}
```

## Image & Animation

### Image
Resim yükleme.

```python
from pygaminal import Image

img = Image.from_file("sprite.png")
// img.width, img.height
```

### Animation
Animasyon sistemi.

**Sprite Sheet:**
```python
from pygaminal import Animation

anim = Animation.from_sprite_sheet(
    "sprite.png",
    frame_width=32,
    frame_height=32,
    frames=[0, 1, 2, 3],  // Optional, None = tüm frame'ler
    speed=10,
    loop=True
)
```

**Frame Listesi:**
```python
anim = Animation.from_files([
    "idle_0.png",
    "idle_1.png",
    "idle_2.png"
], speed=5, loop=False)
```

**Metodlar:**
- `start()` - Animasyonu başlat
- `get_frame()` - Şu anki frame'i al
- `is_over()` - Bitti mi?

## Script Yazma

### Script Template

```python
import pygame
from pygaminal import *

class MyScript:
    def __init__(self, arg1, arg2=None):
        // Constructor, JSON args'dan değer alır
        self.value = arg1

    def update(self, obj):
        // Her frame çağrılır
        app = App()
        scene = app.get_current_scene()
        im = InputManager()

        // Input
        if im.is_pressed(pygame.K_SPACE):
            // Aksiyon
            pass

        // Hareket
        obj.x += 100 * app.dt

        // Obje yaratma
        bullet = Object(obj.x, obj.y, tags=["bullet", "player_owned"])
        scene.add_object(bullet)

        // Obje yok etme
        if obj.x > 800:
            obj.kill()

        // Objelere erişim
        player = scene.get_object("player")
        enemies = scene.get_objects_by_tag("enemy")
        for enemy in enemies:
            if enemy.has_tag("flying"):
                // Uçan düşman
                pass

    def draw(self, obj):
        // Opsiyonel: Custom drawing
        pass
```

### Global Nesneler
Scriptlerde her zaman erişilebilir:
- `App()` - Singleton app instance
- `InputManager()` - Singleton input manager
- `Screen()` - Singleton screen
- `Scene()` veya `app.get_current_scene()` - Aktif sahne

## Çalıştırma

### Kurulum
```bash
cd /home/imns/Desktop/pygamer
python3 -m venv .venv
source .venv/bin/activate
pip install pygame
```

### Oyun Çalıştırma
```bash
cd sample-game
PYTHONPATH=/home/imns/Desktop/pygamer python main.py
```

Veya:
```python
from pygaminal import *
run_app("scene_data.json")
```

## Hızlı Tutorial

### Adım 1: Sahne Oluştur

`scene_data.json`:
```json
{
  "width": 800,
  "height": 600,
  "background_color": "#4488ff",
  "objects": [
    {
      "x": 400,
      "y": 300,
      "name": "player",
      "tags": ["hero"],
      "components": [
        {
          "file": "@ImageComponent",
          "args": ["player.png", "center", "end"]
        },
        {
          "file": "PlayerController",
          "args": []
        }
      ]
    }
  ]
}
```

### Adım 2: Script Yaz

`PlayerController.py`:
```python
import pygame
from pygaminal import *

class PlayerController:
    def update(self, obj):
        app = App()
        im = InputManager()

        speed = 200
        if im.is_pressed(pygame.K_LEFT):
            obj.x -= speed * app.dt
        if im.is_pressed(pygame.K_RIGHT):
            obj.x += speed * app.dt
        if im.is_pressed(pygame.K_UP):
            obj.y -= speed * app.dt
        if im.is_pressed(pygame.K_DOWN):
            obj.y += speed * app.dt
```

### Adım 3: Çalıştır

```bash
PYTHONPATH=/path/to/pygamer python main.py
```

### Adım 4: Kontroller
- **Arrow Keys** - Hareket
- **Close Window** - Çıkış

## Pygame Key Constants

```python
pygame.K_a, pygame.K_b, ...  // Harfler
pygame.K_0, pygame.K_1, ...  // Rakamlar
pygame.K_SPACE               // Space
pygame.K_ESCAPE              // Escape
pygame.K_RETURN              // Enter
pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN  // Yön tuşları
```

## Tips

1. **Delta Time Kullan**: Her zaman `app.dt` ile çarparak hareket ettir
2. **Pivot**: Karakter için `"center"`, zemin objeleri için `"end"` kullan
3. **Depth Sorting**: YSortComponent ekle, objeler otomatik sıralanır
4. **Animasyon**: Sprite sheet kullan, performans için
5. **Cleanup**: Biten objeleri `object.kill()` ile yok et
6. **Cooldowns**: `app.now` kullanarak rate limiting yap
7. **Object Names**: Önemli objelere explicit name ver (player, boss1)
8. **Tags**: Gruplar için kullan (enemy, bullet, pickup)
9. **Tag Query Performance**: `get_objects_by_tag()` O(1)'dir, bolca kullanın
10. **Component Naming**: Önemli component'lere explicit name ver, diğerlerini auto-name bırak

## Performans Notları

### Objeler
- `get_object(name)` → **O(1)** dict lookup
- `get_objects_by_tag(tag)` → **O(1)** dict lookup
- `get_all_objects()` → **O(n)** list comprehension

### Component'ler
- `get_component(name)` → **O(1)** dict lookup
- `get_components(file_name)` → **O(n)** filter (ama nadır kullanılır)

### Update Loop
- Her frame bir kere `_apply_pending_updates()` → **O(n × tags)**
- Tag değişiklikleri → **O(1)** per tag

## Component Best Practices

### Built-in Kullan
Mümkünse built-in component'leri kullan:

```json
{"file": "@ImageComponent", "args": ["player.png", "center", "end"]}
```

### Custom Script Yaz
Özel logic için script yaz:

```python
// EnemyAI.py
class EnemyAI:
    def __init__(self, patrol_range=100):
        self.patrol_range = patrol_range
        self.start_x = 0

    def update(self, obj):
        app = App()
        scene = app.get_current_scene()

        // Patrol logic
        if obj.x > self.start_x + self.patrol_range:
            obj.x -= 100 * app.dt
        elif obj.x < self.start_x:
            obj.x += 100 * app.dt

        // Player'a yaklaşma
        player = scene.get_object("player")
        if player:
            distance = ((obj.x - player.x)**2 + (obj.y - player.y)**2)**0.5
            if distance < 100:
                // Saldır!
                pass
```

```json
{"file": "EnemyAI", "args": [150]}
```

### Component Reuse
İyi yazılmış bir script'i built-in yap:
1. Script'i `pygaminal/components/` dizinine kopyala
2. JSON'da `@` prefix ile kullan

## Gelişmiş Kullanım Senaryoları

### Senaryo 1: Bullet Spawn
```python
// ShootingScript.py
class ShootingScript:
    def __init__(self, cooldown=0.5):
        self.cooldown = cooldown
        self.last_shot = 0

    def update(self, obj):
        app = App()
        scene = app.get_current_scene()
        im = InputManager()

        // Cooldown kontrolü
        if app.now - self.last_shot < self.cooldown:
            return

        // Ateş et
        if im.is_pressed(pygame.K_SPACE):
            bullet = Object(obj.x, obj.y, tags=["bullet", "player_owned"])
            scene.add_object(bullet)
            self.last_shot = app.now
```

```python
// BulletScript.py
class BulletScript:
    def __init__(self, speed=300):
        self.speed = speed

    def update(self, obj):
        app = App()
        scene = app.get_current_scene()

        // Hareket
        obj.x += self.speed * app.dt

        // Ekran dışına çıktı mı?
        if obj.x > scene.width:
            obj.kill()

        // Çarpışma kontrolü
        enemies = scene.get_objects_by_tag("enemy")
        for enemy in enemies:
            if self.check_collision(obj, enemy):
                enemy.kill()
                obj.kill()
                break
```

### Senaryo 2: Boss Fight
```python
// Boss Second Phase
class BossScript:
    def __init__(self):
        self.phase = 1
        self.health = 100

    def update(self, obj):
        app = App()
        scene = app.get_current_scene()

        // Phase 2'ye geç
        if self.health < 50 and self.phase == 1:
            self.phase = 2
            obj.add_tag("flying")  // Tag ekle
            // Next frame'de get_objects_by_tag("flying") bu objeyi de içerecek
```

### Senaryo 3: Tag Kategorileri
```json
// Editörde
{
  "name": "player",
  "tags": ["hero", "controllable", "ground"]
}

{
  "name": "enemy1",
  "tags": ["enemy", "ground", "melee"]
}

{
  "tags": ["enemy", "flying", "ranged"]
}
```

```python
// Script'te
ground_enemies = scene.get_objects_by_tag("enemy")  // Tüm düşmanlar
for enemy in ground_enemies:
    if enemy.has_tag("ground"):  // Ground'da mı?
        chase_player()
    elif enemy.has_tag("flying"):  // Uçan mı?
        fly_around()
```

### Senaryo 4: Multiple Components
```python
// Karakter: Birden fazla image layer
{
  "name": "player",
  "components": [
    {"file": "@ImageComponent", "name": "shadow", "args": ["shadow.png"]},
    {"file": "@ImageComponent", "name": "body", "args": ["body.png"]},
    {"file": "@ImageComponent", "name": "armor", "args": ["armor.png"]},
    {"file": "@ImageComponent", "name": "weapon", "args": ["sword.png"]}
  ]
}

// Runtime'da
shadow = obj.get_component("shadow")
shadow_comp.visible = False  // Gölgeyi kapat

// Veya tüm ImageComponent'leri al
all_layers = obj.get_components("@ImageComponent")
for layer in all_layers:
    layer.visible = False
```

## Object Communication

### Name İle Erişim
```python
// Script'ten diğer objeye erişim
scene = app.get_current_scene()
player = scene.get_object("player")

if player and player.x < obj.x:
    // Player solda
    chase()
```

### Tag İle Grup Erişim
```python
// Tüm düşmanlara mesaj gönder
enemies = scene.get_objects_by_tag("enemy")
for enemy in enemies:
    enemy.add_tag("alarmed")

// Tüm mermileri temizle
bullets = scene.get_objects_by_tag("bullet")
for bullet in bullets:
    bullet.kill()
```

### Distance Check
```python
// Player'a en yakın düşman
scene = app.get_current_scene()
player = scene.get_object("player")
enemies = scene.get_objects_by_tag("enemy")

closest = None
min_dist = float('inf')

for enemy in enemies:
    dist = ((enemy.x - player.x)**2 + (enemy.y - player.y)**2)**0.5
    if dist < min_dist:
        min_dist = dist
        closest = enemy

if closest and min_dist < 100:
    // En yakın düşman 100px içinde
    closest.add_tag("targeted")
```

## Custom Rendering

```python
def draw(self, obj):
    screen = Screen()
    // Custom drawing logic
    screen.draw_circle(obj.x, obj.y, 10, (255, 0, 0))
```

## Frame Consistency

Tüm değişiklikler **frame sonunda** uygulanır:
- `add_object()` → Next frame'de aktif
- `obj.kill()` → Next frame'de silinir
- `obj.add_tag()` → scene._tags'de next frame
- `obj.remove_tag()` → scene._tags'ten next frame

**Immediate works:**
- `obj.has_tag()` → obj.tags'de hemen kontrol
- `obj.tags` → Direct access
- Component changes

**Next frame works:**
- `scene.get_object(name)`
- `scene.get_objects_by_tag(tag)`
- Scene update/draw loop
