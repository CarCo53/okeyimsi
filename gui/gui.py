import tkinter as tk
from gui.visuals import Visuals
from gui.buttons import ButtonManager
from gui.status import StatusBar
from state import GameState

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
        for i, oyuncu in enumerate(self.oyun.oyuncular):
            key = f"oyuncu_{i+1}"
            frame = self.alanlar[key]
            frame.config(text=f"{oyuncu.isim} ({len(oyuncu.el)} taş)")
            for widget in frame.winfo_children():
                widget.destroy()
            for tas in oyuncu.el:
                img = self.visuals.tas_resimleri.get(tas.imaj_adi)
                if img:
                    border = "yellow" if tas.id in self.secili_tas_idler and i == 0 else "#F7F5F2"
                    label = tk.Label(frame, image=img, bg=border)
                    label.pack(side=tk.LEFT, padx=1, pady=1)
                    if i == 0:
                        label.bind("<Button-1>", lambda e, t_id=tas.id: self.tas_sec(t_id))
        
        for widget in self.masa_frame.winfo_children():
            widget.destroy()
        
        for oyuncu_idx, per_listesi in self.oyun.acilan_perler.items():
            if not per_listesi: continue
            oyuncu_adi = self.oyun.oyuncular[oyuncu_idx].isim
            oyuncu_per_cercevesi = tk.Frame(self.masa_frame)
            oyuncu_per_cercevesi.pack(anchor="w", pady=2)
            tk.Label(oyuncu_per_cercevesi, text=f"{oyuncu_adi}:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

            for per_idx, per in enumerate(per_listesi):
                per_cerceve_dis = tk.Frame(oyuncu_per_cercevesi)
                per_cerceve_dis.pack(side=tk.LEFT, padx=5)
                for tas in per:
                    cerceve_renk = "#F0F0F0"
                    padding = 0
                    if tas.joker_yerine_gecen:
                        cerceve_renk = tas.joker_yerine_gecen.renk
                        padding = 5
                    
                    tas_cerceve = tk.Frame(per_cerceve_dis, bg=cerceve_renk, padx=padding, pady=padding)
                    tas_cerceve.pack(side=tk.LEFT)

                    img = self.visuals.tas_resimleri.get(tas.imaj_adi)
                    if img:
                        label = tk.Label(tas_cerceve, image=img, borderwidth=0)
                        label.pack()
                        label.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: self.per_sec(o_idx, p_idx))

        for widget in self.deste_frame.winfo_children():
             if widget != self.deste_sayisi_label:
                widget.destroy()
        self.deste_sayisi_label.config(text=f"Kalan: {len(self.oyun.deste.taslar)}")
        if self.oyun.deste.taslar:
             img_kapali = self.visuals.tas_resimleri.get("kapali.png")
             if img_kapali:
                 tk.Label(self.deste_frame, image=img_kapali).pack()

        for widget in self.atilan_frame.winfo_children():
            widget.destroy()
        for tas in self.oyun.atilan_taslar:
             img = self.visuals.tas_resimleri.get(tas.imaj_adi)
             if img:
                 label = tk.Label(self.atilan_frame, image=img)
                 label.pack(side=tk.LEFT)

        self.button_manager.butonlari_guncelle(self.oyun.oyun_durumu)
        
        if self.oyun.oyun_durumu == GameState.BITIS:
            kazanan = self.oyun.oyuncular[self.oyun.kazanan_index]
            self.statusbar.guncelle(f"Oyun Bitti! Kazanan: {kazanan.isim}. Yeni oyuna başlayabilirsiniz.")
        else:
            oyuncu_durum = "Açılmış" if self.oyun.acilmis_oyuncular[0] else f"Görev: {self.oyun.mevcut_gorev}"
            sira_bilgi = f"Sıra: {self.oyun.oyuncular[self.oyun.sira_kimde_index].isim}"
            if self.oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
                degerlendiren = self.oyun.oyuncular[self.oyun.atilan_tas_degerlendirici.siradaki()].isim
                sira_bilgi = f"Değerlendiren: {degerlendiren}"
            elif self.oyun.oyun_durumu == GameState.ILK_TUR:
                sira_bilgi = f"Sıra: {self.oyun.oyuncular[self.oyun.sira_kimde_index].isim} (Taş atarak başlayın)"

            self.statusbar.guncelle(f"{sira_bilgi} | {oyuncu_durum}")
        
        self.pencere.after(500, self.ai_oynat)

    def tas_sec(self, tas_id):
        if tas_id in self.secili_tas_idler:
            self.secili_tas_idler.remove(tas_id)
        else:
            if len(self.secili_tas_idler) >= 1 and self.oyun.acilmis_oyuncular[0]:
                 self.secili_tas_idler = [tas_id]
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
    
    def ai_oynat(self):
        if self.oyun.oyun_bitti_mi(): return
        
        oyun = self.oyun
        sira_index = oyun.sira_kimde_index
        
        if sira_index == 0: return

        if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME and oyun.atilan_tas_degerlendirici:
            degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
            if degerlendiren_idx != 0:
                ai = oyun.oyuncular[degerlendiren_idx]
                atilan_tas = oyun.atilan_taslar[-1]
                if ai.atilan_tasi_degerlendir(oyun, atilan_tas):
                    oyun.atilan_tasi_al(degerlendiren_idx)
                else:
                    oyun.atilan_tasi_gecti()
                self.arayuzu_guncelle()
                return

        ai = oyun.oyuncular[sira_index]
        if oyun.oyun_durumu == GameState.ILK_TUR:
             tas = ai.karar_ver_ve_at()
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
            self.arayuzu_guncelle()

        elif oyun.oyun_durumu == GameState.NORMAL_TAS_ATMA:
             tas = ai.karar_ver_ve_at()
             if tas: oyun.tas_at(sira_index, tas.id)
             self.arayuzu_guncelle()

    def baslat(self):
        self.pencere.mainloop()