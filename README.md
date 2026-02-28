# INJECTED

48 saatlik game jam için geliştirilen 2D top-down aksiyon oyunu.

## Konsept

İnsan vücuduna enjekte edilmiş yapay bir hücresin. Kan damarlarında yol alarak vücudu istila eden hastalıkları temizle. Ancak bağışıklık sistemi seni de bir yabancı olarak görebilir.

Jöle kıvamında amorf formunla sıvı içinde yüz, içindeki ilaç granüllerini düşmanlara fırlat, akyuvarlardan kaç.

## Özellikler

**Oynanış:**
- Jölemsi fizik sistemi - ivme, sürtünme, yay benzeri çarpışma
- 360° mouse kontrolü
- Hıza bağlı hücre deformasyonu (stretch efekti)
- İçinde hareketli ilaç granülleri

**Görsel:**
- Parallax arkaplan (3 layer, kan damarı teması)
- Organik hücre animasyonları
- Smooth kamera takibi
- Seamless sonsuz dünya

## Kontroller

- **Sol Mouse** - Hedefe doğru hareket et
- **Tık Bırak** - Yavaşla (sürtünme)

## Teknoloji

- **Pygame** - Grafik ve input
- **PyGaminal** - Özel ECS framework (JSON tabanlı sahne sistemi)

## Çalıştırma

```bash
python src/main.py
```

## Geliştirme Durumu

Şu an çalışan:
- ✅ Karakter hareketi ve fizik
- ✅ Hücre deformasyonu
- ✅ Kamera sistemi
- ✅ Parallax arkaplan
- ⏳ Ateş sistemi (yakında)
- ⏳ Düşmanlar (yakında)
