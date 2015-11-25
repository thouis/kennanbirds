import pygame
import mahotas
import numpy as np
import bird

def generate_distance_field(width, height):
    background = np.ones((width, height))
    background[1:-1, 1:-1] = 0
    background[width // 3, 0:(height // 6)] = 1
    background[2 * width // 3, -(height // 6):] = 1
    return background, mahotas.distance(background)


def draw_bird(screen, pos, dir, type, bird_shape):
    dir = dir / dir.mag()
    perp = dir.perp()
    directed_shape = [dir * s[1] + perp * s[0] + pos for s in bird_shape]
    directed_shape = [(pt.x, pt.y) for pt in directed_shape]
    color = [255, 0, 0] if type == 1 else [0, 255, 0]
    pygame.draw.polygon(screen, color, directed_shape)

if __name__ == '__main__':
    NUM_BIRDS = 100
    WIDTH = 800
    HEIGHT = 600
    BIRD_SHAPE = [[0, 0],
                  [10, -5],
                  [0, -2],
                  [-10, -5]]

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # generate background image and distance field
    bg, dist = generate_distance_field(WIDTH, HEIGHT)
    bg_img = pygame.surfarray.make_surface(255 * (1 - np.dstack([bg] * 3)))

    gradient = np.gradient(dist)

    birds = [bird.Bird(WIDTH, HEIGHT) for _ in range(NUM_BIRDS)]
    [b.set_type(1) for b in birds[::2]]

    while True:
        screen.blit(bg_img, (0, 0))
        for b in birds:
            b.update(WIDTH, HEIGHT, birds)
            draw_bird(screen, b.position, b.velocity, b.type, BIRD_SHAPE)

        pygame.display.flip()

    pygame.quit()
