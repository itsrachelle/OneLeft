from core.game.Card import Card
from core.game.ColorType import ColorType
from core.game.CardType import CardType
from typing import List
from random import shuffle

WILD_CARD_COUNT = 4
ACTION_CARD_COUNT = 3
COLOR_CARD_COUNT = 2


class GameEngineHelper:
    @staticmethod
    def create_game_deck() -> List[Card]:
        deck: List[Card] = []
        for color_type in ColorType:
            if color_type == ColorType.BLACK:
                for black_card_type in GameEngineHelper.get_wild_cards():
                    for n in range(WILD_CARD_COUNT):
                        deck.append(Card(black_card_type, color_type))
            else:
                for card_type in GameEngineHelper.get_color_cards():
                    if card_type == CardType.ZERO:
                        deck.append(Card(card_type, color_type))
                    else:
                        for n in range(COLOR_CARD_COUNT):
                            deck.append(Card(card_type, color_type))
        shuffle(deck)
        return deck

    @staticmethod
    def get_color_cards() -> List[CardType]:
        color_cards = [CardType.ZERO, CardType.ONE, CardType.TWO, CardType.THREE, CardType.FOUR, CardType.FIVE,
                       CardType.SIX, CardType.SEVEN, CardType.EIGHT, CardType.NINE]
        color_cards.extend(GameEngineHelper.get_action_cards())
        return color_cards

    @staticmethod
    def get_action_cards() -> List[CardType]:
        return [CardType.DRAW_TWO, CardType.REVERSE, CardType.SKIP]

    @staticmethod
    def get_wild_cards() -> List[CardType]:
        return [CardType.WILD_DRAW_FOUR, CardType.WILD]
