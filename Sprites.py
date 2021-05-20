import Constants
import Utilities
import math
import pygame


class Object:
    def __init__(self, lifetime, z_order, tags):
        self.lifetime = lifetime
        self.kill = False

        # Draw order
        self.z_order = z_order

        # Set of string tags that can identify an object
        self.tags = set(tags)

        # Position of object
        self.pos = None

        # Separate physics from appearance
        self.render_body = None
        self.physics_body = None

    @staticmethod
    def rotate(image, rect, angle):
        """Rotate the image while keeping its center."""
        # Rotate the original image without modifying it.
        new_image = pygame.transform.rotate(image, angle)
        # Get a new rect with the center of the old rect.
        rect = new_image.get_rect(center=rect.center)
        return new_image, rect

    def run_sprite(self, screen, game):
        self.render(screen, game)
        if not game.PAUSED and not game.IS_CUTSCENE:
            self.update(screen, game)

    def render(self, screen, game):
        pass

    def update(self, screen, game):
        pass
