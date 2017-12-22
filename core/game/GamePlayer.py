from core.game.IPlayer import IPlayer
from core.game.Card import Card
from typing import List


class GamePlayer:
    def __init__(self, player: IPlayer, hand: List[Card], player_id: int):
        self._player_id: int = player_id
        self._player: IPlayer = player
        self._hand: List[Card] = hand

    @property
    def player(self):
        return self._player

    @property
    def hand(self) -> List[Card]:
        return self._hand

    @property
    def player_id(self):
        return self._player_id

    @hand.setter
    def hand(self, value: List[Card]):
        self._hand = value
