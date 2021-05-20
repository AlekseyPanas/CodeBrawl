import Constants
import pygame
import math


# Scales a set of coordinates to the current screen size based on a divisor factor
def cscale(*coordinate, divisor=(850, 700)):
    if len(coordinate) > 1:
        return tuple([int(coordinate[x] / divisor[x % 2] * Constants.SCREEN_SIZE[x % 2]) for x in range(len(coordinate))])
    else:
        return int(coordinate[0] / divisor[0] * Constants.SCREEN_SIZE[0])


# Scales a set of coordinates to the current screen size based on a divisor factor. Doesn't return integers
def posscale(*coordinate, divisor=(850, 700)):
    if len(coordinate) > 1:
        return tuple([coordinate[x] / divisor[x % 2] * Constants.SCREEN_SIZE[x] for x in range(len(coordinate))])
    else:
        return coordinate[0] / divisor[0] * Constants.SCREEN_SIZE[0]


def load_image(path, size=None):
    img = pygame.image.load(path)
    if size is not None:
        img = pygame.transform.smoothscale(img, size)
    return img.convert_alpha()


def distance(p, q):
    return math.sqrt((q[1] - p[1]) ** 2 + (q[0] - p[0]) ** 2)