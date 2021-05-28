import Constants
import pygame
import math
from enum import IntEnum


class PhysTypes(IntEnum):
    CIRCLE = 0
    RECT = 1


class CircleBody:
    def __init__(self, radius):
        self.radius = radius

        self.type = PhysTypes.CIRCLE


class RectBody:
    # Requires pygame rect
    def __init__(self, rect):
        self.rect = rect

        self.type = PhysTypes.RECT


def is_colliding(body1, body1_center, body2, body2_center):
    # Circle Circle
    if body1.type == PhysTypes.CIRCLE and body2.type == PhysTypes.CIRCLE:
        return distance(body1_center, body2_center) <= body1.radius + body2.radius

    # Rect Rect
    elif body1.type == PhysTypes.RECT and body2.type == PhysTypes.RECT:
        body1.rect.center = body1_center
        body2.rect.center = body2_center

        return body1.rect.colliderect(body2.rect)

    # Rect Circle
    elif (body1.type == PhysTypes.RECT and body2.type == PhysTypes.CIRCLE) or (body2.type == PhysTypes.RECT and body1.type == PhysTypes.CIRCLE):
        # Needs to be done
        return False

    else:
        # Defaults to false
        return False


# Scales a set of coordinates to the current screen size based on a divisor factor
def cscale(*coordinate, screen_size, divisor=(1000, 900)):
    if len(coordinate) > 1:
        return tuple([int(coordinate[x] / divisor[x % 2] * screen_size[x % 2]) for x in range(len(coordinate))])
    else:
        return int(coordinate[0] / divisor[0] * screen_size[0])


# Scales a set of coordinates to the current screen size based on a divisor factor. Doesn't return integers
def posscale(*coordinate, screen_size, divisor=(1000, 900)):
    if len(coordinate) > 1:
        return tuple([coordinate[x] / divisor[x % 2] * screen_size[x] for x in range(len(coordinate))])
    else:
        return coordinate[0] / divisor[0] * screen_size[0]


def load_image(path, size=None):
    img = pygame.image.load(path)
    if size is not None:
        img = pygame.transform.smoothscale(img, (int(size[0]), int(size[1])))
    return img.convert_alpha()


def distance(p, q):
    return math.sqrt((q[1] - p[1]) ** 2 + (q[0] - p[0]) ** 2)
