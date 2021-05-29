import random
import Sprites
from enum import IntEnum


class Map:

    # Less than this many powerups on the map will prompt spawning
    SPAWN_THRESHOLD = 5

    # Format is an int, as in 1000 translates to 1/1000 chance
    SPAWN_CHANCE_PRE_THRESH = 600
    SPAWN_CHANCE_POST_THRESH = 80

    class PowerupTypes(IntEnum):
        MISSILE = 0
        ENERGY = 1
        REGULAR = 2
        HIGHVEL = 3

    def __init__(self):
        self.spawn_positions = []

        # Enum maps index to powerup type
        self.all_positions = [[], [], [], []]
        self.draw_chances = [10, 100, 50, 30]

    def generate_map(self, game):
        center_x = game.SCREEN_SIZE[0] / 2
        center_y = game.SCREEN_SIZE[1] / 2

        self.all_positions[Map.PowerupTypes.ENERGY.value] = [(center_x - 50, center_y), (center_x + 50, center_y), (center_x, center_y - 50), (center_x, center_y + 50)]
        for p in self.all_positions[Map.PowerupTypes.ENERGY.value]:
            game.add_sprite(Sprites.EnergyPowerup(p))

        self.all_positions[Map.PowerupTypes.MISSILE.value] = [(center_x, center_y)]
        for p in self.all_positions[Map.PowerupTypes.MISSILE.value]:
            game.add_sprite(Sprites.MissilePowerup(p))

        self.all_positions[Map.PowerupTypes.REGULAR.value] = [(center_x - 200, center_y - 200), (center_x - 200, center_y + 200), (center_x + 200, center_y - 200), (center_x + 200, center_y + 200)]
        for p in self.all_positions[Map.PowerupTypes.REGULAR.value]:
            game.add_sprite(Sprites.RegularBulletPowerup(p))

        self.all_positions[Map.PowerupTypes.HIGHVEL.value] = [(center_x - 300, center_y), (center_x + 300, center_y), (center_x, center_y - 300), (center_x, center_y + 300)]
        for p in self.all_positions[Map.PowerupTypes.HIGHVEL.value]:
            game.add_sprite(Sprites.HighvelBulletPowerup(p))

    def make_new_spawn_position(self):
        self.spawn_positions.append((random.randint(50, 950), random.randint(50, 850)))

    def run_map(self, game):
        pre_thresh_roll = random.randint(1, Map.SPAWN_CHANCE_PRE_THRESH) == 1
        post_thresh_roll = random.randint(1, Map.SPAWN_CHANCE_POST_THRESH) == 1

        # Spawn resources
        if (len(game.POWERUPS) <= Map.SPAWN_THRESHOLD and post_thresh_roll) or pre_thresh_roll:

            # Gets the winner index
            choice = random.randint(1, sum(self.draw_chances))

            # Gets the index of powerup which was the randomizer landed on
            cur_num = 0
            idx_choice = 0
            for i in range(len(self.draw_chances)):
                cur_num += self.draw_chances[i]
                if choice <= cur_num:
                    idx_choice = i
                    break

            # Chooses a position of a formerly existing powerup to place it in near vicinity
            powerup_pos_list = self.all_positions[idx_choice]
            powerup_pos_list_length = len(powerup_pos_list)

            pos_change_idx = random.randint(0, powerup_pos_list_length - 1)

            powerup_pos_list[pos_change_idx] = (min(game.SCREEN_SIZE[0] - 50, max(50, powerup_pos_list[pos_change_idx][0] + random.randint(-50, 50))),
                                                min(game.SCREEN_SIZE[1] + 50, max(50, powerup_pos_list[pos_change_idx][1] + random.randint(-50, 50))))

            # Spawns powerup
            if Map.PowerupTypes(idx_choice) == Map.PowerupTypes.MISSILE:
                game.add_sprite(Sprites.MissilePowerup(powerup_pos_list[pos_change_idx]))
            elif Map.PowerupTypes(idx_choice) == Map.PowerupTypes.REGULAR:
                game.add_sprite(Sprites.RegularBulletPowerup(powerup_pos_list[pos_change_idx]))
            elif Map.PowerupTypes(idx_choice) == Map.PowerupTypes.ENERGY:
                game.add_sprite(Sprites.EnergyPowerup(powerup_pos_list[pos_change_idx]))
            elif Map.PowerupTypes(idx_choice) == Map.PowerupTypes.HIGHVEL:
                game.add_sprite(Sprites.HighvelBulletPowerup(powerup_pos_list[pos_change_idx]))



