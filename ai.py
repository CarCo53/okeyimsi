# ai.py dosyasının tam içeriği

from player import Player
import random
from log import logger
from rules_manager import Rules
from itertools import combinations, chain
from collections import defaultdict
from rules.per_validators import seri_mu, kut_mu

class AIPlayer(Player):
    def __init__(self, isim):
        super().__init__(isim)

    @logger.log_function
    def karar_ver_ve_at(self, oyun_context=None):
        if not self.el: return None
        gorev_perleri = self._gorevi_tamamlayan_perleri_bul(oyun_context.mevcut_gorev)
        if gorev_perleri:
            gorev_tas_idler = {tas.id for per in gorev_perleri for tas in per}
            atilabilecekler = [tas for tas in self.el if tas.id not in gorev_tas_idler]
            if not atilabilecekler:
                if self.el: return self.el[-1]
                return None
            return self._en_ise_yaramaz_tasi_bul(atilabilecekler)
        return self._en_ise_yaramaz_tasi_bul(self.el)

    def _en_ise_yaramaz_tasi_bul(self, tas_listesi):
        en_dusuk_skor = 100
        en_kotu_tas = None
        guvenli_liste = [t for t in tas_listesi if t.renk != 'joker']
        if not guvenli_liste:
             return random.choice(tas_listesi) if tas_listesi else None
        for tas in guvenli_liste:
            skor = 0
            for diger_tas in self.el:
                if tas.id == diger_tas.id: continue
                if tas.deger == diger_tas.deger: skor += 5
                if tas.renk == diger_tas.renk and abs(tas.deger - diger_tas.deger) <= 2: skor += 3
            if skor < en_dusuk_skor:
                en_dusuk_skor = skor
                en_kotu_tas = tas
        return en_kotu_tas if en_kotu_tas else random.choice(guvenli_liste)

    @logger.log_function
    def atilan_tasi_degerlendir(self, oyun, atilan_tas):
        olasi_el = self.el + [atilan_tas]
        test_oyuncu = AIPlayer("test")
        test_oyuncu.el = olasi_el
        if test_oyuncu._gorevi_tamamlayan_perleri_bul(oyun.mevcut_gorev):
            return True
        for combo in combinations(self.el, 2):
            if Rules.genel_per_dogrula(list(combo) + [atilan_tas]):
                return True
        return False

    @logger.log_function  
    def ai_el_ac_dene(self, oyun, oyuncu_index):
        if oyun.acilmis_oyuncular[oyuncu_index]: return None
        gorev_perleri = self._gorevi_tamamlayan_perleri_bul(oyun.mevcut_gorev)
        if gorev_perleri:
            en_iyi_kombinasyon = max(gorev_perleri, key=lambda p: len(p))
            for tas in en_iyi_kombinasyon:
                if tas.renk == 'joker' and not tas.joker_yerine_gecen:
                    olasi = Rules.joker_icin_olasi_taslar(en_iyi_kombinasyon)
                    if olasi and olasi.get(tas):
                        tas.joker_yerine_gecen = olasi.get(tas)[0]
            return [tas.id for tas in en_iyi_kombinasyon]
        return None

    def _gorevi_tamamlayan_perleri_bul(self, gorev):
        jokerler = [t for t in self.el if t.renk == 'joker']
        normal_taslar = [t for t in self.el if t.renk != 'joker']
        
        tum_olasi_perler = self._bul_tum_perler(normal_taslar, jokerler)
        if not tum_olasi_perler: return []

        tamamlayan_kombinasyonlar = []
        for per in tum_olasi_perler:
            if Rules.per_dogrula(per, gorev):
                tamamlayan_kombinasyonlar.append(per)

        if " " in gorev:
            for i in range(len(tum_olasi_perler)):
                for j in range(i + 1, len(tum_olasi_perler)):
                    per1, per2 = tum_olasi_perler[i], tum_olasi_perler[j]
                    if set(p.id for p in per1).isdisjoint(set(p.id for p in per2)):
                        toplam_per = per1 + per2
                        if Rules.per_dogrula(toplam_per, gorev):
                            tamamlayan_kombinasyonlar.append(toplam_per)
        return tamamlayan_kombinasyonlar

    def _bul_tum_perler(self, normal_taslar, jokerler):
        """YENİ: Eldeki tüm olası perleri bulan 'açgözlü' algoritma."""
        bulunan_perler = []
        kullanilabilir_taslar = normal_taslar[:]
        kullanilabilir_jokerler = jokerler[:]

        # Önce en uzun serileri bul
        seriler = self._bul_olasi_seriler(kullanilabilir_taslar, kullanilabilir_jokerler)
        seriler.sort(key=len, reverse=True)
        for seri in seriler:
            ids_in_seri = {t.id for t in seri if t.renk != 'joker'}
            jokers_in_seri = [t for t in seri if t.renk == 'joker']
            if all(t in kullanilabilir_taslar for t in seri if t.renk != 'joker') and len(kullanilabilir_jokerler) >= len(jokers_in_seri):
                bulunan_perler.append(seri)
                kullanilabilir_taslar = [t for t in kullanilabilir_taslar if t.id not in ids_in_seri]
                for _ in jokers_in_seri: kullanilabilir_jokerler.pop()

        # Kalan taşlarla kütleri bul
        kutler = self._bul_olasi_kutler(kullanilabilir_taslar, kullanilabilir_jokerler)
        kutler.sort(key=len, reverse=True)
        bulunan_perler.extend(kutler)
        
        return bulunan_perler

    def _bul_olasi_kutler(self, taslar, jokerler):
        olasi_kutler = []
        sayi_gruplari = defaultdict(list)
        for tas in taslar: sayi_gruplari[tas.deger].append(tas)
        for deger, ayni_sayili_taslar in sayi_gruplari.items():
            farkli_renk_taslar = list({t.renk: t for t in ayni_sayili_taslar}.values())
            for per_boyutu in range(3, 5):
                gerekli_tas_sayisi = per_boyutu - len(jokerler)
                if gerekli_tas_sayisi > 0 and len(farkli_renk_taslar) >= gerekli_tas_sayisi:
                    for combo in combinations(farkli_renk_taslar, gerekli_tas_sayisi):
                        per = list(combo) + jokerler
                        if kut_mu(per, per_boyutu): olasi_kutler.append(per)
        return olasi_kutler

    def _bul_olasi_seriler(self, taslar, jokerler):
        olasi_seriler = []
        renk_gruplari = defaultdict(list)
        for tas in taslar: renk_gruplari[tas.renk].append(tas)
        for renk, ayni_renk_taslar in renk_gruplari.items():
            if len(ayni_renk_taslar) + len(jokerler) < 3: continue
            ayni_renk_taslar.sort(key=lambda t: t.deger)
            for i in range(len(ayni_renk_taslar)):
                mevcut_seri = [ayni_renk_taslar[i]]
                kalan_joker = len(jokerler)
                for j in range(i + 1, len(ayni_renk_taslar)):
                    son_tas = mevcut_seri[-1]
                    siradaki_tas = ayni_renk_taslar[j]
                    bosluk = siradaki_tas.deger - son_tas.deger - 1
                    if bosluk < 0: continue
                    if bosluk <= kalan_joker:
                        mevcut_seri.append(siradaki_tas)
                        kalan_joker -= bosluk
                if len(mevcut_seri) + len(jokerler) - kalan_joker >= 3:
                    per = mevcut_seri + jokerler[:len(jokerler) - kalan_joker]
                    if seri_mu(per, len(per)): olasi_seriler.append(per)
        return olasi_seriler

    @logger.log_function
    def isleme_dene(self, oyun, oyuncu_index):
        for tas in self.el[:]:
            for per_sahibi_idx, per_listesi in oyun.acilan_perler.items():
                for per_idx, per in enumerate(per_listesi):
                    if Rules.islem_dogrula(per, tas):
                        if oyun.islem_yap(oyuncu_index, per_sahibi_idx, per_idx, tas.id):
                            return True
        return False