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

## Yapılan İşler

### 1. CellImage Component

**Dosya:** `src/scripts/CellImage.py`

Deforme olabilen jölemsi hücre görseli.

**Özellikler:**
- 16 noktalı dinamik deformasyon
- Catmull-Rom spline ile yumuşak eğriler
- Zaman bazlı "nefes alma" animasyonu (wobble)
- Siyah çerçeve (outline)

**Granül Sistemi:**
- 6 adet hareketli ilaç taneciği
- Her granül bağımsız hareket eder:
  - Merkez etrafında rotasyon
  - Mini orbit hareketi
  - Rastgele wobble
  - Boyat pulse (büyüyüp küçülme)

**Parametreler:**
```python
__init__(radius=32, color=(255, 180, 80), wobble_speed=2.0, wobble_amount=4.0)
```

**Kullanım (JSON):**
```json
{
  "file": "scripts/CellImage",
  "args": [16, [255, 180, 80], 2, 2]
}
```

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
   ```
   hedef = mouse_pozisyonu
   yön = normalize(hedef - obje_pozisyonu)
   hız += yön * acceleration * dt
   ```

2. **Sürtünme:**
   ```
   hız *= (1 - friction * dt)
   ```

3. **Çarpışma İtme:**
   ```
   overlap = (r1 + r2) - mesafe
   itme_gücü = overlap * repulsion_force
   hız += yön * itme_gücü * dt
   ```

4. **Pozisyon Güncelle:**
   ```
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
- InputManager'ın yeni mouse fonksiyonlarını kullanır

**InputManager Mouse API:**
```python
im = InputManager()
mouse_x, mouse_y = im.get_mouse_position()
im.is_mouse_pressed(1)  # Sol tık
im.is_mouse_just_pressed(1)
im.is_mouse_released(1)
```

---

## Proje Yapısı

```
injected/
├── src/
│   ├── main.py                    # Entry point
│   ├── main_scene.json            # Sahne tanımı
│   └── scripts/
│       ├── CellImage.py           # Deforme hücre çizimi
│       ├── CircleHitbox.py        # Dairesel hitbox
│       ├── Movement.py            # Yumuşak fizik sistemi
│       └── PlayerController.py    # Mouse kontrol
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
- ✅ Dairesel hitbox
- ✅ Yumuşak fizik sistemi
- ✅ Mouse ile hareket
- ✅ Yay benzeri çarpışma

**Test Edilebilir:**
```bash
PYTHONPATH=.venv/lib/python3.13/site-packages:src/scripts python src/main.py
```

**Kontroller:**
- Sol mouse tık basılı tut - Hedefe doğru hareket et
- Tık bırak - Sürtünme ile yavaşla

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
   - Kan damarı arka planı
   - Alyuvarlar (çevresel)
   - Partikül efektleri

### Orta Vadede

4. **İlaç Sistemi**
   - Granül kapasite göstergesi
   - Yenileme pickup'ları
   - Burst yeteneği (tüm granülleri aynı anda)

5. **Akyuvarlar**
   - Oyuncuyu kovalayan AI
   - Çarpışma hasarı

6. **UI/Arayüz**
   - Can barı
   - İlaç kapasitesi (görsel)
   - Minimap veya vücut silüeti

### Uzun Vadede (Opsiyonel)

7. **Boss Savaşları**
   - Büyük mutasyon
   - Farklı fazlar
   - Burst mekaniği

8. **Lenf/Bağışıklık Bölgesi**
   - İkinci biyom
   - Daha agresif düşmanlar
   - Farklı ortam

9. **Polish**
   - Ses efektleri
   - Vignette efekt
   - Chromatic aberration
   - Daha fazla partikül

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

---

## Performans Notları

**Şu An:**
- 2 obje, 6 granül, 16 deformasyon noktası
- ~60 FPS (320x180 çözünürlük)

**Tahmini (Düşmanlar Eklendiğinde):**
- 10-20 obje
- 50-100 mermi
- 100-200 partikül
- Hala 60 FPS (basit çizim + O(1) çarpışma)

**Optimizasyon Gerekiyorsa:**
- Spatial hashing (çok obje olursa)
- Object pooling (mermi/partikül)
- Daha az granül (6 → 3-4)

---

## GDD Kapsam Özeti

**Oyun Döngüsü:**
```
Spawn → Hareket et → Düşman bul → Ateş et → Granül harca
                                              ↓
                                        Yağla/Kaç → İlaç al → Tekrar
```

**İlerleme:**
```
Bölüm 1: Kan Damarı (20-30 dk)
├── Tutorial
├── Bakteri grupları
├── İlaç pickup
└── Mini-boss

Bölüm 2: Lenf (opsiyonel)
├── Akyuvar spawnları
├── Daha zor kombinasyonlar
└── Boss
```

**Zaman Yönetimi (48 Saat):**

| Yapılan | Süre |
|---------|------|
| Framework kurulumu | 2 saat |
| CellImage + Granüller | 4 saat |
| CircleHitbox | 1 saat |
| Movement + Fizik | 3 saat |
| PlayerController | 1 saat |
| **Toplam** | **11 saat** |

| Yapılacak | Tahmini |
|----------|---------|
| Ateş sistemi | 4 saat |
| Düşmanlar | 6 saat |
| Çevresel objeler | 3 saat |
| UI | 2 saat |
| Boss | 4 saat |
| Polish | 6 saat |
| Test & Debug | 4 saat |
| **Toplam** | **29 saat** |

**Toplam:** 40 saat (buffer dahil)

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
- JSON dosyaları: `kebab-case.json` (main_scene.json)

---

## Hızlı Referans

**Yeni Component Oluşturma:**

1. `src/scripts/MyComponent.py` oluştur
2. Sınıf yaz:
   ```python
   class MyComponent:
       def __init__(self, arg1):
           self.arg1 = arg1

       def update(self, obj):
           pass

       def draw(self, obj):
           pass
   ```
3. JSON'da kullan:
   ```json
   {
     "file": "scripts/MyComponent",
     "args": [42]
   }
   ```

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
```

**Scene Tags:**
```python
obj.add_tag("hero")
obj.has_tag("hero")  # True/False
obj.remove_tag("hero")
```

---

## Sonraki Adımlar

1. **Ateş sistemi** - ShootingComponent.py
2. **Bakteri düşmanı** - EnemyAI.py
3. **Mermi** - Bullet.py
4. **Çarpışma hasarı** - Health.py
5. **UI** - IlacBar.py

**Hedef:** 48 saat içinde oynanabilir prototype!
