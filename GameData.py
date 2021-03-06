import json
import Sprites
from typing import List


class GameDataManager:
    def __init__(self, game):
        self.game_data = self.get_skeleton(game)

    def get_skeleton(self, game):
        return {
            "screen_size": game.SCREEN_SIZE,
            "players": [],

            "command_success": {
                "movement": [True, True],
                "shoot_ammo": True,
                "use_sword": True
            },

            "regular_bullets": [], "highvel_bullets": [], "missiles": [], "swords": [], "powerups": []
        }

    def get_game_data_bytes(self, movement_success: List[bool], shoot_success: bool, sword_success: bool,
                      player_id: int):
        # Sets is_you flag to True for given player
        for ply in self.game_data["players"]:
            if ply["id"] == player_id:
                ply["is_you"] = True
            else:
                ply["is_you"] = False

        # Sets success values
        self.game_data["command_success"]["movement"] = movement_success
        self.game_data["command_success"]["shoot_ammo"] = shoot_success
        self.game_data["command_success"]["use_sword"] = sword_success

        # Gives data
        return bytes(json.dumps(self.game_data, separators=(',', ':')), "utf-8")

    # Adds or updates player object
    def set_player(self, obj):
        if not obj.added_to_json:

            obj.added_to_json = True

            self.game_data["players"].append(
                {
                    "id": int(obj.id),
                    "is_you": False,
                    "display_name": obj.display_name,
                    "location": [float(i) for i in obj.pos],
                    "speed": float(obj.SPEED),
                    "radius": obj.radius,
                    "health": float(obj.health),
                    "energy": float(obj.energy),
                    "shoot_cooldown": int(obj.shooting_cooldown),
                    "regular_bullet_ammo": int(obj.ammo_bag[Sprites.Bullet.BulletTypes.REGULAR.value]),
                    "highvel_bullet_ammo": int(obj.ammo_bag[Sprites.Bullet.BulletTypes.HIGH_VEL.value]),
                    "missile_bullet_ammo": int(obj.ammo_bag[Sprites.Bullet.BulletTypes.MISSILE.value])
                }
            )

        else:
            for itm in self.game_data["players"]:
                if itm["id"] == obj.id:
                    itm["health"] = float(obj.health)
                    itm["energy"] = float(obj.energy)
                    itm["location"] = [float(i) for i in obj.pos]
                    itm["regular_bullet_ammo"] = int(obj.ammo_bag[Sprites.Bullet.BulletTypes.REGULAR.value])
                    itm["highvel_bullet_ammo"] = int(obj.ammo_bag[Sprites.Bullet.BulletTypes.HIGH_VEL.value])
                    itm["missile_bullet_ammo"] = int(obj.ammo_bag[Sprites.Bullet.BulletTypes.MISSILE.value])
                    itm["shooting_cooldown"] = int(obj.shooting_cooldown)

                    break

    def set_regular_bullet(self, obj):
        if not obj.added_to_json:
            obj.added_to_json = True

            self.game_data["regular_bullets"].append(
                {
                    "id": int(obj.id),
                    "shooter_id": int(obj.shooter.id),
                    "speed": float(obj.speed),
                    "radius": int(obj.physics_body.radius),
                    "location": [float(i) for i in obj.pos],
                    "vector": [float(i) for i in obj.vector]
                }
            )

        else:
            for itm in self.game_data["regular_bullets"]:
                if itm["id"] == obj.id:
                    itm["location"] = [float(i) for i in obj.pos]

                    break

    def set_highvel_bullet(self, obj):
        if not obj.added_to_json:
            obj.added_to_json = True

            self.game_data["highvel_bullets"].append(
                {
                    "id": int(obj.id),
                    "shooter_id": int(obj.shooter.id),
                    "speed": float(obj.speed),
                    "radius": int(obj.physics_body.radius),
                    "location": [float(i) for i in obj.pos],
                    "vector": [float(i) for i in obj.vector]
                }
            )

        else:
            for itm in self.game_data["highvel_bullets"]:
                if itm["id"] == obj.id:
                    itm["location"] = [float(i) for i in obj.pos]

                    break

    def set_missile(self, obj):
        if not obj.added_to_json:
            obj.added_to_json = True

            self.game_data["missiles"].append(
                {
                    "id": int(obj.id),
                    "shooter_id": int(obj.shooter.id),
                    "target_id": int(obj.target.id),
                    "speed": float(obj.speed),
                    "radius": int(obj.physics_body.radius),
                    "location": [float(i) for i in obj.pos],
                    "vector": [float(i) for i in obj.vector],
                    "angle": float(obj.angle)
                }
            )

        else:
            for itm in self.game_data["missiles"]:
                if itm["id"] == obj.id:
                    itm["location"] = [float(i) for i in obj.pos]
                    itm["vector"] = [float(i) for i in obj.vector]
                    itm["angle"] = float(obj.angle)

                    break

    def set_sword(self, obj):
        if not obj.added_to_json:
            obj.added_to_json = True

            self.game_data["swords"].append(
                {
                    "id": int(obj.id),
                    "wielder_id": int(obj.parent.id),
                    "location": [float(i) for i in obj.pos],
                    "radius": int(obj.physics_body.radius),
                    "is_blocked": obj.cancel_hit,
                    "is_cooldown": obj.counter <= Sprites.Sword.HIT_DELAY,
                    "hit_objects": [int(i.id) for i in obj.hit_targets]
                }
            )

        else:
            for itm in self.game_data["swords"]:
                if itm["id"] == obj.id:
                    itm["location"] = [float(i) for i in obj.pos]
                    itm["is_blocked"] = obj.cancel_hit
                    itm["is_cooldown"] = obj.counter <= Sprites.Sword.HIT_DELAY
                    itm["hit_objects"] = [int(i.id) for i in obj.hit_targets]

                    break

    def set_powerup(self, obj):
        if not obj.added_to_json:
            obj.added_to_json = True

            self.game_data["powerups"].append(
                {
                    "id": int(obj.id),
                    "location": [float(i) for i in obj.pos],
                    "radius": int(Sprites.Powerup.POWERUP_RADIUS),
                    "type_id": int(obj.powerup_type.value)
                }
            )

        #else:
        #    for itm in self.game_data["players"]:
        #        if itm["id"] == obj.id:
        #            break

    # General method
    def remove_object(self, arr, id):
        remove_index = None

        for idx in range(len(arr)):
            if arr[idx]["id"] == id:
                remove_index = idx
                break

        if remove_index is not None:
            arr.pop(remove_index)

    def remove_player(self, obj):
        self.remove_object(self.game_data["players"], obj.id)

    def remove_regular_bullet(self, obj):
        self.remove_object(self.game_data["regular_bullets"], obj.id)

    def remove_highvel_bullet(self, obj):
        self.remove_object(self.game_data["highvel_bullets"], obj.id)

    def remove_missile(self, obj):
        self.remove_object(self.game_data["missiles"], obj.id)

    def remove_sword(self, obj):
        self.remove_object(self.game_data["swords"], obj.id)

    def remove_powerup(self, obj):
        self.remove_object(self.game_data["powerups"], obj.id)


