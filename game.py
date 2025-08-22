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

    @logger.log_function
    def baslat(self):
        baslat_oyun(self)

    @logger.log_function
    def tas_at(self, oyuncu_index, tas_id):
        if self.oyun_durumu not in [GameState.ILK_TUR, GameState.NORMAL_TUR, GameState.NORMAL_TAS_ATMA]:
            return False
        if oyuncu_index != self.sira_kimde_index:
            return False
        oyuncu = self.oyuncular[oyuncu_index]
        if self.oyun_durumu == GameState.ILK_TUR and len(oyuncu.el) != 14:
            return False
        atilan_tas = oyuncu.tas_at(tas_id)
        if atilan_tas:
            self.atilan_taslar.append(atilan_tas)
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
        # *** DÜZELTME: Fonksiyon, orijinal ve doğru çalışan mantığına geri döndürüldü ***
        if self.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return

        # Atılan taşın listede olduğundan emin ol
        if not self.atilan_taslar:
            logger.warning("Yerden alınacak taş bulunamadı!")
            return

        alici_oyuncu = self.oyuncular[oyuncu_index]
        atilan_tas = self.atilan_taslar.pop()
        alici_oyuncu.tas_al(atilan_tas)
        
        asil_sira_index = self.atilan_tas_degerlendirici.asilin_sirasi()

        # Eğer sırası gelen doğru oyuncu taşı aldıysa
        if oyuncu_index == asil_sira_index:
            alici_oyuncu.el_sirala()
            self.sira_kimde_index = oyuncu_index
            self.oyun_durumu = GameState.NORMAL_TAS_ATMA
            self.turda_tas_cekildi = [False for _ in range(4)]
            self.atilan_tas_degerlendirici = None
        # Eğer oyuncu sırası gelmeden (cezalı olarak) taşı aldıysa
        else:
            ceza_tas = self.deste.tas_cek()
            if ceza_tas:
                alici_oyuncu.tas_al(ceza_tas)
            alici_oyuncu.el_sirala()
            
            # Değerlendirme devam eder, sadece bu oyuncu atlanır
            self.atilan_tas_degerlendirici.gecen_ekle(oyuncu_index)
            # Sıra, taşı atan oyuncunun sağındakine geçer ve o desteden çeker
            self.sira_kimde_index = asil_sira_index
            self.oyun_durumu = GameState.NORMAL_TUR
            self.turda_tas_cekildi = [False for _ in range(4)]
            self.atilan_tas_degerlendirici = None


    @logger.log_function
    def atilan_tasi_gecti(self):
        if self.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return
        self.atilan_tas_degerlendirici.gecen_ekle(self.atilan_tas_degerlendirici.siradaki())
        self.atilan_tas_degerlendirici.bir_sonraki()
        if self.atilan_tas_degerlendirici.herkes_gecti_mi():
            self.sira_kimde_index = self.atilan_tas_degerlendirici.asilin_sirasi()
            self.oyun_durumu = GameState.NORMAL_TUR
            self.turda_tas_cekildi = [False for _ in range(4)]
            self.atilan_tas_degerlendirici = None

    @logger.log_function
    def desteden_cek(self, oyuncu_index):
        if not (self.oyun_durumu == GameState.NORMAL_TUR and self.sira_kimde_index == oyuncu_index): return False
        if self.turda_tas_cekildi[oyuncu_index]: return False
        oyuncu = self.oyuncular[oyuncu_index]
        tas = self.deste.tas_cek()
        if tas:
            oyuncu.tas_al(tas)
            oyuncu.el_sirala()
            self.turda_tas_cekildi[oyuncu_index] = True
            self.oyun_durumu = GameState.NORMAL_TAS_ATMA
            return True
        return False
        
    @logger.log_function
    def el_ac(self, oyuncu_index, tas_id_list):
        oyuncu = self.oyuncular[oyuncu_index]
        secilen_taslar = [tas for tas in oyuncu.el if tas.id in tas_id_list]
        jokerler = [t for t in secilen_taslar if t.renk == 'joker']
        if jokerler:
            olasi_secimler = Rules.joker_icin_olasi_taslar(secilen_taslar)
            if olasi_secimler is None: return False
            for joker, secenekler in olasi_secimler.items():
                if len(secenekler) > 1:
                    logger.warning("Okey için birden fazla seçenek var, oyuncu seçimi gerekiyor.")
                    return False 
                elif len(secenekler) == 1:
                    joker.joker_yerine_gecen = secenekler[0]
        gecerli_mi = False
        if not self.acilmis_oyuncular[oyuncu_index]:
            if Rules.per_dogrula(secilen_taslar, self.mevcut_gorev):
                self.acilmis_oyuncular[oyuncu_index] = True
                gecerli_mi = True
        else:
            if Rules.genel_per_dogrula(secilen_taslar):
                gecerli_mi = True
        if gecerli_mi:
            for tas in secilen_taslar:
                oyuncu.tas_at(tas.id)
            self.acilan_perler[oyuncu_index].append(secilen_taslar)
            oyuncu.el_sirala()
            return True
        else:
            for joker in jokerler:
                joker.joker_yerine_gecen = None
            return False

    @logger.log_function
    def islem_yap(self, isleyen_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        if not self.acilmis_oyuncular[isleyen_oyuncu_idx]: return False
        if isleyen_oyuncu_idx != self.sira_kimde_index: return False
        tas = next((t for t in self.oyuncular[isleyen_oyuncu_idx].el if t.id == tas_id), None)
        if not tas: return False
        if per_sahibi_idx not in self.acilan_perler or per_idx >= len(self.acilan_perler[per_sahibi_idx]):
            return False
        per = self.acilan_perler[per_sahibi_idx][per_idx]
        if Rules.islem_dogrula(per, tas):
            self.oyuncular[isleyen_oyuncu_idx].tas_at(tas.id)
            per.append(tas)
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