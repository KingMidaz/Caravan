from PySide6.QtCore import QPoint, QRect

import cards
import socket
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Player:
    name: str
    human: bool
    clientsocket: socket.socket
    socketaddress: (str, int)
    id: int
    deck: cards.Deck
    drawpile: cards.DrawPile
    hand: cards.Hand
    discardzone: QRect
    nturns: int

    lanes: dict[str, cards.Lane]

    flip: bool = False

    def deal(self):
        self.deck.shuffle()
        for i in range(0, 8):
            self.hand.addCard(self.deck.drawCard())
        self.drawpile.cards = self.deck.cards
        self.drawpile.flipDraw()

    def move(self, card, lane):
        setattr(self, lane, getattr(self, lane).add_card(self.hand.playCard(card)))

    def check_end(self) -> bool:
        return False

    def getHand(self):
        return self.hand

    def getDrawPile(self):
        return self.drawpile
    
    def flipSides(self):
        self.flip = not self.flip
    
    def draw(self, flip: bool) -> bool:
        if self.hand.cardCount() < 8:
            cardtodraw = self.drawpile.drawCard()
            if cardtodraw is not None:
                self.hand.addCard(cardtodraw)
                self.hand.flipHand(flip)
                return True
        return False

    def detectHit(self, mouse: QPoint) -> cards.Card:
        if self.drawpile.isMouseOver(mouse):
            return self.drawpile.getTopCard()
        
        card = None
        for c in self.hand.getCards():
            if c.isMouseOver(mouse):
                card = c

        return card

    def __init__(self, deck: cards.Deck, name: str, id: int, human: bool):
        self.name = name
        self.id = id
        self.deck = deck
        self.drawpile = cards.DrawPile()
        self.hand = cards.Hand()
        self.human = human
        self.nturns = 0

        self.lanes = {"Freeside" : cards.Lane(), "Goodsprings" : cards.Lane(), "The Strip" : cards.Lane()}
        
        self.discardzone = QRect()
        
        self.clientsocket = None
        self.socketaddress = (0, 0)
        
        self.deal()
