import random           # FOR RANDOM BEGINNINGS
import math
from Tkinter import *   # ALL VISUAL EQUIPMENT
from vec import TwoD
import mahotas
import numpy as np

WIDTH = 800            # OF SCREEN IN PIXELS
HEIGHT = 600           # OF SCREEN IN PIXELS
BIRDS = 30              # IN SIMULATION
BIRD_RADIUS = 3         # FOR BIRDS IN PIXELS
OFFSET_START = 20       # FROM WALL IN PIXELS

################################################################################

def main():
    # Start the program.
    initialise()
    mainloop()

def initialise():
    # Setup simulation variables.
    bg, distance_field = generate_distance_field()
    build_birds(distance_field)
    build_graph(make_update(distance_field, bg))

def generate_distance_field():
    background = np.ones((HEIGHT, WIDTH))
    background[1:-1, 1:-1] = 0
    background[0:(HEIGHT // 6), WIDTH // 3, ] = 1
    background[-(HEIGHT // 6):, 2 * WIDTH // 3] = 1
    return background, mahotas.distance(background)

def build_graph(update):
    # Build GUI environment.
    global graph
    root = Tk()
    root.overrideredirect(True)
    root.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, (root.winfo_screenwidth() - WIDTH) / 2,
                                   (root.winfo_screenheight() - HEIGHT) / 2))
    root.bind('q', lambda event: event.widget.quit())
    graph = Canvas(root, width=WIDTH, height=HEIGHT, background='white')
    graph.bind('q', lambda event: event.widget.quit())
    graph.after(40, update)
    graph.focus_set()
    graph.pack()

def make_update(df, bg):
    def update():
        # Main simulation loop.
        draw(bg)
        move(df)
        graph.after(40, update)

def draw(background):
    # Draw all birds.
    graph.delete(ALL)
    for bird in birds:
        x1 = bird.position.x - BIRD_RADIUS
        y1 = bird.position.y - BIRD_RADIUS
        x2 = bird.position.x + BIRD_RADIUS
        y2 = bird.position.y + BIRD_RADIUS

        graph.create_oval((x1, y1, x2, y2), fill='red' if (bird.type == 0) else 'green')

def move():
    # Move all birds.
    for bird in birds:
        bird.update_velocity(birds)
    for bird in birds:
        bird.move()

def build_birds():
    # Create birds variable.
    global birds
    birds = tuple(Bird(WIDTH, HEIGHT, OFFSET_START) for bird in xrange(BIRDS))
    [b.set_type(1) for b in birds[::2]]


################################################################################

# BIRD RULE IMPLEMENTATION CLASS

class Bird:

    def __init__(self, width, height, offset):
        self.width = width
        self.height = height
        self.velocity = TwoD(random.uniform(0, width) - width / 2.0, random.uniform(0, height) - height / 2.0) * 0.01
        self.speed = 10
        self.position = TwoD(random.uniform(0, width), random.uniform(0, height))

        # bird-controlling values
        self.lookahead = 10
        self.friend_radius = min(width, height) / 10
        self.velocity_matching_factor = 0.07
        self.personal_space = min(width, height) / 120
        self.avoidance_factor = 0.05
        self.type = 0

    def set_type(self, val):
        self.type = val
        self.speed = 5
        
    def update_velocity(self, birds):
        self.new_velocity = self.velocity.copy()
        self.follow_friends(birds)  # fly like our nearby friends
        self.keep_personal_space(birds)  # don't fly too close to other birds
        self.keep_speed()  # try to fly our preferred speed
        self.avoid_things(birds)  # First rule of birds: don't crash into things
        self.velocity = self.new_velocity

    def move(self):
        self.position += self.velocity

    def avoid_wall(self, wall_normal, wall_offset):
        # check if we're going to collide.
        for step in range(1, self.lookahead):
            wall_distance = (self.position + self.new_velocity * step).dot(wall_normal) + wall_offset
            if wall_distance < 10:
                # uh oh, we're going to hit a wall.
                old_speed = self.new_velocity.mag()
                how_soon = self.lookahead - step
                self.new_velocity *= (0.9 ** how_soon)  # slow down

                # second: turn away, using some of our momentum
                new_speed = self.new_velocity.mag()
                speed_change = old_speed - new_speed
                perpendicular_direction = self.new_velocity.perp(wall_normal)
                self.new_velocity += perpendicular_direction * speed_change

                # only check each wall once
                break

    def keep_speed(self):
        cur_speed = self.new_velocity.mag()
        if cur_speed < self.speed:
            self.new_velocity *= 1.05
        else:
            self.new_velocity *= 0.95
            
    def avoid_things(self, birds):
        # avoid walls
        self.avoid_wall(TwoD(1, 0), 0)
        self.avoid_wall(TwoD(-1, 0), self.width)
        self.avoid_wall(TwoD(0, 1), 0)
        self.avoid_wall(TwoD(0, -1), self.height)

    def follow_friends(self, birds):
        average_friend_velocity = TwoD(0, 0)
        friend_count = 0
        for other_bird in birds:
            if other_bird is self:
                continue
            distance_to_other_bird = (other_bird.position - self.position).mag()
            if distance_to_other_bird < self.friend_radius:
                friend_count += 1
                difference_in_velocities = other_bird.velocity - self.velocity
                average_friend_velocity += other_bird.velocity - self.velocity
        if friend_count > 0:
            average_friend_velocity /= friend_count
            self.new_velocity += average_friend_velocity * self.velocity_matching_factor

    def keep_personal_space(self, birds):
        for other_bird in birds:
            if other_bird is self:
                continue
            distance_to_other_bird = (other_bird.position - self.position).mag()
            if distance_to_other_bird < self.personal_space:
                self.new_velocity += (self.position - other_bird.position) * self.avoidance_factor

################################################################################

# Execute the simulation.
if __name__ == '__main__':
    main()
