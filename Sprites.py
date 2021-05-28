import Constants
import Utilities
import math
import pygame
import time
import random
import copy
from enum import IntEnum


class Object:
    def __init__(self, lifetime, pos, z_order, tags):
        self.lifetime = lifetime
        self.kill = False

        # Draw order
        self.z_order = z_order

        # Set of string tags that can identify an object
        self.tags = set(tags)

        # Center position of object
        self.pos = list(pos)

        # Separate physics from appearance
        self.render_body = None
        self.physics_body = None

    @staticmethod
    def rotate(image, rect, angle):
        """Rotate the image while keeping its center."""
        # Rotate the original image without modifying it.
        new_image = pygame.transform.rotate(image, angle).convert_alpha()
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
    def collision_react(self, game, obj):
        pass

    # Reacts to collision with map bounds
    def collision_wall_react(self, game):
        pass

    # Called once when sprite is resolved for deletion
    def death_procedure(self, game):
        pass


class TooManyModules(Exception):
    def __init__(self):
        super().__init__("You cannot create a player with a radius of more than 30! (4 radius default + max 26 modules)")


class Sword(Object):

    SWORD_DAMAGE = 30
    # Default length
    SWORD_LENGTH = 35

    # How fast the sword is deployed (value of render_shift towards circle center is multiplied by this every tick)
    DEPLOYMENT_MULT = 0.8
    SHEATH_MULT = 1.2

    # How long until it begins to retract
    DEPLOYMENT_TIME = 30
    # How many ticks until the sword deals damage
    HIT_DELAY = DEPLOYMENT_TIME / 5

    def __init__(self, parent, angle, sword_length_add=0, dmg_mult=1.0):
        super().__init__(None, parent.pos, -1, {})
        self.tags.add("sword")

        # Player who deployed the sword
        self.parent = parent

        # Vector in the direction of the angle based on radius of parent
        self.vector = (math.cos(math.radians(angle)) * (parent.radius + Sword.SWORD_LENGTH / 2),
                       -math.sin(math.radians(angle)) * (parent.radius + Sword.SWORD_LENGTH / 2))

        # Sets position
        self.update_pos()

        self.render_shift = list(copy.copy(self.vector))

        # The sword can only hit targets once
        self.hit_targets = []

        self.sword_length = Sword.SWORD_LENGTH + sword_length_add
        self.sword_damage = Sword.SWORD_DAMAGE * dmg_mult

        self.physics_body = Utilities.CircleBody(self.sword_length / 2)
        self.render_body = pygame.transform.rotate(Utilities.load_image("assets/images/sword.png", size=(self.sword_length, 10)), angle).convert_alpha()

        # Tracks how long it has been deployed
        self.counter = 0

        # If 2 swords clash, damage is cancelled
        self.cancel_hit = False

        # Debug circle color
        self.col = (0, 255, 0)

    def update(self, screen, game):
        self.update_pos()

        # Deploys Sword
        if self.counter < Sword.DEPLOYMENT_TIME:
            self.render_shift[0] *= Sword.DEPLOYMENT_MULT
            self.render_shift[1] *= Sword.DEPLOYMENT_MULT
        else:
            self.render_shift[0] *= Sword.SHEATH_MULT
            self.render_shift[1] *= Sword.SHEATH_MULT
            if abs(self.render_shift[0]) > abs(self.vector[0]):
                self.kill = True

        self.counter += 1

        # Debug color change
        if self.counter > Sword.HIT_DELAY and not self.col == (0, 0, 255):
            self.col = (255, 0, 0)

    def update_pos(self):
        self.pos = [self.parent.pos[0] + self.vector[0],
                    self.parent.pos[1] + self.vector[1]]

    def render(self, screen, game):
        screen.blit(self.render_body, self.render_body.get_rect(center=(self.pos[0] - self.render_shift[0],
                                                                        self.pos[1] - self.render_shift[1])))

        pygame.draw.circle(screen, self.col, self.pos, self.physics_body.radius, width=1)

    def collision_react(self, game, obj):
        if not obj == self.parent and obj not in self.hit_targets:

            if "ply" not in obj.tags or self.counter > Sword.HIT_DELAY:
                self.hit_targets.append(obj)

            if "sword" in obj.tags:
                self.cancel_hit = True
                self.col = (0, 0, 255)

                avg_pos = (self.pos[0] + obj.pos[0]) / 2, (self.pos[1] + obj.pos[1]) / 2
                game.add_sprite(SwordClashCircle(avg_pos, inflate_time=random.randint(15, 30)))

            if "ply" in obj.tags and self.counter > Sword.HIT_DELAY and not self.cancel_hit:
                obj.deal_damage(game, self.sword_damage)

    def death_procedure(self, game):
        self.parent.is_sword_deployed = False
        self.parent.sword = None


class Player(Object):

    # Starting radius
    default_radius = 4

    # Starting HP
    default_health = default_radius * 5

    # Default movement speed, in pixels
    default_speed = 2

    # Default energy
    default_energy = 100

    # Stat constants
    HEALTH_PER_RADIUS = 5
    FORCE_PER_RADIUS = .1   # Bullet speed multiplier
    DODGE_PER_RADIUS = 2   # Percent chance
    DAMAGE_PER_RADIUS = .1  # Multiplier
    SPEED_PER_RADIUS = .1  # Multiplier
    ENERGY_PER_RADIUS = 10  # Adds to starting energy and max capacity for later gain
    SWORD_PER_RADIUS = 3  # Pixels in length

    # Max radius including default
    max_radius = 30

    # Energy deduction multiplier (pixel distance travelled is multiplied by this value to calculte deduction)
    ENERGY_DEDUCTION_MULT = 0.02

    # Cost to use sword
    SWORD_ENERGY_DEDUCTION = 10

    def __init__(self, pos, mod_force=0, mod_dodge=0, mod_dmg=0, mod_spd=0, mod_energy=0, mod_swrd=0, mod_hp=0):
        super().__init__(None, pos, 10, {})
        self.tags.add("ply")

        # All modules in an array
        modules = [mod_force, mod_dodge, mod_dmg, mod_spd, mod_energy, mod_swrd, mod_hp]
        # Sum of all modules
        total_mods = sum(modules)

        # Checks if too many modules were specified
        if total_mods + Player.default_radius > Player.max_radius:
            raise TooManyModules

        # Sets radius
        self.radius = total_mods + Player.default_radius

        # Determines stats
        self.MAX_HEALTH = Player.default_health + (mod_hp * Player.HEALTH_PER_RADIUS)
        self.BULLET_SPEED_MULT = 1 + (Player.FORCE_PER_RADIUS * mod_force)
        self.DODGE_CHANCE = Player.DODGE_PER_RADIUS * mod_dodge
        self.DAMAGE_MULT = 1 + (Player.DAMAGE_PER_RADIUS * mod_dmg)
        self.SPEED = int((1 + (Player.SPEED_PER_RADIUS * mod_spd)) * Player.default_speed)
        self.MAX_ENERGY = (Player.ENERGY_PER_RADIUS * mod_energy) + Player.default_energy
        self.SWORD_LENGTH = Player.SWORD_PER_RADIUS * mod_swrd

        # Current stat trackers, initially copies of max
        self.health = self.MAX_HEALTH
        self.energy = self.MAX_ENERGY

        # Sets physics descriptor
        self.physics_body = Utilities.CircleBody(self.radius)

        # Creates sprite surface
        self.render_body = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA, 32)

        # Ammo inventory where index corresponds to bullet type
        self.ammo_bag = [50, 0, 0]

        # Flag whether or not sword is in use
        self.is_sword_deployed = False
        self.sword = None

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

        # Game State Related Variables
        ##############################

        # Vector from -1-1 which will by multiplied by the speed to move the player horizontally or vertically
        self.vel_vertical = 0
        self.vel_horizontal = 0

    def deal_damage(self, game, damage):
        # Rolls dodge chance and deals damage
        if random.randint(1, 100) > self.DODGE_CHANCE:
            self.health -= damage

            # Adds damage indicator
            game.add_sprite(get_damage_inflate(damage, self.pos))
        else:
            # Adds dodge indicator
            game.add_sprite(get_damage_inflate("DODGE", self.pos, is_string=True, color=(150, 150, 255)))

    def add_ammo(self, ammo_type, quantity):
        self.ammo_bag[ammo_type.value] += quantity

    def add_energy(self, energy):
        self.energy += energy
        if self.energy > self.MAX_ENERGY:
            self.energy = self.MAX_ENERGY

    def render(self, screen, game):
        screen.blit(self.render_body, self.render_body.get_rect(center=self.pos))

    # Call this method to move the player during the next update tick
    def move(self, vector_horizontal=0, vector_vertical=0):
        # Keeps within -1, 1 bounds
        self.vel_horizontal = min(max(-1, vector_horizontal), 1)
        self.vel_vertical = min(max(-1, vector_vertical), 1)

    def use_sword(self, game, angle):
        if not self.is_sword_deployed and self.energy >= Player.SWORD_ENERGY_DEDUCTION:
            self.is_sword_deployed = True

            self.sword = Sword(self, angle, sword_length_add=self.SWORD_LENGTH, dmg_mult=self.DAMAGE_MULT)
            game.add_sprite(self.sword)

            self.energy -= Player.SWORD_ENERGY_DEDUCTION

    def shoot_bullet(self, game, ammo_type, angle):
        # Checks if ammo is available
        if self.ammo_bag[ammo_type.value]:
            self.ammo_bag[ammo_type.value] -= 1

            # Shifts position to edge of circle
            pos = (self.pos[0] + math.cos(math.radians(angle)) * self.radius,
                   self.pos[1] + -math.sin(math.radians(angle)) * self.radius)
            game.add_sprite(Bullet(copy.copy(pos), angle, ammo_type, speed_mult=self.BULLET_SPEED_MULT, dmg_mult=self.DAMAGE_MULT, shooter=self))

    # Target must be object
    def shoot_missile(self, game, target):
        if self.ammo_bag[Bullet.BulletTypes.MISSILE.value]:
            self.ammo_bag[Bullet.BulletTypes.MISSILE.value] -= 1

            # Rocket go fly fly
            game.add_sprite(Missile(copy.copy(self.pos), target, speed_mult=self.BULLET_SPEED_MULT, dmg_mult=self.DAMAGE_MULT, shooter=self))

    def update(self, screen, game):
        self.manage_movement(game)

        # Kills if ded
        if self.health <= 0:
            self.kill = True

        print(self.energy)

    # Actually moves the player
    def manage_movement(self, game):
        # For energy deduction calculation
        vels = [0, 0]

        if self.vel_horizontal:
            # Calculates distance to move horizontally
            dist = self.SPEED * self.vel_horizontal

            # Halves if no energy
            if self.energy == 0:
                dist /= 2

            # Cancels movement if moving out of bounds of the map
            if game.is_out_of_bounds(self.physics_body, (self.pos[0] + dist, self.pos[1])):
                dist = 0

            # Moves player
            self.pos[0] += dist

            # For calculating energy deduction below
            vels[0] = abs(dist)

            # Resets values for next frame
            self.vel_horizontal = 0

        if self.vel_vertical:
            # Calculates distance to move vertically
            dist = self.SPEED * self.vel_vertical

            # Halves if no energy
            if self.energy == 0:
                dist /= 2

            # Cancels movement if moving out of bounds of the map
            if game.is_out_of_bounds(self.physics_body, (self.pos[0], self.pos[1] + dist)):
                dist = 0

            # Moves player
            self.pos[1] += dist

            # For calculating energy deduction below
            vels[1] = abs(dist)

            # Resets values for next frame
            self.vel_vertical = 0

        # Deducts energy based on distance moved
        energy_deduction = math.sqrt(vels[0] ** 2 + vels[1] ** 2) * Player.ENERGY_DEDUCTION_MULT
        if self.energy > 0 and energy_deduction > 0:
            self.energy -= energy_deduction
            if self.energy < 0:
                self.energy = 0

    # Reacts to collision with obj
    def collision_react(self, game, obj):
        pass

    def death_procedure(self, game):
        if self.sword is not None:
            self.sword.kill = True

        # Adds animation fragments
        for obj in fragmentate(self.render_body, self.pos):
            game.add_sprite(obj)


class Bullet(Object):

    class BulletTypes(IntEnum):
        REGULAR = 0
        HIGH_VEL = 1
        MISSILE = 2

    # Radius for bullet collision
    BULLET_RADII = {BulletTypes.HIGH_VEL: 4,
                    BulletTypes.REGULAR: 3,
                    BulletTypes.MISSILE: 15}

    BULLET_IMAGES = {BulletTypes.HIGH_VEL: Utilities.load_image("assets/images/high_vel_bullet.png", size=(15, 3)),
                     BulletTypes.REGULAR: Utilities.load_image("assets/images/regular_bullet.png", size=(10, 4)),
                     BulletTypes.MISSILE: Utilities.load_image("assets/images/missile.png", size=(30, 20))}

    BULLET_DAMAGE = {BulletTypes.HIGH_VEL: 7,
                     BulletTypes.REGULAR: 5,
                     BulletTypes.MISSILE: 15}

    BULLET_SPEED = {BulletTypes.HIGH_VEL: 8,
                    BulletTypes.REGULAR: 3,
                    BulletTypes.MISSILE: 3}

    # Angle must be provided in degrees
    def __init__(self, pos, angle, bullet_type, speed_mult=1.0, dmg_mult=1.0, shooter=None):
        super().__init__(None, pos, 0, {})
        self.tags.add("bullet")

        # Object reference to shooter
        self.shooter = shooter

        # X,Y vector with a hypotenuse of 1 (to be multiplied by speed)
        self.vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))

        # Int Enum of bullet type
        self.bullet_type = bullet_type

        # Pixel speed of the bullet (distance change per frame)
        self.speed = Bullet.BULLET_SPEED[self.bullet_type] * speed_mult

        # Gets sprite
        self.render_body = self.get_image(angle)
        # Sets physics body
        self.physics_body = Utilities.CircleBody(Bullet.BULLET_RADII[self.bullet_type])

        # Bullet damage upon collision with player
        self.damage = round(Bullet.BULLET_DAMAGE[self.bullet_type] * dmg_mult)

        # DEBUG
        self.col = (255, 0, 0)

    def get_image(self, angle):
        return Bullet.BULLET_IMAGES[self.bullet_type] if angle == 0 else pygame.transform.rotate(Bullet.BULLET_IMAGES[self.bullet_type], angle).convert_alpha()

    def render(self, screen, game):
        screen.blit(self.render_body, self.render_body.get_rect(center=self.pos))
        pygame.draw.circle(screen, self.col, self.pos, self.physics_body.radius, width=1)

    def update(self, screen, game):
        #if Constants.tick % 20 == 0:
        self.pos[0] += self.vector[0] * self.speed
        self.pos[1] += self.vector[1] * self.speed

        self.col = (255, 0, 0)

    def collision_react(self, game, obj):
        # Not colliding with shooter
        if not obj == self.shooter:
            # Not colliding with bullets shot by shooter
            if not ("bullet" in obj.tags and obj.shooter == self.shooter):
                # Not colliding with shooter's sword
                if not ("sword" in obj.tags and obj.parent == self.shooter):
                    # Not colliding with a powerup
                    if not "pwp" in obj.tags:
                        # Deletes bullet upon any collision
                        self.kill = True

                        # Deals damage if player
                        if "ply" in obj.tags:
                            obj.deal_damage(game, self.damage)

                        # Debug color change
                        self.col = (0, 255, 0)

    def collision_wall_react(self, game):
        self.kill = True

    def death_procedure(self, game):
        # Missiles explode on death
        if self.bullet_type == Bullet.BulletTypes.MISSILE:
            game.add_sprite(Explosion(self.pos))

    def update_vector(self, angle):
        self.vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))


class Missile(Bullet):

    # Angle change per tick to face target
    TURNABILITY = 0.2

    MISSILE_LIFETIME = 500

    def __init__(self, pos, target_object, speed_mult=1.0, dmg_mult=1.0, shooter=None):
        super().__init__(pos, 0, Bullet.BulletTypes.MISSILE, speed_mult=speed_mult, dmg_mult=dmg_mult, shooter=shooter)

        # Sets lifetime
        self.lifetime = Missile.MISSILE_LIFETIME

        # Target player
        self.target = target_object

        # Angles missile in direction of target
        self.angle = self.get_proposed_angle()

    def render(self, screen, game):
        # Rotates image
        self.render_body = self.get_image(self.angle)

        # Draws image
        screen.blit(self.render_body, self.render_body.get_rect(center=self.pos))
        pygame.draw.circle(screen, self.col, self.pos, self.physics_body.radius, width=1)

    def fixate_target(self):
        proposed_angle = self.get_proposed_angle()

        if proposed_angle - self.angle > 0:
            self.angle += Missile.TURNABILITY * self.speed
        elif proposed_angle - self.angle < 0:
            self.angle -= Missile.TURNABILITY * self.speed

    # Gets the angle needed to face target
    def get_proposed_angle(self):
        # Updates angle to curve towards target
        proposed_angle = math.degrees(math.atan2(-(self.target.pos[1] - self.pos[1]), self.target.pos[0] - self.pos[0]))
        if proposed_angle < 0:
            # Sets the scale for the proposed angle to go from 0 to 360 rather than from -180 to 180
            proposed_angle = (180 - abs(proposed_angle)) + 180

        return proposed_angle

    def update(self, screen, game):
        # Face target
        self.fixate_target()
        # New vector
        self.update_vector(self.angle)

        # Move
        dist_x = self.vector[0] * self.speed
        dist_y = self.vector[1] * self.speed
        self.pos[0] += dist_x
        self.pos[1] += dist_y

        self.col = (255, 0, 0)

        # Spawn particle
        if Constants.tick % 3 == 0:
            shift_x = random.randint(-100, 100) / 100 * (self.speed / 5)
            shift_y = random.randint(-100, 100) / 100 * (self.speed / 5)

            game.add_sprite(MissileTrailParticle(copy.copy(self.pos), (-dist_x + shift_x, -dist_y + shift_y)))


# Creates moving, rotating, fading, and inflating surfaces for visual effects
class InflateSurface(Object):
    def __init__(self, lifetime, z_order, tags, surface, start_scale, stop_scale, scale_time, pos, fade=False,
                 initial_opacity=255, delay_inflation=0, vel=(0, 0), angle_vel=0.0):
        super().__init__(lifetime, pos, z_order, tags)

        self.surface_rect = surface.get_rect()

        self.vel = vel

        self.angle = 0
        self.angle_vel = angle_vel

        self.start_scale = (self.surface_rect.w * start_scale, self.surface_rect.h * start_scale)
        self.stop_scale = (self.surface_rect.w * stop_scale, self.surface_rect.h * stop_scale)
        self.scale_time = scale_time
        self.current_scale = list(copy.copy(self.start_scale))
        self.scale_increment = ((self.stop_scale[0] - self.start_scale[0]) / self.scale_time,
                                (self.stop_scale[1] - self.start_scale[1]) / self.scale_time)

        self.surface = pygame.Surface(self.surface_rect.size, pygame.SRCALPHA, 32).convert_alpha()
        self.surface.blit(surface, (0, 0))

        self.opacity = initial_opacity
        self.fade_increment = (self.opacity + 1) / self.scale_time
        self.fade = fade

        # Delays inflation for a given amount of time
        self.delay_inflation = delay_inflation

    def update(self, screen, game):
        if self.delay_inflation == 0:
            if self.current_scale[0] < self.stop_scale[0]:
                self.current_scale[0] += self.scale_increment[0]
                self.current_scale[1] += self.scale_increment[1]
            if self.fade:
                self.opacity -= self.fade_increment
            if self.angle_vel:
                self.angle += self.angle_vel
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]

            self.more_logic(screen, game)
        else:
            self.delay_inflation -= 1

    def more_logic(self, screen, game):
        pass

    def render(self, screen, game):
        if self.opacity > 0:
            new_surf = pygame.transform.scale(self.surface, [int(x) for x in self.current_scale]).convert_alpha()

            if self.angle_vel:
                new_surf = pygame.transform.rotate(new_surf, self.angle).convert_alpha()

            rect = new_surf.get_rect()
            rect.center = self.pos

            if self.fade:
                new_surf.fill((255, 255, 255, self.opacity if self.opacity >= 0 else 0), None, pygame.BLEND_RGBA_MULT)

            screen.blit(new_surf, rect)


# Cuts the given surface in half and returns 2 flying inflating surfaces for the halves
def fragmentate(surf, center):
    height = surf.get_height()
    width = surf.get_width() / 2

    pos1 = center[0] - width / 2, center[1]
    pos2 = center[0] + width / 2, center[1]

    surface1 = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    surface1.blit(surf, (0, 0))
    surface1 = surface1.convert_alpha()

    surface2 = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    surface2.blit(surf, (-width, 0))
    surface2 = surface2.convert_alpha()

    return (InflateSurface(150, -1, {}, surface1, 1, 1.2, 100, pos1, fade=True,
                           angle_vel=(random.randint(-30, 30) / 10),
                           vel=(random.randint(-20, 20) / 10, random.randint(-20, 20) / 10)),
            InflateSurface(150, -1, {}, surface2, 1, 1.2, 100, pos2, fade=True,
                           angle_vel=(random.randint(-30, 30) / 10),
                           vel=(random.randint(-20, 20) / 10, random.randint(-20, 20) / 10)))


# When 2 swords block each other, this thing is spawned
class SwordClashCircle(InflateSurface):
    def __init__(self, pos, inflate_time=20):
        surf = pygame.Surface((50, 50), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(surf, (255, 255, 255), (25, 25), 25, 4)

        super().__init__(70, 50, {}, surf, 0, 2.5, inflate_time, pos, True, initial_opacity=150)


class MissileTrailParticle(InflateSurface):
    def __init__(self, pos, vel):
        surf = pygame.Surface((10, 10)).convert_alpha()
        surf.fill((255, random.randint(100, 255), 0))

        super().__init__(70, 50, {}, surf, 0.5, 1.2, random.randint(15, 30), pos, True, initial_opacity=100,
                         angle_vel=(random.randint(-20, 20) / 10), vel=vel)


# Geta arial bold font
def get_arial_font_bold(size):
    return pygame.font.SysFont("Arial", size, True)


# Gets a flying piece of red text indicating a damage value
def get_damage_inflate(damage, pos, is_string=False, color=(255, 180, 180)):
    if is_string:
        font_size = 15
    else:
        font_size = int(20 + damage / 30)

    dmg_surf = get_arial_font_bold(font_size).render(str(damage), True, color)
    return InflateSurface(200, 30, {}, dmg_surf, .5, 1.5, 50, copy.copy(pos), True, vel=(random.randint(-10, 10) / 10, -2))


class Animation(Object):
    def __init__(self, lifetime, z_order, tags, sheet_dimensions, animation_speed, sheet, pos, frame_count, binder=None):
        # If none is entered for lifetime, the lifetime is set to -1 iteration of the animation
        if lifetime == -1:
            life = frame_count * animation_speed - 1
        else:
            life = lifetime
        super().__init__(life, pos, z_order, tags)

        # The dimensions of the sprite sheet by frame count (width, height)
        self.sheet_dimensions = sheet_dimensions
        # The amount of game ticks that should pass between each frame
        self.animation_speed = animation_speed

        self.sheet_frames_w = sheet_dimensions[0]
        self.sheet_frames_h = sheet_dimensions[1]

        # The sprite sheet image
        self.sheet = sheet
        # Dimensions of an individual frame
        self.frame_width = self.sheet.get_width() / self.sheet_frames_w
        self.frame_height = self.sheet.get_height() / self.sheet_frames_h

        # Counts the ticks. Used for reference in the animation calculations
        self.tick = 0
        # Gives the current frame number
        self.frame = 1
        # Gets the vertical and horizontal frame coordinates to point to the current frame
        self.frame_pos = [0, 0]
        # Total # of frames in sheet
        self.frame_count = frame_count

        # Refers to another object to which this one is bound. The explosion will follow the binder object
        self.binder = binder

        # Surface onto which the animation will be drawn
        self.surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA, 32)
        # Calls update once to blit the first frame and resets the tick
        self.surface.blit(self.sheet, (0, 0))

    def update(self, screen, game):
        # If bound, change position
        if self.binder is not None:
            self.pos = self.binder.pos

        # Updates
        if self.tick % self.animation_speed == 0:
            # Calculates the sheet position of frame
            horizontal_pos = self.frame % self.sheet_frames_w
            self.frame_pos = ((horizontal_pos if not horizontal_pos == 0 else self.sheet_frames_w) - 1, int(self.frame / self.sheet_frames_w - .01))

            # Clears surface
            self.surface.fill((255, 255, 255, 0))

            # Resets frame when it finishes cycling the sheet
            self.frame += 1
            if self.frame > self.frame_count:
                self.frame = 1

            # Shifts the sheet accordingly and blits the frame onto the surface
            self.surface.blit(self.sheet,
                              (-self.frame_pos[0] * self.frame_width, -self.frame_pos[1] * self.frame_height))

        self.tick += 1

    def render(self, screen, game):
        # Blits surface onto screen
        screen.blit(self.surface, self.surface.get_rect(center=self.pos))


class Powerup(Animation):

    POWERUP_RADIUS = 20

    def __init__(self, sheet, pos):
        super().__init__(None, 1, {}, (4, 1), 15, sheet, pos, 4)
        self.tags.add("pwp")

        self.physics_body = Utilities.CircleBody(Powerup.POWERUP_RADIUS)


class MissilePowerup(Powerup):

    QUANTITY = 3

    def __init__(self, pos):
        super().__init__(Utilities.load_image("assets/images/missile_powerup.png", size=(200*1.2, 50*1.2)), pos)

    def collision_react(self, game, obj):
        if "ply" in obj.tags:
            self.kill = True

            obj.add_ammo(Bullet.BulletTypes.MISSILE, MissilePowerup.QUANTITY)


class RegularBulletPowerup(Powerup):

    QUANTITY = 25

    def __init__(self, pos):
        super().__init__(Utilities.load_image("assets/images/regular_bullet_powerup.png", size=(200*1.2, 50*1.2)), pos)

    def collision_react(self, game, obj):
        if "ply" in obj.tags:
            self.kill = True

            obj.add_ammo(Bullet.BulletTypes.REGULAR, MissilePowerup.QUANTITY)


class HighvelBulletPowerup(Powerup):

    QUANTITY = 15

    def __init__(self, pos):
        super().__init__(Utilities.load_image("assets/images/highvel_bullet_powerup.png", size=(200*1.2, 50*1.2)), pos)

    def collision_react(self, game, obj):
        if "ply" in obj.tags:
            self.kill = True

            obj.add_ammo(Bullet.BulletTypes.HIGH_VEL, MissilePowerup.QUANTITY)


class EnergyPowerup(Powerup):

    QUANTITY = 100

    def __init__(self, pos):
        super().__init__(Utilities.load_image("assets/images/energy_powerup.png", size=(200*1.2, 50*1.2)), pos)

    def collision_react(self, game, obj):
        if "ply" in obj.tags:
            self.kill = True

            obj.add_energy(EnergyPowerup.QUANTITY)


class Explosion(Animation):
    def __init__(self, pos):
        super().__init__(-1, 200, {}, (8, 1), 3,
                          Utilities.load_image("assets/images/Explosion.png", size=(8 * 50 * 2.5, 50 * 2.5)),
                          pos, 8)
