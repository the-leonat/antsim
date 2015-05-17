import numpy as np

from World import *

class Obstacle(WorldObject):

    numpy_shape = (2, 2)

    def __init__(self, position, radius, world_instance = None):
        WorldObject.__init__(self, position, world_instance)
        self.set_type("obstacle")

        self.radius = radius

        self.points = []
        ang = 0.0
        while ang < 360:
            self.points.append(self.position + rotate_vector(np.array([self.radius, 0]), ang))
            ang += 0.5

    def to_dict(self):
        d = {}
        d["position"] = self.position
        d["type"] = self.type
        return d

    def to_numpy(self):
        arr = np.zeros(Obstacle.numpy_shape)
        arr[0,:] = self.position
        arr[1,0] = self.radius
        return arr

    def get_points(self):
        

        return self.points

    def tick(self, delta):
        pass