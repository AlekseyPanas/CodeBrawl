import pygame
import Game
pygame.init()

fps = 0
last_fps_show = 0
clock = pygame.time.Clock()

GAME = Game.Game()
GAME.run_game()
