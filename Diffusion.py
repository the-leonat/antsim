import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def diffuse(mapp):
	rate = np.array([[0.0625,0.0625,0.0625],[0.0625,0.5,0.0625],[0.0625,0.0625,0.0625]])
	#rate = np.array([[0.2,0.2,0.2],[0.2,0.5,0.2],[0.2,0.2,0.2]])
	return scipy.signal.convolve(mapp, rate)


map = np.zeros((400,400))



diffuse(map)
plt.imshow(map)
