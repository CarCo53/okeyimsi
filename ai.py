from player import Player
import random
from log import logger
from rules_manager import Rules
from itertools import combinations
from collections import defaultdict

class AIPlayer(Player):
    def __init__(self, isim):
        super().__init__(isim)

    @logger.log_function
    def karar_ver_ve_at(self, oyun_context=None):
        if not self.el:
            return None

        if oyun_context and oyun_context.acilmis_oyuncular[oyun_context.sira_kimde_index]:
            kalan_taslar = self.el[:]
            isleyebildim = True
            while isleyebildim:
                isleyebildim = False
                tas_islendi = None
                for tas in kalan_taslar:
                    for per_listesi in oyun_context.acilan_perler.values():
                        for per in per_listesi:
                            if Rules.islem_dogrula(per, tas):
                                tas_islendi = tas
                                break
                        if tas_islendi: break
                    if tas_islendi: break
                if tas_islendi:
                    kalan_taslar.remove(tas_islendi)
                    isleyebildim = True
            
            if len(kalan_taslar) <= 1:
                logger.info(f"AI Oyuncu {self.isim} bitmek için son taşını atıyor.")
                return self.el[-1]

        if oyun_context:
            ise_yarayan_taslar = set()
            for combo in combinations(self.el, 2):
                if oyun_context.atilan_taslar and Rules.genel_per_dogrula(list(combo) + [oyun_context.atilan_taslar[-1]]):
                    for tas in combo: ise_yarayan_taslar.add(tas)

            atilabilecek_taslar = [tas for tas in self.el if tas not in ise_yarayan_taslar]
            if atilabilecek_taslar:
                return random.choice(atilabilecek_taslar)

        return random.choice(self.el)

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
        
        # YENİ ve VERİMLİ EL AÇMA MANTIĞI
        # 1. Eldeki taşları grupla
        renk_gruplari = defaultdict(list)
        sayi_gruplari = defaultdict(list)
        jokerler = []
        for tas in self.el:
            if tas.renk == "joker":
                jokerler.append(tas)
            else:
                renk_gruplari[tas.renk].append(tas)
                sayi_gruplari[tas.deger].append(tas)

        # 2. Olası tüm perleri bul
        olasi_perler = []
        # Serileri bul
        for renk, taslar in renk_gruplari.items():
            if len(taslar) + len(jokerler) >= 3:
                 for size in range(len(taslar) + len(jokerler), 2, -1):
                     for combo in combinations(taslar + jokerler, size):
                         if Rules.per_dogrula(list(combo), "Seri 3"):
                             olasi_perler.append(list(combo))
        
        # Kütleri bul
        for sayi, taslar in sayi_gruplari.items():
            if len(taslar) + len(jokerler) >= 3:
                for size in range(min(len(taslar) + len(jokerler), 4), 2, -1):
                     for combo in combinations(taslar + jokerler, size):
                         if Rules.per_dogrula(list(combo), "Küt 3"):
                             olasi_perler.append(list(combo))

        # 3. Göreve uygun perleri ara ve döndür
        if not olasi_perler:
            return None

        # En uzun peri açmayı tercih et
        olasi_perler.sort(key=len, reverse=True)
        for per in olasi_perler:
            if Rules.per_dogrula(per, gorev):
                return [tas.id for tas in per]
                
        return None

    @logger.log_function
    def isleme_dene(self, oyun, oyuncu_index):
        for tas in self.el[:]:
            for per_sahibi_idx, per_listesi in oyun.acilan_perler.items():
                for per_idx, per in enumerate(per_listesi):
                    if Rules.islem_dogrula(per, tas):
                        if oyun.islem_yap(oyuncu_index, per_sahibi_idx, per_idx, tas.id):
                            return True
        return False