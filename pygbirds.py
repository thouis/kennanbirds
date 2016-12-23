import pygame
import mahotas
import numpy as np
import bird

def clamp(v, lo, hi):
    return min(hi, max(v, lo))

def generate_distance_field(width, height, segments):
    background = np.ones((width, height))
    segmaps = []

    for seg in segments:
        (x0, y0), (x1, y1) = seg
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        tmp = np.ones((width, height))
        x0 = clamp(x0, 0, width - 1)
        x1 = clamp(x1, 0, width - 1)
        y0 = clamp(y0, 0, height - 1)
        y1 = clamp(y1, 0, height - 1)
        tmp[x0:x1+1, y0:y1+1] = 0
        background[x0:x1+1, y0:y1+1] = 0
        segmaps.append(mahotas.distance(tmp))

    segstack = np.dstack(segmaps)
    segstack = np.sort(segstack, 2)
    closest = segstack[:, :, 0] + 1.0
    next = segstack[:, :, 1] + 1.0
    weight = next ** 2 / (next ** 2 + closest ** 2)
    distances = weight * closest + (1.0 - weight) * next
    return background, distances - 10

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

    # generate background image and distance field
    background_lines = [[(0, 0), (WIDTH, 0)],
                        [(0, HEIGHT), (WIDTH, HEIGHT)],
                        [(0, 0), (0, HEIGHT)],
                        [(WIDTH, 0), (WIDTH, HEIGHT)],
                        [(WIDTH // 3, HEIGHT // 6), (WIDTH // 3, 2 * HEIGHT // 6)],
                        [(2 * WIDTH // 3, HEIGHT - HEIGHT // 6), (2 * WIDTH // 3, HEIGHT - 2 * HEIGHT // 6)]]
    bg, dist = generate_distance_field(WIDTH, HEIGHT, background_lines)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


    bg_img = pygame.surfarray.make_surface(255 * np.dstack([bg] * 3))

    gradients = np.gradient(dist)

    birds = [bird.Bird(WIDTH, HEIGHT) for _ in range(NUM_BIRDS)]
    [b.set_type(1) for b in birds[::2]]

    while True:
        screen.blit(bg_img, (0, 0))
        for b in birds:
            b.update(dist, gradients, birds)
            draw_bird(screen, b.position, b.velocity, b.type, BIRD_SHAPE)

        pygame.display.flip()

    pygame.quit()
