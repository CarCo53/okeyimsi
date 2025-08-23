import tkinter as tk
from gui.visuals import Visuals
from gui.buttons import ButtonManager
from gui.status import StatusBar
from state import GameState
from gui.arayuzguncelle import arayuzu_guncelle

class Arayuz:
    def __init__(self, oyun):
        self.oyun = oyun
        self.pencere = tk.Tk()
        self.pencere.title("Okey Oyunu")
        self.pencere.geometry("1400x900")
        self.visuals = Visuals()
        self.visuals.yukle()
        self.statusbar = StatusBar(self)
        self.button_manager = ButtonManager(self)
        self.secili_tas_idler = []
        self.alanlar = {}
        self._layout_olustur()
        self.arayuzu_guncelle()

    def _layout_olustur(self):
        self.statusbar.ekle_status_label(self.pencere)
        oyuncu_cercevesi = tk.Frame(self.pencere)
        oyuncu_cercevesi.pack(pady=5, fill="x")
        
        self.alanlar['oyuncu_1'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "Oyuncu 1 (Siz)")
        self.alanlar['oyuncu_2'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "AI Oyuncu 2")
        self.alanlar['oyuncu_3'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "AI Oyuncu 3")
        self.alanlar['oyuncu_4'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "AI Oyuncu 4")

        self.masa_frame = tk.LabelFrame(self.pencere, text="Masa (Açılan Perler)", padx=10, pady=10)
        self.masa_frame.pack(pady=10, fill="both", expand=True)

        deste_ve_atilan_cerceve = tk.Frame(self.pencere)
        deste_ve_atilan_cerceve.pack(pady=5)
        
        self.deste_frame = tk.LabelFrame(deste_ve_atilan_cerceve, text="Deste", padx=5, pady=5)
        self.deste_frame.pack(side=tk.LEFT, padx=10)
        
        self.atilan_frame = tk.LabelFrame(deste_ve_atilan_cerceve, text="Atılan Taşlar", padx=5, pady=5)
        self.atilan_frame.pack(side=tk.LEFT, padx=10)
        
        self.deste_sayisi_label = tk.Label(self.deste_frame, text="", font=("Arial", 12, "bold"))
        self.deste_sayisi_label.pack(side=tk.TOP, pady=2)
        
        self.button_manager.ekle_butonlar(self.pencere)

    def _oyuncu_alani_olustur(self, parent, isim):
        frame = tk.LabelFrame(parent, text=isim, padx=5, pady=5)
        frame.pack(pady=2, fill="x")
        return frame

    def arayuzu_guncelle(self):
        arayuzu_guncelle(self)

    def tas_sec(self, tas_id):
        if tas_id in self.secili_tas_idler:
            self.secili_tas_idler.remove(tas_id)
        else:
            self.secili_tas_idler.append(tas_id)
        self.arayuzu_guncelle()

    def per_sec(self, oyuncu_index, per_index):
        if not self.oyun.acilmis_oyuncular[0]:
            self.statusbar.guncelle("Taş işlemek için önce elinizi açmalısınız.")
            return
        if len(self.secili_tas_idler) == 1:
            tas_id = self.secili_tas_idler[0]
            if self.oyun.islem_yap(0, oyuncu_index, per_index, tas_id):
                self.secili_tas_idler = []
                self.arayuzu_guncelle()
            else:
                self.statusbar.guncelle("Bu taş bu pere işlenemez.")
        else:
            self.statusbar.guncelle("İşlemek için elinizden 1 taş seçmelisiniz.")
            
    def joker_secim_penceresi_ac(self, secenekler, joker, secilen_taslar):
        """Joker için olası taşları kullanıcıya sunan bir pencere açar."""
        secim_penceresi = tk.Toplevel(self.pencere)
        secim_penceresi.title("Joker Seçimi")
        secim_penceresi.geometry("300x150")
        secim_penceresi.transient(self.pencere) # Ana pencerenin üzerinde kalmasını sağlar
        secim_penceresi.grab_set() # Diğer pencerelerle etkileşimi engeller

        tk.Label(secim_penceresi, text="Joker'i hangi taş yerine kullanmak istersiniz?").pack(pady=10)

        buttons_frame = tk.Frame(secim_penceresi)
        buttons_frame.pack(pady=10)

        for tas_secenek in secenekler:
            img = self.visuals.tas_resimleri.get(tas_secenek.imaj_adi)
            if img:
                b = tk.Button(buttons_frame, image=img,
                              command=lambda s=tas_secenek: self.joker_secildi(s, joker, secilen_taslar, secim_penceresi))
                b.pack(side=tk.LEFT, padx=5)

    def joker_secildi(self, secilen_deger, joker, secilen_taslar, pencere):
        """Kullanıcı joker seçimini yaptığında çağrılır."""
        pencere.destroy()
        self.oyun.el_ac_joker_ile(0, secilen_taslar, joker, secilen_deger)
        self.secili_tas_idler = []
        self.arayuzu_guncelle()
    
    def ai_oynat(self):
        if self.oyun.oyun_bitti_mi(): return
        
        oyun = self.oyun
        
        if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME and oyun.atilan_tas_degerlendirici:
            degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
            if degerlendiren_idx != 0:
                ai = oyun.oyuncular[degerlendiren_idx]
                if not oyun.atilan_taslar:
                    return
                atilan_tas = oyun.atilan_taslar[-1]
                if ai.atilan_tasi_degerlendir(oyun, atilan_tas):
                    oyun.atilan_tasi_al(degerlendiren_idx)
                else:
                    oyun.atilan_tasi_gecti()
                self.arayuzu_guncelle()
            return

        sira_index = oyun.sira_kimde_index
        if sira_index == 0:
            return

        ai = oyun.oyuncular[sira_index]
        if oyun.oyun_durumu == GameState.ILK_TUR:
             tas = ai.karar_ver_ve_at(oyun)
             if tas: oyun.tas_at(sira_index, tas.id)
             self.arayuzu_guncelle()

        elif oyun.oyun_durumu == GameState.NORMAL_TUR:
            if oyun.acilmis_oyuncular[sira_index] and ai.isleme_dene(oyun, sira_index):
                pass
            
            if not oyun.acilmis_oyuncular[sira_index]:
                ac_kombo = ai.ai_el_ac_dene(oyun, sira_index)
                if ac_kombo:
                    oyun.el_ac(sira_index, ac_kombo)
            
            if oyun.oyuncunun_tas_cekme_ihtiyaci(sira_index):
                 oyun.desteden_cek(sira_index)
            
            if len(ai.el) % 3 != 1:
                tas = ai.karar_ver_ve_at(oyun)
                if tas: oyun.tas_at(sira_index, tas.id)

            self.arayuzu_guncelle()

        elif oyun.oyun_durumu == GameState.NORMAL_TAS_ATMA:
             tas = ai.karar_ver_ve_at(oyun)
             if tas: oyun.tas_at(sira_index, tas.id)
             self.arayuzu_guncelle()

    def baslat(self):
        self.pencere.mainloop()