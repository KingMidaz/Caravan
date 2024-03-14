import math

from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QMainWindow

import random
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering


class Suit(Enum):
    SPADE = 1
    CLUB = 2
    HEART = 3
    DIAMOND = 4


@total_ordering
class CardNum(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Direction(Enum):
    ASCENDING = 1
    DESCENDING = 2
    NO_DIRECTION = 3


@dataclass
class Card:
    suit: Suit
    num: CardNum
    idx: int = 0
    topleft: QPoint = QPoint(0, 0)
    width: int = 120
    height: int = 180
    zidx: int = 0
    flipped: bool = False

    def isMouseOver(self, coord: QPoint):
        if coord.x() > self.topleft.x() and coord.x() < self.topleft.x() + self.width and coord.y() > self.topleft.y() and coord.y() < self.topleft.y() + self.height:
            return True
        return False


@dataclass
class Lane:
    playzone: QRect = QRect()
    direction: Direction = Direction.NO_DIRECTION
    suit: Suit = Suit.SPADE
    cards: list[Card] = field(default_factory=list)
    topleft: QPoint = QPoint(0, 0)
    score: int = 0
    discarded: Card = None

    def resetLane(self) -> bool:
        if len(self.cards) > 0:
            self.cards.clear()
            self.scoreLane()
            return True
        return False

    def addCard(self, card: Card):
        self.discarded = None

        if len(self.cards) >= 1:
            if card.num < CardNum.JACK:
                if self.getLastNumCard().num is not None and self.getLastNumCard().num > card.num:
                    self.direction = Direction.DESCENDING
                else:
                    self.direction = Direction.ASCENDING

        if card.num == CardNum.QUEEN:
            self.suit = card.suit
            if self.direction == Direction.ASCENDING:
                self.direction = Direction.DESCENDING
            else:
                self.direction = Direction.ASCENDING
        elif card.num == CardNum.JACK:
            if self.getLastCard().num >= CardNum.JACK:
                self.discardLast()
            self.discardLast()
            self.scoreLane()
            return self
        card.flipped = False
        self.cards.append(card)
        self.scoreLane()
        return self

    def discardLast(self):
        self.discarded = self.cards.pop()

        if len(self.cards) >= 1:
            if self.cards[len(self.cards) - 2].num > self.cards[len(self.cards) - 1].num:
                self.direction = Direction.DESCENDING
            else:
                self.direction = Direction.ASCENDING

    def getLastCard(self) -> Card:
        if len(self.cards) == 0:
            return None
        return self.cards[len(self.cards) - 1]

    def getLastNumCard(self) -> Card:
        for i in range(len(self.cards) - 1, -1, -1):
            if self.cards[i].num < CardNum.JACK:
                return self.cards[i]
        return None

    def playCard(self, card: Card) -> bool:
        if card is None:
            return False
        if self.direction == Direction.NO_DIRECTION and card.num <= CardNum.TEN:
            self.addCard(card)
            return True
        elif len(self.cards) == 0:
            return False
        elif card.suit == self.getLastCard().suit:
            self.addCard(card)
            return True
        elif len(self.cards) > 0 and card.num >= CardNum.JACK:
            self.addCard(card)
            return True
        elif (self.direction == Direction.ASCENDING and card.num > self.getLastNumCard().num) or (
                self.direction == Direction.DESCENDING and card.num < self.getLastNumCard().num):
            self.addCard(card)
            return True
        return False

    def scoreLane(self) -> int:
        self.score = 0
        if len(self.cards) > 0:
            for i in range(len(self.cards) - 1, -1, -1):
                if self.cards[i].num < CardNum.JACK:
                    self.score += self.cards[i].num.value
                elif self.cards[i].num == CardNum.KING:
                    j = 0
                    while self.cards[i - j - 1].num == CardNum.KING:
                        j += 1
                    self.score += self.cards[i - j - 1].num.value * (2**j)

        return self.score


@dataclass
class DrawPile:
    cards: list[Card] = field(default_factory=list)
    topleft: QPoint = QPoint(700, 500)
    width: int = 120
    height: int = 180

    def drawCard(self) -> Card:
        if len(self.cards) > 0:
            return self.cards.pop(0)
        else:
            return None

    def getTopCard(self) -> Card:
        return self.cards[len(self.cards) - 1]

    def isMouseOver(self, coord: QPoint):
        if coord.x() > self.topleft.x() and coord.x() < self.topleft.x() + self.width and coord.y() > self.topleft.y() and coord.y() < self.topleft.y() + self.height:
            return True
        return False

    def flipDraw(self):
        for c in self.cards:
            c.flipped = True


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)
    topleft: QPoint = QPoint(600, 400)

    def addCard(self, card):
        self.cards.append(card)
        self.reindex()

    def reindex(self):
        for i in range(0, len(self.cards)):
            self.cards[i].idx = i
            self.cards[i].topleft = QPoint(self.topleft.x() + i * self.cards[i].width / 2,
                                           self.topleft.y() - 2 * (i % 2))

    def flipHand(self, flip: bool):
        for c in self.cards:
            c.flipped = flip

    def discard(self, idx):
        if len(self.cards) <= idx:
            return False
        if self.cards.pop(idx) is not None:
            self.reindex()
            return True
        return False

    def playCard(self, idx) -> Card:
        crd = self.cards.pop(idx)
        self.reindex()
        return crd

    def getCards(self):
        return self.cards

    def cardCount(self) -> int:
        return len(self.cards)


@dataclass
class Deck:
    cards: list[Card] = list[Card]

    def addCard(self, card):
        self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def drawCard(self) -> Card:
        if len(self.cards) > 0:
            return self.cards.pop(0)
        else:
            return None

