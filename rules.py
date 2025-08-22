"""Oyun görevleri ve per kontrol kuralları."""

class Rules:
    GOREVLER = [
        "Küt 3", "Seri 3", "2x Küt 3", "2x Seri 3", "Küt 3 + Seri 3",
        "Küt 4", "Seri 4", "2x Küt 4", "2x Seri 4", "Küt 4 + Seri 4",
        "Seri 5", "Çift"
    ]

    @staticmethod
    def per_dogrula(taslar, gorev):
        """
        Verilen taşlar ve göreve göre açma kontrolü.
        İlk açma için görev kontrolü yapar.
        """
        if gorev == "Küt 3":
            return Rules.kut_mu(taslar, 3)
        elif gorev == "Seri 3":
            return Rules.seri_mu(taslar, 3)
        elif gorev == "2x Küt 3":
            return Rules.coklu_per_dogrula(taslar, "küt", 3, 2)
        elif gorev == "2x Seri 3":
            return Rules.coklu_per_dogrula(taslar, "seri", 3, 2)
        elif gorev == "Küt 3 + Seri 3":
            return Rules.karma_per_dogrula(taslar, 3)
        elif gorev == "Küt 4":
            return Rules.kut_mu(taslar, 4)
        elif gorev == "Seri 4":
            return Rules.seri_mu(taslar, 4)
        elif gorev == "2x Küt 4":
            return Rules.coklu_per_dogrula(taslar, "küt", 4, 2)
        elif gorev == "2x Seri 4":
            return Rules.coklu_per_dogrula(taslar, "seri", 4, 2)
        elif gorev == "Küt 4 + Seri 4":
            return Rules.karma_per_dogrula(taslar, 4)
        elif gorev == "Seri 5":
            return Rules.seri_mu(taslar, 5)
        elif gorev == "Çift":
            return Rules.cift_per_mu(taslar)
        return False

    @staticmethod
    def genel_per_dogrula(taslar):
        """
        Oyuncu açtıktan sonra istediği per'i açabilir.
        Geçerli küt/seri kontrolü yapar.
        """
        return Rules.kut_mu(taslar, 3) or Rules.seri_mu(taslar, 3)

    @staticmethod
    def kut_mu(taslar, min_sayi=3):
        """Aynı değerde, farklı renkte en az min_sayi taş (joker dahil)."""
        if len(taslar) < min_sayi:
            return False
            
        degerler = set()
        renkler = set()
        joker_sayisi = 0
        
        for t in taslar:
            if t.renk == "joker":
                joker_sayisi += 1
            else:
                degerler.add(t.deger)
                renkler.add(t.renk)
        
        # Aynı renk taş varsa küt değil
        if len(renkler) != len([t for t in taslar if t.renk != "joker"]):
            return False
            
        # Farklı değer varsa küt değil (joker hariç)
        if len(degerler) > 1:
            return False
            
        # En az min_sayi taş ve maksimum 4 taş olmalı (4 renk var)
        return min_sayi <= len(taslar) <= 4

    @staticmethod
    def seri_mu(taslar, min_sayi=3):
        """Aynı renkte, ardışık en az min_sayi taş (joker dahil)."""
        if len(taslar) < min_sayi:
            return False
            
        renk = None
        sayilar = []
        joker_sayisi = 0
        
        for t in taslar:
            if t.renk == "joker":
                joker_sayisi += 1
            else:
                if renk is None:
                    renk = t.renk
                elif t.renk != renk:
                    return False  # Farklı renk var
                sayilar.append(t.deger)
        
        if len(sayilar) == 0:  # Sadece joker varsa
            return joker_sayisi >= min_sayi
            
        sayilar.sort()
        
        # Aynı sayı tekrar ediyorsa seri değil
        if len(set(sayilar)) != len(sayilar):
            return False
            
        # Ardışık kontrol et
        for i in range(1, len(sayilar)):
            fark = sayilar[i] - sayilar[i-1]
            if fark > 1:
                # Boşluk var, jokerle doldurabiliyor muyuz?
                gereken_joker = fark - 1
                if gereken_joker > joker_sayisi:
                    return False
                joker_sayisi -= gereken_joker
            elif fark == 0:
                return False  # Aynı sayı tekrar ediyor
                
        return True

    @staticmethod
    def coklu_per_dogrula(taslar, tip, min_sayi, adet):
        """
        Birden fazla per kontrolü (örn: 2x Küt 3)
        """
        if len(taslar) < min_sayi * adet:
            return False
            
        # Taşları gruplara ayırmaya çalış
        # Basit algoritma: tüm kombinasyonları dene
        return Rules._gruplara_ayir_ve_kontrol_et(taslar, tip, min_sayi, adet)

    @staticmethod
    def karma_per_dogrula(taslar, min_sayi):
        """
        Karma per kontrolü (örn: Küt 3 + Seri 3)
        """
        if len(taslar) < min_sayi * 2:
            return False
            
        # Bir grubu küt, diğerini seri yapmaya çalış
        for i in range(min_sayi, len(taslar) - min_sayi + 1):
            # İlk i taşı küt olarak dene
            kut_taslar = taslar[:i]
            seri_taslar = taslar[i:]
            
            if Rules.kut_mu(kut_taslar, min_sayi) and Rules.seri_mu(seri_taslar, min_sayi):
                return True
                
            # İlk i taşı seri olarak dene
            if Rules.seri_mu(kut_taslar, min_sayi) and Rules.kut_mu(seri_taslar, min_sayi):
                return True
                
        return False

    @staticmethod
    def cift_per_mu(taslar):
        """
        Çift per kontrolü - 7 adet çift (14 taş)
        """
        if len(taslar) != 14:
            return False
            
        # Taşları değere göre grupla
        deger_gruplari = {}
        joker_sayisi = 0
        
        for tas in taslar:
            if tas.renk == "joker":
                joker_sayisi += 1
            else:
                if tas.deger not in deger_gruplari:
                    deger_gruplari[tas.deger] = 0
                deger_gruplari[tas.deger] += 1
        
        cift_sayisi = 0
        for deger, sayi in deger_gruplari.items():
            cift_sayisi += sayi // 2
            
        # Jokerlerle eksik çiftleri tamamla
        gereken_cift = 7
        eksik_cift = max(0, gereken_cift - cift_sayisi)
        
        return joker_sayisi >= eksik_cift * 2

    @staticmethod
    def _gruplara_ayir_ve_kontrol_et(taslar, tip, min_sayi, adet):
        """
        Taşları gruplara ayırıp kontrol eden yardımcı fonksiyon
        Basit implementasyon - geliştirilmesi gerekebilir
        """
        if len(taslar) < min_sayi * adet:
            return False
            
        # Şimdilik basit kontrol: toplam taş sayısı yeterli mi?
        # Gerçek implementasyon için daha karmaşık algoritma gerekli
        return len(taslar) >= min_sayi * adet

    @staticmethod
    def islem_dogrula(per, tas):
        """Bir per'e taş işlenebilir mi kontrolü."""
        if not per or not tas:
            return False
            
        # Per'in tipini belirle (küt mü seri mi)
        if Rules._per_kut_mu(per):
            return Rules._kut_islem_dogrula(per, tas)
        elif Rules._per_seri_mu(per):
            return Rules._seri_islem_dogrula(per, tas)
            
        return False

    @staticmethod
    def _per_kut_mu(per):
        """Per'in küt olup olmadığını kontrol eder"""
        if len(per) < 2:
            return False
            
        degerler = set()
        for tas in per:
            if tas.renk != "joker":
                degerler.add(tas.deger)
                
        return len(degerler) <= 1

    @staticmethod
    def _per_seri_mu(per):
        """Per'in seri olup olmadığını kontrol eder"""
        if len(per) < 2:
            return False
            
        renkler = set()
        for tas in per:
            if tas.renk != "joker":
                renkler.add(tas.renk)
                
        return len(renkler) <= 1

    @staticmethod
    def _kut_islem_dogrula(per, tas):
        """Küt per'e taş işleme kontrolü"""
        if len(per) >= 4:  # Maksimum 4 taş (4 renk)
            return False
            
        # Aynı değerde olmalı
        deger = None
        for p_tas in per:
            if p_tas.renk != "joker":
                deger = p_tas.deger
                break
                
        return tas.renk == "joker" or tas.deger == deger

    @staticmethod
    def _seri_islem_dogrula(per, tas):
        """Seri per'e taş işleme kontrolü"""
        # Aynı renkte olmalı
        renk = None
        sayilar = []
        
        for p_tas in per:
            if p_tas.renk != "joker":
                renk = p_tas.renk
                sayilar.append(p_tas.deger)
                
        if tas.renk != "joker" and renk and tas.renk != renk:
            return False
            
        # Seri başına veya sonuna eklenebilir mi kontrol et
        if tas.renk != "joker" and sayilar:
            sayilar.sort()
            return tas.deger == sayilar[0] - 1 or tas.deger == sayilar[-1] + 1
            
        return True  # Joker her zaman eklenebilir

    @staticmethod
    def joker_mi(tas):
        """Taş joker mi (fake okey)?"""
        return tas.renk == "joker"