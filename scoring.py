"""El sonu puanlama fonksiyonları."""

def puan_hesapla(oyuncular):
    """
    Her oyuncunun elinde kalan taşların sayısına göre puan hesaplar.
    Kazanan 0, diğerleri toplam taş değeri kadar puan alır.
    """
    puanlar = []
    for oyuncu in oyuncular:
        toplam = sum(tas.deger if tas.deger else 0 for tas in oyuncu.el)
        puanlar.append(toplam)
    return puanlar