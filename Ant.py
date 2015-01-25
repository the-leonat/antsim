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
        self.max_speed = 200
        self.min_speed = 5
        self.length = 10
        self.center_radius = 5 * 15
        self.head_radius = 4
        self.head_angle = 100

        self.max_turn_angle = 20

    def get_weighted_collision_vector(self, object_list):
        if len(object_list) == 0:
            return np.array([0,0], dtype=np.float64)

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

    def evade(self, delta):
        #this is the main collision method

        o_in_center_range = self.world.get_objects_in_range(self.position, self.center_radius)
        o_in_top_range = self.world.get_objects_in_range_and_radius(self.position, self.direction, self.head_radius, self.head_angle)

        o_in_range = o_in_center_range + o_in_top_range

        # remove ourself from o_in_range
        for o in o_in_range:
            o.position
            if o == self:
                o_in_range.remove(o)

        collision_vector = self.get_weighted_collision_vector(o_in_range)

        avoiding_vector = self.get_avoiding_vector(collision_vector, delta)

        #print "avoiding" , avoiding_vector

        self.direction = avoiding_vector

    def tick(self, delta):
        '''
        put here all the movement logic
        '''
        self.evade(delta)
        self.position = self.position + ( self.direction * self.min_speed * delta)

