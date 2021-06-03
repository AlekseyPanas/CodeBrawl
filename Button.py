import pygame
import Sprites
import Utilities


class Button(Sprites.Object):

    def __init__(self, pos, size, is_disabled, static_image_path, hover_image_path, disabled_image_path):
        super().__init__(None, pos, 0, {})

        # Position of center of button.
        self.pos = list(pos)

        # Width/height of image and the loaded image.
        self.size = size

        # Sprites
        self.static_image = Utilities.load_image(static_image_path, size=size)
        self.hover_image = Utilities.load_image(hover_image_path, size=size)
        self.disabled_image = Utilities.load_image(disabled_image_path, size=size)

        # Current Sprite
        self.current_image = self.static_image

        self.button_rect = self.static_image.get_rect(center=self.pos)

        self.is_disabled = is_disabled

    def run_sprite(self, screen, game):
        self.render(screen, game)
        self.update(screen, game)

    def render(self, screen, game):
        screen.blit(self.current_image, self.button_rect)

    def update(self, screen, game):
        # Sets current image
        if self.is_disabled:
            self.current_image = self.disabled_image
        elif self.button_rect.collidepoint(pygame.mouse.get_pos()):
            self.current_image = self.hover_image
        else:
            self.current_image = self.static_image

        # Sets rect center
        self.button_rect.center = (self.pos[0], self.pos[1])

    def enable(self):
        self.is_disabled = False

    def disable(self):
        self.is_disabled = True

    def is_clicked(self, pos):
        return (not self.is_disabled) and self.button_rect.collidepoint(pos)
