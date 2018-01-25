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
    def __init__(self, players, rounds_per_match):
        players_count = len(players)
        if players_count < MIN_REQUIRED_PLAYERS or players_count > MAX_REQUIRED_PLAYERS:
            raise ValueError('Amount of players (currently: {players_count}) must be at least 2 and cannot exceed 10')
        self._players = players
        self._roundsPerMatch = rounds_per_match
        self._deck = GameEngineHelper.create_game_deck()
        self._amount_of_cards_used_in_round = 0
        self._top_card_in_pile = None
        # Card played in turn
        self._card_played = None
        self._card_pile = []
        # To be used to catch possible stack overflow
        self._repetition_count = 0
        # To be used to track stacked draws
        self._are_draw_cards_stacked = False
        self._did_player_skip = False

    def __get_and_create_game_players(self, players):
        game_players = []
        for index, player in enumerate(players):
            player_hand = self.__draw_cards(INITIAL_HAND_SIZE, True)
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
        self._card_pile = [card_pile_after_shuffle]
        self._amount_of_cards_used_in_round = len(self._card_pile)

    def __is_deck_out_of_cards(self, amount_to_be_drawn: int = 0) -> bool:

        player_hand_count = self.__get_players_hand_counts(self._players)

        # this is coupled to the players defined in the constructor, which may not be the players of the round
        cards_used_from_deck_count = self._amount_of_cards_used_in_round + player_hand_count

        if cards_used_from_deck_count == DECK_SIZE:
            return True
        elif cards_used_from_deck_count + amount_to_be_drawn > DECK_SIZE:
            return True
        elif cards_used_from_deck_count > DECK_SIZE:
            print('Morty, *BURP* this isn\'t good, we somehow drew more cards than this universe allows!!??')
            return True
        else:
            return False

    def __draw_cards(self, draw_count: int, initial_hand_draw: bool = False):
        # We don't need to worry about checking deck size at the beginning of the game
        # if not initial_hand_draw:
        # if self.__is_deck_out_of_cards(draw_count):
        #     self.__shuffle_cards()

        drawn_cards = []
        for n in range(draw_count):
            drawn_cards.append(self._deck.pop(0))
        self._amount_of_cards_used_in_round += len(drawn_cards)
        return drawn_cards

    def __first_card_draw(self) -> [Card]:
        # No matter what the player (easy,hard,etc. we will play the first card from the deck
        # We need to check that the first card if is an action card isn't a wild or wild draw four.
        card_drawn = self.__draw_cards(1, True)[0]
        while card_drawn.card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            # Put back in deck at end
            self._deck.append(card_drawn)
            # Update deck size tracker
            self._amount_of_cards_used_in_round -= 1
            # Try again
            card_drawn = self.__draw_cards(1, True)[0]
        # This is the first card in the card pile
        self._card_pile.append(card_drawn)
        return card_drawn

    def __create_player_game_helper(self, active_player: GamePlayer):
        hand = active_player.hand
        last_card_played = self._card_pile[-1]
        card_pile = self._card_pile
        deck_count = len(self._deck)
        opp_hand_count = []
        return PlayerGameHelper(hand, last_card_played, card_pile, deck_count, opp_hand_count)

    def __get_legal_response_cards(self, player_game_helper: PlayerGameHelper):
        last_card_played = self._card_pile[-1]
        legal_card_responses = []
        for current_card in player_game_helper.get_hand():
            if not self.__is_action(last_card_played):
                # It has to match either color or number
                if current_card.color_type == last_card_played.color_type \
                        or current_card.card_type == last_card_played.card_type:
                    legal_card_responses.append(current_card)
                if current_card.card_type in [CardType.WILD_DRAW_FOUR, CardType.WILD]:
                    # If it is not an action, we can always play any Wild card
                    legal_card_responses.append(current_card)
            else:
                if last_card_played.card_type == CardType.WILD_DRAW_FOUR:
                    # If a wild card +4 was played, you can only play that card
                    if current_card.card_type == last_card_played.card_type:
                        legal_card_responses.append(current_card)
                elif last_card_played.color_type == ColorType.BLACK \
                        and last_card_played.card_type == CardType.WILD:
                    # If a wild card was played, but no color was chosen
                    # This should be handled before we get here: choose a color at random
                    print('Wild card was played, but no color type was declared!')
                    return legal_card_responses
                elif last_card_played.color_type != ColorType.BLACK \
                        and last_card_played.card_type == CardType.WILD:
                    # If a wild card was played, you can only play cards of the color declared
                    # or more wild
                    if current_card.color_type == last_card_played.color_type \
                            or current_card.card_type in [CardType.WILD_DRAW_FOUR, CardType.WILD]:
                        legal_card_responses.append(current_card)
                elif last_card_played.card_type == CardType.DRAW_TWO:
                    # Draws can be stacked
                    if current_card.card_type == last_card_played.card_type \
                            and current_card.color_type == last_card_played.color_type:
                        legal_card_responses.append(current_card)
                elif last_card_played.card_type == CardType.REVERSE:
                    if current_card.color_type == last_card_played.color_type \
                            or current_card.card_type in [CardType.WILD_DRAW_FOUR, CardType.WILD]:
                        legal_card_responses.append(current_card)
                elif last_card_played.card_type == CardType.SKIP:
                    if self._did_player_skip:
                        if current_card.color_type == last_card_played.color_type \
                                or current_card.card_type in [CardType.WILD_DRAW_FOUR, CardType.WILD]:
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
        cards_drawn = self.__draw_cards(amount_to_draw, False)

        # This should work now that I added a setter property on GamePlayer.hand
        game_player.hand.extend(cards_drawn)

    def __get_players_hand_counts(self, players) -> int:
        hand_count = 0
        for player in players:
            if hasattr(player.get_game_helper(), 'get_hand'):
                hand_count += len(player.get_game_helper().get_hand())
            else:
                print('Uhhh this player has no hand.... ')
        return hand_count

    def __determine_winner(self, winning_player_ids) -> GamePlayer:
        dict_of_occurrences = Counter(winning_player_ids)
        max_occurrence_count = max(dict_of_occurrences.values())
        for value, occurrence_count in dict_of_occurrences.items():
            if occurrence_count == max_occurrence_count:
                print('Player with id {} won the match!!'.format(value))
                for game_player in self.__get_and_create_game_players(self._players):
                    if game_player.player_id == value:
                        return game_player
        print('Oddly enough, we cannot figure out the player that won?!?!? \nReturning the first player...')
        return self.__get_and_create_game_players(self._players)[0]

    def __handle_stacked_draws(self, game_player: GamePlayer):
        print('hello')
        # Needs to handle stacked draws
        # if self._are_draw_cards_stacked:
        #     self._are_draw_cards_stacked = False
        #     cards_to_draw = 0
        #     draw_card_type_stacked = self._card_pile[-2]
        #     for card in reversed(self._card_pile):
        #         if card.card_type in [CardType.WILD_DRAW_FOUR]:
        #             cards_to_draw += 4
        #         if card.card_type in [CardType.DRAW_TWO]:
        #             cards_to_draw += 2
        #         if draw_card_type_stacked.card_type != card.card_type:
        #             break
        #     self.__draw_card_to_hand(game_player, cards_to_draw)

    def __order_of_players_reversed(self, players_in_round, index: int):
        new_end_of_list = players_in_round[index]
        first_half_reversed_list = list(reversed(players_in_round[:index]))
        second_half_reversed_list = list(reversed(players_in_round[index + 1:]))
        first_half_reversed_list.extend(second_half_reversed_list)
        first_half_reversed_list.append(new_end_of_list)
        return first_half_reversed_list

    def start(self) -> GamePlayer:
        current_round = 0
        round_winners_player_ids = []
        while current_round <= self._roundsPerMatch:
            # At the beginning of every round, get a fresh list of players and reset round variables.
            round_players = self.__get_and_create_game_players(self._players)
            self._deck = GameEngineHelper.create_game_deck()
            self._amount_of_cards_used_in_round = 0
            self._card_pile = []
            current_round += 1
            round_won = False
            print('- Round {0}'.format(current_round))

            # Keep playing the same round until a winner is chosen.
            while not round_won:
                print('koloss')
                active_player = None

                self.__first_card_draw()

                # Use while loop since we are messing with the order of round_players while iterating over it
                # Examples: Reverses in > 2 players
                # Main game loop starts here, loop through each player until a player has 0 cards.
                i = 0
                while i < len(round_players):

                    active_player = round_players[i]

                    for player in round_players:
                        print(len(player.hand))

                    # Adjust iterator for while loop
                    if i == len(round_players) - 1:
                        i = 0
                    else:
                        i += 1

                    # create PlayerGameHelper
                    active_player_game_helper = self.__create_player_game_helper(active_player)
                    # PlayerGameHelper is only for this turn for this player
                    active_player.player.set_game_helper(active_player_game_helper)
                    current_game_helper = active_player.player.get_game_helper()

                    last_card_played = self._card_pile[-1]
                    player_action = active_player.player.take_turn()
                    self._card_played = player_action.card

                    # check what was played is legal and from their hand AND they aren't skipping
                    if player_action.action == ActionType.PLAY:
                        # legal_responses = self.__get_legal_response_cards(current_game_helper)
                        legal_responses = current_game_helper.get_valid_hand()
                        if self._card_played not in legal_responses:
                            # Logic here to draw, reverse/skip, skip in case they don't respond with a matching card
                            if last_card_played.card_type in [CardType.DRAW_TWO, CardType.REVERSE,
                                                              CardType.SKIP, CardType.WILD_DRAW_FOUR]:
                                print('You don''t have this card in your hand: {}, the last card played was: {}'
                                      .format(self._card_played.get_card_text(), last_card_played.get_card_text()))

                                if last_card_played.card_type == CardType.SKIP:
                                    self._did_player_skip = True
                                    print('You have to skip your turn')
                                elif last_card_played.card_type == CardType.REVERSE:
                                    if len(round_players) > 2:
                                        # We only reverse if more than 2 players
                                        round_players = self.__order_of_players_reversed(round_players, i)
                                elif last_card_played.card_type in [CardType.DRAW_TWO, CardType.WILD_DRAW_FOUR]:
                                    print('You have to draw and skip your turn')
                                    # Draw logic if stack Draws
                                    print('hey')
                                    self.__handle_stacked_draws(active_player)

                                continue
                            else:
                                if self._card_played is None:
                                    print('ERROR')
                                if self._card_played.card_type is not None:
                                    print('ILLEGAL play or this card is not in your hand, tsk tsk!\n'
                                          'Type: {}  \n Drawing a card and skipping your turn instead'
                                          .format(self._card_played.card_type.value))
                                self.__draw_card_to_hand(active_player, 1)
                                self.__handle_stacked_draws(active_player)
                                continue
                        else:
                            # IT IS LEGAL remove card from hand
                            # This card can be rightfully added to the pile
                            for c in self._card_pile:
                                self._deck.append(c)

                            self._card_pile = [self._card_played]
                            shuffle(self._deck)

                            # Skip is no longer on top of the card pile
                            self._did_player_skip = False

                            # We can stack Draw +4(Wild)/+2 cards, and we can reply using Reverse
                            # if last_card_played.card_type in [CardType.DRAW_TWO, CardType.WILD_DRAW_FOUR]:
                            #     if last_card_played.card_type == self._card_played.card_type:
                            #         self._are_draw_cards_stacked = True
                            # else:
                            #     self.__handle_stacked_draws(active_player)

                            if len(round_players) > 2 \
                                    and last_card_played.card_type == CardType.REVERSE \
                                    and self._card_played.card_type == CardType.REVERSE:
                                # We only reverse if more than 2 players
                                round_players = self.__order_of_players_reversed(round_players, i)

                            # Remove the card from the player's hand
                            for index, card in enumerate(active_player.hand):
                                if card.card_type == self._card_played.card_type \
                                        and card.color_type == self._card_played.color_type:
                                    del active_player.hand[index]
                                    break

                    else:
                        if last_card_played == CardType.SKIP:
                            self._did_player_skip = True
                            print("A skip card was played and the player did skip their turn")
                        elif last_card_played == CardType.REVERSE:
                            # Reverse logic here for > 2 ppl game
                            if len(round_players) > 2 \
                                    and last_card_played.card_type == CardType.REVERSE:
                                # encapsulate in handle reverse
                                round_players = self.__order_of_players_reversed(round_players, i)
                            print("A reverse card was played and the player did skip their turn")
                        else:
                            # skip and draw logic here
                            self.__draw_card_to_hand(active_player, 1)
                            # print(
                            #     '{} drew a card and skipped their turn'.format(active_player.player.get_player_name()))
                            self._did_player_skip = True
                            # if last_card_played in [CardType.DRAW_TWO, CardType.WILD_DRAW_FOUR]:
                            #     self.__handle_stacked_draws(active_player)

                        continue

                    # print('{} uses action {}'.format(active_player.player.get_player_name(), player_action.action))
                    # print('{}'.format(self._card_played.get_card_text()))

                    # After the card has been played, if that player has no more cards, they win the round.
                    if len(active_player.hand) <= 0:
                        round_won = True
                        print('{} won the round!'.format(active_player.player.get_player_name()))
                        round_winners_player_ids.append(active_player.player_id)

        # After all rounds have been played, handle any Match over logic here
        print('Match is over!')
        return self.__determine_winner(round_winners_player_ids)
