from rules_manager import Rules
from state import GameState
import random

def baslat_oyun(game):
    """Oyunu başlatır veya yeniden başlatır."""
    game.mevcut_gorev = random.choice(Rules.GOREVLER)
    game.kazanan_index = None
    game.deste.olustur()
    game.deste.karistir()
    game.sira_kimde_index = 0
    for i, oyuncu in enumerate(game.oyuncular):
        oyuncu.el = []
        tas_sayisi = 14 if i == game.sira_kimde_index else 13
        for _ in range(tas_sayisi):
            oyuncu.tas_al(game.deste.tas_cek())
        oyuncu.el_sirala()
    game.oyun_durumu = GameState.ILK_TUR
    game.atilan_taslar = []
    game.acilan_perler = {i: [] for i in range(4)}
    game.turda_tas_cekildi = [False for _ in range(4)]
    game.atilan_tas_degerlendirici = None
    game.oyun_basladi_mi = False
    game.acilmis_oyuncular = [False for _ in range(4)]