from __future__ import division
import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def diffuse(mapp):
    rate = np.array([[0.0625,0.0625,0.0625],[0.0625,0.5,0.0625],[0.0625,0.0625,0.0625]])
    #rate = np.array([[0.2,0.2,0.2],[0.2,0.5,0.2],[0.2,0.2,0.2]])
    return scipy.signal.convolve(mapp, rate)


class PheromoneMap():
    def __init__(self, dimension, resolution = 1):
        #elements
        self.resolution = resolution

        self.phero_map = np.zeros(tuple(dimension * resolution), dtype=np.float)

        self.diffusion_matrix = np.array([[0.0,0.2,0.0],[0.2,0.0,0.2],[0.0,0.2,0.0]])

    def tick(self, delta):
        self.phero_map = scipy.signal.convolve(self.phero_map, self.diffusion_matrix * delta)

    def convert_coordinates(self, position):
        return np.array(position * self.resolution, dtype=np.int)

    def get_pheromone_concentration(self, position, radius):
        r = int(radius * self.resolution)
        n = 2 * r +1

        a, b = self.convert_coordinates(position)
        #setting up circular mask
        y,x = np.ogrid[-a:n-a, -b:n-b]
        mask = x*x + y*y <= r*r

        #disortion of mask
        # -

        return np.average(self.phero_map[mask])

    def set_random_values(self):
        pass
