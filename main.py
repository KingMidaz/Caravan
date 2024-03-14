import socket
import sys
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


# Populate full deck with standard numbers and suits
def create_full_deck() -> cards.Deck:
    dck = []
    for j in cards.Suit:
        for k in cards.CardNum:
            dck.append(cards.Card(j, k))
    return cards.Deck(dck)


def build_deck() -> cards.Deck:
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

    if "nogui" not in sys.argv:
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
        self.playthread: list[threading.Thread] = []

        self.playerturn = None
        self.player1, self.player2, self.winner = None, None, None
        self.server = None
        self.serverthread: threading.Thread = None
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

            thrd = threading.Thread(target=self.nextTurn)
            thrd.start()
            self.playthread.append(thrd)
            c = 0
            for t in self.playthread:
                if t.isAlive():
                    c += 1
            print(str(c) + " threads alive")
        else:
            self.player1, self.player2 = start_game()
            self.playerturn = self.player1

    def nextTurn(self):
        winner, ooc = self.gameWon()
        while winner is None:
            if self.playerturn.id == self.player1.id:
                if not self.player1.human:
                    while not self.playAITurn(self.player1):
                        pass
                    self.playerturn = self.player2
                else:
                    self.playerturn = self.player2
                if self.player2.human:
                    break
            else:
                if not self.player2.human:
                    while not self.playAITurn(self.player2):
                        pass
                    self.playerturn = self.player1
                else:
                    self.playerturn = self.player1
                if self.player1.human:
                    break

            if "nogui" not in sys.argv:
                pwindow.findChild(MyOpenGLWidget, "playspaceWidget").update()
            winner, ooc = self.gameWon()

        if "loopai" in sys.argv:
            self.playGame(True)

    def getTurn(self):
        return self.playerturn

    def playAITurn(self, p: Player) -> bool:

        if "default" in sys.argv:
            return self.useDefaultAI(p)
        else:
            if p.clientsocket is None:
                print("No socket connected for player " + str(p.id))
                return False

            p.clientsocket.send(self.writeAIGamestate(p, 0, False).encode("utf-8"))

            try:
                request = p.clientsocket.recv(1024).decode("utf-8")
                request = int(request)

            except ValueError:
                print("ValueErorr on request move: " + request)
                return False

            except ConnectionAbortedError:
                print("Player " + str(p.id) + " connection abort error " + str(p.socketaddress))

            reward = 0
            validmove = True

            if request >= 32:
                v = p.lanes[list(p.lanes.keys())[request - 32]].scoreLane()
                if not p.lanes[list(p.lanes.keys())[request - 32]].resetLane():
                    validmove = False
                    reward = 0
                elif v > 26:
                    reward = 2
                else:
                    reward = 0
            elif 24 <= request <= 31:
                if not p.hand.discard(request - 24):
                    validmove = False
                    reward = 0
                else:
                    reward = 1
            elif request <= 23:
                for c in p.hand.getCards():
                    for k, i in zip(p.lanes.keys(), range(0, 3)):
                        if request == 3 * c.idx + i:
                            if not p.lanes[k].playCard(c):
                                validmove = False
                                reward = 0
                            else:
                                p.hand.discard(c.idx)
                                reward = self.getReward(c, p, k)
                            break
            p.nturns += 1

            p.clientsocket.send(self.writeAIGamestate(p, reward, False).encode("utf-8"))

            try:
                request = p.clientsocket.recv(1024).decode("utf-8")
                if request == "close":
                    if "nogui" not in sys.argv:
                        pwindow.hide()
                        mwindow.show()
                    self.stop = True
                    self.server.close()

            except ConnectionResetError:
                print("Player " + str(p.id) + " connection abort error " + str(p.socketaddress))

        if validmove:
            p.draw(True)

        return validmove

    def getReward(self, card: cards.Card, p: Player, k: str) -> int:
        lanescore = p.lanes[k].score
        lanescore_p2 = self.player1.lanes[k].score if p.id == self.player2.id else self.player2.lanes[k].score
        reward = 0

        if card.num < cards.CardNum.JACK:
            t_lane = cards.Lane()
            t_lane.cards = p.lanes[k].cards[0:len(p.lanes[k].cards) - 1]

            cardscore = card.num.value
            startscore = t_lane.scoreLane()

            reward += cardscore

            if 21 <= lanescore <= 26 and not 21 <= startscore <= 26:
                reward += 15
            elif startscore <= lanescore_p2 <= lanescore:
                reward += 15
        else:
            match card.num:
                case cards.CardNum.JACK:
                    startscore = lanescore + p.lanes[k].discarded.num.value
                    if lanescore < 27 <= startscore:
                        reward += 8
                    else:
                        reward += 0
                case cards.CardNum.KING:
                    t_lane = cards.Lane()
                    t_lane.cards = p.lanes[k].cards[0:len(p.lanes[k].cards) - 1]
                    startscore = t_lane.scoreLane()

                    reward += lanescore - startscore

                    if 21 <= lanescore <= 26 and not 21 <= startscore <= 26:
                        reward += 15
                    elif startscore <= lanescore_p2 <= lanescore:
                        reward += 15
                case cards.CardNum.QUEEN:
                    reward += 5

        return reward

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
                        return True
        p.hand.discard(0)
        p.draw(True)
        return True

    def writeAIGamestate(self, p: Player, reward: int, filewrite: bool) -> str:
        outDict = {"hand": p.hand,
                   "lanes": [p.lanes, self.player1.lanes if p.id == self.player2.id else self.player2.lanes],
                   "winner": "None" if self.winner is None else str(self.winner.name),
                   "reward": reward}
        if filewrite:
            with open("end_gamestate_" + str(p.id) + ".json", "a") as f:
                f.write(json.dumps(outDict, cls=MyEncoder))
        return json.dumps(outDict, cls=MyEncoder)

    def gameWon(self) -> (Player, bool):
        s1, s2, tot = 0, 0, 3
        ooc = False
        if len(self.player1.hand.getCards()) == 0:
            self.winner = self.player2
            ooc = True
        elif len(self.player2.hand.getCards()) == 0:
            self.winner = self.player1
            ooc = True
        else:

            for k in self.player1.lanes.keys():
                ls1, ls2 = self.player1.lanes[k].scoreLane(), self.player2.lanes[k].scoreLane()
                if (ls1 > ls2 or ls2 > 26) and 20 < ls1 < 27:
                    s1 += 1
                elif (ls2 > ls1 or ls1 > 26) and 20 < ls2 < 27:
                    s2 += 1

            if s1 + s2 == tot:
                if s1 > s2:
                    self.winner = self.player1
                if s2 > s1:
                    self.winner = self.player2

        if self.winner is not None:
            print("Winner " + self.winner.name)
            for p in [self.player1, self.player2]:
                if not p.human and "default" not in sys.argv:
                    if p.id == self.winner.id and not ooc:
                        p.clientsocket.send(self.writeAIGamestate(p, 20 + 20 * 10 / p.nturns, True).encode("utf-8"))
                    else:
                        p.clientsocket.send(self.writeAIGamestate(p, 0, True).encode("utf-8"))

            if "nogui" not in sys.argv:
                if "loopai" not in sys.argv:
                    QMessageBox(text="Winner " + self.winner.name,
                                parent=pwindow.findChild(MyOpenGLWidget, "centralwidget")).exec()
                    pwindow.hide()
                    mwindow.show()

            self.stop = True
            self.server.close()

        return self.winner, ooc

    def runServer(self):
        server_ip = "127.0.0.1"
        port = 8500

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server_ip, port))

        self.server.listen(0)
        print(f"Listening on {server_ip}:{port}")

        self.stop = False
        if self.serverthread is not None:
            self.serverthread.join()
        self.serverthread = threading.Thread(target=self.waitForClients)
        self.serverthread.start()

    def waitForClients(self):
        try:
            while True:
                if self.stop:
                    return

                # accept a client connection
                client_socket, addr = self.server.accept()
                print(f"Accepted connection from {addr[0]}:{addr[1]}")

                self.connectClients(client_socket, addr)
        except:
            print("Socket error")

    def connectClients(self, client_socket: socket.socket, address):
        for p in [self.player1, self.player2]:
            if p.socketaddress[0] == address[0] and p.socketaddress[1] == address[1]:
                return

        for p in [self.player1, self.player2]:
            if not p.human and p.clientsocket is None:
                p.clientsocket = client_socket
                p.socketaddress = address
                print("Socket connected for player " + str(p.id) + " " + str(address))
                return


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

    pwindow = PlayWindow()

    if "nogui" not in sys.argv:
        mwindow = MainWindow()
        bwindow = BuildWindow()
        mwindow.show()

        if "loopai" in sys.argv:
            mwindow.play_ai_game()
    else:
        pwindow.playGame(True)
    app.exec()
