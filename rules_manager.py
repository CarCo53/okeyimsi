from rules.gorevler import GOREV_LISTESI
from rules.per_validators import kut_mu, seri_mu, coklu_per_dogrula, karma_per_dogrula, cift_per_mu
from tile import Tile
from itertools import combinations, permutations

class Rules:
    GOREVLER = GOREV_LISTESI

    @staticmethod
    def per_dogrula(taslar, gorev):
        # ... (Bu fonksiyonun geri kalanı aynı)
        if gorev == "Küt 3": return kut_mu(taslar, 3)
        elif gorev == "Seri 3": return seri_mu(taslar, 3)
        elif gorev == "2x Küt 3": return coklu_per_dogrula(taslar, "küt", 3, 2)
        elif gorev == "2x Seri 3": return coklu_per_dogrula(taslar, "seri", 3, 2)
        elif gorev == "Küt 3 + Seri 3": return karma_per_dogrula(taslar, 3)
        elif gorev == "Küt 4": return kut_mu(taslar, 4)
        elif gorev == "Seri 4": return seri_mu(taslar, 4)
        elif gorev == "2x Küt 4": return coklu_per_dogrula(taslar, "küt", 4, 2)
        elif gorev == "2x Seri 4": return coklu_per_dogrula(taslar, "seri", 4, 2)
        elif gorev == "Küt 4 + Seri 4": return karma_per_dogrula(taslar, 4)
        elif gorev == "Seri 5": return seri_mu(taslar, 5)
        elif gorev == "Çift": return cift_per_mu(taslar)
        return False

    @staticmethod
    def genel_per_dogrula(taslar):
        return kut_mu(taslar, 3) or seri_mu(taslar, 3)

    @staticmethod
    def islem_dogrula(per, tas):
        if not per or not tas: return False
        
        # Okey'i geri alma kuralı
        for p_tas in per:
            if p_tas.renk == "joker" and p_tas.joker_yerine_gecen:
                yerine_gecen = p_tas.joker_yerine_gecen
                if yerine_gecen.renk == tas.renk and yerine_gecen.deger == tas.deger:
                    return True

        if Rules._per_kut_mu(per): return Rules._kut_islem_dogrula(per, tas)
        elif Rules._per_seri_mu(per): return Rules._seri_islem_dogrula(per, tas)
        return False

    @staticmethod
    def _per_kut_mu(per):
        degerler = set()
        joker_degeri_atanmis_mi = False
        for tas in per:
            if tas.joker_yerine_gecen:
                degerler.add(tas.joker_yerine_gecen.deger)
                joker_degeri_atanmis_mi = True
            elif tas.renk != "joker":
                degerler.add(tas.deger)
        # Eğer per sadece jokerlerden oluşuyorsa veya atanmış bir joker varsa, bunu küt say
        if joker_degeri_atanmis_mi and len(degerler) <= 1:
            return True
        return len(degerler) <= 1

    @staticmethod
    def _per_seri_mu(per):
        renkler = set()
        joker_rengi_atanmis_mi = False
        for tas in per:
            if tas.joker_yerine_gecen:
                renkler.add(tas.joker_yerine_gecen.renk)
                joker_rengi_atanmis_mi = True
            elif tas.renk != "joker":
                renkler.add(tas.renk)
        if joker_rengi_atanmis_mi and len(renkler) <= 1:
            return True
        return len(renkler) <= 1
        
    @staticmethod
    def _kut_islem_dogrula(per, tas):
        if len(per) >= 4: return False
        deger = None
        renkler = set()
        for p_tas in per:
            gercek_tas = p_tas.joker_yerine_gecen or p_tas
            if gercek_tas.renk != "joker":
                deger = gercek_tas.deger
                renkler.add(gercek_tas.renk)
        if tas.renk == "joker": return True
        return tas.deger == deger and tas.renk not in renkler

    @staticmethod
    def _seri_islem_dogrula(per, tas):
        renk = None
        sayilar = []
        for p_tas in per:
            gercek_tas = p_tas.joker_yerine_gecen or p_tas
            if gercek_tas.renk != "joker":
                renk = gercek_tas.renk
                sayilar.append(gercek_tas.deger)
        if tas.renk == "joker": return True
        if renk and tas.renk != renk: return False
        if sayilar:
            sayilar.sort()
            return tas.deger == sayilar[0] - 1 or tas.deger == sayilar[-1] + 1
        return True

    @staticmethod
    def joker_icin_olasi_taslar(taslar):
        jokerler = [t for t in taslar if t.renk == 'joker']
        diger_taslar = [t for t in taslar if t.renk != 'joker']
        if not jokerler: return {}

        # Küt (aynı sayılı) per kontrolü
        degerler = {t.deger for t in diger_taslar}
        if len(degerler) == 1:
            deger = degerler.pop()
            mevcut_renkler = {t.renk for t in diger_taslar}
            tum_renkler = {"sari", "mavi", "siyah", "kirmizi"}
            eksik_renkler = list(tum_renkler - mevcut_renkler)
            
            if len(jokerler) <= len(eksik_renkler):
                # DÜZELTME: Birden fazla joker için tüm permütasyonları bul
                olasi_kombinasyonlar = list(combinations(eksik_renkler, len(jokerler)))
                if olasi_kombinasyonlar:
                    # Şimdilik ilk olasılığı alıyoruz, GUI'de bu genişletilebilir
                    secenekler = [Tile(renk, deger, f"{renk}_{deger}.png", -1) for renk in olasi_kombinasyonlar[0]]
                    return {joker: [secenek] for joker, secenek in zip(jokerler, secenekler)}

        # Seri (sıralı) per kontrolü
        renkler = {t.renk for t in diger_taslar}
        if len(renkler) == 1:
            renk = renkler.pop()
            sayilar = sorted([t.deger for t in diger_taslar])
            if sayilar:
                # Olası eksik sayıları bul
                eksik_sayilar = []
                for i in range(sayilar[0], sayilar[-1]):
                    if i not in sayilar:
                        eksik_sayilar.append(i)
                
                if len(jokerler) == len(eksik_sayilar):
                    secenekler = [Tile(renk, sayi, f"{renk}_{sayi}.png", -1) for sayi in eksik_sayilar]
                    return {jokerler[0]: secenekler}

        return None