# ai/cift_stratejisi.py

from collections import defaultdict
from rules.per_validators import cift_per_mu

def en_iyi_ciftleri_bul(el, gorev):
    """
    "Çift" görevi için eldeki en iyi çift kombinasyonunu bulur.
    En az 4 çift varsa, bu çiftleri içeren bir per döndürür.
    """
    if gorev != "Çift":
        return None

    # Çiftleri ve tekleri bul
    ciftler, _ = _ciftleri_ve_tekleri_bul(el)
    
    # cift_per_mu kuralı en az 8 taş (4 çift) gerektirir.
    # Elimizdeki tüm çiftleri birleştirerek bu kuralı test edelim.
    tum_cift_taslari = [tas for cift in ciftler for tas in cift]
    
    # Jokerleri de hesaba katmak için cift_per_mu'yu kullanalım
    if cift_per_mu(el):
        # Eğer el açmaya uygunsa, tüm eli döndür, çünkü çift açarken
        # tüm çiftler aynı anda açılmalıdır.
        return el
        
    return None

def atilacak_en_kotu_tas(el):
    """
    "Çift" görevi sırasında atılacak en işe yaramaz taşı bulur.
    Öncelik her zaman tek kalan taşlardır.
    """
    _, tekler = _ciftleri_ve_tekleri_bul(el)
    
    if tekler:
        # Tek kalan taşlar arasından en yüksek değerli olanı atmak genellikle iyi bir stratejidir.
        return max(tekler, key=lambda tas: tas.deger if tas.deger else 0)
    else:
        # Eğer hiç tek taş kalmadıysa (tüm el çiftlerden oluşuyorsa),
        # en yüksek değerli çiftten birini boz.
        tum_taslar = sorted([t for t in el if t.renk != 'joker'], key=lambda t: t.deger, reverse=True)
        if tum_taslar:
            return tum_taslar[0]
    
    # Sadece joker kaldıysa
    return el[0] if el else None


def _ciftleri_ve_tekleri_bul(el):
    """Eldeki taşları çiftler ve tekler olarak ayıran yardımcı fonksiyon."""
    tas_gruplari = defaultdict(list)
    jokerler = []
    for tas in el:
        if tas.renk == 'joker':
            jokerler.append(tas)
        else:
            anahtar = (tas.renk, tas.deger)
            tas_gruplari[anahtar].append(tas)
    
    ciftler = []
    tekler = []

    for _, tas_listesi in tas_gruplari.items():
        if len(tas_listesi) % 2 == 0:
            ciftler.extend([tas_listesi[i:i+2] for i in range(0, len(tas_listesi), 2)])
        else:
            ciftler.extend([tas_listesi[i:i+2] for i in range(0, len(tas_listesi)-1, 2)])
            tekler.append(tas_listesi[-1])

    # Jokerleri tek kalan taşlarla eşleştir
    while jokerler and tekler:
        cift = [tekler.pop(0), jokerler.pop(0)]
        ciftler.append(cift)
        
    # Kalan jokerler tek sayılır (çünkü eşleri yok)
    tekler.extend(jokerler)
    
    return ciftler, tekler