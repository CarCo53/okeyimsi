import sys
import os

# Projenin ana klasörünü Python'un modül arama yoluna ekle
# Bu satır, tüm "import" hatalarını çözecektir
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from game import Game
from gui.gui import Arayuz

if __name__ == "__main__":
    oyun = Game()
    oyun.baslat()
    gui = Arayuz(oyun)
    gui.baslat()