from state import GameState, AtilanTasDegerlendirici
from log import logger

class TurnManager:
    def __init__(self, game):
        self.game = game

    @logger.log_function
    def tas_at(self, oyuncu_index, tas_id):
        game = self.game
        if game.oyun_durumu not in [GameState.ILK_TUR, GameState.NORMAL_TUR, GameState.NORMAL_TAS_ATMA]:
            return False
        if oyuncu_index != game.sira_kimde_index:
            return False

        oyuncu = game.oyuncular[oyuncu_index]
        
        if game.oyun_durumu == GameState.ILK_TUR and len(oyuncu.el) != 14:
            logger.error("İlk turda oyuncunun 14 taşı olmalı.")
            return False

        atilan_tas = oyuncu.tas_at(tas_id)
        
        if atilan_tas:
            game.atilan_taslar.append(atilan_tas)
            
            if game.acilmis_oyuncular[oyuncu_index] and not oyuncu.el:
                game.oyun_durumu = GameState.BITIS
                game.kazanan_index = oyuncu_index
                return True

            game.oyun_durumu = GameState.ATILAN_TAS_DEGERLENDIRME
            game.atilan_tas_degerlendirici = AtilanTasDegerlendirici(oyuncu_index, len(game.oyuncular))
            game.oyun_basladi_mi = True
            return True
        return False

    @logger.log_function
    def atilan_tasi_al(self, oyuncu_index):
        game = self.game
        if game.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return
        
        alici_oyuncu = game.oyuncular[oyuncu_index]
        atilan_tas = game.atilan_taslar.pop()
        alici_oyuncu.tas_al(atilan_tas)
        alici_oyuncu.el_sirala()

        asil_sira_index = game.atilan_tas_degerlendirici.asilin_sirasi()
        if oyuncu_index == asil_sira_index:
            game.sira_kimde_index = oyuncu_index
            game.oyun_durumu = GameState.NORMAL_TAS_ATMA
            game.turda_tas_cekildi = [False for _ in range(4)]
            game.atilan_tas_degerlendirici = None
        else:
            ceza_tas = game.deste.tas_cek()
            if ceza_tas: alici_oyuncu.tas_al(ceza_tas)
            alici_oyuncu.el_sirala()
            game.atilan_tas_degerlendirici.gecen_ekle(oyuncu_index)
            game.atilan_tas_degerlendirici.bir_sonraki()
            if game.atilan_tas_degerlendirici.herkes_gecti_mi():
                 game.sira_kimde_index = asil_sira_index
                 game.oyun_durumu = GameState.NORMAL_TUR
                 game.turda_tas_cekildi = [False for _ in range(4)]
                 game.atilan_tas_degerlendirici = None

    @logger.log_function
    def atilan_tasi_gecti(self):
        game = self.game
        if game.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return

        game.atilan_tas_degerlendirici.gecen_ekle(game.atilan_tas_degerlendirici.siradaki())
        game.atilan_tas_degerlendirici.bir_sonraki()
        
        if game.atilan_tas_degerlendirici.herkes_gecti_mi():
            game.sira_kimde_index = game.atilan_tas_degerlendirici.asilin_sirasi()
            game.oyun_durumu = GameState.NORMAL_TUR
            game.turda_tas_cekildi = [False for _ in range(4)]
            game.atilan_tas_degerlendirici = None

    @logger.log_function
    def desteden_cek(self, oyuncu_index):
        game = self.game
        if not (game.oyun_durumu == GameState.NORMAL_TUR and game.sira_kimde_index == oyuncu_index): return False
        if game.turda_tas_cekildi[oyuncu_index]: return False
        
        oyuncu = game.oyuncular[oyuncu_index]
        tas = game.deste.tas_cek()
        if tas:
            oyuncu.tas_al(tas)
            oyuncu.el_sirala()
            game.turda_tas_cekildi[oyuncu_index] = True
            game.oyun_durumu = GameState.NORMAL_TAS_ATMA
            return True
        return False