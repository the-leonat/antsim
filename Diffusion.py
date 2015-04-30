from __future__ import division
import scipy.ndimage
import numpy as np

import yaml
config = yaml.load(open("config.yml"))

class PheromoneMap():
    def __init__(self, resolution = 1.):
        self.delta = 0.

        self.resolution = resolution

        self.phero_map = np.zeros(tuple(np.array(config["world_dimension"]) * resolution), dtype=np.float32)
        self.phero_changes = []

        #self.diffusion_matrix = np.array([[0.1,0.1,0.1],[0.1,0.2,0.1],[0.1,0.1,0.1]], dtype=np.float32)
        self.diffusion_matrix = np.array([[0.0999,0.0999,0.0999],[0.0999,0.197,0.0999],[0.0999,0.0999,0.0999]], dtype=np.float32)

    def to_dict(self):
        d = {}
        d["resolution"] = self.resolution
        d["phero_map"] = self.phero_map
        return d

    def tick(self, delta):
        self.delta += delta

        # apply all changes enqued during last round
        for i in self.phero_changes:
            self.phero_map[i[0], i[1]] = i[2]
        self.phero_changes = []

        # convolve to blur pheromone
        while self.delta > 0.1:
            self.delta -= 0.1
            scipy.ndimage.filters.convolve(self.phero_map, self.diffusion_matrix, output=self.phero_map, mode="constant")

        # dunno why, looks like scipy messes with the array somehow
        self.phero_map = self.phero_map.astype(np.float32)

    def convert_coordinates(self, position):
        shift = np.array(self.phero_map.shape) / 2.
        position = np.array((position * self.resolution) + shift, dtype=np.int)
        for i in range(position.shape[0]):
            if position[i] >= self.phero_map.shape[i]:
                position[i] %= self.phero_map.shape[i]
            elif position[i] < 0:
                position[i] = self.phero_map.shape[i] - (-position[i] % self.phero_map.shape[i])
        return position

    def get_pheromone_concentration(self, position, radius):
        y,x = self.convert_coordinates(position)
        return self.phero_map[x,y]

    def set_pheromone_concentration(self, position, amount):
        y,x = self.convert_coordinates(position)
        # enque for application after round
        self.phero_changes.append([x, y, amount])

    def add_pheromone_concentration(self, position, amount):
        y,x = self.convert_coordinates(position)
        # enque for application after round
        self.phero_changes.append([x, y, self.phero_map[x,y] + amount])
