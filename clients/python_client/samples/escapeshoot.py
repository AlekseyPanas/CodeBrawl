import socket
import json
import random
from enum import IntEnum
import time
import math


def setup():
    # Change the values to set your mods and Name String!
    # Do not exceed a sum of 26!
    # Do not touch the key names!

    return {"NAME": "RunnyBoi",

            "MOD_HEALTH": 0,
            "MOD_FORCE": 0,
            "MOD_SWORD": 0,
            "MOD_DAMAGE": 0,
            "MOD_SPEED": 26,
            "MOD_ENERGY": 0,
            "MOD_DODGE": 0}


vec = [-1, 0]
deg = -90


def dist(a,b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def update(game_data):
    global deg
    global vec, mode
    me = None

    en_pos = None

    for ply in game_data["players"]:
        if ply["is_you"]:
            me = ply
        else:
            en_pos = ply["location"]

    me_pos = me["location"]

    if en_pos is not None:
        diff = [en_pos[0] - me_pos[0], en_pos[1] - me_pos[1]]
        largest = max([abs(i) for i in diff])

        if largest != 0:
            vec = [diff[0] / largest, diff[1] / largest]
        else:
            vec = diff

        shoot_regular(math.degrees(math.atan2(-vec[1], vec[0])))

        if 250 < dist(me_pos, en_pos) < 600:
            if (diff[0] < 0 < diff[1]) or (diff[0] > 0 > diff[1]):
                deg = 90
            else:
                deg = -90

            print("LIS")
            ang = math.radians(math.degrees(math.atan2(-vec[1], vec[0])) + 90)

            vec = math.cos(ang), -math.sin(ang)
            largest = max([abs(i) for i in vec])
            vec = (vec[0] / largest, vec[1] / largest)

        move(-vec[0], -vec[1])




class PowerupTypes(IntEnum):
    MISSILE_AMMO = 0
    ENERGY = 1
    REGULAR_AMMO = 2
    HIGHVEL_AMMO = 3

#######################################
#######################################


def move(horizontal_vector, vertical_vector):
    """
    Call this function to move your player

    :param horizontal_vector: A number between 0 and 1 representing the fraction of the speed to move horizontally
    :param vertical_vector: A number between 0 and 1 representing the fraction of the speed to move vertically
    """

    CLIENT.commands["is_movement_command"] = True
    CLIENT.commands["movement_command_vectors"] = [horizontal_vector, vertical_vector]


def shoot_regular(angle):
    """
    Call this function to shoot a regular bullet

    :param angle: A number representing the angle, in degrees, at which you want to fire your ammo
    """

    if not CLIENT.has_shot:
        CLIENT.has_shot = True

        CLIENT.commands["is_shoot_regular_bullet_command"] = True
        CLIENT.commands["shoot_regular_bullet_angle"] = angle

    else:
        print("WARNING: You cannot shoot multiple projectiles at once! 'shoot_regular' command cancelled!")


def shoot_highvel(angle):
    """
    Call this function to shoot a high velocity bullet (increased speed)

    :param angle: A number representing the angle, in degrees, at which you want to fire your ammo
    """

    if not CLIENT.has_shot:
        CLIENT.has_shot = True

        CLIENT.commands["is_shoot_highvel_bullet_command"] = True
        CLIENT.commands["shoot_highvel_bullet_angle"] = angle

    else:
        print("WARNING: You cannot shoot multiple projectiles at once! 'shoot_highvel' command cancelled!")


def shoot_missile(target_id):
    """
    Call this function to shoot a missile at a target player

    :param target_id: The player ID of the player you would like the missile to target
    """

    if not CLIENT.has_shot:
        CLIENT.has_shot = True

        CLIENT.commands["is_shoot_missile_command"] = True
        CLIENT.commands["shoot_missile_target_id"] = target_id

    else:
        print("WARNING: You cannot shoot multiple projectiles at once! 'shoot_missile' command cancelled!")


def use_sword(angle):
    """
    Call this to deploy your sword for a brief period of time in the specified direction

    :param angle: A number representing the angle, in degrees, at which you want to stab your sword
    """

    CLIENT.commands["is_use_sword_command"] = True
    CLIENT.commands["use_sword_angle"] = angle

#######################################


HOST = 'localhost'  # The server's hostname or IP address
PORT = 42069      # The port used by the server


class Client:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port

        # Has a shoot command been executed this frame
        self.has_shot = False

        # Command JSON to be sent to the server
        self.commands = {
            "is_movement_command": False,
            "movement_command_vectors": [0, 0],

            "is_shoot_regular_bullet_command": False,
            "shoot_regular_bullet_angle": 0,

            "is_shoot_highvel_bullet_command": False,
            "shoot_highvel_bullet_angle": 0,

            "is_shoot_missile_command": False,
            "shoot_missile_target_id": 0,

            "is_use_sword_command": False,
            "use_sword_angle": 0
        }

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Connects to server
            s.connect((self.HOST, self.PORT))

            # Gets initial mod data, bytifies it, and sends it off
            s.sendall(bytes(Client.get_mods(), "utf-8"))

            # Lobby waiting loop
            while 1:
                data = s.recv(64)
                if not data or data.decode("utf-8") == "s":
                    break
                s.sendall(b"1")

            # Initiates communications loop
            while 1:
                # Receives game data json
                game_data = s.recv(131072)

                # Breaks if data ends connection
                if not game_data:
                    break

                # Clears shot
                self.has_shot = False

                # Clears commands
                self.commands["is_shoot_missile_command"] = False
                self.commands["is_use_sword_command"] = False
                self.commands["is_movement_command"] = False
                self.commands["is_shoot_regular_bullet_command"] = False
                self.commands["is_shoot_highvel_bullet_command"] = False

                # Calls logic function with parsed json game data
                update(json.loads(game_data.decode("utf-8")))

                # Sends commands
                s.sendall(bytes(json.dumps(self.commands, separators=(',', ':')), "utf-8"))

            # Closes connection
            s.close()
            print("Connection closed successfully")

    @staticmethod
    def get_mods():
        return json.dumps(setup(), separators=(',', ':'))


CLIENT = Client(HOST, PORT)
CLIENT.connect()
