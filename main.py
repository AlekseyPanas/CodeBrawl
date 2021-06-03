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

# TODO: Add unique IDs to all sprites (Parent object class)
# TODO: Add game_data collection and sending to each frame of game (json object formation)
# TODO: Make main loop wait until all client players respond, or until a time limit is met
# TODO: Build Python client
# TODO: Build Java client
# TODO: Build C# client

# TODO: Add Win condition and display (server closure and win screen)
# TODO: Add player killing on disconnect

# TODO: Break test the app and implement corresponding error handling/ fix bugs

# TODO: Build 1v1 key controlled test game for python
# TODO: Build 1v1 key controlled test game for java and c# (include clients)
