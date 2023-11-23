import cards
from dataclasses import dataclass
from enum import Enum


@dataclass
class Player:
    name: str
    deck: cards.Deck
    drawpile: cards.DrawPile = cards.DrawPile()
    hand: cards.Hand = cards.Hand()

    freeside: cards.Lane = cards.Lane()
    goodsprings: cards.Lane = cards.Lane()
    novac: cards.Lane = cards.Lane()
    thestrip: cards.Lane = cards.Lane()

    def deal(self):
        self.deck.shuffle()
        for i in range(0, 7):
            self.hand.add_card(self.deck.draw_card())
        self.drawpile.cards = self.deck.cards

    def move(self, card, lane):
        setattr(self, lane, getattr(self, lane).add_card(self.hand.play_card(card)))

    def check_end(self) -> bool:
        return False

    def __init__(self, deck: cards.Deck):
        self.deck = deck
        self.name = "Player"

        self.deal()
