from itertools import combinations

def kut_mu(taslar, min_sayi=3):
    """Aynı değerde, farklı renkte en az min_sayi taş (joker dahil)."""
    if len(taslar) < min_sayi:
        return False
    degerler = set()
    renkler = set()
    for t in taslar:
        gercek_tas = t.joker_yerine_gecen if t.joker_yerine_gecen else t
        if gercek_tas.renk == "joker":
            continue
        degerler.add(gercek_tas.deger)
        renkler.add(gercek_tas.renk)
    if len(renkler) != len([t for t in taslar if (t.joker_yerine_gecen or t.renk != "joker")]):
        return False
    if len(degerler) > 1:
        return False
    return min_sayi <= len(taslar) <= 4

def seri_mu(taslar, min_sayi=3):
    """Aynı renkte, ardışık en az min_sayi taş (joker dahil)."""
    if len(taslar) < min_sayi:
        return False
    renk = None
    sayilar = []
    joker_sayisi = 0
    for t in taslar:
        gercek_tas = t.joker_yerine_gecen if t.joker_yerine_gecen else t
        if t.renk == "joker" and not t.joker_yerine_gecen:
            joker_sayisi += 1
            continue
        if renk is None:
            renk = gercek_tas.renk
        elif gercek_tas.renk != renk:
            return False
        sayilar.append(gercek_tas.deger)
    if not sayilar:
        return joker_sayisi >= min_sayi
    sayilar.sort()
    if len(set(sayilar)) != len(sayilar):
        return False
    gereken_joker = (sayilar[-1] - sayilar[0] + 1) - len(sayilar)
    return joker_sayisi >= gereken_joker

def coklu_per_dogrula(taslar, tip, min_sayi, adet):
    if len(taslar) != min_sayi * adet:
        return False
    kontrol_fonksiyonu = kut_mu if tip == "küt" else seri_mu
    for grup1_kombinasyonu in combinations(taslar, min_sayi):
        kalan_taslar = [t for t in taslar if t not in grup1_kombinasyonu]
        if kontrol_fonksiyonu(list(grup1_kombinasyonu), min_sayi) and kontrol_fonksiyonu(kalan_taslar, min_sayi):
            return True
    return False

def karma_per_dogrula(taslar, min_sayi):
    if len(taslar) != min_sayi * 2:
        return False
    for kut_kombinasyonu in combinations(taslar, min_sayi):
        seri_taslar = [t for t in taslar if t not in kut_kombinasyonu]
        if kut_mu(list(kut_kombinasyonu), min_sayi) and seri_mu(seri_taslar, min_sayi):
            return True
    for seri_kombinasyonu in combinations(taslar, min_sayi):
        kut_taslar = [t for t in taslar if t not in seri_kombinasyonu]
        if seri_mu(list(seri_kombinasyonu), min_sayi) and kut_mu(kut_taslar, min_sayi):
            return True
    return False

def cift_per_mu(taslar):
    """Bir elin 7 çiftten oluşup oluşmadığını kontrol eder."""
    if len(taslar) != 14:
        return False
    
    tas_gruplari = {}
    joker_sayisi = 0
    
    for tas in taslar:
        if tas.renk == "joker":
            joker_sayisi += 1
        else:
            # DÜZELTME: Taşları sadece değerine göre değil, (renk, değer) ikilisine göre grupla
            anahtar = (tas.renk, tas.deger)
            tas_gruplari[anahtar] = tas_gruplari.get(anahtar, 0) + 1
            
    tek_kalan_sayisi = 0
    for sayi in tas_gruplari.values():
        if sayi % 2 != 0:
            tek_kalan_sayisi += 1
            
    # Tek kalan taşlar jokerlerle eşleşebiliyorsa el geçerlidir.
    return joker_sayisi >= tek_kalan_sayisi