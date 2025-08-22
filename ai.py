from player import Player
import random
from log import logger
from rules_manager import Rules
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
        
        # *** DÜZELTME: Hatalı min_tas tahmini kaldırıldı. ***
        # Artık AI, 3'lü kombinasyonlardan başlayarak elindeki taş sayısına kadar tüm
        # olası perleri dener. Bu, "Küt 4" gibi görevleri kaçırmasını engeller.
        for size in range(3, len(self.el) + 1):
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