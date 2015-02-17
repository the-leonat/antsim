from __future__ import division
import Settings as settings
from World import *
from Ant import *

import time
import pygame
import pygame.gfxdraw
import numpy as np
import pyglet
import cPickle as pickle

import copy


class Simulator():
    '''
    This class simulates the behavior of worldobjects over time
    '''

    def __init__(self, delta_time = 1 / 40.):
        #always use set_mode function to set mode. dont set string directly

        self.world = World(delta_time)

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

        for x in range(n):
            self.world.update()
            #VERY IMPORTANT, copy the list!

            data_list.append( copy.deepcopy(self.world.world_objects) ) 

        #setting up the dict to safe
        dump_dict["delta_time"] = self.world.delta_time
        dump_dict["data_list"] = data_list
        dump_dict["version"] = "0.1"

        
        pickle.dump(dump_dict, open( filename, "wb" ))



def create_random_objects(n):
    '''
    returns a list of n antobjects with random position and direction vectors
    '''


    #returns n objects with position between (10,10) and (390,390)
    return [Ant( np.random.uniform(-1,1, (2)) * 100, np.random.uniform(-1,1, (2)) ) for a in range(0,n)]

def create_test_objects(n = 0):
    a1 = Ant([200, 160], [0, 1])
    a2 = Ant([220, 240], [0, -1])

    return [a1,a2]

def setup(n = 100, p = 50):
    '''
    this is the startup function which initializes a Simulator-Object and loads the settings file
    n = number of elements to create
    '''

    #creates a simulator instance
    s = Simulator()

    #add some ants
    s.world.add_objects( create_random_objects(n) )

    return s

if __name__ == "__main__":
    #startup()
    s = setup(n = 10)

    pass

