from __future__ import division
import Settings as settings
from World import *
from Viewer import *
from Ant import *
import time
import pygame
import pygame.gfxdraw
import numpy as np
import View as view
import pyglet


class Simulator(pyglet.window.Window):
    '''
    This class simulates the behavior of worldobjects over time
    '''
    s_modes = ["live", "record"]

    def __init__(self, mode):
        #always use set_mode function to set mode. dont set string directly

        self.world = World()

        super().__init__(width=512, height=512,visible=True)

    def init_screen(self, width, height):
        return pyglet.window.Window()


    def simulate_steps(self, n = 1, redraw=True):
        '''
        this function simulates the behavior of worldobjects for one step and returns a list of objects
        optional param n is the number of steps to simulate
        '''

        t_start = time.clock()


        for x in range(0,n):
            #update the world model
            self.world.update()

        print "time per frame: ", (time.clock() - t_start) / n

    def s(self, n = 1, redraw=True):
        self.simulate_steps(n, redraw)


    def convert_coordinates(self, position_vector):
        '''
        convert the coordinates from the model to pygame coordinates
        it will set (0,0) to the center of the screen
        '''

        screen_x, screen_y = self.screen.get_size()

        #transformation vector
        transform_v = np.array([screen_x / 2, screen_y / 2])

        #convert to integer array
        position_int = np.array(np.rint(position_vector + transform_v), dtype=int)

        return position_int


    @window.event    
    def draw_data():
        self.clear()




def create_random_objects(n):
    '''
    returns a list of n antobjects with random position and direction vectors
    '''


    #returns n objects with position between (10,10) and (390,390)
    return [Ant( np.random.uniform(-1,1, (2)) * 100, np.random.uniform(-1,1, (2)) ) for a in range(0,n)]

def create_random_pheromones(p, mapp):
    mx, my = mapp.shape
    for i in range(p):
        x = np.random.randint(1, mx)
        y = np.random.randint(1, my)
        if mapp[x, y] == 0.:
            mapp[x, y] = 1.

    mapp[0,0] = 1.
    return mapp

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
    s = Simulator("live")

    #add some ants
    s.world.add_objects( create_random_objects(n) )

    #add pheromones
    #s.world.phero_map = create_random_pheromones(100, s.world.phero_map)

    return s

def pp(s):
    for o in s.world.get_objects():
        print o.position


if __name__ == "__main__":
    #startup()
    s = setup(n = 10)
    s.simulate_steps()
    pass

