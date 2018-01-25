from core.game.GameEngine import GameEngine
from Player import Player
# from players.EasyPlayer import Player as EasyPlayer
# from players.HardPlayer import Player as HardPlayer
# from players.MediumPlayer import Player as MediumPlayer
from players.RandomPlayer import RandomPlayer
from players.RandomPlayer2 import RandomPlayer2

players = [RandomPlayer(), RandomPlayer2()]

rounds = 3
# Rounds can't be even, we don't want ties
if rounds % 2 == 0:
    rounds += 1
game_engine = GameEngine(players, rounds)
game_engine.start()
