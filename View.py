from __future__ import division

import pyglet
from pyglet import clock


from World import *
from Ant import *
from Storage import *
from pygarrayimage.arrayimage import ArrayInterfaceImage

import time
import numpy as np
import pyglet

import matplotlib.pyplot as plt

import pyglet.window.key as key

import Global as g

class MainView(pyglet.window.Window):
    version = "0.4"

    def __init__(self, filename, fps = 20):
        super(MainView, self).__init__(resizable=True)

        #the batch for grouped rendering
        self.batch = pyglet.graphics.Batch()  
        self.current_frame = 0
        self.state_play = False
        #can either be -1,0 or 1 (left, none, right)
        self.state_navigation = 0

        self.init_labels()

        self.fps = fps
        self.transform = np.array([0,0], dtype=np.int)

        self.load_file()

        self.init_border()

        self.init_vertex()

        self.start()

    def load_file(self):
        if not self.check_version( g.storage.keyval_get("version") ): return

        self.delta_time = g.storage.keyval_get("world_delta_time")
        self.number_of_frames = g.storage.keyval_get("frame_count")
        self.dimensions = g.storage.keyval_get("world_dimensions")
        self.record_step = g.storage.keyval_get("record_step")
        self.ant_count = g.storage.keyval_get("ant_count")

    def check_version(self, file_version):
        if file_version != MainView.version:
            print("Viewer Version != Simulator Version: " + str(self.VERSION))
            return False
        return True

    def init_labels(self):
        self.label_time_passed = pyglet.text.Label('0', y = 5, batch=self.batch)
        self.label_current_frame = pyglet.text.Label('0', x = 100, y = 5, batch=self.batch)
        self.label_fps = pyglet.text.Label('0', x = 300, y = 5, batch=self.batch)

    def init_border(self):
        sx, sy = np.array(self.dimensions, dtype=np.float) / 2.

        self.border = self.batch.add(4, pyglet.gl.GL_LINE_LOOP, None, 
            ("v2f", (
                sx, sy,
                sx, -sy,
                -sx, -sy,
                -sx, sy
                )
            )
        )

    def init_vertex(self):
        #double size ant is drawn with 2 vertices (line)
        self.ants = self.batch.add(self.ant_count * 2, pyglet.gl.GL_LINES, None, 
            "v2f/stream", ("c3B/static", tuple(np.full((self.ant_count * 3 * 2), 255, dtype=int) ))
        )

    def start(self):    
        clock.schedule_interval(self.update_frame_count, 1. / self.fps)

    def on_draw(self):
        time_passed = self.delta_time * self.current_frame * self.record_step

        self.label_time_passed.text = "{:.2f}".format(time_passed) + "s"
        self.label_current_frame.text = "f_num:" + str(self.current_frame + 1) + "/" + str(g.storage.length)
        self.label_fps.text = str(pyglet.clock.get_fps()) + "fps"

        #get the right frame of data
        ant_numpy_list = g.storage.get("ant", self.current_frame)

        #-------- draw ---------
        self.clear()
        pyglet.gl.glLoadIdentity()

        tx, ty = self.convert_coordinates([0,0])

        pyglet.gl.glTranslatef(tx, ty, 0); 

        phero_map = g.storage.get("phero", self.current_frame)
        image = self.convert_phero_map(phero_map)
        image.blit(0,0)

        self.ants.vertices[0::4] = ant_numpy_list[0,:,0] - (ant_numpy_list[1,:,0] * 5)
        self.ants.vertices[1::4] = ant_numpy_list[0,:,1] - (ant_numpy_list[1,:,1] * 5)
        self.ants.vertices[2::4] = ant_numpy_list[0,:,0] + (ant_numpy_list[1,:,0] * 5)
        self.ants.vertices[3::4] = ant_numpy_list[0,:,1] + (ant_numpy_list[1,:,1] * 5)

        self.batch.draw()

    def draw_grid(self):
        range_x = range(-500, 500, 100)
        range_y = range(-500, 500, 100)

    def convert_phero_map(self, phero_map):
        label = phero_map.copy()
        dim_x, dim_y = phero_map.shape

        #amplify values
        label /= 10
        label = np.clip(label, 0., 1.)

        #display phero map in light red
        label3=np.dstack((label * 255,label * 1,label * 1)).astype(np.uint8)

        image = pyglet.image.ImageData(dim_x, dim_y, 'RGB', label3.data.__str__())
        #image = pyglet.image.ImageData(dim_x, dim_y, 'RGB', label3.tostring('C'))

        image.anchor_x = int(dim_x / 2)
        image.anchor_y = int(dim_y / 2)

        return image




    def on_key_press(self, symbol, modifiers):
        ## play / pause
        if symbol == key.SPACE:
            if self.state_play:
                self.state_play = False
            else:
                if self.current_frame == g.storage.length - 1:
                    self.current_frame = 0
                self.state_play = True

        ## frame left
        elif symbol == key.LEFT:
            self.state_navigation = -1

        ## frame right
        elif symbol == key.RIGHT:
            self.state_navigation = 1

        elif symbol == key.W:
            self.transform[1] -= 50
            self.init_border()
        elif symbol == key.A:
            self.transform[0] += 50
            self.init_border()
        elif symbol == key.S:
            self.transform[1] += 50
            self.init_border()
        elif symbol == key.D:
            self.transform[0] -= 50
            self.init_border()


    def on_key_release(self, symbol, modifiers):
        ## reset navigation
        if symbol == key.LEFT:
            self.state_navigation = 0

        elif symbol == key.RIGHT:
            self.state_navigation = 0

    def on_resize(self, width, height):
        self.state_play = False

        #reinit the border
        self.init_border()


        #call the parent class on_resize
        return super(MainView, self).on_resize(width, height)

    #here work needs to be done
    def next_frame(self, howmany = 1):
        if self.current_frame + howmany > g.storage.length - howmany:
            self.current_frame = 0
        else:
            #stop at border
            if self.current_frame == g.storage.length - 2:
                self.state_navigation = 0

            self.current_frame += howmany

    def previous_frame(self):
        if self.current_frame - 1 < 0:
            self.current_frame = g.storage.length - 1
        else:
            #stop at border
            if self.current_frame == 1:
                self.state_navigation = 0

            self.current_frame -= 1


    def update_frame_count(self, dt):
        if self.state_navigation == 1:
            self.state_play = False
            self.next_frame()
        elif self.state_navigation == -1:
            self.state_play = False
            self.previous_frame()

        if not self.state_play: return

        if self.current_frame + 1 < g.storage.length:
            self.next_frame()
        else:
            self.state_play = False

    def convert_coordinates(self, position_vector):
        '''
        convert the coordinates from the model to pygame coordinates
        it will set (0,0) to the center of the screen
        '''

        screen_x, screen_y = self.width,self.height

        #transformation vector
        transform_v = np.array([screen_x / 2, screen_y / 2])

        #convert to integer array
        return position_vector + transform_v + self.transform


def start_view(fps):
    view = MainView(fps)
    pyglet.app.run()

