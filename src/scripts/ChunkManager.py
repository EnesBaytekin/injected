"""
Chunk Manager - Dünyayı grid'lere böler, performans için.
Sadece player'ın etrafındaki chunk'lar aktiftir.
"""
from pygaminal import App


class ChunkManager:
    """
    Chunk sistemi yöneticisi.
    Dünyayı grid'lere böler, uzak objeleri deaktif eder.
    """

    def __init__(self, chunk_size=1000):
        """
        Args:
            chunk_size: Her bir chunk'ın piksel boyutu
        """
        self.chunk_size = chunk_size
        self.active_chunks = set()  # Aktif chunk koordinatları

    def update(self, obj):
        """Her frame chunk kontrolü."""
        app = App()
        scene = app.get_current_scene()

        # Player pozisyonunu al
        heroes = scene.get_objects_by_tag("hero")

        if not heroes or heroes[0].dead:
            return  # Player yok, her şey aktif

        hero = heroes[0]

        # Player'ın chunk koordinatını hesapla
        player_chunk_x = int(hero.x / self.chunk_size)
        player_chunk_y = int(hero.y / self.chunk_size)

        # Aktif chunk'ları belirle (player'ın etrafındaki 3x3 alan)
        new_active_chunks = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                chunk_x = player_chunk_x + dx
                chunk_y = player_chunk_y + dy
                new_active_chunks.add((chunk_x, chunk_y))

        # Yeni aktif chunk'lar
        added_chunks = new_active_chunks - self.active_chunks
        # Artık aktif olmayan chunk'lar
        removed_chunks = self.active_chunks - new_active_chunks

        # Objeleri güncelle
        self._update_objects_by_chunks(scene, added_chunks, removed_chunks)

        self.active_chunks = new_active_chunks

    def _update_objects_by_chunks(self, scene, added_chunks, removed_chunks):
        """
        Chunk'lara göre objelerin aktivasyonunu yönet.
        Aktif olmayan chunk'lardaki objelerin update'i durdur.
        """
        for scene_obj in scene.get_all_objects():
            # Camera manager ve spawner her zaman aktif
            if "camera" in scene_obj.tags or "spawner" in scene_obj.tags:
                continue

            # Objenin chunk koordinatını hesapla
            obj_chunk_x = int(scene_obj.x / self.chunk_size)
            obj_chunk_y = int(scene_obj.y / self.chunk_size)
            chunk_coord = (obj_chunk_x, obj_chunk_y)

            # Obje aktif mi?
            is_active = chunk_coord in self.active_chunks

            # Aktiflik durumunu güncelle (custom attribute ile)
            if not hasattr(scene_obj, '_chunk_active'):
                scene_obj._chunk_active = True

            if is_active and not scene_obj._chunk_active:
                # Yeni aktif oldu
                scene_obj._chunk_active = True
            elif not is_active and scene_obj._chunk_active:
                # Artık aktif değil
                scene_obj._chunk_active = False

    def get_chunk_objects(self, scene, chunk_x, chunk_y):
        """Belirtilen chunk'taki objeleri döndür."""
        objects = []

        for scene_obj in scene.get_all_objects():
            obj_chunk_x = int(scene_obj.x / self.chunk_size)
            obj_chunk_y = int(scene_obj.y / self.chunk_size)

            if obj_chunk_x == chunk_x and obj_chunk_y == chunk_y:
                objects.append(scene_obj)

        return objects

    def is_chunk_active(self, obj):
        """Objenin bulunduğu chunk aktif mi?"""
        if not hasattr(obj, '_chunk_active'):
            return True  # Varsayılan aktif
        return obj._chunk_active

    def draw(self, obj):
        """Çizim yok."""
        pass
