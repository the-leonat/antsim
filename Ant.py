from __future__ import division
from World import *

import numpy as np

class Ant(WorldObject):
    '''
    class Ant inherits from WorldObject and additionally holds a direction vector ...
    '''

    def __init__(self, position, direction, world_instance = None):
        WorldObject.__init__(self, position, world_instance)

        #NOTE: All elements are relative to one second!

        #norm the direction to 1

        self.direction = norm_vector(np.array(direction))
        self.type = "ant"
        self.speed = 100
        self.max_speed = 100
        self.min_speed = 5
        self.length = 10
        self.center_radius = 5 * 5
        self.head_radius = 4
        self.head_angle = 100

        self.max_turn_angle = 45

    def get_left_antenna_position(self):
        pos_head = self.get_head_position()
        return pos_head + rotate_vector(self.direction * self.head_radius, self.head_angle / 2)

    def get_right_antenna_position(self):
        pos_head = self.get_head_position()
        return pos_head + rotate_vector(self.direction * self.head_radius, 360 - self.head_angle / 2)

    def get_head_position(self):
        return self.position + self.direction * (self.length / 2)

    def get_weighted_collision_vector(self, object_list):
        v_sum = np.array([0,0], dtype=np.float)
        for o in object_list:
            v = ((self.position - o.position) / np.linalg.norm(self.position - o.position))
            v_sum = v_sum + v

        average = v_sum / len(object_list)

        return average

    def get_avoiding_vector(self, collision_vector, delta):
        o_turn_angle, turn_angle, orientation = get_oriented_angle(self.direction, self.direction + collision_vector)

        #check if angle exceeds max angle
        if turn_angle > self.max_turn_angle * delta:
            o_turn_angle = self.max_turn_angle * orientation * delta

        #rotate the vector
        new_direction = rotate_vector(self.direction, o_turn_angle)

        return norm_vector(new_direction)

    def evade_objects(self, delta):
        #this is the main collision method

        o_in_center_range = self.world.get_objects_in_range(self.position, self.center_radius)
        o_in_top_range = self.world.get_objects_in_range_and_radius(self.position, self.direction, self.head_radius, self.head_angle)

        o_in_range = o_in_center_range + o_in_top_range

        # remove ourself from o_in_range
        for o in o_in_range:
            o.position
            if o == self:
                o_in_range.remove(o)

        if len(o_in_range) > 0:
            collision_vector = self.get_weighted_collision_vector(o_in_range)
            avoiding_vector = self.get_avoiding_vector(collision_vector, delta)
            self.direction = avoiding_vector

            return True

        return False

    def trail_pheromone(self):
        # turns the ant to the side with higher pheromone concentration

        pos_left = self.get_left_antenna_position()
        pos_right = self.get_right_antenna_position()

        # concentrations
        c_left = self.world.phero_map.get_pheromone_concentration(pos_left, self.head_radius)
        c_right = self.world.phero_map.get_pheromone_concentration(pos_right, self.head_radius)

        # angle
        # maybe divide by max pheromone concentration
        a = c_left - c_right

        if np.allclose(a, 0, 1e-4):
            return False

        # cap at max_angle
        if a > self.max_turn_angle:
            a = self.max_turn_angle
        else:
            if a < -1 * self.max_turn_angle:
                a = -1 * self.max_turn_angle

        self.direction = rotate_vector(self.direction, a)
        return True

    def tick(self, delta):
        '''
        put here all the movement logic
        '''

        evaded = False
        trailed = False

        evaded = self.evade_objects(delta)
        if not evaded:
            trailed = self.trail_pheromone()

        speed = self.max_speed if not evaded else self.min_speed
        self.position = self.position + ( self.direction * speed * delta)

