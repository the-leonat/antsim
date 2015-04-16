from __future__ import division
import numpy as np
from Diffusion import *
from scipy.spatial import cKDTree

import yaml
config = yaml.load(open("config.yml"))

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

    #haaaardcode XXX
    if np.isnan(angle):
        return 180., 180., 0

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

    def __init__(self):
        self.dimensions = np.array(config["world_dimension"])
        self.world_objects = []

        #kd tree for faster search
        self.kdtree = None

        #the pheromone concentration map
        self.phero_map = PheromoneMap()

        #time which passes between two ticks
        self.delta_time = config["delta"]

    def to_dict(self):
        d = {}
        d["dimensions"] = self.dimensions
        d["delta_time"] = self.delta_time
        d["phero_map"] = self.phero_map.to_dict()
        d["world_objects"] = self.world_objects_to_dict()
        return d

    def world_objects_to_dict(self, type=None):
        objects = []
        for o in self.world_objects:
            objects.append(o.to_dict())
        return objects

    def world_objects_to_numpy(self, type=None):
        arr = np.zeros((2, len(self.world_objects), 2), dtype=np.float32)
        for i in range(len(self.world_objects)):
            arr[0,i,:] = self.world_objects[i].position
            arr[1,i,:] = self.world_objects[i].direction
        return arr


    def update_kdtree(self):
        #construct kdtree
        point_list = []

        shift = self.dimensions / 2.
        border = 10.
        for o in self.world_objects:
            point_list.append(o.position)

            # add object onto the opposite side but outside world
            for j in range(self.dimensions.shape[0]):
                if o.position[j] >= shift[j] - border:
                    col_pos = o.position.copy()
                    d = shift[j] - col_pos[j]
                    col_pos[j] = -shift[j] - d
                    point_list.append(col_pos)
                elif o.position[j] < -shift[j] + border:
                    col_pos = o.position.copy()
                    d = col_pos[j] + shift[j]
                    col_pos[j] = shift[j] - d
                    point_list.append(col_pos)

        self.kdtree = cKDTree(np.array(point_list, dtype=np.float), 50)

    def get_objects_in_range(self, pos, radius):
        '''returns a list of objects in a given range
        needs a position vector and a radius
        '''

        in_range = []

        for o in self.world_objects:
            if get_distance(o.position, pos) <= radius * 2:
                in_range.append(o)

        return in_range

    def get_positions_in_range_kd(self, pos, radius):
        indices = self.kdtree.query_ball_point(pos, radius * 2)

        new_indices = []

        for i in indices:
            if not np.array_equal(self.kdtree.data[i], pos):
                new_indices.append(i)

        return self.kdtree.data[new_indices]


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

    def get_positions_in_range_and_radius_kd(self, pos2, dir, radius, check_angle):
        in_range = self.get_positions_in_range_kd(pos2, radius)
        in_angle = [];

        for pos1 in in_range:
            o_direction = pos1 - pos2
            angle = get_angle(dir, o_direction)

            if 0 <= angle <= (check_angle / 2):
                in_angle.append(pos1)

        return np.array(in_angle)


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
            o.world = self
            self.add_object(o)

    def remove_all_objects(self):
        self.world_objects = []

    def tick(self):
        # update kdtree for fast neighbour lookup
        self.update_kdtree()

        # tick objects
        for o in self.world_objects:
            o.tick(self.delta_time)

        #update pheromap
        self.phero_map.tick(self.delta_time)


class WorldObject():
    '''
    class WorldObject has a position-vector and a type
    '''

    #this list defines the different object-types which can be later used as labels or for type-filtering
    object_types = ["ant"]

    def __init__(self, position, world_instance = None):
        self.position = np.array(position, dtype=float)
        self.type = None
        self.world = world_instance

    def to_dict(self):
        d = {}
        d["position"] = self.position
        d["type"] = self.type
        return d

    def set_type(self, typestring):
        if typestring in WorldObject.object_types:
            self.type = typestring
        else:
            self.type = None

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
