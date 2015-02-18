from __future__ import division
import scipy.signal
import numpy as np

def diffuse(mapp):
    rate = np.array([[0.0625,0.0625,0.0625],[0.0625,0.5,0.0625],[0.0625,0.0625,0.0625]])
    #rate = np.array([[0.2,0.2,0.2],[0.2,0.5,0.2],[0.2,0.2,0.2]])
    return scipy.signal.convolve(mapp, rate)


class PheromoneMap():
    def __init__(self, dimension, resolution = 1):
        #elements
        self.resolution = resolution

        #self.phero_map = np.zeros(tuple(dimension * resolution), dtype=np.float)
        #self.phero_map = np.random.uniform(0.0, 1.0, tuple(dimension * resolution))
        self.phero_map = np.zeros(tuple(dimension * resolution))

        self.phero_map[480:520,:] = np.random.uniform(0.0,0.8)

        #self.diffusion_matrix = np.array([[0.0,0.2,0.0],[0.2,0.0,0.2],[0.0,0.2,0.0]])
        self.diffusion_matrix = np.array([[0.0625,0.0625,0.0625],[0.0625,0.5,0.0625],[0.0625,0.0625,0.0625]])
        #self.diffusion_matrix = np.array([[.5, 0.01],[0.01, 0.01]])

        for x in range(10):
            self.tick(1)

    def tick(self, delta):
        self.phero_map = scipy.signal.convolve(self.phero_map, self.diffusion_matrix * delta)

    def convert_coordinates(self, position):
        shift = np.array(self.phero_map.shape) / 2.
        return np.array((position * self.resolution) + shift, dtype=np.int)

    def get_pheromone_concentration(self, position, radius):
        x,y = self.convert_coordinates(position)

        return self.phero_map[x,y]


    def set_random_values(self):
        pass
