from __future__ import division
import numpy as np
import Diffusion as df
### helper functions ###

def get_distance(v1, v2):
    '''Returns the distance between to 2d vectors'''

    diff = v1 - v2
    return np.linalg.norm(diff)

def norm_vector(v1):
    return v1 / np.linalg.norm(v1)

def get_angle(v1, v2):
    angle = np.degrees( np.arccos( np.dot(v1,v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)) ) )
    return angle

def get_oriented_angle(v1, v2):
    angle = get_angle(v1,v2)
    oriented_angle = angle
    orientation = 0

    #create 2x2 matrix from v1,v2
    a = np.concatenate((v1, v2), axis=0).reshape((2,2))

    det = np.linalg.det(a)

    if det > 0:
        orientation = 1
    elif det < 0:
        orientation = -1
        oriented_angle = oriented_angle * -1

    elif det == 0:
        orientation = 0

    return oriented_angle, angle, orientation

def rotate_vector(v, r):
    '''counter clock wise rotation'''
    theta = np.radians(r)
    rotMatrix = np.array([[np.cos(theta), -np.sin(theta)],
                         [np.sin(theta),  np.cos(theta)]])

    return np.dot(rotMatrix, v)


class World():
    '''
    class World holds a set of objects which must have a positionvector [x,y]
    It can give back distances between objects or return a set of objects in a given range
    '''
    def __init__(self, dimensions = [400,400]):
        '''
        2d array - dimensions of the world
        '''

        self.dimensions = dimensions

        #first we use a list to hold objects
        self.world_objects = []

        self.phero_map = np.zeros(tuple(dimensions))

        #time which passes between two ticks
        self.delta_time = 1 / 40


    def get_objects_in_range(self, pos, radius):
        '''returns a list of objects in a given range
        needs a position vector and a radius
        '''

        in_range = []

        for o in self.world_objects:
            if get_distance(o.position, pos) <= radius * 2:
                in_range.append(o)

        return in_range

    def get_objects_in_range_and_radius(self, pos, dir, radius, check_angle):
        '''returns a list of objects in a given range, direction and angle'''

        in_range = self.get_objects_in_range(pos, radius)
        in_angle = [];

        for o in in_range:
            o_direction = o.position - pos
            angle = get_angle(dir, o_direction)

            if 0 <= angle <= (check_angle / 2):
                in_angle.append(o)

        return in_angle

    def any_objects_in_range(self, pos, radius):
        for o in self.world_objects:
            distance = get_distance(o.position, pos)

            #if distance == 0, its the object itself!
            if distance <= radius * 2 and distance != 0.:
                return True

        return False

    def get_objects(self, type = "all"):
        '''returns all objects

        type: optional parameter to filter by object type
        '''

        return self.world_objects

    def add_object(self, object):
        #set world_instance to self
        object.world = self

        self.world_objects.append(object)


    def set_objects(self, object_list):
        self.world_objects = object_list

    def add_objects(self, object_list):
        for o in object_list:
            self.add_object(o)

    def remove_all_objects(self):
        self.world_objects = []


    #update objects
    def update(self):
        self.update_objects()

        #update pheromap
        #self.phero_map = df.diffuse(self.phero_map)

    def update_objects(self):
        '''
        iterates through all objects and calls the tick-method
        '''
        for o in self.world_objects:
            o.tick(self.delta_time)


class WorldObject():
    '''
    class WorldObject has a position-vector and a type
    '''

    #this list defines the different object-types which can be later used as labels or for type-filtering
    object_types = ["ant", "pheromone"]

    def __init__(self, position, world_instance = None):
        self.position = np.array(position, dtype=float)
        self.type = ""
        self.world = world_instance

    def is_type(self, typestring):
        if self.type == typestring:
            return True
        return False

    def tick(self, delta):
        '''
        this will be overwritten by child classes
        '''
        pass

    def get_distance(self, object):
        '''returns the distance between this and another object

        '''
        pass