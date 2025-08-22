from game import Game
from gui.gui import Arayuz

if __name__ == "__main__":
    oyun = Game()
    oyun.baslat()
    gui = Arayuz(oyun)
    gui.baslat()