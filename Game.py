import pygame
import Constants
import Utilities
import Sprites
import math
import time
import random
import Map


class Game:
    def __init__(self, screen_width=1000):
        # Screen info
        self.SCREEN_SIZE = int(screen_width), int(screen_width * Constants.SCREEN_WIDTH2HEIGHT)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.DOUBLEBUF)

        # All sprites in the game
        self.SPRITES = [Sprites.Player((300, 400), mod_spd=26),
                        Sprites.Player((300, 500), mod_dodge=26)]
        #self.SPRITES.append(Sprites.Missile((700, 700), self.SPRITES[0]))

        # Bullet Lag Test
        """for _ in range(200):
            self.SPRITES.append(Sprites.Bullet((random.randint(50, 900), random.randint(50, 900)), random.randint(0, 359),
                                                Sprites.Bullet.BulletTypes.REGULAR))"""

        self.test_thingie = self.SPRITES[0]

        # Additional sprite separation lists
        self.POWERUPS = []

        # Sprite queues
        self.sprite_remove_queue = []
        self.sprite_add_queue = []

        # Loop flag
        self.running = True

        # Map object for game
        self.map = Map.Map()
        self.map.generate_map(self)

        # Events list
        self.events = []

        # Sorts Sprites
        self.SPRITES = sorted(self.SPRITES, key=lambda s: s.z_order)

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
            self.screen.fill((30, 50, 40))

            # Runs map (Delay is needed so that initial powerups are added)
            if Constants.tick > 1:
                self.map.run_map(self)

            # Game event loop
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.test_thingie.use_sword(self, math.degrees(math.atan2(-(event.pos[1] - self.test_thingie.pos[1]), event.pos[0] - self.test_thingie.pos[0])))

            self.test_thingie.move(vector_horizontal=-pygame.key.get_pressed()[pygame.K_LEFT] + pygame.key.get_pressed()[pygame.K_RIGHT],
                                   vector_vertical=-pygame.key.get_pressed()[pygame.K_UP] + pygame.key.get_pressed()[pygame.K_DOWN])

            # Counts how many times the loop ran
            fire_count = 0
            # Runs sprites
            for spr1 in range(len(self.SPRITES)):
                sprite1 = self.SPRITES[spr1]

                # DEBUG #################################################################################
                if "ply" in sprite1.tags:
                    #sprite1.move(vector_horizontal=math.cos(time.time()), vector_vertical=math.sin(time.time()))

                    if Constants.tick % 20 == 0:
                        sprite1.shoot_bullet(self, Sprites.Bullet.BulletTypes.REGULAR, Constants.tick*1.2)
                        sprite1.shoot_bullet(self, Sprites.Bullet.BulletTypes.HIGH_VEL, Constants.tick * 1.2)
                        sprite1.shoot_missile(self, random.choice(self.SPRITES))

                        #sprite1.use_sword(self, random.randint(1, 359))
                # #######################################################################################

                # Must have physics
                if sprite1.physics_body is not None:
                #if False:

                    # Checks if collision with wall occured and reacts accordingly
                    if self.is_out_of_bounds(sprite1.physics_body, sprite1.pos):
                        sprite1.collision_wall_react(self)

                    else:
                        # Collision detection optimized loop
                        for spr2 in range(spr1 + 1, len(self.SPRITES)):
                            sprite2 = self.SPRITES[spr2]

                            # Must have physics
                            if sprite2.physics_body is not None:

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
                                        # Counts loop runs
                                        fire_count += 1
                                        if Utilities.is_colliding(sprite1.physics_body, spr1_pos, sprite2.physics_body, spr2_pos):
                                            # Calls reaction methods
                                            sprite1.collision_react(self, sprite2)
                                            sprite2.collision_react(self, sprite1)

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
                    sprite1.death_procedure(self)
                    self.sprite_remove_queue.append(sprite1)

            # Uncomment for debug, counts how many times the collision loops fired all together
            #print("FireCount", fire_count)
            #print()

            # Updates display
            pygame.display.update()

            # Manages post frame sprite stuff
            #################################

            # Adds new sprites
            if len(self.sprite_add_queue):
                for spr in self.sprite_add_queue:

                    # Adds item to additional separation lists for easier searching
                    if "pwp" in spr.tags:
                        self.POWERUPS.append(spr)

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
                    if spr in self.POWERUPS:
                        self.POWERUPS.remove(spr)
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
