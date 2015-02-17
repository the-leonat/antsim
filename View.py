from __future__ import division

import pyglet
from pyglet import clock


from World import *
from Ant import *

import time
import pygame
import pygame.gfxdraw
import numpy as np
import pyglet
import cPickle as pickle


class MainView(pyglet.window.Window):
	def __init__(self, fps = 20):
		super(MainView, self).__init__()

		self.label_time_passed = pyglet.text.Label('0')
		self.label_current_frame = pyglet.text.Label('0', x = 100)

		self.fps = fps
		self.delta_time = None
		self.data = None
		self.VERSION = "0.1"
		self.current_frame = 0

		clock.schedule_interval(self.update_frame_counter, 1. / self.fps)


	def on_draw(self):
		if not self.data: return

		time_passed = self.delta_time * self.current_frame
		self.label_time_passed.text = "{:.2f}".format(time_passed) + "s"
		self.label_current_frame.text = "f_num:" + str(self.current_frame) + "/" + str(len(self.data))

		#get the right frame of data
		ant_list = self.data[self.current_frame]

		#-------- draw ---------
		self.clear()

		for ant in ant_list:
			position = self.convert_coordinates(ant.position)
			pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
	    		('v2i', tuple( position ) )
			)

		self.label_time_passed.draw()
		self.label_current_frame.draw()

	def load_file(self, file):
		try:
			dump_dict = pickle.load(open(str(file), 'rb'))
			if dump_dict["version"] != self.VERSION:
				print "!! Viewer Version != Simulator Version: ", self.VERSION 
				return
			self.data = dump_dict["data_list"]
			self.delta_time = dump_dict["delta_time"]
		except Exception, e:
			raise

		#reset framecounter to zero
		self.current_frame = 0

	def update_frame_counter(self, dt):
		if not self.data: return

		if self.current_frame + 1 < len(self.data):
			self.current_frame += 1

	def convert_coordinates(self, position_vector):
		'''
		convert the coordinates from the model to pygame coordinates
		it will set (0,0) to the center of the screen
		'''

		screen_x, screen_y = 0,0

		#transformation vector
		transform_v = np.array([screen_x / 2, screen_y / 2])

		#convert to integer array
		position_int = np.array(np.rint(position_vector + transform_v), dtype=int)

		return position_int


if __name__ == "__main__":
    #startup()
    view = MainView(fps=60)
    view.load_file("record.sim")
    pyglet.app.run()

