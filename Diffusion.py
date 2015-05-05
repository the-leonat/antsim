from __future__ import division
import scipy.ndimage
import scipy.signal
import numpy as np

import threading

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
            #scipy.ndimage.filters.convolve(self.phero_map, self.diffusion_matrix, output=self.phero_map, mode="constant")
            convs = []
            convs.append( Convolutor(self.diffusion_matrix, self.phero_map, (0, 0), (499, 499)) )
            convs.append( Convolutor(self.diffusion_matrix, self.phero_map, (500, 0), (999, 499)) )
            convs.append( Convolutor(self.diffusion_matrix, self.phero_map, (0, 500), (499, 999)) )
            convs.append( Convolutor(self.diffusion_matrix, self.phero_map, (500, 500), (999, 999)) )
            
            for c in convs:
                c.start()
            for c in convs:
                c.join()

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


class Convolutor(threading.Thread):
    lock = threading.Lock()

    def __init__(self, matr, arr, begin, end):
        threading.Thread.__init__(self)
        self.matr = matr
        self.arr = arr
        self.begin = begin
        self.end = end
        return

    def run(self):
        sliced = self.arr[self.begin[0]:self.end[0], self.begin[1]:self.end[1]].astype(np.float32)
        
        #conv = scipy.ndimage.filters.convolve(sliced, self.matr, mode="constant")
        conv = scipy.signal.fftconvolve(sliced, self.matr, mode="full")

        Convolutor.lock.acquire()
        #middle
        self.arr[self.begin[0]:self.end[0], self.begin[1]:self.end[1]] = conv[1:-1, 1:-1]

        #borders
        #top
        self.arr[self.begin[0], self.begin[1]:self.end[1]] += conv[-0, 1:-1]
        #bottom
        self.arr[self.end[0], self.begin[1]:self.end[1]] += conv[0, 1:-1]
        #left
        self.arr[self.begin[0]:self.end[0], self.begin[1]] += conv[1:-1, -0]
        #right
        self.arr[self.begin[0]:self.end[0], self.end[1]] += conv[1:-1, 0]

        Convolutor.lock.release()

        return






