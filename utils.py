"""Yardımcı fonksiyonlar."""

import random

def benzersiz_id_uret():
    """Benzersiz bir ID üretir (taşlar için)."""
    return random.randint(100000, 999999)