"""Okey destesi ve taş üretimi."""

import random
from tile import Tile
from utils import benzersiz_id_uret
from log import logger  # Log sistemi eklendi

class Deck:
    def __init__(self):
        self.taslar = []

    #@logger.log_function
    def olustur(self):
        """106 taşı oluşturur ve desteye ekler."""
        self.taslar = []
        renkler = ["sari", "mavi", "siyah", "kirmizi"]
        for renk in renkler:
            for deger in range(1, 14):
                for kopya in range(2):
                    id = benzersiz_id_uret()
                    self.taslar.append(Tile(renk, deger, f"{renk}_{deger}.png", id))
        for i in range(2):
            id = benzersiz_id_uret()
            self.taslar.append(Tile("joker", None, "fake_okey.png", id))

    #@logger.log_function
    def karistir(self):
        random.shuffle(self.taslar)

    #@logger.log_function
    def tas_cek(self):
        if self.taslar:
            return self.taslar.pop()
        return None