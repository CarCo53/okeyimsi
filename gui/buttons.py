import tkinter as tk
from state import GameState

class ButtonManager:
    def __init__(self, arayuz):
        self.arayuz = arayuz
        self.butonlar = {}

    def ekle_butonlar(self, parent):
        """
        Oyun arayüzüne butonları ekler.
        """
        frame = tk.Frame(parent)
        frame.pack(pady=10)
        self.butonlar["yerden_al"] = tk.Button(frame, text="Yerden Al", command=self.yerden_al)
        self.butonlar["gec"] = tk.Button(frame, text="Geç", command=self.gec)
        self.butonlar["desteden_cek"] = tk.Button(frame, text="Desteden Çek", command=self.desteden_cek)
        self.butonlar["el_ac"] = tk.Button(frame, text="Elini Aç", command=self.el_ac)
        self.butonlar["tas_at"] = tk.Button(frame, text="Taş At", command=self.tas_at)
        self.butonlar["yeni_oyun"] = tk.Button(frame, text="Yeni Oyun", command=self.yeni_oyun)
        
        for btn in self.butonlar.values():
            btn.pack(side=tk.LEFT, padx=8)

    def butonlari_guncelle(self, oyun_durumu):
        """
        Oyun durumuna göre hangi butonların aktif olacağını yönetir.
        """
        for btn in self.butonlar.values():
            btn.config(state=tk.DISABLED)
        
        oyun = self.arayuz.oyun
        sira_bende = oyun.sira_kimde_index == 0
        
        # *** DÜZELTME: ILK_TUR durumu için eksik olan koşul eklendi ***
        if oyun_durumu == GameState.ILK_TUR:
            if sira_bende:
                self.butonlar["tas_at"].config(state=tk.NORMAL)

        elif oyun_durumu == GameState.NORMAL_TUR:
            if sira_bende:
                self.butonlar["el_ac"].config(state=tk.NORMAL)
                self.butonlar["desteden_cek"].config(state=tk.NORMAL)
                
        elif oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
            degerlendiren_ben_miyim = oyun.atilan_tas_degerlendirici and oyun.atilan_tas_degerlendirici.siradaki() == 0
            if degerlendiren_ben_miyim:
                # İlk oyuncu oyunun başında yerden taş alamaz
                if not (oyun.sira_kimde_index == 0 and not oyun.oyun_basladi_mi):
                    self.butonlar["yerden_al"].config(state=tk.NORMAL)
                self.butonlar["gec"].config(state=tk.NORMAL)

        elif oyun_durumu == GameState.NORMAL_TAS_ATMA:
            if sira_bende:
                if oyun.acilmis_oyuncular[0]:
                    self.butonlar["el_ac"].config(state=tk.NORMAL) # Taş işleme veya yeni per açma için
                self.butonlar["tas_at"].config(state=tk.NORMAL)

        elif oyun_durumu == GameState.BITIS:
            self.butonlar["yeni_oyun"].config(state=tk.NORMAL)

    def yerden_al(self):
        self.arayuz.oyun.atilan_tasi_al(0)
        self.arayuz.arayuzu_guncelle()

    def gec(self):
        self.arayuz.oyun.atilan_tasi_gecti()
        self.arayuz.arayuzu_guncelle()

    def desteden_cek(self):
        self.arayuz.oyun.desteden_cek(0)
        self.arayuz.arayuzu_guncelle()

    def el_ac(self):
        secili = self.arayuz.secili_tas_idler
        if secili:
            if self.arayuz.oyun.el_ac(0, secili):
                self.arayuz.secili_tas_idler = []
                self.arayuz.statusbar.guncelle("Per başarıyla açıldı!")
            else:
                self.arayuz.statusbar.guncelle("Geçersiz per veya okey için seçim gerekli!")
            self.arayuz.arayuzu_guncelle()

    def tas_at(self):
        secili = self.arayuz.secili_tas_idler
        if len(secili) == 1:
            self.arayuz.oyun.tas_at(0, secili[0])
            self.arayuz.secili_tas_idler = []
        else:
            self.arayuz.statusbar.guncelle("Lütfen atmak için sadece 1 taş seçin.")
        self.arayuz.arayuzu_guncelle()

    def yeni_oyun(self):
        self.arayuz.oyun.baslat()
        self.arayuz.arayuzu_guncelle()