from core.game.Card import Card
from core.game.IPlayer import IPlayer
from core.game.GameEngineHelper import GameEngineHelper
from core.game.PlayerGameHelper import PlayerGameHelper
from core.game.GamePlayer import GamePlayer
from typing import List

INITIAL_HAND_SIZE: int = 7
MIN_REQUIRED_PLAYERS: int = 2
MAX_REQUIRED_PLAYERS: int = 10


class GameEngine:
    def __init__(self, players: List[IPlayer], rounds_per_match: int):
        players_count = len(players)
        if players_count < MIN_REQUIRED_PLAYERS or players_count > MAX_REQUIRED_PLAYERS:
            raise ValueError(f'Amount of players (currently: {players_count}) must be at least 2 and cannot exceed 10')
        self._players: List[IPlayer] = players
        self._roundsPerMatch: int = rounds_per_match
        self._deck: List[Card] = GameEngineHelper.create_game_deck()

    def __get_game_players(self, players: List[IPlayer]) -> List[GamePlayer]:
        game_players = []
        for index, player in enumerate(players):
            player_hand = self.__draw_cards(INITIAL_HAND_SIZE)
            game_player = GamePlayer(player, player_hand, index)
            game_players.append(game_player)
        return game_players

    def __draw_cards(self, draw_count: int) -> List[Card]:
        drawn_cards = []
        for n in range(draw_count):
            drawn_cards.append(self._deck.pop(0))
        return drawn_cards

    def __create_player_game_helper(self, active_player: GamePlayer, last_card_played: Card):
        hand = active_player.hand
        last_card_played = last_card_played
        card_pile = []
        deck_count = len(self._deck)
        opp_hand_count = []
        return PlayerGameHelper(hand, last_card_played, card_pile, deck_count, opp_hand_count)

    def start(self):
        current_round: int = 0

        while current_round <= self._roundsPerMatch:
            # At the beginning of every round, get a fresh list of players and resent round variables.
            round_players = self.__get_game_players(self._players)
            self._deck = GameEngineHelper.create_game_deck()
            current_round += 1
            round_won = False
            round_winner = None
            print('- Round {0}'.format(current_round))

            # Keep playing the same round until a winner is chosen.
            while not round_won:
                active_player: GamePlayer = None
                last_card_played = self.__draw_cards(1)

                # Main game loop starts here, loop through each player until a player has 0 cards.
                for game_player in round_players:
                    active_player = game_player.player
                    active_player_game_helper = self.__create_player_game_helper(game_player, last_card_played)
                    game_player.player.set_game_helper(active_player_game_helper)
                    player_action = game_player.player.take_turn()
                    print('{} uses action {}'.format(active_player.get_player_name(), player_action.action))
                    print('{}'.format(player_action.card.get_card_text()))

                    # Until game loop is actually implemented, remove a card from the player's hand.
                    game_player.hand.pop()

                    # After the card has been played, if that player has no more cards, they win the round.
                    if len(game_player.hand) <= 0:
                        round_won = True
                        print('{} won the round!'.format(active_player.get_player_name()))
                        round_winner = active_player

        # After all rounds have been played, handle any Match over logic here
        print('Match is over!')
