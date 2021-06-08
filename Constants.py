from enum import IntEnum

SCREEN_WIDTH2HEIGHT = 0.9

# Above what speed does a bullet have to be moving to perform a midpoint collision check (prevent bullet skipping)
BULLET_MIDPT_SPEED_MIN = 10


class ServerModes(IntEnum):
    # Normal server for competition
    COMPETITION = 0
    # Test server for python teams (includes 2 builtin players)
    PYTHON_TEST_SERVER = 1
    # Test server for non-python teams (includes 1 key controlled builtin)
    OTHER_TEST_SERVER = 2


# Current server mode
SERVER_MODE = ServerModes.PYTHON_TEST_SERVER

tick = 0
