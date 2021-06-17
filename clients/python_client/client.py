import socket
import json
from enum import IntEnum

import time
import math
import random


def setup():
    # Change the values to set your mods and Name String!
    # Do not exceed a sum of 26 for your mods!
    # Do not touch the key names!

    return {"NAME": "Your Player Name",

            "MOD_HEALTH": 0,
            "MOD_FORCE": 0,
            "MOD_SWORD": 0,
            "MOD_DAMAGE": 0,
            "MOD_SPEED": 0,
            "MOD_ENERGY": 0,
            "MOD_DODGE": 0}


def update(game_data):
    """
    This is your update function where you will write all the logic for your player!!

    Feel free to import libraries, create classes, functions, or variables to suit your needs!

    Order of events within the game
        - Server executes next frame
        - Server gathers game state information
        - Server sends game state info to clients
        - Client (this file) calls the update function providing you with game_data
        - Client sends commands that you executed back to the server
        - < Repeat from the top >

    :param game_data: a large python dictionary containing information about the current game state
    """
    print(game_data)


# This Enum class links powerup IDs to their corresponding power up type.

# You can choose to use this enum in your code, but mainly this enum will help you identify
# which integer ID value represents which powerup.
# (since game_data differentiates powerups based on a numerical ID, without this enum you wouldn't be able to identify)
class PowerupTypes(IntEnum):
    MISSILE_AMMO = 0
    ENERGY = 1
    REGULAR_AMMO = 2
    HIGHVEL_AMMO = 3

############################################################################################
# Commands
############################################################################################
# ░█▀▀█ ░█▀▀▀█ ░█▀▄▀█ ░█▀▄▀█ ─█▀▀█ ░█▄─░█ ░█▀▀▄ ░█▀▀▀█
# ░█─── ░█──░█ ░█░█░█ ░█░█░█ ░█▄▄█ ░█░█░█ ░█─░█ ─▀▀▀▄▄
# ░█▄▄█ ░█▄▄▄█ ░█──░█ ░█──░█ ░█─░█ ░█──▀█ ░█▄▄▀ ░█▄▄▄█
############################################################################################
# Call the commands below from inside the update function above
# DO NOT actually change any of the code below this divider
############################################################################################


def move(horizontal_vector, vertical_vector):
    """
    Call this function to move your player

    :param horizontal_vector: A number between -1 and 1 representing the fraction of the speed to move horizontally
    :param vertical_vector: A number between -1 and 1 representing the fraction of the speed to move vertically
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

#######################################################################################
#  ████████╗░█████╗░██████╗░ ░█████╗░░█████╗░██████╗░███████╗
#  ╚══██╔══╝██╔══██╗██╔══██╗ ██╔══██╗██╔══██╗██╔══██╗██╔════╝
#  ░░░██║░░░██║░░╚═╝██████╔╝ ██║░░╚═╝██║░░██║██║░░██║█████╗░░
#  ░░░██║░░░██║░░██╗██╔═══╝░ ██║░░██╗██║░░██║██║░░██║██╔══╝░░
#  ░░░██║░░░╚█████╔╝██║░░░░░ ╚█████╔╝╚█████╔╝██████╔╝███████╗
#  ░░░╚═╝░░░░╚════╝░╚═╝░░░░░ ░╚════╝░░╚════╝░╚═════╝░╚══════╝
#######################################################################################
#######################################################################################
# Definitely do not tamper with code below this divider
# Tampering with it could prevent you from properly connecting and interacting with the server
#######################################################################################


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
