"""İnsan oyuncu sınıfı."""

from tile import Tile
from log import logger  # Log sistemi eklendi

class Player:
    def __init__(self, isim):
        self.isim = isim
        self.el = []  # Elimizdeki taşlar (Tile nesneleri)

    #@logger.log_function
    def tas_al(self, tas: 'Tile'):
        """Eline taş ekle."""
        if tas:
            self.el.append(tas)

    @logger.log_function
    def tas_at(self, tas_id):
        """Belirli tas_id'ye sahip taşı elden çıkar, döndürür."""
        for i, tas in enumerate(self.el):
            if tas.id == tas_id:
                return self.el.pop(i)
        return None

    @logger.log_function
    def el_sirala(self):
        """Eli renge ve değere göre sırala (jokerler en sona)."""
        self.el.sort(key=lambda t: (t.renk == "joker", t.renk, t.deger if t.deger else 0))