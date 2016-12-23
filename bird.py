import random
from vec import TwoD

class Bird(object):
    def __init__(self, width, height):
        self.velocity = TwoD(random.uniform(0, width) - width / 2.0, random.uniform(0, height) - height / 2.0) * 0.01
        self.speed = 10
        self.position = TwoD(random.uniform(0, width), random.uniform(0, height))

        # bird-controlling values
        self.lookahead = 30
        self.friend_radius = min(width, height) / 10
        self.velocity_matching_factor = 0.07
        self.personal_space = min(width, height) / 100
        self.avoidance_factor = 0.05
        self.type = 0

    def set_type(self, val):
        self.type = val
        self.speed = 7

    def update(self, width, height, birds):
        self.update_velocity(width, height, birds)
        self.move()

    def update_velocity(self, distance_field, gradients, birds):
        self.new_velocity = self.velocity.copy()
        self.follow_friends(birds)  # fly like our nearby friends
        self.keep_personal_space(birds)  # don't fly too close to other birds
        self.keep_speed()  # try to fly our preferred speed

        # First rule of birds: don't crash into things.  Done last to ensure
        # this is most important
        self.avoid_things(distance_field, gradients)

        self.velocity = self.new_velocity

    def move(self):
        self.position += self.velocity

    def keep_speed(self):
        cur_speed = self.new_velocity.mag()
        if cur_speed < self.speed:
            self.new_velocity *= 1.05
        else:
            self.new_velocity *= 0.95

    def avoid_things(self, distance_field, gradients):
        # first, clamp us to the field
        self.position.x = max(2, min(distance_field.shape[0] - 3, self.position.x))
        self.position.y = max(2, min(distance_field.shape[1] - 3, self.position.y))
        x_idx = int(self.position.x)
        y_idx = int(self.position.y)

        # find how far we are from the walls
        cur_distance = distance_field[x_idx, y_idx]

        # how quickly are we moving toward the wall, and how soon will we hit it?
        grad = TwoD(gradients[0][x_idx, y_idx], gradients[1][x_idx, y_idx])
        d_distance_dt = self.velocity.dot(grad)
        if d_distance_dt >= 0:
            # we're moving away
            return

        time_to_collision = - (cur_distance - 5) / d_distance_dt
        if time_to_collision >= self.lookahead:
            # no worries, keep on current path
            return

        old_speed = self.new_velocity.mag()
        self.new_velocity *= 0.98 ** ((self.lookahead - time_to_collision) / 2.0)  # slow down

        # second: turn away, using some of our momentum
        new_speed = self.new_velocity.mag()
        speed_change = old_speed - new_speed
        perpendicular_direction = self.new_velocity.perp().projection(grad).unit()
        self.new_velocity += perpendicular_direction * speed_change

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
