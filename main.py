import pygame
import json
import time
pygame.init()

# Allows for convert_alpha operations and such
pygame.display.set_mode((400, 700), pygame.DOUBLEBUF)

# Imports game
import Game

# Libraries for server
import socket
import threading

# List containing connection threads
Conns = []


# Appends new connection thread and starts it
def add_thread():
    global Conns
    Conns.append(threading.Thread(target=echo_comms))
    Conns[-1].start()


def echo_comms():
    conn, addr = s.accept()

    # Upon connection, creates new thread to listen for new connection
    add_thread()

    print('Connected by', addr)
    #while 1:
    data = conn.recv(1024)
    #if not data: break
    #print(json.loads(data.decode("utf-8")))
    conn.sendall(b"1")
    #conn.close()
    if not conn.recv(1024):
        print('Connection closed', addr)

    #while 1:
    conn.sendall(b"FUCK")

    while 1:
        conn = 1

    #conn = 1


HOST = '0.0.0.0'                 # Symbolic name meaning all available interfaces
PORT = 42069              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

# Adds initial thread
add_thread()

#GAME = Game.Game()
#GAME.run_game()


"""
- Add server logic

- build clients
"""
