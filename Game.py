import pygame
import Constants
import Utilities
import Sprites
import math
import time


class Game:
    def __init__(self, screen_width=1000):
        # Screen info
        self.SCREEN_SIZE = int(screen_width), int(screen_width * Constants.SCREEN_WIDTH2HEIGHT)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.DOUBLEBUF)

        # All sprites in the game
        self.SPRITES = [Sprites.Player((300, 300)),
                        Sprites.Player((300, 500), mod_spd=26),
                        Sprites.Bullet((195, 300), 0, 1, Sprites.Bullet.BulletTypes.HIGH_VEL),
                        Sprites.Bullet((187, 300), 0, 1, Sprites.Bullet.BulletTypes.REGULAR)]
        self.SPRITES.append(Sprites.Missile((700, 700), self.SPRITES[1], 3))

        # Sprite queues
        self.sprite_remove_queue = []
        self.sprite_add_queue = []

        # Loop flag
        self.running = True

        # Events list
        self.events = []

    def add_sprite(self, sprite: Sprites.Object):
        self.sprite_add_queue.append(sprite)

    def kill_sprite(self, sprite: Sprites.Object):
        self.sprite_remove_queue.append(sprite)

    # Checks if given hitbox and center are out of bounds
    def is_out_of_bounds(self, physics_body, center):
        # width/height or radius for out of bounds detection
        w = 0
        h = 0
        if physics_body.type == Utilities.PhysTypes.RECT:
            w = physics_body.rect.get_width() / 2
            h = physics_body.rect.get_height() / 2
        elif physics_body.type == Utilities.PhysTypes.CIRCLE:
            w = physics_body.radius
            h = physics_body.radius

        # Collision detected
        if center[0] + w >= self.SCREEN_SIZE[0] or center[0] - w <= 0 or center[1] + h >= self.SCREEN_SIZE[1] or center[1] - h <= 0:
            return True
        return False

    def run_game(self):
        fps = 0
        last_fps_show = 0
        clock = pygame.time.Clock()

        while self.running:
            # Increments tick variable
            Constants.tick += 1

            # Sets events
            self.events = pygame.event.get()

            # Clears screen
            self.screen.fill((50, 50, 50))

            # Game event loop
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Runs sprites
            for spr1 in range(len(self.SPRITES)):
                sprite1 = self.SPRITES[spr1]

                # DEBUG #################################################################################
                if "ply" in sprite1.tags:
                    sprite1.move(vector_horizontal=math.cos(time.time()), vector_vertical=math.sin(time.time()))
                # #######################################################################################

                # Checks if collision with wall occured and reacts accordingly
                if self.is_out_of_bounds(sprite1.physics_body, sprite1.pos):
                    sprite1.collision_wall_react()

                else:
                    # Collision detection optimized loop
                    for spr2 in range(spr1 + 1, len(self.SPRITES)):
                        sprite2 = self.SPRITES[spr2]

                        # List of all position combinations to check
                        sprite1_positions = [sprite1.pos]
                        sprite2_positions = [sprite2.pos]

                        # Bullets that are travelling super fast will be tested against an additional midpt
                        for spr, pos_arr in ((sprite1, sprite1_positions), (sprite2, sprite2_positions)):
                            if "bullet" in spr.tags and spr.speed > Constants.BULLET_MIDPT_SPEED_MIN:
                                # Adds pos of bullet midway to its future pos according to its velocity
                                pos_arr.append((spr.pos[0] + (spr.vector[0] * (spr.speed / 2)),
                                                spr.pos[1] + (spr.vector[1] * (spr.speed / 2))))

                        break_flag = False
                        # Checks collision of sprites across all midway pts
                        for spr1_pos in sprite1_positions:
                            for spr2_pos in sprite2_positions:
                                if Utilities.is_colliding(sprite1.physics_body, spr1_pos, sprite2.physics_body, spr2_pos):
                                    # Calls reaction methods
                                    sprite1.collision_react(sprite2)
                                    sprite2.collision_react(sprite1)

                                    # Breaks both loops
                                    break_flag = True
                                    break
                            if break_flag:
                                break

                # Runs sprite logic
                sprite1.run_sprite(self.screen, self)
                if sprite1.lifetime is not None:
                    sprite1.lifetime -= 1

                # Checks if sprite is dead
                if sprite1.kill or (sprite1.lifetime is not None and sprite1.lifetime <= 0):
                    sprite1.death_procedure()
                    self.sprite_remove_queue.append(sprite1)

            # Updates display
            pygame.display.update()

            # Manages post frame sprite stuff
            #################################

            # Adds new sprites
            if len(self.sprite_add_queue):
                for spr in self.sprite_add_queue:
                    self.SPRITES.append(spr)
                # Resort sprites by z order (for drawing purposes) (lower z order = under)
                self.SPRITES = sorted(self.SPRITES, key=lambda s: s.z_order)
                # Clears queue
                self.sprite_add_queue = []

            # Removes sprites
            if len(self.sprite_remove_queue):
                for spr in self.sprite_remove_queue:
                    if spr in self.SPRITES:
                        self.SPRITES.remove(spr)
                # Clears queue
                self.sprite_remove_queue = []

            # sets fps to a variable. can be set to caption any time for testing.
            last_fps_show += 1
            if last_fps_show == 30:  # every 30th frame:
                fps = clock.get_fps()
                pygame.display.set_caption("FPS: " + str(fps))
                last_fps_show = 0

            # fps max 60
            clock.tick(60)
