"""Oyun durumu ve üst bilgi yönetimi."""

import tkinter as tk

class StatusBar:
    def __init__(self, arayuz):
        self.arayuz = arayuz
        self.status_label = None

    def ekle_status_label(self, parent):
        self.status_label = tk.Label(parent, text="", font=("Arial", 14), bg="#E3FCBF")
        self.status_label.pack(pady=4)

    def guncelle(self, metin):
        if self.status_label:
            self.status_label.config(text=metin)