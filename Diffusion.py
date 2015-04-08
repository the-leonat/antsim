from __future__ import division
import scipy.signal
import numpy as np

class PheromoneMap():
    def __init__(self, dimension, resolution = 1.):
        #elements
        self.resolution = resolution

        self.phero_map = np.zeros(tuple(dimension * resolution), dtype=np.float16)
        #self.phero_map.fill(0.5)
        #self.phero_map = np.random.normal(0.5, 0.5, tuple(dimension * resolution))
        #self.phero_map = np.zeros(tuple(dimension * resolution))

        #self.phero_map[480:520,:] = np.random.uniform(0.0,0.8)

        #self.diffusion_matrix = np.array([[0.0,0.2,0.0],[0.2,0.0,0.2],[0.0,0.2,0.0]])
        #self.diffusion_matrix = np.array([[0.0625,0.0625,0.0625],[0.0625,0.5,0.0625],[0.0625,0.0625,0.0625]], dtype=np.float32)
        self.diffusion_matrix = np.array([[0.1,0.1,0.1],[0.1,0.19995,0.1],[0.1,0.1,0.1]], dtype=np.float16)

        #self.diffusion_matrix = np.array([[.5, 0.01],[0.01, 0.01]])


    def tick(self, delta):
        self.phero_map = scipy.signal.fftconvolve(self.phero_map, self.diffusion_matrix, mode="same")

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
        #return and disort
        y,x = self.convert_coordinates(position)

        return self.phero_map[x,y] + np.random.normal(0., 0.015)

    def set_pheromone_concentration(self, position, amount):
        y,x = self.convert_coordinates(position)

        self.phero_map[x,y] = amount

    def add_pheromone_concentration(self, position, amount):
        y,x = self.convert_coordinates(position)

        self.phero_map[x,y] += amount

    def set_random_values(self):
        pass
