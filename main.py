import sys
import random

from PySide6 import QtWidgets
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QMainWindow

from UI.ui_main import Ui_MainWindow
from UI.ui_play import Ui_PlayWindow
from UI.ui_build import Ui_BuildWindow
import cards
import player


mwindow, bwindow, pwindow = None, None, None


def create_full_deck() -> cards.Deck:
    dck = []
    for j in cards.Suit:
        for k in cards.CardNum:
            dck.append(cards.Card(j, k))
    return cards.Deck(dck)


def build_deck(plyr) -> player.Player:
    plyr.deck = create_full_deck()
    return plyr


def start_game():
    player1 = build_deck(player.Player)
    player2 = build_deck(player.Player)

    return player1, player2


def discard(plyr, card):
    plyr.hand.discard(card)


def move(plyr, card, lane):
    plyr.move(card, lane)


def tick(player1, player2, turn):
    return


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    @Slot()
    def exit(self):
        sys.exit()

    @Slot()
    def play_game(self):
        mwindow.hide()
        pwindow.show()
        pwindow.setFocus(Qt.FocusReason.MouseFocusReason)
        print("Play")

    @Slot()
    def build_deck(self):
        mwindow.hide()
        bwindow.show()
        bwindow.setFocus(Qt.FocusReason.MouseFocusReason)
        print("Build Deck")


class PlayWindow(QMainWindow):
    def __init__(self):
        super(PlayWindow, self).__init__()
        self.ui = Ui_PlayWindow()
        self.ui.setupUi(self)


class BuildWindow(QMainWindow):
    def __init__(self):
        super(BuildWindow, self).__init__()
        self.ui = Ui_BuildWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mwindow = MainWindow()
    bwindow = BuildWindow()
    pwindow = PlayWindow()

    mwindow.show()

    app.exec()
