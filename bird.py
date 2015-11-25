import random
from vec import TwoD

class Bird(object):
    def __init__(self, width, height):
        self.velocity = TwoD(random.uniform(0, width) - width / 2.0, random.uniform(0, height) - height / 2.0) * 0.01
        self.speed = 10
        self.position = TwoD(random.uniform(0, width), random.uniform(0, height))

        # bird-controlling values
        self.lookahead = 10
        self.friend_radius = min(width, height) / 10
        self.velocity_matching_factor = 0.07
        self.personal_space = min(width, height) / 100
        self.avoidance_factor = 0.05
        self.type = 0

    def set_type(self, val):
        self.type = val
        self.speed = 5

    def update(self, width, height, birds):
        self.update_velocity(width, height, birds)
        self.move()

    def update_velocity(self, width, height, birds):
        self.new_velocity = self.velocity.copy()
        self.follow_friends(birds)  # fly like our nearby friends
        self.keep_personal_space(birds)  # don't fly too close to other birds
        self.keep_speed()  # try to fly our preferred speed
        self.avoid_things(width, height, birds)  # First rule of birds: don't crash into things
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
                perpendicular_direction = self.new_velocity.perp().projection(wall_normal).unit()
                self.new_velocity += perpendicular_direction * speed_change

                # only check each wall once
                break

    def keep_speed(self):
        cur_speed = self.new_velocity.mag()
        if cur_speed < self.speed:
            self.new_velocity *= 1.05
        else:
            self.new_velocity *= 0.95

    def avoid_things(self, width, height, birds):
        # avoid walls
        self.avoid_wall(TwoD(1, 0), 0)
        self.avoid_wall(TwoD(-1, 0), width)
        self.avoid_wall(TwoD(0, 1), 0)
        self.avoid_wall(TwoD(0, -1), height)

    def follow_friends(self, birds):
        average_friend_velocity = TwoD(0, 0)
        friend_count = 0
        for other_bird in birds:
            if other_bird is self:
                continue
            distance_to_other_bird = (other_bird.position - self.position).mag()
            if distance_to_other_bird < self.friend_radius:
                friend_count += 1
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
