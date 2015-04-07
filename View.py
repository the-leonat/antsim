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

import matplotlib.pyplot as plt

import pyglet.window.key as key


class MainView(pyglet.window.Window):
	def __init__(self, fps = 20):
		super(MainView, self).__init__(resizable=True)

		self.label_time_passed = pyglet.text.Label('0')
		self.label_current_frame = pyglet.text.Label('0', x = 100)

		self.fps = fps

		#set by input file ---
		self.delta_time = None
		self.data_list = None
		self.pheromone_image_data = None
		self.VERSION = "0.1"
		# -----

		self.current_frame = 0
		self.number_of_frames = None
		self.state_play = False

		#can either be -1,0 or 1 (left, none, right)
		self.state_navigation = 0

		clock.schedule_interval(self.update_frame_count, 1. / self.fps)

	def on_draw(self):
		if not self.data_list: return

		time_passed = self.delta_time * self.current_frame
		self.label_time_passed.text = "{:.2f}".format(time_passed) + "s"
		self.label_current_frame.text = "f_num:" + str(self.current_frame + 1) + "/" + str(len(self.data_list))

		#get the right frame of data
		ant_list = self.data_list[self.current_frame]

		#-------- draw ---------
		self.clear()

		center_x, center_y = self.convert_coordinates( np.array([0,0]) )

		self.pheromone_image_data[self.current_frame].blit(center_x, center_y)

		for ant in ant_list:
			position = self.convert_coordinates(ant.position)
			direction = ant.direction * 5

			direction_line = np.concatenate((position - direction, position + direction))

			pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
				("v2f", direction_line)
			)

			# pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
	  #   		('v2f', position ), ('c4B', (255,0,0,255))
			# )


		self.label_time_passed.draw()
		self.label_current_frame.draw()

	def draw_grid(self):
		range_x = range(-500, 500, 100)
		range_y = range(-500, 500, 100)

	def convert_phero_map(self, phero_map):
		label = phero_map
		dim_x, dim_y = phero_map.shape

		#amplify values
		label *= 10
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
				if self.current_frame == len(self.data_list) - 1:
					self.current_frame = 0
				self.state_play = True

		## frame left
		elif symbol == key.LEFT:
			self.state_navigation = -1

		## frame right
		elif symbol == key.RIGHT:
			self.state_navigation = 1

	def on_key_release(self, symbol, modifiers):
		## reset navigation
		if symbol == key.LEFT:
			self.state_navigation = 0

		elif symbol == key.RIGHT:
			self.state_navigation = 0

	def on_resize(self, width, height):
		self.state_play = False

		#call the parent class on_resize
		return super(MainView, self).on_resize(width, height)

	#here work needs to be done
	def next_frame(self, howmany = 1):
		if not self.data_list: return

		if self.current_frame + howmany > len(self.data_list) - howmany:
			self.current_frame = 0
		else:
			#stop at border
			if self.current_frame == len(self.data_list) - 2:
				self.state_navigation = 0

			self.current_frame += howmany

	def previous_frame(self):
		if not self.data_list: return

		if self.current_frame - 1 < 0:			
			self.current_frame = len(self.data_list) - 1
		else:
			#stop at border
			if self.current_frame == 1:
				self.state_navigation = 0

			self.current_frame -= 1


	def load_file(self, filename):
		try:
			dump_dict = pickle.load(open(str(filename + "-objectdata"), 'rb'))
			if dump_dict["version"] != self.VERSION:
				print "!! Viewer Version != Simulator Version: ", self.VERSION 
				return
			self.data_list = dump_dict["data_list"]
			self.delta_time = dump_dict["delta_time"]
			self.number_of_frames = dump_dict["number_of_frames"]
			self.dimensions = dump_dict["world_dimensions"]
		except Exception, e:
			print "file not found:", filename
			raise

		try:
			matrix = np.load(filename + "-numpy.npy")
			self.pheromone_image_data = [None] * self.number_of_frames

			dimx, dimy = self.dimensions

			for x in range(self.number_of_frames):
				matrix_part = matrix[(x * dimx):(dimx * (x + 1)),:]

				self.pheromone_image_data[x] = self.convert_phero_map( matrix_part )

		except Exception, e:
			raise

		#reset framecounter to zero
		self.current_frame = 0

	def update_frame_count(self, dt):
		if not self.data_list: return

		if self.state_navigation == 1:
			self.state_play = False
			self.next_frame()
		elif self.state_navigation == -1:
			self.state_play = False
			self.previous_frame()

		if not self.state_play: return

		if self.current_frame + 1 < len(self.data_list):
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
		return position_vector + transform_v

def sp():
	plt.imshow(view.phero_map_list)
	plt.show()

# if __name__ == "__main__":
#     #startup()
#     view = MainView(fps=40)
#     view.load_file("record7")
#     pyglet.app.run()

