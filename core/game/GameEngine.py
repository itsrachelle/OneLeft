from core.game.Card import Card
from core.game.IPlayer import IPlayer
from core.game.GameEngineHelper import GameEngineHelper
from core.game.PlayerGameHelper import PlayerGameHelper
from core.game.GamePlayer import GamePlayer
from typing import List
from core.game.ActionType import ActionType
from core.game.CardType import CardType
from core.game.ColorType import ColorType
from random import shuffle
from collections import Counter

INITIAL_HAND_SIZE: int = 7
MIN_REQUIRED_PLAYERS: int = 2
MAX_REQUIRED_PLAYERS: int = 10
DECK_SIZE: int = 108


class GameEngine:
    def __init__(self, players: List[IPlayer], rounds_per_match: int):
        players_count = len(players)
        if players_count < MIN_REQUIRED_PLAYERS or players_count > MAX_REQUIRED_PLAYERS:
            raise ValueError(f'Amount of players (currently: {players_count}) must be at least 2 and cannot exceed 10')
        self._players: List[IPlayer] = players
        self._roundsPerMatch: int = rounds_per_match
        self._deck: List[Card] = GameEngineHelper.create_game_deck()
        self._amount_of_cards_used_in_round: int = 0
        self._top_card_in_pile: Card = None
        # Card played in turn
        self._card_played: Card = None
        self._card_pile: List[Card] = []
        # To be used to catch possible stack overflow
        self._repetition_count: int = 0

    def __get_game_players(self, players: List[IPlayer]) -> List[GamePlayer]:
        game_players = []
        for index, player in enumerate(players):
            player_hand = self.__draw_cards(INITIAL_HAND_SIZE)
            game_player = GamePlayer(player, player_hand, index)
            game_players.append(game_player)
        return game_players

    def __shuffle_cards(self):
        # We want to shuffle the entire card pile except the top one
        shuffled_card_pile = self._card_pile[:-1]
        card_pile_after_shuffle = self._card_pile[-1]
        shuffle(shuffled_card_pile)
        # We want to set the variables again now that the deck is shuffled
        self._deck = shuffled_card_pile
        self._card_pile = card_pile_after_shuffle

    def __is_deck_out_of_cards(self) -> bool:
        # this is coupled to the players defined in the constructor, which may not the players of the round
        cards_used_from_deck_count = self._amount_of_cards_used_in_round + \
                                     self.__get_players_hand_counts(self.__get_game_players(self._players))

        if cards_used_from_deck_count == DECK_SIZE:
            return True
        elif cards_used_from_deck_count > DECK_SIZE:
            print('Morty, *BURP* this isn\'t good, we somehow drew more cards than this universe allows!!??')
        else:
            return False

    def __draw_cards(self, draw_count: int) -> List[Card]:

        if self.__is_deck_out_of_cards():
            self.__shuffle_cards()

        drawn_cards = []
        for n in range(draw_count):
            drawn_cards.append(self._deck.pop(0))
        self._amount_of_cards_used_in_round += len(drawn_cards)
        return drawn_cards

    def __first_card_draw(self) -> [Card]:
        # No matter what the player (easy,hard,etc. we will play the first card from the deck
        # We need to check that the first card if is an action card isn't a wild or wild draw four.
        card_drawn = self.__draw_cards(1)[0]
        while card_drawn.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            # Put back in deck at end
            self._deck.append(card_drawn)
            # Update deck size tracker
            self._amount_of_cards_used_in_round -= 1
            # Try again
            card_drawn = self.__draw_cards(1)[0]
        return card_drawn

    def __create_player_game_helper(self, active_player: GamePlayer, last_card_played: Card):
        hand = active_player.hand
        last_card_played = last_card_played
        # we should check before we append
        self._card_pile.append(last_card_played)
        card_pile = self._card_pile
        deck_count = len(self._deck)
        opp_hand_count = []
        return PlayerGameHelper(hand, last_card_played, card_pile, deck_count, opp_hand_count)

    def __get_legal_response_cards(self, player_game_helper: PlayerGameHelper) -> List[Card]:
        last_card_played = player_game_helper.get_last_card_played()
        legal_card_responses: List[Card] = []
        for current_card in player_game_helper.get_hand():
            if not self.__is_action(last_card_played):
                # It has to match either color or number
                if current_card.color_type == last_card_played.color_type \
                        or current_card.card_type == last_card_played.card_type:
                    legal_card_responses.append(current_card)
            else:
                if last_card_played.card_type == CardType.WILD_DRAW_FOUR:
                    # If a wild card +4 was played, you can only play that card
                    if current_card.card_type == last_card_played.card_type:
                        legal_card_responses.append(current_card)
                elif last_card_played.color_type == ColorType.BLACK \
                        and last_card_played.card_type == CardType.WILD:
                    # If a wild card was played, but no color was chosen
                    print(f'Wild card was played, but no color type was declared!')
                    return legal_card_responses
                elif last_card_played.color_type != ColorType.BLACK \
                        and last_card_played.card_type == CardType.WILD:
                    # If a wild card was played, you can only play cards of the color declared
                    if current_card.color_type == last_card_played.color_type:
                        legal_card_responses.append(current_card)
                else:
                    # If a draw, reverse/skip, skip - you can only play the same card back
                    # or draw/skip your turn
                    if current_card.card_type == last_card_played.card_type:
                        legal_card_responses.append(current_card)
        return legal_card_responses

    def __is_color_change(self) -> bool:
        if self._top_card_in_pile.color_type == self._card_played.color_type:
            return False
        else:
            return True

    def __is_action(self, card: Card) -> bool:

        if card.card_type in [CardType.DRAW_TWO, CardType.REVERSE, CardType.SKIP,
                              CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return True
        else:
            return False

    def __draw_card_to_hand(self, game_player: GamePlayer, amount_to_draw: int):
        cards_drawn = self.__draw_cards(amount_to_draw)

        # This should work now that I added a setter property on GamePlayer.hand
        game_player.hand.extend(cards_drawn)

    def __get_players_hand_counts(self, players: List[GamePlayer]) -> int:
        hand_count = 0
        for player in players:
            hand_count += len(player.hand)
        return hand_count

    def __determine_winner(self, winning_player_ids: List[int]) -> int:
        dict_of_occurrences = Counter(winning_player_ids)
        max_occurrence_count = max(dict_of_occurrences.values())
        for value, occurrence_count in dict_of_occurrences.items():
            if occurrence_count == max_occurrence_count:
                print('Player with id {} won the macth!!'.format(value))
                return value

    def start(self) -> int:
        current_round: int = 0
        round_winners_player_ids: List[int] = []
        while current_round <= self._roundsPerMatch:
            # At the beginning of every round, get a fresh list of players and reset round variables.
            round_players = self.__get_game_players(self._players)
            self._deck = GameEngineHelper.create_game_deck()
            current_round += 1
            round_won = False
            print('- Round {0}'.format(current_round))

            # Keep playing the same round until a winner is chosen.
            while not round_won:

                active_player: GamePlayer = None

                last_card_played = self.__first_card_draw()

                # Main game loop starts here, loop through each player until a player has 0 cards.
                for game_player in round_players:

                    active_player = game_player.player

                    # create PlayerGameHelper
                    active_player_game_helper = self.__create_player_game_helper(game_player, last_card_played)
                    # PlayerGameHelper is only for this turn for this player
                    game_player.player.set_game_helper(active_player_game_helper)
                    current_game_helper = game_player.player.get_game_helper()

                    player_action = game_player.player.take_turn()

                    self._card_played = player_action.card

                    # check what was played is legal and from their hand AND they aren't skipping
                    if player_action.action == ActionType.PLAY:
                        legal_responses = self.__get_legal_response_cards(current_game_helper)
                        if player_action.card not in legal_responses:
                            # Logic here to draw, reverse/skip, skip in they don't respond with a matching card
                            if last_card_played.card_type in [CardType.DRAW_TWO, CardType.REVERSE,
                                                              CardType.SKIP, CardType.WILD_DRAW_FOUR]:
                                print(f'You don''t have this card in your hand: {self.last_card_played.card_type}')
                                if last_card_played.card_type in [CardType.SKIP, CardType.REVERSE]:
                                    print('You have to skip your turn')
                                    continue
                                elif last_card_played.card_type in [CardType.DRAW_TWO, CardType.WILD_DRAW_FOUR]:
                                    print('You have to draw and skip your turn')
                                    if last_card_played.card_type == CardType.DRAW_TWO:
                                        self.__draw_card_to_hand(game_player, 2)
                                    else:
                                        self.__draw_card_to_hand(game_player, 4)
                                    continue
                            else:
                                print('ILLEGAL play or this card is not in your hand, tsk tsk!\n'
                                      f'Type: {player_action.card.card_type} Color: {player_action.card.color_type}\n'
                                      'Drawing a card and skipping your turn instead')
                                self.__draw_card_to_hand(game_player, 1)
                                continue
                        else:
                            # IT IS LEGAL remove card from hand (Except: draw two, reverse, skip, wild +4, wild)
                            # This card can be rightfully added to the pile
                            self._card_pile.append(self._card_played)
                            last_card_played = self._card_played

                    else:
                        if last_card_played == CardType.SKIP:
                            print("A skip card was played and the player did skip their turn")
                        elif last_card_played == CardType.REVERSE:
                            print("A reverse card was played and the player did skip their turn")
                        else:
                            # skip and draw logic here
                            self.__draw_card_to_hand(game_player, 1)
                            print(f'Player drew a card and skipped their turn. Hand is now: {game_player.hand}')
                            continue

                    print('{} uses action {}'.format(active_player.get_player_name(), player_action.action))
                    print('{}'.format(player_action.card.get_card_text()))

                    # Until game loop is actually implemented, remove a card from the player's hand.
                    game_player.hand.pop()

                    # After the card has been played, if that player has no more cards, they win the round.
                    if len(game_player.hand) <= 0:
                        round_won = True
                        print('{} won the round!'.format(active_player.get_player_name()))
                        round_winners_player_ids.append(game_player.player_id)

        # After all rounds have been played, handle any Match over logic here
        print('Match is over!')
        return self.__determine_winner(round_winners_player_ids)
