import pygame
pygame.init()

fps = 0
last_fps_show = 0
clock = pygame.time.Clock()

while True:

    # sets fps to a variable. can be set to caption any time for testing.
    last_fps_show += 1
    if last_fps_show == 30:  # every 30th frame:
        fps = clock.get_fps()
        pygame.display.set_caption("FPS: " + str(fps))
        last_fps_show = 0

    # fps max 60
    clock.tick(60)
