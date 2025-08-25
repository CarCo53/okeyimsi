# ai/coklu_per_stratejisi.py

from itertools import combinations
from rules_manager import Rules
from collections import defaultdict

def en_iyi_coklu_per_bul(el, gorev):
    """
    Eldeki taşlarla, "2x Küt 4" veya "Küt 3 + Seri 3" gibi çoklu per
    gerektiren görevleri tamamlayan kombinasyonları bulur.
    """
    # Önce eldeki tüm olası tekil perleri bir havuzda topla
    tum_tekil_perler = []
    for combo_size in range(3, 6): # 3, 4 ve 5'li olası perleri ara
        for combo in combinations(el, combo_size):
            per = list(combo)
            if Rules.genel_per_dogrula(per):
                tum_tekil_perler.append(per)
    
    if not tum_tekil_perler:
        return None

    tum_tekil_perler.sort(key=len, reverse=True)

    # Bu per havuzundan, görevi tamamlayan ve kesişmeyen iki per bul
    for i in range(len(tum_tekil_perler)):
        for j in range(i + 1, len(tum_tekil_perler)):
            per1 = tum_tekil_perler[i]
            per2 = tum_tekil_perler[j]
            
            # İki per'in taşları birbirinden tamamen farklı olmalı
            if set(p.id for p in per1).isdisjoint(set(p.id for p in per2)):
                toplam_per = per1 + per2
                if Rules.per_dogrula(toplam_per, gorev):
                    return toplam_per # Görevi tamamlayan ilk kombinasyonu döndür
    
    return None