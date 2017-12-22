# File For Easy Player
"""
The Player class is an implementation of the IPlayer class. This class
represents a very simple AI
"""
from core.game.IPlayer import IPlayer
from core.game.CardAction import CardAction
from core.game.ActionType import ActionType
from core.game.ColorType import ColorType
from core.game.CardType import CardType
from core.game.Card import Card
import random


class Player(IPlayer):

    def __init__(self):

        self.top_card_in_pile: Card = None
        self.card_played: Card = None
        self.legal_Response: Card = None

    """
    Player's class implemented version of get_player_name.
    Change the name returned in this method to name your AI.
    """

    def get_player_name(self) -> str:

        return 'Easy AI'

    """
    Player's class implemented version of take_turn.
    This the CardAction returned here is used by the game engine to 
    play your AIs card against your opponents. Modify this method
    as much as necessary to create the logic for your AI.
    """

    def take_turn(self) -> CardAction:

        self.top_card_in_pile = self.get_game_helper().get_card_pile()[-1]
        self.card_played = self.get_game_helper().get_last_card_played()
        card = self.get_game_helper().get_hand()[0]
        return CardAction(ActionType.PLAY, card)

    def get_turn(self):
        # copied from random
        last_card_played = self.get_game_helper().get_last_card_played()[0]
        my_hand = self.get_game_helper().get_hand()
        matched_cards_on_color = [c for c in my_hand if c.color_type == last_card_played.color_type]
        matched_cards_on_value = [c for c in my_hand if c.card_type == last_card_played.card_type]
        wild_cards = [c for c in my_hand if c.card_type == CardType.WILD or c.card_type == CardType.WILD_DRAW_FOUR]
        if len(matched_cards_on_color) > 0:
            return CardAction(ActionType.PLAY, random.choice(matched_cards_on_color))
        elif len(matched_cards_on_value) > 0:
            return CardAction(ActionType.PLAY, random.choice(matched_cards_on_value))
        elif len(wild_cards) > 0:
            return CardAction(ActionType.PLAY, random.choice(wild_cards))
        else:
            return CardAction(ActionType.SKIP)

    def turn_decider(self) -> Card:
        # try not to play the previous color, since chances are they don't have it
        # also don't play the card they just played since odds are you played both copies of that card in the game
        # we have to make sure this logic if used for wilds/actions handles this gracefully
        # Example 3R -> 3R 3B
        # We should reply using anything but red and anything but 3B

        # method here to get legal response cards

        if self.is_color_change():
            for x in self.get_game_helper().get_hand():
                #  not Red and not 3 blue
                if x.color_type != self.top_card_in_pile.color_type and x.card_type != self.top_card_in_pile.card_type:
                    return x
                elif x.color_type != self.top_card_in_pile.color_type and x.card_type == self.top_card_in_pile.card_type:
                    pass

    def process_played_card(self, card_played: Card):

        color_was_changed = self.is_color_change()
        if color_was_changed:
            pass
        if card_played.color_type == ColorType.BLACK:
            pass  # Blacks can be an action (draw) or change of color \
        #  need code to determine if color change or action (if both we knows its a wild draw 4)
        else:
            pass  # Colors can be change of color state or action (reverse, skip, draw 2)
