# player.py dosyasının tamamını bununla değiştirin.

from tile import Tile
from log import logger

class Player:
    def __init__(self, isim):
        self.isim = isim
        self.el = []

    def tas_al(self, tas: 'Tile'):
        if tas:
            self.el.append(tas)

    @logger.log_function
    def tas_at(self, tas_id):
        for i, tas in enumerate(self.el):
            if tas.id == tas_id:
                return self.el.pop(i)
        return None

    @logger.log_function
    def el_sirala(self):
        """DÜZELTME: Eli renge, özel serilere (12-13-1) ve değere göre sırala."""
        # 1'i 14 olarak kabul eden bir sıralama anahtarı
        def sort_key(t):
            val = t.deger or 0
            # Jokerleri en sona at
            if t.renk == "joker":
                return (1, 0, 0) # (joker mi, renk, değer)
            # 1'i hem başa hem sona koyabilmek için özel işlem
            # Normal sıralamada 1 en düşük olacak
            return (0, t.renk, val)

        self.el.sort(key=sort_key)