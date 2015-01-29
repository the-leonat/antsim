import matplotlib
#matplotlib.use('GTKAgg')
import matplotlib.pyplot as plt


import numpy as np
import time
import sys

n = 1000

fig=plt.figure() #Figure Objekt
ax = plt.axes(xlim=(n),ylim=(n))

image = ax.imshow( np.zeros((n,n)), vmin=0, vmax=100)

#fig.canvas.draw()
#plt.pause(0.01)

def set_phero_map(mapp):
	image.set_data(mapp)

def tick():
	print "draw"
	fig.canvas.draw()
	plt.pause(0.0001)
	#fig.canvas.flush_events()

