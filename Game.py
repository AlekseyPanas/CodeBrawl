import pygame
import Constants
import Utilities
import Sprites
import math
import time
import random
import Map
import server
import Button
import GameData


class Game:

    def __init__(self, screen_width=1000):
        # Screen info
        self.SCREEN_SIZE = int(screen_width), int(screen_width * Constants.SCREEN_WIDTH2HEIGHT)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.DOUBLEBUF)

        # All sprites in the game
        #self.SPRITES = [Sprites.Player((300, 400), 0, 0, mod_swrd=26),  #mod_hp=10, mod_energy=6, mod_force=6, mod_spd=4),
        #                Sprites.Player((300, 500), 0, 0, mod_dodge=26)]
        #self.SPRITES.append(Sprites.Missile((700, 700), self.SPRITES[0]))
        self.SPRITES = []

        # Bullet Lag Test
        """for _ in range(200):
            self.SPRITES.append(Sprites.Bullet((random.randint(50, 900), random.randint(50, 900)), random.randint(0, 359),
                                                Sprites.Bullet.BulletTypes.REGULAR))"""

        #self.test_thingie = self.SPRITES[0]

        # Additional sprite separation lists
        self.POWERUPS = []

        # Sprite ID indexer
        self.next_available_id = 0

        # Sprite queues
        self.sprite_remove_queue = []
        self.sprite_add_queue = []
        self.connected_player_queue = []

        # Loop flag
        self.running = True

        # Map object for game
        self.map = Map.Map()

        # Events list
        self.events = []

        # Creates Server
        self.server = server.Server(self)

        # Large game data object
        self.game_data_manager = GameData.GameDataManager()

        # Start button for lobby
        self.start_button = Button.Button((50, 50), (100, 40), True,
                                          "assets/images/startbutton_neutral.png",
                                          "assets/images/startbutton_hover.png",
                                          "assets/images/startbutton_disabled.png")

        # Flag for main file to know whether game is starting
        self.game_starting = False

    def run_lobby(self):
        # Screen values for lobby display
        SCREEN_SIZE = 400, 700
        self.screen = pygame.display.set_mode((400, 700), pygame.DOUBLEBUF)

        # Updates start button position
        self.start_button.pos = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] - SCREEN_SIZE[1] * .05)

        # Constants for display
        FONT_SIZE = 20
        SHIFT_SPACE_MULT = 1.3

        # Pre rendered surfaces of header text and underline
        HEADER_TEXT = Utilities.get_courier(int(FONT_SIZE*1.3)).render("CONNECTED PLAYERS:", True, (0, 0, 0))
        UNDERLINE = Utilities.get_courier(int(FONT_SIZE * 1.3)).render("------------------", True, (0, 0, 0))

        lobby_loop = True
        # Runs lobby Loop
        while lobby_loop:
            # Manages drawing lobby stuff
            #####################################
            # Clears screen
            self.screen.fill((150, 150, 190))

            # Ends loop and server upon window closure
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    lobby_loop = False
                    self.server.shutdown_server(self)

                # If start button is clicked...
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    if self.start_button.is_clicked(event.pos):
                        lobby_loop = False
                        self.game_starting = True

            # Vertical text shift as each new name appears
            shift = 100

            # Draws headers
            self.screen.blit(HEADER_TEXT, HEADER_TEXT.get_rect(center=(SCREEN_SIZE[0]/2, 40)))
            self.screen.blit(UNDERLINE, UNDERLINE.get_rect(center=(SCREEN_SIZE[0] / 2, 60)))

            # For each queued connected player...
            for ply in self.connected_player_queue:
                # Render name of player (display name)
                name_text = Utilities.get_courier(FONT_SIZE).render(ply.display_name, True, (0, 0, 150))

                # Draw name based on shift
                self.screen.blit(name_text, name_text.get_rect(center=(SCREEN_SIZE[0] / 2, shift)))

                # Shift down for next name to appear lower
                shift += FONT_SIZE * SHIFT_SPACE_MULT

            # Displays start button
            self.start_button.run_sprite(self.screen, self)

            # Updates display
            pygame.display.update()
            #####################################

            # Enables start button after 2 players connect
            if len(self.connected_player_queue) > 1 and self.start_button.is_disabled:
                self.start_button.enable()

            # Creates new connection if ready
            if self.server.ready_for_conn:
                self.server.new_conn()

    def add_sprite(self, sprite: Sprites.Object):
        self.sprite_add_queue.append(sprite)

    def add_connecting_player(self, player: Sprites.Player):
        self.connected_player_queue.append(player)

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

    def add_new_sprites(self, queue):
        # Adds new sprites
        if len(queue):
            while len(queue):

                # Adds item to additional separation lists for easier searching
                if "pwp" in queue[0].tags:
                    self.POWERUPS.append(queue[0])

                self.SPRITES.append(queue[0])

                # Sets sprite ID to a unique ID and increments the indexer
                self.SPRITES[-1].set_id(self.next_available_id)
                self.next_available_id += 1

                # Clears queue
                queue.pop(0)

            # Resort sprites by z order (for drawing purposes) (lower z order = under)
            self.SPRITES = sorted(self.SPRITES, key=lambda s: s.z_order)

    def run_game(self):
        # Variables for FPS display and tracking
        fps = 0
        last_fps_show = 0
        clock = pygame.time.Clock()

        # Resizes screen to game size
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.DOUBLEBUF)

        # Generates map
        self.map.generate_map(self)

        # Sorts Sprites
        self.SPRITES = sorted(self.SPRITES, key=lambda s: s.z_order)

        # Adds connected players
        self.add_new_sprites(self.connected_player_queue)

        # Starts all connections
        for spr in self.SPRITES:
            if "ply" in spr.tags:
                spr.start_connection()

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
                    self.server.shutdown_server(self)

                #elif event.type == pygame.MOUSEBUTTONDOWN:
                    #self.test_thingie.use_sword(self, math.degrees(math.atan2(-(event.pos[1] - self.test_thingie.pos[1]), event.pos[0] - self.test_thingie.pos[0])))

            #self.test_thingie.move(vector_horizontal=-pygame.key.get_pressed()[pygame.K_LEFT] + pygame.key.get_pressed()[pygame.K_RIGHT],
            #                       vector_vertical=-pygame.key.get_pressed()[pygame.K_UP] + pygame.key.get_pressed()[pygame.K_DOWN])

            # Counts how many times the loop ran
            fire_count = 0
            # Runs sprites
            for spr1 in range(len(self.SPRITES)):
                sprite1 = self.SPRITES[spr1]

                # DEBUG #################################################################################
                #if "ply" in sprite1.tags:
                    #sprite1.move(vector_horizontal=math.cos(time.time()), vector_vertical=math.sin(time.time()))

                    #if Constants.tick % 20 == 0:
                    #ang = math.degrees(math.atan2(-(pygame.mouse.get_pos()[1] - self.test_thingie.pos[1]), pygame.mouse.get_pos()[0] - self.test_thingie.pos[0]))
                    #ang = Constants.tick
                    #sprite1.shoot_bullet(self, Sprites.Bullet.BulletTypes.REGULAR, ang)
                    #sprite1.shoot_bullet(self, Sprites.Bullet.BulletTypes.HIGH_VEL, ang)
                    #sprite1.shoot_missile(self, random.choice(self.SPRITES))

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
            self.add_new_sprites(self.sprite_add_queue)

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
