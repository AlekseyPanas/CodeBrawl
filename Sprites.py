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

        # Center position of object
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
        self.update(screen, game)

    def render(self, screen, game):
        pass

    def update(self, screen, game):
        pass

    # Reacts to collision with obj
    def collision_react(self, obj):
        pass


"""
    - Health module = +5 HP / 1 radius
    - Force = +.1x bullet speed / 1 radius
    - Dodge = +2% Dodge chance / 1 radius
    - Damage = +.05x damage mult / 1 radius
    - Speed = +0.1x speed mult / 1 radius
    - Energy = +10 max starting energy and capacity / 1 radius
    - Sword Length = +3px sword length / 1 radius
"""

class TooManyModules(Exception):
    def __init__(self):
        super().__init__("You cannot create a player with a radius of more than 30! (4 radius default + max 26 modules)")


class Player(Object):

    # Starting radius
    default_radius = 4

    # Max radius including default
    max_radius = 30

    def __init__(self, pos, mod_force=0, mod_dodge=0, mod_dmg=0, mod_spd=0, mod_energy=0, mod_swrd=0, mod_hp=0):
        super().__init__(None, 10, {})

        # All modules in an array
        modules = [mod_force, mod_dodge, mod_dmg, mod_spd, mod_energy, mod_swrd, mod_hp]
        # Sum of all modules
        total_mods = sum(modules)

        # Checks if too many modules were specified
        if total_mods + Player.default_radius > Player.max_radius:
            raise TooManyModules

        # Sets radius
        self.radius = total_mods + Player.default_radius

        # Sets initial position
        self.pos = list(pos)

        # Sets physics descriptor
        self.physics_body = Utilities.CircleBody(self.radius)

        # Creates sprite surface
        self.render_body = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA, 32)

        cur_rad = self.radius
        for mod in range(len(modules)):
            mod_val = modules[mod]

            color = (0, 0, 0)
            # Module colors
            if mod == 0:
                # Force module color
                color = (200, 200, 0)
            elif mod == 1:
                # Dodge module color
                color = (0, 70, 150)
            elif mod == 2:
                # Damage module color
                color = (0, 0, 200)
            elif mod == 3:
                # Speed module color
                color = (190, 170, 170)
            elif mod == 4:
                # Energy module color
                color = (0, 200, 0)
            elif mod == 5:
                # Sword module color
                color = (150, 150, 170)
            elif mod == 6:
                # Health module color
                color = (255, 0, 0)

            # Draws circle
            pygame.draw.circle(self.render_body, color, (self.radius, self.radius), cur_rad)
            # Decrements radius (so next module circle is farther in)
            cur_rad -= mod_val

        self.render_body = self.render_body.convert_alpha()

    def render(self, screen, game):
        screen.blit(self.render_body, self.render_body.get_rect(center=self.pos))

    def update(self, screen, game):
        pass

    # Reacts to collision with obj
    def collision_react(self, obj):
        pass
