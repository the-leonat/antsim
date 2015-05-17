import numpy as np

from world import *

class Obstacle(WorldObject):

	def __init__(self, position, radius, world_instance = None):
        WorldObject.__init__(self, position, world_instance)
        self.set_type("obstacle")

        self.radius = radius

    def to_dict(self):
        d = {}
        d["position"] = self.position
        d["type"] = self.type
        return d

    def tick(self, delta):
        pass