import random
from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    SPADE = 1
    CLUB = 2
    HEART = 3
    DIAMOND = 4


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


class Direction(Enum):
    ASCENDING = 1
    DESCENDING = 2


@dataclass
class Card:
    suit: Suit
    num: CardNum
    idx: int = 0


@dataclass
class Lane:
    direction: Direction = Direction.ASCENDING
    suit: Suit = Suit.SPADE
    cards: list[Card] = list[Card]

    def add_card(self, card):
        self.cards.append(card)
        return self


@dataclass
class DrawPile:
    cards: list[Card] = list[Card]

    def draw_card(self) -> Card:
        return self.cards.pop(0)


@dataclass
class Hand:
    cards: list[Card] = list[Card]

    def add_card(self, card):
        self.cards.append(card)
        self.reindex()

    def reindex(self):
        for i in range(0, len(self.cards)):
            self.cards[i].idx = i

    def discard(self, idx):
        self.cards.pop(idx)
        self.reindex()

    def play_card(self, idx) -> Card:
        crd = self.cards.pop(idx)
        self.reindex()
        return crd


@dataclass
class Deck:
    cards: list[Card] = list[Card]

    def add_card(self, card):
        self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self) -> Card:
        return self.cards.pop(0)
