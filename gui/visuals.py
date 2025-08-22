"""Taş ve arayüz görsellerinin yüklenmesi ve cache edilmesi."""

import os
from PIL import Image, ImageTk

class Visuals:
    def __init__(self):
        self.tas_resimleri = {}

    def yukle(self, images_path="images", boyut=(40, 60)):
        """
        images_path dizinindeki tüm taş imajlarını yükler ve cache'ler.
        """
        for dosya in os.listdir(images_path):
            if dosya.endswith(".png"):
                tam_yol = os.path.join(images_path, dosya)
                try:
                    img = Image.open(tam_yol)
                    img = img.resize(boyut, Image.Resampling.LANCZOS)  # Güncel Pillow için düzeltildi
                    self.tas_resimleri[dosya] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Görsel yüklenemedi: {tam_yol} ({e})")