# File for Random Player
import random
from core.game.IPlayer import IPlayer
from core.game.CardAction import CardAction
from core.game.ActionType import ActionType
from core.game.CardType import CardType
from core.game.ColorType import ColorType
from core.game.Card import Card


class RandomPlayer(IPlayer):
    """
    Player's class implemented version of get_player_name.
    """

    def get_player_name(self) -> str:
        return 'Rando Calrissian'

    """
    Implementation method of take turn from IPlayer interface. This will
    get the last card played and the player's hand and randomly select
    a card based on color then value and finally it will play a wild
    card if one is available otherwise it will skip.
    """

    def take_turn(self) -> CardAction:
        last_card_played = self.get_game_helper().get_last_card_played()
        my_hand = self.get_game_helper().get_hand()
        matched_cards_on_color = [c for c in my_hand if c.color_type == last_card_played.color_type]
        matched_cards_on_value = [c for c in my_hand if c.card_type == last_card_played.card_type]
        wild_cards = [c for c in my_hand if c.card_type == CardType.WILD or c.card_type == CardType.WILD_DRAW_FOUR]
        if len(matched_cards_on_color) > 0:
            return CardAction(ActionType.PLAY, random.choice(matched_cards_on_color))
        elif len(matched_cards_on_value) > 0:
            return CardAction(ActionType.PLAY, random.choice(matched_cards_on_value))
        elif len(wild_cards) > 0:
            random_wild_card: Card = random.choice(wild_cards)
            # Set random color for the wild card
            random_wild_card.color_type = random.choice(
                [ColorType.BLUE, ColorType.GREEN, ColorType.RED, ColorType.YELLOW])
            return CardAction(ActionType.PLAY, random_wild_card)
        else:
            return CardAction(ActionType.SKIP)
