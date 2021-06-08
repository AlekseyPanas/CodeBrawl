import pygame
import time
import Constants
pygame.init()

# Allows for convert_alpha operations and such
pygame.display.set_mode((400, 700), pygame.DOUBLEBUF)

# Imports game
import Game


while 1:
    # Resets ticks
    Constants.tick = 0

    # Creates Game
    GAME = Game.Game()

    # Runs lobby which awaits and managed connections
    GAME.run_lobby()

    # Starts game if lobby is ready
    if GAME.game_starting:
        GAME.run_game()

        if GAME.end_game:
            break
    else:
        break


# TODO: Build Java client
# TODO: Build C# client
