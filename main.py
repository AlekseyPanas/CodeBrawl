import pygame
pygame.init()
# Allows for convert_alpha operations and such
pygame.display.set_mode((1000, 900), pygame.DOUBLEBUF)
import Game

fps = 0
last_fps_show = 0
clock = pygame.time.Clock()

GAME = Game.Game()
GAME.run_game()


"""
- Add inflate surface damage indicators (with DODGE when dodged)
- Add fragmentation of player when dead
- Add explosion animation for missile collision

- Add missile trail particles
"""
