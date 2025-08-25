# ai/klasik_per_stratejisi.py

from itertools import combinations
from rules_manager import Rules

def en_iyi_per_bul(el, gorev):
    """
    Eldeki taşlarla, tek bir perden oluşan görevi tamamlayan
    en iyi (en çok taşlı) kombinasyonu bulur.
    """
    bulunan_perler = []
    # Eldeki tüm olası kombinasyonları göreve göre test et
    for combo_size in range(3, len(el) + 1):
        for combo in combinations(el, combo_size):
            per = list(combo)
            if Rules.per_dogrula(per, gorev):
                bulunan_perler.append(per)
    
    if not bulunan_perler:
        return None
    
    # Bulunan geçerli perler arasından en uzun olanı seç
    return max(bulunan_perler, key=len)