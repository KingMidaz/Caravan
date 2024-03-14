from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QBrush, QFont, QCursor, QResizeEvent, QImage, QTransform

import player, cards, time


class MyQWidget(QWidget):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        print(str(event.key()))


class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.player1 = None
        self.player2 = None

        self.HAND_SPACING = -10

        self.mouseDown = False
        self.selectedCard = None
        self.highlightedCard = None

        self.time = round(time.time(), 0)

        self.laneFont = QFont()
        self.laneFont.setPixelSize(20)
        self.laneFont.setBold(True)

        self.cardFont = QFont()
        self.cardFont.setPixelSize(8)
        self.cardFont.setBold(False)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        print(str(event.key()))

        if event.key() == Qt.Key.Key_Right:
            self.update()

        if self.objectName() == "buildspaceWidget":
            if event.key() == Qt.Key.Key_Right:
                pass
            if event.key() == Qt.Key.Key_Left:
                pass

        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.mouseDown = True

        if self.player1.human:
            self.selectedCard = self.player1.detectHit(event.pos())
            self.highlightedCard = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.mouseDown and self.selectedCard is not None:
            self.update()

        if not self.mouseDown and self.player1 is not None:
            self.player1.hand.reindex()
            self.highlightedCard = self.player1.detectHit(self.mapFromGlobal(QCursor.pos()))
            if self.highlightedCard is not None:
                self.highlightedCard.topleft = QPoint(self.highlightedCard.topleft.x(),
                                                      self.highlightedCard.topleft.y() - self.highlightedCard.height / 4)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.mouseDown = False

        self.adjustUIScale()

        if self.player1.human:
            for p in [self.player1]:
                if p is not None and self.selectedCard is not None:
                    if self.window().getTurn().id == p.id:
                        for k in p.lanes.keys():
                            if p.lanes[k].playzone.contains(event.pos()):
                                if p.lanes[k].playCard(self.selectedCard):
                                    p.hand.discard(self.selectedCard.idx)
                                    p.lanes[k].scoreLane()
                                    if self.player1.draw(False):
                                        self.adjustUIScale()
                                    self.window().nextTurn()
                        if p.discardzone.contains(event.pos()):
                            p.hand.discard(self.selectedCard.idx)
                            if self.player1.draw(False):
                                self.adjustUIScale()
                                self.window().nextTurn()
                elif p is not None and self.selectedCard is None:
                    for k, i in zip(p.lanes.keys(), range(0, len(p.lanes.keys()))):
                        if (QRect(QPoint(i * (self.width()) / 5 + self.width() * 2 / 20, self.height() / 2 - 10),
                                  QPoint(i * (self.width()) / 5 + self.width() * 4 / 20,
                                         self.height() / 2 - 10 - 20)).contains(event.pos())):
                            if p.lanes[k].resetLane():
                                self.window().nextTurn()

        self.selectedCard = None
        self.update()

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self.adjustUIScale()

    def adjustUIScale(self):
        for p in [self.player1, self.player2]:
            if p is not None:
                if p.flip:
                    p.hand.topleft = QPoint(self.width() * 9 / 10 - len(p.getHand().cards) * cards.Card.width / 2,
                                            self.reflectY(self.height() * 3 / 5) - cards.Card.height)
                    p.hand.flipHand(True)
                    p.drawpile.topleft = QPoint(self.width() - self.width() / 12, self.reflectY(
                        self.height() - cards.Card.height - self.height() / 30) - cards.Card.height)
                    for k, i in zip(p.lanes.keys(), range(0, 3)):
                        p.lanes[k].playzone = QRect(QPoint((i * (self.width()) / 5),
                                                           self.reflectY((self.height() / 2 + 10) + self.height() / 3)),
                                                    QPoint(((i + 1) * (self.width()) / 5),
                                                           self.reflectY(self.height() / 2 + 10)))
                else:
                    p.hand.topleft = QPoint(self.width() * 9 / 10 - len(p.getHand().cards) * cards.Card.width / 2,
                                            self.height() * 3 / 5)
                    p.drawpile.topleft = QPoint(self.width() - self.width() / 12,
                                                self.height() - cards.Card.height - self.height() / 30)
                    for k, i in zip(p.lanes.keys(), range(0, 3)):
                        p.lanes[k].playzone = QRect(QPoint((i * (self.width()) / 5), self.height() / 2 + 10),
                                                    QPoint(((i + 1) * (self.width()) / 5),
                                                           (self.height() / 2 + 10) + self.height() / 3))
                    p.discardzone = QRect(QPoint(self.width() * 9 / 10 - len(p.getHand().cards) * cards.Card.width / 2,
                                                 self.height() * 3 / 5 + cards.Card.height * 1.2),
                                          QPoint(self.width() * 9 / 10 - len(
                                              p.getHand().cards) * cards.Card.width / 2 + len(
                                              p.getHand().cards) * cards.Card.width / 2,
                                                 self.height() * 3 / 5 + cards.Card.height * 2.2))
                p.hand.reindex()

    def paintEvent(self, e):
        painter = QPainter(self)

        if self.objectName() == "playspaceWidget":
            self.paintPlayBG(painter)

            if self.player1 is not None and self.player2 is not None:
                self.paintLanes(painter)
                self.paintPlayers(painter)

    def paintPlayBG(self, painter: QPainter):
        painter.fillRect(painter.viewport(), Qt.GlobalColor.darkGreen)

        painter.setFont(self.laneFont)

        for l, i in zip(["Freeside", "Goodsprings", "The Strip"], range(0, 3)):
            painter.drawText(QPoint(i * (self.width()) / 5 + self.width() * 2 / 20, self.height() / 2 - 10), l)

    def updatePlayers(self, p1: player.Player, p2: player.Player):
        self.player1 = p1
        self.player2 = p2

        print("Players updated!")
        self.adjustUIScale()
        self.update()

    def paintPlayers(self, painter: QPainter):
        for p in [self.player1, self.player2]:
            for c, i in zip(p.getHand().cards, range(0, len(p.getHand().cards))):
                if c == self.selectedCard:
                    coord = self.mapFromGlobal(QCursor.pos())
                    c.topleft = QPoint(coord.x() + - c.width / 2, coord.y() - c.height / 2)
                    self.paintCard(painter, c, p.flip)
                else:
                    c.topleft = QPoint(c.topleft.x(), c.topleft.y())
                    self.paintCard(painter, c, p.flip)

            drawCoord = p.getDrawPile().topleft
            for c, i in zip(p.getDrawPile().cards[:min(10, len(p.getDrawPile().cards))],
                            range(0, min(10, len(p.getDrawPile().cards)))):
                c.topleft = QPoint(drawCoord.x() - 2 * i, drawCoord.y() - 2 * i)
                self.paintCard(painter, c, p.flip)

    def paintLanes(self, painter: QPainter):
        for p in [self.player1, self.player2]:
            if p is not None:
                for k in p.lanes.keys():
                    for c, i in zip(p.lanes[k].cards, range(0, len(p.lanes[k].cards))):
                        if p.flip:
                            c.topleft = QPoint(
                                p.lanes[k].playzone.bottomLeft().x() + self.width() * 5 / 50 + i % 2 * 4 + i % 3 * 3,
                                p.lanes[k].playzone.bottomLeft().y() - (i + 1) * c.height + c.height * i * 4 / 5 - 40)
                        else:
                            c.topleft = QPoint(
                                p.lanes[k].playzone.topLeft().x() + self.width() * 5 / 50 + i % 2 * 4 + i % 3 * 3,
                                p.lanes[k].playzone.topLeft().y() + i * c.height - c.height * i * 4 / 5)
                        self.paintCard(painter, c, p.flip)

                    painter.setFont(self.laneFont)
                    if not p.flip:
                        painter.drawText(QPoint(p.lanes[k].playzone.topLeft().x() + self.width() / 25,
                                                p.lanes[k].playzone.topLeft().y()), str(p.lanes[k].score))
                    else:
                        painter.drawText(QPoint(p.lanes[k].playzone.bottomLeft().x() + self.width() / 25,
                                                p.lanes[k].playzone.bottomLeft().y()), str(p.lanes[k].score))

    def paintCard(self, painter: QPainter, card: cards.Card, flip: bool):
        painter.setFont(self.cardFont)

        painter.setBrush(QBrush(QColor(250, 250, 250)))

        if flip:
            painter.drawImage(card.topleft, self.cardPath(card).transformed(QTransform().rotate(180)))
        else:
            painter.drawImage(card.topleft, self.cardPath(card))

    def reflectY(self, y):
        return self.height() - y

    def cardPath(self, card: cards.Card) -> QImage:
        img = None
        if card.flipped:
            img = QImage("./Sprites/Cards/" + "Robot_Backing.png")
        else:
            match card.suit:
                case cards.Suit.SPADE:
                    img = QImage("./Sprites/Cards/" + str(card.num.value) + "_" + "Spades.png")
                case cards.Suit.HEART:
                    img = QImage("./Sprites/Cards/" + str(card.num.value) + "_" + "Hearts.png")
                case cards.Suit.CLUB:
                    img = QImage("./Sprites/Cards/" + str(card.num.value) + "_" + "Clubs.png")
                case cards.Suit.DIAMOND:
                    img = QImage("./Sprites/Cards/" + str(card.num.value) + "_" + "Diamonds.png")

        return img.scaled(QSize(card.width, card.height))
