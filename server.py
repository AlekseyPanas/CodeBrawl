# Libraries for server
import socket
import threading
import json
import Sprites


class Server:
    def __init__(self, game):
        self.HOST = '0.0.0.0'  # Symbolic name meaning all available interfaces
        self.PORT = 42069  # Arbitrary non-privileged port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Starts server
        self.sock.bind((self.HOST, self.PORT))
        self.sock.listen(1)
        print("Server Started. Listening on port " + str(self.PORT))

        # Connection threads
        self.conn_threads = []

        # True when ready for a new connection
        self.ready_for_conn = True

        # Instance of parent game class
        self.game = game

        # If true, terminates any further connections
        self.locked = False

    # Appends new connection thread and starts it
    def new_conn(self):
        # No longer ready for new connection
        self.ready_for_conn = False

        if not self.locked:
            self.conn_threads.append(threading.Thread(target=self.comms))
            self.conn_threads[-1].start()

    def shutdown_server(self, game):
        # closes socket
        self.sock.close()

        # closes all player connections
        if game.game_starting:
            for ply in [spr for spr in game.SPRITES if "ply" in spr.tags]:
                ply.close_connection()

    # Establishes and manages new connections
    def comms(self):
        if not self.locked:
            # Accepts a new connection
            try:
                conn, addr = self.sock.accept()

                skip = False
            except:
                # Means that the server was shutdown
                skip = True

            if not skip:
                # double checks
                if not self.locked:
                    # Ready to accept a new connection
                    self.ready_for_conn = True

                    # Announces connection
                    print('Connected by', addr)

                    # Receives initial JSON data (including all MOD values and string name of player)
                    data = conn.recv(1024)
                    print(data)

                    # Loads json
                    loaded_json = json.loads(data.decode("utf-8"))

                    # Checks if sum of mods exceeds 26
                    is_exceed = False
                    if sum([loaded_json[k] for k in loaded_json.keys() if k.startswith("MOD")]) > Sprites.Player.max_radius - Sprites.Player.default_radius:
                        conn.close()
                        is_exceed = True

                    # Adds player
                    if not is_exceed:
                        self.game.add_connecting_player(Sprites.Player(self.game.map.get_new_spawn_position(), conn, addr,
                                                                       name=loaded_json["NAME"],
                                                                       mod_hp=loaded_json["MOD_HEALTH"],
                                                                       mod_swrd=loaded_json["MOD_SWORD"],
                                                                       mod_spd=loaded_json["MOD_SPEED"],
                                                                       mod_dodge=loaded_json["MOD_DODGE"],
                                                                       mod_dmg=loaded_json["MOD_DAMAGE"],
                                                                       mod_force=loaded_json["MOD_FORCE"],
                                                                       mod_energy=loaded_json["MOD_ENERGY"]))
                else:
                    conn.close()
