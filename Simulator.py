from __future__ import division
import Settings as settings
from World import *
from Ant import *
from View import MainView

import time
import pygame
import pygame.gfxdraw
import numpy as np
import pyglet
import cPickle as pickle
import sys

import copy

DELTA = 1 / 40.
DIMENSIONS = [1000,1000]


class Simulator():
    '''
    This class simulates the behavior of worldobjects over time
    '''

    def __init__(self, delta, dimensions):
        #always use set_mode function to set mode. dont set string directly

        self.world = World(delta, dimensions)

    def simulate_steps(self, n = 1):
        '''
        this function simulates the behavior of worldobjects for one step and returns a list of objects
        optional param n is the number of steps to simulate
        '''

        t_start = time.clock()

        for x in range(0,n):
            #update the world model
            self.world.update()

        print "time per frame: ", (time.clock() - t_start) / n


    def record(self, seconds, filename = "record.sim"):
        n = int(seconds / self.world.delta_time)

        dump_dict = {}
        data_list = []

        dimx, dimy = DIMENSIONS

        phero_map_matrix = np.zeros(( dimx * n, dimy ), dtype=np.float)

        print "#start recording..."
        for x in range(n):
            self.world.update()
            #VERY IMPORTANT, copy the list!

            data_list.append( copy.deepcopy(self.world.world_objects) ) 

            phero_map_matrix[(x * dimx):(dimx * (x + 1)),:] = self.world.phero_map.phero_map

            self.print_progress("#simulating frames... ", x, n)


        print "#recorded " + str(n) + " frames."

        #setting up the dict to safe
        dump_dict["delta_time"] = self.world.delta_time
        dump_dict["data_list"] = data_list
        dump_dict["version"] = "0.1"
        dump_dict["number_of_frames"] = n
        dump_dict["world_dimensions"] = DIMENSIONS

        print "#pickle object data..."

        pickle.dump(dump_dict, open( filename + "-objectdata", "wb" ))

        print "#saving pheromone data array..."

        #saving the numpy phero matrix
        np.save(filename + "-numpy", phero_map_matrix)

        print "#all done!"

    def print_progress(self, label, x, max):
        perc = (x / max)
        print "\r" + label + "{:.2%}".format(perc),
        sys.stdout.flush()




def create_random_objects(n, dimension = 300):
    '''
    returns a list of n antobjects with random position and direction vectors
    '''


    #returns n objects with position between (10,10) and (390,390)
    return [Ant( np.random.uniform(-1,1, (2)) * dimension, np.random.uniform(-1,1, (2)) ) for a in range(0,n)]

def setup(n = 100):
    '''
    this is the startup function which initializes a Simulator-Object and loads the settings file
    n = number of elements to create
    '''

    #creates a simulator instance
    s = Simulator(DELTA, DIMENSIONS)

    #add some ants
    s.world.add_objects( create_random_objects(n) )
    #s.world.add_objects( [Ant( np.array([0.,0.]), np.random.uniform(-1,1, (2)) )] )

    return s

if __name__ == "__main__":
    #startup()
    s = setup(n = 30)
    #s.simulate_steps()
    s.record(4, filename="record7")

    view = MainView(fps=40)
    view.load_file("record7")
    pyglet.app.run()

