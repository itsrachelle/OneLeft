"""
The Card represents a card object from the game. Every card contains a color
along with a type. Refer to CardType and ColorType for full descriptions
of each. This class is meant to be a read-only class, meaning once the object
is created, it cannot be modified.
"""

from core.game.CardType import CardType
from core.game.ColorType import ColorType


class Card:
    def __init__(self, card_type: CardType, color_type: ColorType):
        self._card_type: CardType = card_type
        self._color_type: ColorType = color_type

    @property
    def card_type(self) -> CardType:
        return self._card_type

    @property
    def color_type(self) -> ColorType:
        return self._color_type

    @color_type.setter
    def color_type(self, value: ColorType):
        self._color_type = value

    def get_card_text(self) -> str:
        return '{} {}'.format(self._color_type, self.color_type)