import socket
import json
import random


def setup():
    # Change the values to set your mods and Name String!
    # Do not exceed a sum of 26!
    # Do not touch the key names!

    return {"NAME": "".join(chr(random.randint(0, 255)) for _ in range(10)),

            "MOD_HEALTH": 0,
            "MOD_FORCE": 0,
            "MOD_SWORD": 0,
            "MOD_DAMAGE": 0,
            "MOD_SPEED": 0,
            "MOD_ENERGY": 0,
            "MOD_DODGE": 0}


def update(game_data):
    pass


#######################################
#######################################


#######################################

HOST = 'localhost'  # The server's hostname or IP address
PORT = 42069      # The port used by the server


class Client:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Connects to server
            s.connect((self.HOST, self.PORT))

            # Gets initial mod data, bytifies it, and sends it off
            s.sendall(bytes(Client.get_mods(), "utf-8"))

            # Awaits response to start game
            response = s.recv(2048).decode("utf-8")

            print(response)

            #s.recv(2048)
            #s.close()

    @staticmethod
    def get_mods():
        return json.dumps(setup(), separators=(',', ':'))


CLIENT = Client(HOST, PORT)
CLIENT.connect()
