import socket
import sys
import time
import json
import threading

from PySide6 import QtWidgets
from PySide6.QtCore import QEvent, Slot, Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QCursor, QCloseEvent

from UI.ui_main import Ui_MainWindow
from UI.ui_play import Ui_PlayWindow
from UI.ui_build import Ui_BuildWindow
from UI.extended_ui import MyOpenGLWidget

from player import Player
from encodejson import MyEncoder
import cards

mwindow, bwindow, pwindow = None, None, None

#Populate full deck with standard numbers and suits
def create_full_deck() -> cards.Deck:
    dck = []
    for j in cards.Suit:
        for k in cards.CardNum:
            dck.append(cards.Card(j, k))
    return cards.Deck(dck)

def build_deck() -> Player:
    return create_full_deck()

def start_game():
    player1 = Player(build_deck(), "P1", 1, True)
    player2 = Player(build_deck(), "P2", 2, False)
    player2.flipSides()

    pwindow.findChild(MyOpenGLWidget, "playspaceWidget").updatePlayers(player1, player2)
    return player1, player2

def start_ai_game():
    player1 = Player(build_deck(), "P1", 1, False)
    player2 = Player(build_deck(), "P2", 2, False)
    player2.flipSides()

    pwindow.findChild(MyOpenGLWidget, "playspaceWidget").updatePlayers(player1, player2)
    return player1, player2

def discard(plyr: Player, card: cards.Card):
    plyr.hand.discard(card)

def move(plyr: Player, card: cards.Card, lane):
    plyr.move(card, lane)

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
        pwindow.setWindowState(Qt.WindowState.WindowMaximized)
        pwindow.playGame(False)
        print("Play")
    
    @Slot()
    def play_ai_game(self):
        mwindow.hide()
        pwindow.show()
        pwindow.setFocus(Qt.FocusReason.MouseFocusReason)
        pwindow.setWindowState(Qt.WindowState.WindowMaximized)
        pwindow.playGame(True)
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

        self.playerturn = None
        self.player1, self.player2, self.winner = None, None, None
        self.server = None
        self.stop = True

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.stop = True
        self.server.close()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            pwindow.findChild(MyOpenGLWidget, "playspaceWidget").adjustUIScale()
            pwindow.findChild(MyOpenGLWidget, "playspaceWidget").update()
    
    def playGame(self, ai: bool):
        self.winner = None

        self.runServer()

        if ai:
            self.player1, self.player2 = start_ai_game()
            self.playerturn = self.player1
            #self.playAITurn(self.player1)
        else:
            self.player1, self.player2 = start_game()
            self.playerturn = self.player1
    
    def nextTurn(self):
        pwindow.findChild(MyOpenGLWidget, "playspaceWidget").update()

        if self.gameWon() is not None:
            print("Winner " + self.gameWon().name)
            for p in [self.player1, self.player2]: self.writeAIGamestate(p)
            QMessageBox(text="Winner " + self.gameWon().name, parent=pwindow.findChild(MyOpenGLWidget, "centralwidget")).exec()
            pwindow.hide()

            self.stop = True
            self.server.close()
            
            mwindow.show()
            return
        elif self.playerturn.id == self.player1.id:
            if not self.player2.human:
                if self.playAITurn(self.player2):
                    self.playerturn = self.player2
            else:
                self.playerturn = self.player2
        else:
            if not self.player1.human:
                if self.playAITurn(self.player1):
                    self.playerturn = self.player1
            else:
                self.playerturn = self.player1

    def getTurn(self):
        return self.playerturn

    def playAITurn(self, p: Player) -> bool:
        if p.clientsocket == None: return False
        
        p.clientsocket.send(self.writeAIGamestate(p).encode("utf-8"))
        request = p.clientsocket.recv(1024).decode("utf-8")
        
        #self.useDefaultAI(p)
        
        return True

    def useDefaultAI(self, p: Player) -> bool:
        for c in p.hand.getCards():
            for k in p.lanes.keys():
                if p.lanes[k].score > 26:
                    p.lanes[k].resetLane()
                    return True
                if p.lanes[k].score + c.num.value + 1 <= 26 and c.num < cards.CardNum.JACK:
                    if p.lanes[k].playCard(c):
                        p.hand.discard(c.idx)
                        c.flipped = False
                        p.draw(True)
                        self.nextTurn()
                        return True
        
        p.hand.discard(0)
        p.draw(True)
        self.nextTurn()

    def writeAIGamestate(self, p: Player) -> str:
        outDict = {"hand": p.hand, "lanes": [p.lanes, self.player1.lanes if p.id == self.player2.id else self.player2.lanes], "winner": "None" if self.gameWon() is None else str(self.gameWon().name)}
        with open("gamestate_" + str(p.id) + ".json", "w") as f:
            f.write(json.dumps(outDict, cls=MyEncoder))
        with open("gamestate_history_" + str(p.id) + ".json", "a") as f:
            f.write(json.dumps(outDict, cls=MyEncoder))
        return json.dumps(outDict, cls=MyEncoder)
    
    def gameWon(self) -> Player:
        s1, s2, tot = 0, 0, 3
        allSold = False

        for k in self.player1.lanes.keys():
            ls1, ls2 = self.player1.lanes[k].scoreLane(), self.player2.lanes[k].scoreLane()
            if (ls1 > ls2 or ls2 > 26) and ls1 > 20 and ls1 < 27:
                s1 += 1
            elif (ls2 > ls1 or ls1 > 26) and ls2 > 20 and ls2 < 27:
                s2 += 1
        
        if s1 + s2 == tot:
            if s1 > s2:
                self.winner = self.player1
            if s2 > s1:
                self.winner = self.player2
            return self.winner
        return None

    def runServer(self):
        server_ip = "127.0.0.1"
        port = 8000

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server_ip, port))

        self.server.listen(0)
        print(f"Listening on {server_ip}:{port}")

        self.stop = False
        thread = threading.Thread(target=self.waitForClients)
        thread.start()

    def waitForClients(self):
        try:
            while True:
                if self.stop:
                    return

                # accept a client connection
                client_socket, addr = self.server.accept()
                print(f"Accepted connection from {addr[0]}:{addr[1]}")

                self.connectClients(client_socket, addr)

                # start a new thread to handle the client
                #thread = threading.Thread(target=self.connectClients, args=(client_socket, addr,))
                #thread.start()
        except:
            pass

    def connectClients(self, client_socket: socket.socket, address):
        for p in [self.player1, self.player2]:
            if not p.human and p.clientsocket is None:
                p.clientsocket = client_socket
                self.nextTurn()

class BuildWindow(QMainWindow):
    def __init__(self):
        super(BuildWindow, self).__init__()
        self.ui = Ui_BuildWindow()
        self.ui.setupUi(self)

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            pwindow.findChild(MyOpenGLWidget, "buildspaceWidget").adjustUIScale()
            pwindow.findChild(MyOpenGLWidget, "buildspaceWidget").update()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mwindow = MainWindow()
    bwindow = BuildWindow()
    pwindow = PlayWindow()

    mwindow.show()

    app.exec()
