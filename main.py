import pygame
import time
pygame.init()

# Allows for convert_alpha operations and such
pygame.display.set_mode((400, 700), pygame.DOUBLEBUF)

# Imports game
import Game

# Creates Game
GAME = Game.Game()

# Runs lobby which awaits and managed connections
GAME.run_lobby()

# Starts game if lobby is ready
if GAME.game_starting:
    GAME.run_game()

# TODO: Add failed commands notification

# TODO: Build Java client
# TODO: Build C# client

# TODO: Add Win condition and display (server closure and win screen)

# TODO: Break test the app and implement corresponding error handling/ fix bugs

# TODO: Build 1v1 key controlled test game for python
# TODO: Build 1v1 key controlled test game for java and c# (include clients)
