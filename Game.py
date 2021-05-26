import pygame
import Constants
import Utilities
import Sprites


class Game:
    def __init__(self, screen_width=1000):
        # Screen info
        self.SCREEN_SIZE = int(screen_width), int(screen_width * Constants.SCREEN_WIDTH2HEIGHT)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.DOUBLEBUF)

        # All sprites in the game
        self.SPRITES = []

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

    def run_game(self):
        fps = 0
        last_fps_show = 0
        clock = pygame.time.Clock()

        while self.running:

            # Sets events
            self.events = pygame.event.get()

            # Clears screen
            self.screen.fill((100, 100, 100))

            # Game event loop
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Runs sprites
            for spr1 in range(len(self.SPRITES)):
                sprite1 = self.SPRITES[spr1]

                # Runs sprite logic
                sprite1.run_sprite(self.screen, self)
                if sprite1.lifetime is not None:
                    sprite1.lifetime -= 1

                # Collision detection optimized loop
                for spr2 in range(spr1 + 1, len(self.SPRITES)):
                    sprite2 = self.SPRITES[spr2]

                    # Checks collision of sprites
                    if Utilities.is_colliding(sprite1.physics_body, sprite1.pos, sprite2.physics_body, sprite2.pos):
                        # Calls reaction methods
                        sprite1.collision_react(sprite2)
                        sprite2.collision_react(sprite1)

                # Checks if sprite is dead
                if sprite1.kill or (sprite1.lifetime is not None and sprite1.lifetime <= 0):
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
