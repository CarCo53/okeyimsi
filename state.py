"""Oyun state sabitleri ve atılan taş değerlendirme yardımcıları."""

class GameState:
    ILK_TUR = "ILK_TUR"  # YENİ: Oyunun ilk hamlesi için özel durum
    NORMAL_TUR = "NORMAL_TUR"
    ATILAN_TAS_DEGERLENDIRME = "ATILAN_TAS_DEGERLENDIRME"
    NORMAL_TAS_ATMA = "NORMAL_TAS_ATMA"
    BITIS = "BITIS"

class AtilanTasDegerlendirici:
    """Atılan taş değerlendirme aşamasının akışını yönetir."""
    def __init__(self, tasi_atan_index, oyuncu_sayisi=4):
        self.tasi_atan_index = tasi_atan_index
        self.oyuncu_sayisi = oyuncu_sayisi
        self.degerlendiren_index = (tasi_atan_index + 1) % oyuncu_sayisi
        self.gecenler = []
        self.alan_index = None
        self.cezali_alan_index = None

    def siradaki(self):
        """Şu anda değerlendiren oyuncunun indexi."""
        return self.degerlendiren_index

    def bir_sonraki(self):
        """Değerlendiren oyuncuyu sıradakine geçirir."""
        self.degerlendiren_index = (self.degerlendiren_index + 1) % self.oyuncu_sayisi

    def asilin_sirasi(self):
        """Atan taşın sağındaki, yani sırası gelen oyuncunun indexi."""
        return (self.tasi_atan_index + 1) % self.oyuncu_sayisi

    def herkes_gecti_mi(self):
        """Değerlendiren tekrar taş atan olduysa, herkes geçti demektir."""
        return self.degerlendiren_index == self.tasi_atan_index

    def gecen_ekle(self, index):
        self.gecenler.append(index)