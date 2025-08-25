# ai.py dosyasının tam ve doğru içeriği

from player import Player
import random
from log import logger
from rules_manager import Rules
from itertools import combinations
from collections import defaultdict
from rules.per_validators import seri_mu, kut_mu

class AIPlayer(Player):
    def __init__(self, isim):
        super().__init__(isim)

    @logger.log_function
    def karar_ver_ve_at(self, oyun_context=None):
        if not self.el: return None
        gorev_kombinasyonu = self._bul_gorev_kombinasyonu(self.el, oyun_context.mevcut_gorev)
        if gorev_kombinasyonu:
            gorev_tas_idler = {tas.id for per in gorev_kombinasyonu for tas in per}
            atilabilecekler = [tas for tas in self.el if tas.id not in gorev_tas_idler]
            if not atilabilecekler and self.el:
                return self.el[-1]
            return self._en_ise_yaramaz_tasi_bul(atilabilecekler)
        return self._en_ise_yaramaz_tasi_bul(self.el)

    def _en_ise_yaramaz_tasi_bul(self, tas_listesi):
        en_dusuk_skor = 101
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
        if self._bul_gorev_kombinasyonu(olasi_el, oyun.mevcut_gorev):
            logger.info(f"AI {self.isim} görev için taş alıyor: {atilan_tas}")
            return True
        for combo in combinations(self.el, 2):
            if Rules.genel_per_dogrula(list(combo) + [atilan_tas]):
                logger.info(f"AI {self.isim} yeni per için taş alıyor: {atilan_tas}")
                return True
        return False

    @logger.log_function  
    def ai_el_ac_dene(self, oyun, oyuncu_index):
        if oyun.acilmis_oyuncular[oyuncu_index]: return None
        gorev_kombinasyonu = self._bul_gorev_kombinasyonu(self.el, oyun.mevcut_gorev)
        if gorev_kombinasyonu:
            acilan_per = [tas for per in gorev_kombinasyonu for tas in per]
            logger.info(f"AI {self.isim} görevini tamamladı ve elini açıyor: {acilan_per}")
            return [tas.id for tas in acilan_per]
        return None

    def _bul_gorev_kombinasyonu(self, el, gorev_metni):
        """
        Özyinelemeli olarak eli alt görevlere ayırır ve çözer.
        """
        # Görev metnini alt görevlere ayır
        # Örnek: "2x Küt 4" -> ["Küt 4", "Küt 4"]
        # Örnek: "Küt 3 + Seri 3" -> ["Küt 3", "Seri 3"]
        parts = []
        if "2x" in gorev_metni:
            count, per_type, size = 2, gorev_metni.split(" ")[1], int(gorev_metni.split(" ")[-1])
            parts = [f"{per_type} {size}"] * count
        elif "+" in gorev_metni:
            parts = gorev_metni.split(" + ")
        else:
            parts = [gorev_metni]

        return self._coz(el, parts)

    def _coz(self, el, gorev_parcalari):
        if not gorev_parcalari:
            return []  # Başarıyla tüm görevler tamamlandı

        mevcut_gorev = gorev_parcalari[0]
        kalan_gorevler = gorev_parcalari[1:]
        
        boyut = int(mevcut_gorev.split(" ")[-1])
        is_kut = "Küt" in mevcut_gorev
        
        # Mevcut görevi tamamlayan tüm olası perleri bul
        olasi_perler = []
        for combo in combinations(el, boyut):
            per = list(combo)
            if is_kut and kut_mu(per, boyut):
                olasi_perler.append(per)
            elif not is_kut and seri_mu(per, boyut):
                olasi_perler.append(per)
        
        # Her bir olası per için, kalan taşlarla görevin geri kalanını çözmeye çalış
        for per in olasi_perler:
            kalan_taslar = [tas for tas in el if tas not in per]
            sonuc = self._coz(kalan_taslar, kalan_gorevler)
            
            if sonuc is not None:
                # Başarılı bir yol bulundu, perleri birleştirerek döndür
                return [per] + sonuc
        
        return None # Bu yoldan bir çözüm bulunamadı