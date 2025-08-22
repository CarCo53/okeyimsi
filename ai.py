from player import Player
import random
from log import logger
from rules import Rules
from itertools import combinations

class AIPlayer(Player):
    def __init__(self, isim):
        super().__init__(isim)

    @logger.log_function
    def karar_ver_ve_at(self):
        if self.el:
            return random.choice(self.el)
        return None

    @logger.log_function
    def atilan_tasi_degerlendir(self, oyun, atilan_tas):
        # Basit AI: Eğer bu taşla elinde bir per oluşturabiliyorsa al
        for combo in combinations(self.el, 2):
            test_per = list(combo) + [atilan_tas]
            if Rules.genel_per_dogrula(test_per):
                return True
        return False

    @logger.log_function  
    def ai_el_ac_dene(self, oyun, oyuncu_index):
        if oyun.acilmis_oyuncular[oyuncu_index]:
            return None
            
        gorev = oyun.mevcut_gorev
        # Bu kısım öncekiyle aynı, değişiklik yok
        min_tas = 6
        if "4" in gorev: min_tas = 8
        if "5" in gorev: min_tas = 5
        if "Çift" in gorev: min_tas = 14

        for size in range(min_tas, len(self.el) + 1):
            for combo in combinations(self.el, size):
                if Rules.per_dogrula(list(combo), gorev):
                    return [tas.id for tas in combo]
        return None

    @logger.log_function
    def isleme_dene(self, oyun, oyuncu_index):
        for tas in self.el:
            for per_sahibi_idx, per_listesi in oyun.acilan_perler.items():
                for per_idx, per in enumerate(per_listesi):
                    if Rules.islem_dogrula(per, tas):
                        oyun.islem_yap(oyuncu_index, per_sahibi_idx, per_idx, tas.id)
                        return True
        return False