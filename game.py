from deck import Deck
from player import Player
from ai import AIPlayer
from rules_manager import Rules
from state import GameState, AtilanTasDegerlendirici
from log import logger
from tile import Tile
import random
from baslat import baslat_oyun

class Game:
    def __init__(self):
        self.oyuncular = [
            Player("Oyuncu 1 (Siz)"),
            AIPlayer("AI Oyuncu 2"),
            AIPlayer("AI Oyuncu 3"),
            AIPlayer("AI Oyuncu 4")
        ]
        self.deste = Deck()
        self.atilan_taslar = []
        self.sira_kimde_index = 0
        self.oyun_durumu = GameState.NORMAL_TUR
        self.acilan_perler = {i: [] for i in range(4)}
        self.turda_tas_cekildi = [False for _ in range(4)]
        self.atilan_tas_degerlendirici = None
        self.oyun_basladi_mi = False
        self.acilmis_oyuncular = [False for _ in range(4)]
        self.mevcut_gorev = None
        self.kazanan_index = None
        self.tur_numarasi = 1
        self.ilk_el_acan_tur = {}
        self.son_cekilen_bilgisi = None

    @logger.log_function
    def baslat(self):
        baslat_oyun(self)
        self.tur_numarasi = 1
        self.ilk_el_acan_tur = {}
        self.son_cekilen_bilgisi = None

    def _sira_ilerlet(self, yeni_index):
        if yeni_index < self.sira_kimde_index:
            self.tur_numarasi += 1
            logger.info(f"Yeni tura geçildi: Tur {self.tur_numarasi}")
        self.sira_kimde_index = yeni_index

    @logger.log_function
    def tas_at(self, oyuncu_index, tas_id):
        oyuncu = self.oyuncular[oyuncu_index]
        if not oyuncu.el and self.acilmis_oyuncular[oyuncu_index]:
             self.oyun_durumu = GameState.BITIS
             self.kazanan_index = oyuncu_index
             logger.info(f"Oyuncu {oyuncu_index} elindeki son taşı atarak oyunu bitirdi.")
             return True

        if self.oyun_durumu not in [GameState.ILK_TUR, GameState.NORMAL_TUR, GameState.NORMAL_TAS_ATMA]:
            return False
        if oyuncu_index != self.sira_kimde_index:
            return False
        
        atilan_tas = oyuncu.tas_at(tas_id)
        if atilan_tas:
            self.atilan_taslar.append(atilan_tas)
            self.son_cekilen_bilgisi = None
            if self.acilmis_oyuncular[oyuncu_index] and not oyuncu.el:
                self.oyun_durumu = GameState.BITIS
                self.kazanan_index = oyuncu_index
                return True
            self.oyun_durumu = GameState.ATILAN_TAS_DEGERLENDIRME
            self.atilan_tas_degerlendirici = AtilanTasDegerlendirici(oyuncu_index, len(self.oyuncular))
            self.oyun_basladi_mi = True
            return True
        return False

    @logger.log_function
    def atilan_tasi_al(self, oyuncu_index):
        if self.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return

        if not self.atilan_taslar: return

        alici_oyuncu = self.oyuncular[oyuncu_index]
        atilan_tas = self.atilan_taslar.pop()
        alici_oyuncu.tas_al(atilan_tas)
        self.son_cekilen_bilgisi = {"tas": atilan_tas, "kaynak": "yerden"}
        
        asil_sira_index = self.atilan_tas_degerlendirici.asilin_sirasi()

        if oyuncu_index == asil_sira_index:
            alici_oyuncu.el_sirala()
            self._sira_ilerlet(oyuncu_index)
            self.oyun_durumu = GameState.NORMAL_TAS_ATMA
        else:
            ceza_tas = self.deste.tas_cek()
            if ceza_tas: alici_oyuncu.tas_al(ceza_tas)
            alici_oyuncu.el_sirala()
            self.atilan_tas_degerlendirici.gecen_ekle(oyuncu_index)
            self._sira_ilerlet(asil_sira_index)
            self.oyun_durumu = GameState.NORMAL_TUR

        self.turda_tas_cekildi = [False] * 4
        self.atilan_tas_degerlendirici = None

    @logger.log_function
    def atilan_tasi_gecti(self):
        if self.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return
        self.atilan_tas_degerlendirici.gecen_ekle(self.atilan_tas_degerlendirici.siradaki())
        self.atilan_tas_degerlendirici.bir_sonraki()
        if self.atilan_tas_degerlendirici.herkes_gecti_mi():
            yeni_sira_index = self.atilan_tas_degerlendirici.asilin_sirasi()
            self._sira_ilerlet(yeni_sira_index)
            self.oyun_durumu = GameState.NORMAL_TUR
            self.turda_tas_cekildi = [False] * 4
            self.atilan_tas_degerlendirici = None

    @logger.log_function
    def desteden_cek(self, oyuncu_index):
        if not (self.oyun_durumu == GameState.NORMAL_TUR and self.sira_kimde_index == oyuncu_index): return False
        if self.turda_tas_cekildi[oyuncu_index]: return False
        
        oyuncu = self.oyuncular[oyuncu_index]
        tas = self.deste.tas_cek()
        if tas:
            oyuncu.tas_al(tas)
            self.son_cekilen_bilgisi = {"tas": tas, "kaynak": "desteden"}
            oyuncu.el_sirala()
            self.turda_tas_cekildi[oyuncu_index] = True
            self.oyun_durumu = GameState.NORMAL_TAS_ATMA
            return True
        return False

    def el_ac_joker_ile(self, oyuncu_index, secilen_taslar, joker, secilen_deger):
        joker.joker_yerine_gecen = secilen_deger
        return self._eli_ac_ve_isle(oyuncu_index, secilen_taslar)

    def _eli_ac_ve_isle(self, oyuncu_index, secilen_taslar):
        oyuncu = self.oyuncular[oyuncu_index]
        dogrulama_sonucu = False
        
        if not self.acilmis_oyuncular[oyuncu_index]:
            dogrulama_sonucu = Rules.per_dogrula(secilen_taslar, self.mevcut_gorev)
            if dogrulama_sonucu:
                self.acilmis_oyuncular[oyuncu_index] = True
                self.ilk_el_acan_tur[oyuncu_index] = self.tur_numarasi
        else:
            if self.tur_numarasi > self.ilk_el_acan_tur.get(oyuncu_index, -1):
                dogrulama_sonucu = Rules.genel_per_dogrula(secilen_taslar)
            else:
                return {"status": "fail", "message": "Görev dışı per açmak için bir sonraki turu beklemelisiniz."}

        if dogrulama_sonucu:
            for tas in secilen_taslar:
                oyuncu.tas_at(tas.id)
            
            if isinstance(dogrulama_sonucu, tuple):
                self.acilan_perler[oyuncu_index].extend(dogrulama_sonucu)
            else: 
                self.acilan_perler[oyuncu_index].append(secilen_taslar)
            
            oyuncu.el_sirala()
            return {"status": "success"}
        else:
            for tas in secilen_taslar:
                if tas.renk == 'joker':
                    tas.joker_yerine_gecen = None
            return {"status": "fail", "message": "Geçersiz per."}
        
    @logger.log_function
    def el_ac(self, oyuncu_index, tas_id_list):
        oyuncu = self.oyuncular[oyuncu_index]
        secilen_taslar = [tas for tas in oyuncu.el if tas.id in tas_id_list]
        jokerler = [t for t in secilen_taslar if t.renk == 'joker']

        is_complex_mission = self.mevcut_gorev and " " in self.mevcut_gorev
        
        if jokerler and not is_complex_mission:
            olasi_secimler = Rules.joker_icin_olasi_taslar(secilen_taslar)
            if olasi_secimler is None: return {"status": "fail", "message": "Geçersiz per."}

            for joker, secenekler in olasi_secimler.items():
                if len(secenekler) > 1:
                    return { "status": "joker_choice_needed", "options": secenekler, "joker": joker, "secilen_taslar": secilen_taslar }
                elif len(secenekler) == 1:
                    joker.joker_yerine_gecen = secenekler[0]
        
        return self._eli_ac_ve_isle(oyuncu_index, secilen_taslar)

    @logger.log_function
    def islem_yap(self, isleyen_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        isleyen_oyuncu = self.oyuncular[isleyen_oyuncu_idx]
        if not self.acilmis_oyuncular[isleyen_oyuncu_idx]: return False
        if isleyen_oyuncu_idx != self.sira_kimde_index: return False
        
        tas = next((t for t in isleyen_oyuncu.el if t.id == tas_id), None)
        if not tas: return False
        
        if per_sahibi_idx not in self.acilan_perler or per_idx >= len(self.acilan_perler[per_sahibi_idx]):
            return False
            
        per = self.acilan_perler[per_sahibi_idx][per_idx]
        
        def per_sirala(p):
            degerler = [(t.joker_yerine_gecen or t).deger for t in p if (t.joker_yerine_gecen or t).deger is not None]
            if 1 in degerler and 13 in degerler:
                p.sort(key=lambda t: ((t.joker_yerine_gecen or t).deger or 0) % 14)
            else:
                p.sort(key=lambda t: (t.joker_yerine_gecen or t).deger or 0)

        for i, per_tasi in enumerate(per):
            if per_tasi.renk == "joker" and per_tasi.joker_yerine_gecen:
                yerine_gecen = per_tasi.joker_yerine_gecen
                if yerine_gecen.renk == tas.renk and yerine_gecen.deger == tas.deger:
                    joker = per.pop(i)
                    joker.joker_yerine_gecen = None
                    isleyen_oyuncu.tas_al(joker)
                    
                    isleyen_oyuncu.tas_at(tas.id)
                    per.append(tas)
                    isleyen_oyuncu.el_sirala()
                    
                    if Rules._per_seri_mu(per): per_sirala(per)
                    
                    self.oyun_durumu = GameState.NORMAL_TAS_ATMA
                    return True

        if Rules.islem_dogrula(per, tas):
            isleyen_oyuncu.tas_at(tas.id)
            per.append(tas)
            
            if Rules._per_seri_mu(per): per_sirala(per)

            self.oyun_durumu = GameState.NORMAL_TAS_ATMA
            return True
            
        return False
        
    @logger.log_function
    def oyuncunun_tas_cekme_ihtiyaci(self, oyuncu_index):
        if self.oyun_durumu == GameState.ILK_TUR: return False
        return len(self.oyuncular[oyuncu_index].el) % 3 != 2

    def oyun_bitti_mi(self):
        if self.oyun_durumu == GameState.BITIS: return True
        if not self.deste.taslar:
            self.oyun_durumu = GameState.BITIS
            return True
        return False