from __future__ import division
import numpy as np
from vispy import app
from vispy import gloo
from vispy.util.transforms import perspective, translate, rotate, yrotate

from Storage import Storage
from Simulator import Simulator

import Global as g

ant_vertex_shader = """
uniform   vec2 u_dimension;
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;

attribute vec3 a_position;

void main (void)
{
    gl_Position = u_projection * u_view * u_model * vec4(a_position / vec3(u_dimension, 1.0), 1.0);
}
"""

ant_fragment_shader = """
void main()
{
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
"""

phero_vertex_shader = """

uniform   vec2 u_dimension;
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;

attribute vec3 a_position;

void main (void)
{
    gl_Position = u_projection * u_view * u_model * vec4(a_position / vec3(u_dimension, 1.0), 1.0);
}
"""

phero_fragment_shader = """
void main()
{
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
"""

class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')

        self.init_simulation_parameters()

        self.program = gloo.Program(ant_vertex_shader, ant_fragment_shader)
        self.program['u_dimension'] = self.dimensions

        self.init_matrices()

        self.current_frame = 0

        self.timer = app.Timer(interval='auto', connect=self.on_timer)
        self.simulation_timer = app.Timer(interval=1./50, connect=self.update_simulation_data)

        #self.timer.start()
        self.simulation_timer.start()

    def init_matrices(self):
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        rotate(self.view, -60, 1, 0, 0)
        rotate(self.model, 45, 0, 0, 1)
        translate(self.view, 0, 0, -1.3)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
    
    def init_simulation_parameters(self):
    	if g.live:
    		self.dimensions = g.simulator.world.dimensions
    		self.delta_time = g.simulator.world.delta_time
    		self.frame_count = 0
    	else:
	        self.delta_time = g.storage.keyval_get("world_delta_time")
	        self.frame_count = g.storage.keyval_get("frame_count")
	        self.dimensions = g.storage.keyval_get("world_dimensions")
	        self.record_step = g.storage.keyval_get("record_step")
	        #self.ant_count = g.storage.keyval_get("ant_count")

    def update_simulation_data(self, event):
    	if g.live:
    		g.simulator.simulate_steps()
    		ant = g.simulator.world.world_objects_to_numpy()
    		self.frame_count += 1
    	else:
	        if self.current_frame >= self.frame_count:
	            self.current_frame = 0
	        else:
	            self.current_frame += 1   
	        ant = g.storage.get("ant", self.current_frame)

        nant = np.empty((ant.shape[1] * 2, 3))

        
        #set x,y
        nant[0::2, :2] = ant[0,:,:] + ant[1,:,:] * 5
        nant[1::2, :2] = ant[0,:,:] - ant[1,:,:] * 5
        #set z
        nant[:,2:3] = 0
        
        self.program['a_position'] = gloo.VertexBuffer(nant.astype(np.float32))
        self.update()

    def on_initialize(self, event):
        # Set uniform and attribute
        gloo.set_state(clear_color='white')

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)
        self.projection = perspective(60.0, width / float(height), 0.1, 100.0)
        self.program['u_projection'] = self.projection

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('lines')
    
    def on_timer(self, event):
		rotate(self.model, .25, 0, 0, 1)
		self.program['u_model'] = self.model

		self.update()

    def show_fps(self, fps):
        print(fps)


def start_view(fps):
    c = Canvas()
    c.measure_fps(1, c.show_fps)
    c.show()
    app.run()
