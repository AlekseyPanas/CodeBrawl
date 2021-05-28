import pygame
pygame.init()
# Allows for convert_alpha operations and such
pygame.display.set_mode((1000, 900), pygame.DOUBLEBUF)
import Game

GAME = Game.Game()
GAME.run_game()


"""
- Add game map logic
- Add cover boxes

- Add server logic

- build clients

- Add missile trail particles

- Optimize midpt collisions to use linear rectangle
"""
