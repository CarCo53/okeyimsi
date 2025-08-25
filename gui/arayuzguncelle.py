# gui/arayuzguncelle.py dosyasının tam içeriği

import tkinter as tk
from state import GameState

def arayuzu_guncelle(arayuz):
    oyun = arayuz.oyun
    for i, oyuncu in enumerate(oyun.oyuncular):
        key = f"oyuncu_{i+1}"
        frame = arayuz.alanlar[key]
        frame.config(text=f"{oyuncu.isim} ({len(oyuncu.el)} taş)")
        for widget in frame.winfo_children():
            widget.destroy()
        for tas in oyuncu.el:
            img = arayuz.visuals.tas_resimleri.get(tas.imaj_adi)
            if img:
                label = tk.Label(frame, image=img, borderwidth=0)
                if tas.id in arayuz.secili_tas_idler and i == 0:
                    label.config(highlightthickness=3, highlightbackground="black")
                label.pack(side=tk.LEFT, padx=1, pady=1)
                if i == 0:
                    label.bind("<Button-1>", lambda e, t_id=tas.id: arayuz.tas_sec(t_id))

    for widget in arayuz.masa_frame.winfo_children():
        widget.destroy()

    for oyuncu_idx, per_listesi in oyun.acilan_perler.items():
        if not per_listesi: continue
        oyuncu_adi = oyun.oyuncular[oyuncu_idx].isim
        oyuncu_per_cercevesi = tk.Frame(arayuz.masa_frame)
        oyuncu_per_cercevesi.pack(anchor="w", pady=2)
        tk.Label(oyuncu_per_cercevesi, text=f"{oyuncu_adi}:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        for per_idx, per in enumerate(per_listesi):
            per_cerceve_dis = tk.Frame(oyuncu_per_cercevesi, borderwidth=1, relief="sunken", padx=2, pady=2)
            per_cerceve_dis.pack(side=tk.LEFT, padx=5)
            per_cerceve_dis.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: arayuz.per_sec(o_idx, p_idx))

            for tas in per:
                bg_renk = "#F0F0F0"
                cerceve_renk = "black"
                cerceve_kalinligi = 0
                
                if tas.joker_yerine_gecen:
                    renk = tas.joker_yerine_gecen.renk
                    
                    # DÜZELTME: Türkçe renk isimlerini İngilizce'ye çevir
                    renk_map = {
                        "kirmizi": "red",
                        "mavi": "blue",
                        "sari": "yellow",
                        "siyah": "black"
                    }
                    tk_renk = renk_map.get(renk, "black") # Bilinmeyen bir renk gelirse siyah yap

                    bg_renk_map = {
                        "red": "#ffdddd",
                        "blue": "#ddddff",
                        "yellow": "#ffffcc",
                        "black": "#d3d3d3"
                    }
                    bg_renk = bg_renk_map.get(tk_renk, "#F0F0F0")
                    cerceve_renk = tk_renk
                    cerceve_kalinligi = 2

                tas_cerceve = tk.Frame(per_cerceve_dis, bg=bg_renk)
                tas_cerceve.pack(side=tk.LEFT)
                
                img = arayuz.visuals.tas_resimleri.get(tas.imaj_adi)
                if img:
                    label = tk.Label(tas_cerceve, image=img, borderwidth=0, bg=bg_renk,
                                     highlightbackground=cerceve_renk, highlightcolor=cerceve_renk, 
                                     highlightthickness=cerceve_kalinligi)
                    label.pack(padx=1, pady=1)
                    label.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: arayuz.per_sec(o_idx, p_idx))

    for widget in arayuz.deste_frame.winfo_children():
         if widget != arayuz.deste_sayisi_label:
            widget.destroy()
    arayuz.deste_sayisi_label.config(text=f"Kalan: {len(oyun.deste.taslar)}")
    if oyun.deste.taslar:
         img_kapali = arayuz.visuals.tas_resimleri.get("kapali.png")
         if img_kapali:
             tk.Label(arayuz.deste_frame, image=img_kapali).pack()

    if oyun.atilan_tas_degerlendirici:
        atan_index = oyun.atilan_tas_degerlendirici.tasi_atan_index
        atan_oyuncu_adi = oyun.oyuncular[atan_index].isim
        arayuz.atilan_frame.config(text=f"Atan Oyuncu: {atan_oyuncu_adi}")
    else:
        arayuz.atilan_frame.config(text="Atılan Taşlar")

    for widget in arayuz.atilan_frame.winfo_children():
        widget.destroy()
    for tas in oyun.atilan_taslar:
         img = arayuz.visuals.tas_resimleri.get(tas.imaj_adi)
         if img:
             label = tk.Label(arayuz.atilan_frame, image=img)
             label.pack(side=tk.LEFT)

    arayuz.button_manager.butonlari_guncelle(oyun.oyun_durumu)

    if oyun.oyun_durumu == GameState.BITIS:
        kazanan = oyun.oyuncular[oyun.kazanan_index] if oyun.kazanan_index is not None else "Bilinmiyor"
        kazanan_isim = kazanan.isim if hasattr(kazanan, 'isim') else kazanan
        arayuz.statusbar.guncelle(f"Oyun Bitti! Kazanan: {kazanan_isim}. Yeni oyuna başlayabilirsiniz.")
    else:
        oyuncu_durum = "Açılmış" if oyun.acilmis_oyuncular[0] else f"Görev: {oyun.mevcut_gorev}"
        sira_bilgi = f"Sıra: {oyun.oyuncular[oyun.sira_kimde_index].isim}"
        if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME and oyun.atilan_tas_degerlendirici:
            degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
            degerlendiren = oyun.oyuncular[degerlendiren_idx].isim
            sira_bilgi = f"Değerlendiren: {degerlendiren}"
        elif oyun.oyun_durumu == GameState.ILK_TUR:
            sira_bilgi = f"Sıra: {oyun.oyuncular[oyun.sira_kimde_index].isim} (Taş atarak başlayın)"

        arayuz.statusbar.guncelle(f"{sira_bilgi} | {oyuncu_durum}")

    arayuz.pencere.after(500, arayuz.ai_oynat)