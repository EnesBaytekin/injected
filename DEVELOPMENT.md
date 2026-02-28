# INJECTED - Geliştirme Özeti

## Oyun Konsepti

İnsan vücuduna enjekte edilmiş yapay bir hücre olarak kan damarlarında ilerle. Vücudu istila eden hastalıkları temizle, ancak bağışıklık sistemi seni de bir yabancı olarak görebilir.

**Temel Mekanik:**
- Jöle kıvamında amorf form ile sıvı içinde yüz
- İçindeki ilaç granüllerini düşmanlara fırlat
- Akyuvarlardan kaç

**Gameplay Pillars:**
1. Jölemsi Hareket - İvme + sürtünme + yay benzeri çarpışma
2. Sınırlı Kaynak Yönetimi - İlaç granülleri sınırlı
3. Kaçış ve Konumlandırma - Düşmanlara ateş ederken kaç
4. Mikroskop Estetiği - Partiküller, deformasyon, organik hareket

---

## Component'ler ve Sistemler

### 1. CellImage Component

**Dosya:** `src/scripts/CellImage.py`

Deforme olabilen jölemsi hücre görseli. Hücre formuna sahip karakter için görsel render.

**Temel Özellikler:**
- 16 noktalı dinamik deformasyon
- Catmull-Rom spline ile yumuşak eğriler
- Zaman bazlı "nefes alma" animasyonu (wobble)
- Hıza bağlı eliptik deformasyon (stretch)
- Siyah çerçeve (outline)

**Hız Bazlı Eliptik Deformasyon:**
- Hücre hareket ettiğinde hız yönünde uzar
- Hıza dik yönde_compress (kısalır)
- `stretch_max` parametresi ile maksimum stretch oranı
- Örn: 2.5 → hız 200 iken 2.5x uzama
- Matematik: Velocity ve perpendicular bileşenlerine ayır, scale et

**Granül Sistemi:**
- 6 adet hareketli ilaç taneciği
- Her granül bağımsız hareket eder:
  - Merkez etrafında rotasyon
  - Mini orbit hareketi
  - Rastgele wobble
  - Boyut pulse (büyüyüp küçülme)
- Granüller de stretch'ten etkilenir (dışarı taşmayı önlemek için)

**Parametreler:**
```python
__init__(radius=32, color=(255, 180, 80), wobble_speed=2.0,
         wobble_amount=4.0, stretch_max=2.5)
```

**Kullanım (JSON):**
```json
{
  "file": "scripts/CellImage",
  "args": [16, [255, 180, 80], 2, 2, 2.5]
}
```

**Teknik Detaylar:**
- Surface boyutu: `int(radius * (2 + stretch_max))`
- Clamp olmaması için yeterince büyük surface
- Her frame'de wobble ve velocity hesaplanır
- Catmull-Rom spline: 4 nokta arasında yumuşak enterpolasyon
- 8 segment per edge (toplam 128 segment)

---

### 2. CircleHitbox Component

**Dosya:** `src/scripts/CircleHitbox.py`

Dairesel hitbox - radius bazlı çarpışma kontrolü.

**Metodlar:**
- `get_world_center(obj)` → Dünyadaki merkez noktası
- `get_world_radius()` → Yarıçap
- `collides_with_circle(other, obj1, obj2)` → Daire-daire çarpışma
- `collides_with_point(x, y, obj)` → Nokta çarpışma
- `draw_debug(obj)` → Debug çizimi (yeşil çember)

**Kullanım (JSON):**
```json
{
  "file": "scripts/CircleHitbox",
  "args": [16]  // radius
}
```

**Python'da:**
```python
hitbox = obj.get_component("CircleHitbox")
if hitbox.collides_with_circle(other_hitbox, obj, other_obj):
    # Çarpışma!
```

---

### 3. Movement Component (Yumuşak Fizik)

**Dosya:** `src/scripts/Movement.py`

İvme, sürtünme, mouse takibi ve yay benzeri çarpışma sistemi.

**Fizik Modeli:**
- **İvme (acceleration)** - Hedefe doğru hızlanma
- **Sürtünme (friction)** - Hız azalma katsayısı
- **Yay benzeri çarpışma** - İç içe geçme miktarına göre itme kuvveti
- **360° hareket** - Mouse yönüne doğru serbest çekim

**Parametreler:**
```python
__init__(acceleration=800, friction=3.0, repulsion_force=600)
```

- `acceleration` - İvme gücü (piksel/saniye²)
- `friction` - Sürtünme katsayısı
- `repulsion_force` - Çarpışma itme kuvveti

**Metodlar:**
- `set_target(x, y)` - Hedef nokta belirle (mouse)
- `clear_target()` - Hedefi temizle
- `get_speed()` - Mevcut hız
- `set_velocity(vx, vy)` - Hız manuel ayarla

**Çalışma Prensibi:**

1. **Mouse Çekim:**
   ```python
   hedef = mouse_pozisyonu
   yön = normalize(hedef - obje_pozisyonu)
   hız += yön * acceleration * dt
   ```

2. **Sürtünme:**
   ```python
   hız *= (1 - friction * dt)
   ```

3. **Çarpışma İtme:**
   ```python
   overlap = (r1 + r2) - mesafe
   itme_gücü = overlap * repulsion_force
   hız += yön * itme_gücü * dt
   ```

4. **Pozisyon Güncelle:**
   ```python
   pozisyon += hız * dt
   ```

**Kullanım (JSON):**
```json
{
  "file": "scripts/Movement",
  "args": [200, 2.0, 50]  // acceleration, friction, repulsion
}
```

---

### 4. PlayerController Component

**Dosya:** `src/scripts/PlayerController.py`

Mouse ile hareket kontrolü.

**Özellikler:**
- Sol tık basılıyken Movement.set_target() çağırır
- Tık bırakınca Movement.clear_target() çağırır
- InputManager'ın mouse fonksiyonlarını kullanır
- ScreenToWorld dönüşümü (kamera varlığı için)

**InputManager Mouse API:**
```python
im = InputManager()
mouse_x, mouse_y = im.get_mouse_position()
im.is_mouse_pressed(1)  # Sol tık
im.is_mouse_just_pressed(1)
im.is_mouse_released(1)
```

**Kamera Dönüşümü:**
```python
# Screen koordinatlarını world koordinatlarına çevir
from scripts.Camera import Camera
camera = Camera()
world_x, world_y = camera.screen_to_world(mouse_x, mouse_y)
movement.set_target(world_x, world_y)
```

---

### 5. Camera Component

**Dosya:** `src/scripts/Camera.py`

Singleton kamera sistemi - karakteri takip eder.

**Özellikler:**
- Singleton pattern (tek实例)
- Smooth follow (lerp ile yumuşak geçiş)
- Character centering (karakter ekranın ortasında)
- World ↔ Screen koordinat dönüşümleri

**Parametreler:**
```python
follow_lerp = 5.0  # Takip hızı (saniye)
```

**Metodlar:**
- `update(dt)` - Her frame güncelle
- `get_offset()` → (x, y) kamera ofseti
- `world_to_screen(wx, wy)` → World'den screen'e
- `screen_to_world(sx, sy)` → Screen'den world'e
- `set_target(object)` - Takip edilecek obje

**Merkezleme Mantığı:**
```python
screen_center_x = scene.width / 2
screen_center_y = scene.height / 2

# Hedef kamera pozisyonu (karakter ekranın ortasında)
target_x = character.x - screen_center_x
target_y = character.y - screen_center_y

# Lerp ile yumuşak geçiş
self.x += (target_x - self.x) * self.follow_lerp * dt
self.y += (target_y - self.y) * self.follow_lerp * dt
```

**Koordinat Dönüşümleri:**
- `world_to_screen`: world_pos - camera_offset
- `screen_to_world`: screen_pos + camera_offset

---

### 6. CameraManager Component

**Dosya:** `src/scripts/CameraManager.py`

Kamerayı güncelleyen manager component.

**Parametreler:**
```python
__init__(target_tag="hero")  # Takip edilecek obje tag'i
```

**Çalışma:**
- Her frame'de Camera.update(dt) çağırır
- Tag ile obje bulur: `scene.get_objects_by_tag(target_tag)`
- İlk objeyi kamera hedefi yapar

**Kullanım (JSON):**
```json
{
  "file": "scripts/CameraManager",
  "args": ["hero"]  // Tag
}
```

---

### 7. BackgroundRenderer Component (Parallax)

**Dosya:** `src/scripts/BackgroundRenderer.py`

Sonsuz parallax arkaplan sistemi - kan damarı teması.

**Parallax Sistemi:**
- 3 layer: Back (uzak), Middle (orta), Front (yakın)
- Her layer farklı chunk boyutunda ve parallax faktöründe
- Chunk'lar tiled olarak tekrarlanır (seamless geçiş)
- Hücreler wrap-around ile chunk sınırlarından taşmaz

**Layer Parametreleri:**
```python
self.parallax_layers = [
    {"factor": 0.15, "chunk_mult": 2.0, "name": "back"},    # Uzak - büyük chunk
    {"factor": 0.35, "chunk_mult": 1.0, "name": "middle"},  # Orta
    {"factor": 0.60, "chunk_mult": 0.5, "name": "front"}    # Yakın - küçük chunk
]
```

**Parallax Mantığı:**
- `factor` ne kadar küçükse, o kadar yavaş kayar = uzak
- `chunk_mult` ne kadar küçükse, chunk o kadar küçüktür
- Örn: Back layer → 2.0x chunk → yavaş hareket

**Hücre Dağılımı:**
- Grid tabanlı (80x80 grid hücreleri)
- Her grid hücresinde %40 ihtimalle hücre
- Uniform dağılım (bir yere yığılma yok)
- Chunk kenarından padding ile uzak (wrap-around için)

**Wrap-Around Seamless Geçiş:**
- Hücre chunk sınırından taşarsa diğer taraftan devam eder
- Komşu tile'lara da aynı hücre çizilir
- Bounding box kontrolü ile optimizasyon

**Renk Derinliği:**
- Uzak layer → koyu (lower brightness)
- Yakın layer → açık (higher brightness)
- Formül: `base_brightness = 55 + int(parallax_factor * 40)`

**Seamless Geçiş Tekniği:**
```python
# Her hücre için 9 tile'a çiz (merkez + 8 komşu)
for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
        offset_points = [(px + dx*chunk_w, py + dy*chunk_h) for px, py in points]
        # Sadece görünecek tile'ları çiz
```

**Chunk Sistemi:**
- Ekranı dolduracak kadar chunk hesaplanır
- Start/end chunk aralığı dinamik
- Her chunk aynı pattern'i kullanır (seed sabit)
- 4'ten fazla chunk gerekebilir (özellikle küçük chunk'lar için)

**Kullanım (JSON):**
```json
{
  "file": "scripts/BackgroundRenderer",
  "args": [960, 480]  // screen_w, screen_h (chunk boyutları için)
}
```

**Teknik Detaylar:**
- Transparan surface'ler (SRCALPHA)
- Pre-render edilmiş chunk yüzeyleri
- Performans için ekran sınırları kontrolü
- Grid spacing: 80px
- Padding: 15px (chunk kenarından)
- Hücre sayısı: chunk alanına orantılı

---

## Proje Yapısı

```
injected/
├── src/
│   ├── main.py                    # Entry point
│   ├── main_scene.json            # Sahne tanımı
│   └── scripts/
│       ├── CellImage.py           # Deforme hücre çizimi + stretch
│       ├── CircleHitbox.py        # Dairesel hitbox
│       ├── Movement.py            # Yumuşak fizik sistemi
│       ├── PlayerController.py    # Mouse kontrol
│       ├── Camera.py              # Kamera sistemi (singleton)
│       ├── CameraManager.py       # Kamera manager
│       └── BackgroundRenderer.py  # Parallax arkaplan
├── .venv/                         # Virtual environment
├── DOCUMENTATION.md               # Framework dökümanı
├── README.md                      # Proje tanımı
└── DEVELOPMENT.md                 # Bu dosya
```

---

## Framework Özellikleri (PyGaminal)

**Entity-Component System:**
- Her obje unique isme sahip
- Tag sistemi ile gruplama (O(1) lookup)
- Component'ler JSON ile yüklenir

**Built-in Component'ler:**
- `@ImageComponent` - Sprite çizim
- `@AnimationComponent` - Animasyon
- `@YSortComponent` - Depth sorting
- `@Hitbox` - Dikdörtgen hitbox
- `@Movability` - Hareket (kullanılmıyor)

**Custom Script Component:**
```python
class MyScript:
    def __init__(self, arg1, arg2):
        # Constructor

    def update(self, obj):
        # Her frame çağrılır

    def draw(self, obj):
        # Çizim (opsiyonel)
```

---

## Şu Anki Durum

**Çalışan Özellikler:**
- ✅ Deforme hücre görseli
- ✅ İçinde hareketli granüller
- ✅ Hız bazlı eliptik deformasyon (stretch)
- ✅ Dairesel hitbox
- ✅ Yumuşak fizik sistemi
- ✅ Mouse ile hareket
- ✅ Yay benzeri çarpışma
- ✅ Kamera sistemi (smooth follow)
- ✅ Parallax arkaplan (3 layer, seamless)

**Test Edilebilir:**
```bash
PYTHONPATH=.venv/lib/python3.13/site-packages:src/scripts python src/main.py
```

**Kontroller:**
- Sol mouse tık basılı tut - Hedefe doğru hareket et
- Tık bırak - Sürtünme ile yavaşla
- Hareket ederken hücre stretch (uzama) efekti

**Görsel Özellikler:**
- Kan damarı teması (koyu kırmızı arkaplan)
- Parallax depth (uzak = koyu, yakın = açık)
- Organik hücre hareketleri
- Smooth kamera takibi
- Seamless sonsuz arkaplan

---

## Tasarım Kararları

### Neden Yumuşak Fizik?

**Kıyas:** Katı çarpışma vs Yumşak fizik

| Katı Çarpışma | Yumuşak Fizik |
|---------------|---------------|
| Değinince hemen durur | İç içe geçebilir |
| 8 yönlü hareket | 360° serbest hareket |
| Doğal değil | Hücre gibi organik |
| Kolay implementasyon | Daha karmaşık |

**Seçim:** Yumuşak fizik - hücre oyunu olduğu için organik his gerekli.

### Neden Dairesel Hitbox?

- Hücreler yuvarlak
- Daire-daire çarpışma hızlı (mesafe < r1 + r2)
- Rotasyon beklenmiyor
- Daha basit ve performanslı

### Neden Mouse Kontrol?

- 360° hareket
- Daha hassas kontrol
- Top-down shooter için standart
- WASD + kombinasyonu da mümkün (ileride)

### Neden Parallax Arkaplan?

- 3D derinlik hissi
- Kan damarı içindeymiş gibi atmosfer
- Performanslı (chunk sistemi + cache)
- Sonsuz dünya hissi

### Neden Wrap-Around Seamless?

- Chunk kenarlarında kesik görünümü önler
- Hücreler düzgün geçiş yapar
- Daha organik his
- Tekrar pattern'i belirgin değildir

---

## Performans Notları

**Şu An:**
- 3 parallax layer
- Her layer için 4+ chunk çizimi
- ~60 FPS (320x180 çözünürlük)

**Optimizasyonlar:**
- Pre-render chunk surfaces
- Ekran sınırları kontrolü
- Wrap-around için sadece 9 tile
- Grid tabanlı uniform dağılım

**Gelecek Optimizasyonlar (gerekirse):**
- Layer sayısını azaltmak (3 → 2)
- Chunk boyutunu artırmak
- Daha az hücre sayısı

---

## Geliştirme Sürecindeki Sorunlar ve Çözümler

### Sorun 1: Surface Clipping
**Sorun:** Hücre stretch olduğunda surface sınırlarını aşıyordu, kesik görünüyordu.

**Çözüm:** Surface boyutunu `radius * (2 + stretch_max)` formülüyle hesapladık.

### Sorun 2: Double Rendering
**Sorun:** Wrap-around'da hücreler chunk sınırında iki kere çiziliyordu, garip köşeler oluşuyordu.

**Çözüm:** Padding ekledik - hücreleri chunk kenarından uzakta tuttuk (15px).

### Sorun 3: Seyrek Dağılım
**Sorun:** Chunk boyutu artınca hücreler seyrek dağılıyordu.

**Çözüm:** Grid tabanlı uniform dağılım - her 80x80 grid hücresinde %40 ihtimalle hücre.

### Sorun 4: Ters Renk Derinliği
**Sorun:** Uzak layer açık, yakın layer koyu görünüyordu (ters).

**Çözüm:** `base_brightness = 55 + int(parallax_factor * 40)` formülü ile düzelttik.

### Sorun 5: Camera Transform Uygulaması
**Sorun:** Arkaplan kamerayla birlikte hareket ediyordu (parallax yokmuş gibi).

**Çözüm:** Her layer için ayrı parallax offset hesapladık, dünya koordinatlarına göre çizdik.

---

## Gelecek Planlar

### Kısa Vadede

1. **Ateş Sistemi**
   - Granül fırlatma
   - Mermi script'i
   - Cooldown

2. **Düşmanlar**
   - Bakteri (temel düşman)
   - Mutant patojen (mini boss)
   - AI hareket script'i

3. **Saha Efektleri**
   - Partikül efektleri
   - Kan damarı detayları

### Orta Vadede

4. **İlaç Sistemi**
   - Granül kapasite göstergesi
   - Yenileme pickup'ları
   - Burst yeteneği

5. **Akyuvarlar**
   - Oyuncuyu kovalayan AI
   - Çarpışma hasarı

6. **UI/Arayüz**
   - Can barı
   - İlaç kapasitesi

### Uzun Vadede (Opsiyonel)

7. **Boss Savaşları**
8. **Lenf/Bağışıklık Bölgesi**
9. **Polish** (Ses, efektler)

---

## Kod Standartları

**Python:**
- PEP 8 uyumlu
- Type hints (opsiyonel)
- Docstring gerekli
- `update()` ve `draw()` metodları

**İsimlendirme:**
- Component sınıfları: `PascalCase`
- Fonksiyonlar: `snake_case`
- JSON dosyaları: `kebab-case.json`

---

## Hızlı Referans

**Yeni Component Oluşturma:**

1. `src/scripts/MyComponent.py` oluştur
2. Sınıf yaz
3. JSON'da kullan

**Objeye Erişme:**
```python
scene = App().get_current_scene()
obj = scene.get_object("player")
objs = scene.get_objects_by_tag("enemy")
```

**Component'e Erişme:**
```python
movement = obj.get_component("Movement")
hitbox = obj.get_component("CircleHitbox")
camera = Camera()  # Singleton
```

---

## Sonraki Adımlar

1. **Ateş sistemi** - ShootingComponent.py
2. **Bakteri düşmanı** - EnemyAI.py
3. **Mermi** - Bullet.py
4. **Çarpışma hasarı** - Health.py
5. **UI** - IlacBar.py

**Hedef:** 48 saat içinde oynanabilir prototype!
