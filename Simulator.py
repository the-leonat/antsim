import Settings as settings
from World import * 
from Viewer import *
import time
import matplotlib.pyplot as plt
import pygame
import pygame.gfxdraw
import numpy as np

class Simulator():
	'''
	This class simulates the behavior of worldobjects over time
	'''
	s_modes = ["live", "record"]

	def __init__(self, mode):
		#always use set_mode function to set mode. dont set string directly
		self.mode = None
		self.set_mode(mode)

		self.world = World()

		self.screen = None

		if self.is_mode("live"):
			self.screen = self.init_screen(400,400)
			self.screen.fill((255,255,255))



	def set_mode(self, mode):
		'''
		sets the simulation mode to a mode. modes are defined in world.s_modes.
		'''

		if str(mode) in Simulator.s_modes:
			self.mode = str(mode)
		else:
			print "! mode '" + str(mode) + "' not found. set to '" + Simulator.s_modes[0] + "'"
			self.mode = Simulator.s_modes[0]

	def is_mode(self, mode):
		'''
		checks if mode equals the current mode
		'''
		if str(mode) in Simulator.s_modes:
			if str(mode) == self.mode:
				return True
			else: 
				return False

		return False

	def process_pygame_events(self):
		pygame.event.pump()
		events = pygame.event.get()

		for event in events:
			if event.type==pygame.VIDEORESIZE:
				self.screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
				self.screen.fill((255,255,255))
				pygame.display.flip()
				print "new display size"


	def init_screen(self, width, height):
		pygame.init()
		size = width, height
		
		return pygame.display.set_mode(size, pygame.RESIZABLE)


	def simulate_steps(self, n = 1, redraw=True):
		'''
		this function simulates the behavior of worldobjects for one step and returns a list of objects
		optional param n is the number of steps to simulate		
		'''

		self.process_pygame_events()

		for x in range(0,n):
			#update the world model
			self.world.update()

			if self.is_mode("live") and redraw:
				#self.draw_data()
				self.draw_position_over_time()

		if self.is_mode("live"):
			#self.draw_data()
			self.draw_position_over_time()
	
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
		position_int = np.array(np.rint(position_vector + transform_v), dtype=np.int)

		return position_int

	def draw_position_over_time(self):

		for o in self.world.get_objects():
			if o.is_type("ant"):
				x,y = self.convert_coordinates(o.position)
				self.screen.set_at((x, y), (0,0,0))


		# #update the screen
		pygame.display.flip()




	def draw_data(self):
		'''
		takes all gameobjects and renders them
		'''
		self.screen.fill((255,255,255,0))

		# phero_surface = pygame.Surface((400,400), flags=pygame.SRCALPHA)
		# phero_surface.fill((50,50,255,0))

		# #render the phero map first then blit ants into it
		# alpha_data = self.world.phero_map.copy()
		# #convert to rgba alpha format, 0 - 255
		# alpha_data = alpha_data * 255
		# alpha_data = alpha_data.astype(dtype=np.uint8)

		# # alpha_map = pygame.surfarray.pixels_alpha(phero_surface)
		# # alpha_map = alpha_data

		# #suuuper langsam
		# for y in range(400):
		# 	for x in range(400):
		# 		phero_surface.set_at((x,y), (50,50,255, alpha_data[x,y])) 


		# self.screen.blit(phero_surface, (0,0))

		#render the ants
		for o in self.world.get_objects():
			#print "[" + str(o.type) + "] pos:", o.position

			#render ant
			if o.is_type("ant"):
				position_int = self.convert_coordinates(o.position)

				#convert to int
				direction_int = np.array(np.rint( o.direction * o.speed), dtype=int)

				#print "position int: ", position_int


				#render position
				pygame.draw.circle(self.screen, (0,0,0,255), tuple(position_int), o.center_radius, 1)

				
				pygame.draw.line(self.screen, (255,0,0,255), tuple(position_int), tuple(position_int + direction_int), 2)
		                


		# #update the screen
		pygame.display.flip()





def create_random_objects(n):
	'''
	returns a list of n antobjects with random position and direction vectors
	'''


	#returns n objects with position between (10,10) and (390,390)
	return [Ant([np.random.randint(-200,200), np.random.randint(-200,200)], [np.random.uniform(-1,1), np.random.uniform(-1,1)]) for a in range(0,n)]

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
	s.world.phero_map = create_random_pheromones(100, s.world.phero_map) 
       

	
	return s

if __name__ == "__main__":
	#startup()
	s = setup(n = 10)
	s.simulate_steps()
	pass
	
