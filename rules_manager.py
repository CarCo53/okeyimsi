from rules.gorevler import GOREV_LISTESI
from rules.per_validators import kut_mu, seri_mu, coklu_per_dogrula, karma_per_dogrula, cift_per_mu
from tile import Tile
from itertools import combinations

class Rules:
    GOREVLER = GOREV_LISTESI

    @staticmethod
    def per_dogrula(taslar, gorev):
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
        if Rules._per_kut_mu(per): return Rules._kut_islem_dogrula(per, tas)
        elif Rules._per_seri_mu(per): return Rules._seri_islem_dogrula(per, tas)
        return False

    @staticmethod
    def _per_kut_mu(per):
        if len(per) < 2: return False
        degerler = set()
        for tas in per:
            if tas.renk != "joker": degerler.add(tas.deger)
        return len(degerler) <= 1

    @staticmethod
    def _per_seri_mu(per):
        if len(per) < 2: return False
        renkler = set()
        for tas in per:
            if tas.renk != "joker": renkler.add(tas.renk)
        return len(renkler) <= 1

    @staticmethod
    def _kut_islem_dogrula(per, tas):
        if len(per) >= 4: return False
        deger = None
        renkler = set()
        for p_tas in per:
            if p_tas.renk != "joker":
                deger = p_tas.deger
                renkler.add(p_tas.renk)
        if tas.renk == "joker": return True
        return tas.deger == deger and tas.renk not in renkler

    @staticmethod
    def _seri_islem_dogrula(per, tas):
        renk = None
        sayilar = []
        for p_tas in per:
            if p_tas.renk != "joker":
                renk = p_tas.renk
                sayilar.append(p_tas.deger)
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
        degerler = {t.deger for t in diger_taslar}
        if len(degerler) <= 1:
            deger = degerler.pop() if degerler else None
            mevcut_renkler = {t.renk for t in diger_taslar}
            tum_renkler = {"sari", "mavi", "siyah", "kirmizi"}
            eksik_renkler = list(tum_renkler - mevcut_renkler)
            if deger and len(jokerler) <= len(eksik_renkler):
                secenekler = [Tile(renk, deger, "", -1) for renk in eksik_renkler]
                return {jokerler[0]: secenekler}
        renkler = {t.renk for t in diger_taslar}
        if len(renkler) <= 1:
            renk = renkler.pop() if renkler else None
            sayilar = sorted([t.deger for t in diger_taslar])
            if renk and sayilar:
                for i in range(len(sayilar) - 1):
                    if sayilar[i+1] - sayilar[i] == 2 and len(jokerler) == 1:
                        eksik_deger = sayilar[i] + 1
                        return {jokerler[0]: [Tile(renk, eksik_deger, "", -1)]}
        return None