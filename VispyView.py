from __future__ import division
import numpy as np
from vispy import app
from vispy import gloo
from vispy.util.transforms import perspective, translate, rotate

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
// Uniforms
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;
uniform vec2 u_dimension;


// Attributes
attribute vec2 a_position;
attribute vec2 a_texcoord;

// Varyings
varying vec2 v_texcoord;
varying float v_max_value;


// Main
void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position / u_dimension,0,1.0);
}
"""

phero_fragment_shader = """
uniform sampler2D u_texture;
uniform vec3 u_color;

varying vec2 v_texcoord;

float convertColor(float normed_lum, float from, float to)
{
    if(normed_lum >= from && normed_lum <= to) {
        return (normed_lum - from) / (to - from);
    }
    else if(normed_lum > to) {
        return 1.;
    } else {
        return 0.;
    }
}


vec4 convertRGBA(float lum)
{
    float a = 0.0001;
    float normed_lum = (exp(a * lum) -1.) / (exp(a) -1.);

    return vec4(
        1. - normed_lum * (1. - u_color[0]),
        1. - normed_lum * (1. - u_color[1]),
        1. - normed_lum * (1. - u_color[2]), 0.);
}

void main()
{
    float luminance = texture2D(u_texture, v_texcoord).r;
    gl_FragColor = convertRGBA(luminance);
}
"""

class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')

        self.init_simulation_parameters()

        self.ant_shader = gloo.Program(ant_vertex_shader, ant_fragment_shader)
        self.phero_shader = gloo.Program(phero_vertex_shader, phero_fragment_shader)

        self.init_matrices()
        self.init_texture_bounds()

        self.ant_shader['u_dimension'] = self.dimensions / 2
        self.phero_shader['u_dimension'] = self.dimensions / 2

        self.texture = gloo.Texture2D(np.zeros(self.dimensions, dtype=np.float32))
       	self.phero_shader['u_texture'] = self.texture
        self.phero_shader['u_color'] = np.array([240, 10, 130]) / 255.

        self.phero_shader.bind(gloo.VertexBuffer(self.texture_bounds))

        self.current_frame = 0

        self.timer = app.Timer(interval='auto', connect=self.on_timer)
        self.simulation_timer = app.Timer(interval='auto', connect=self.update_simulation_data)

        self.timer.start()
        self.simulation_timer.start()
        self.bool = True

    def init_matrices(self):
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.translate = 2.3

        #rotate(-60, (1, 0, 0))
        #rotate(self.model, 45, 0, 0, 1)
        #translate((0, 0, -self.translate))

        self.view = self.view.dot(rotate(-60, (1, 0, 0)))
        self.view = self.view.dot(translate((0, 0, -self.translate)))

        self.ant_shader['u_model'] = self.model
        self.ant_shader['u_view'] = self.view

        self.phero_shader['u_model'] = self.model
        self.phero_shader['u_view'] = self.view

    def init_texture_bounds(self):
        W, H = self.dimensions / 2
        data = np.zeros(4, dtype=[('a_position', np.float32, 2),
                                  ('a_texcoord', np.float32, 2)])
        data['a_position'] = np.array([[-W, -H], [W, -H], [-W, H], [W, H]])
        data['a_texcoord'] = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])

        self.texture_bounds = data

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
            phero = g.simulator.world.phero_map.phero_map.astype(np.float32)
            self.frame_count += 1
        else:
            if self.current_frame >= self.frame_count - 1:
                self.current_frame = 0
            else:
                self.current_frame += 1

            ant = g.storage.get("ant", self.current_frame)
            phero = g.storage.get("phero", self.current_frame)


        #norm phero map to values between 0 and 1
        if self.bool:
            self.bool = False
        else:
            #print np.amax(phero)
            self.bool = True
            phero = phero / np.amax(phero)
            self.texture.set_data(phero.astype(np.float32))
        #self.phero_shader['u_mean'] = np.mean(phero)
        #self.phero_shader['u_deviation'] = np.std(phero)

        #print self.phero_shader['u_mean']


        nant = np.empty((ant.shape[1] * 2, 3))

        #set x,y
        nant[0::2, :2] = ant[0,:,:] + ant[1,:,:] * 5
        nant[1::2, :2] = ant[0,:,:] - ant[1,:,:] * 5
        #set z
        nant[:,2:3] = 0

        self.ant_shader['a_position'] = gloo.VertexBuffer(nant.astype(np.float32))

        #self.update()

    def on_initialize(self, event):
        # Set uniform and attribute
        gloo.set_state(clear_color='white')

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)
        self.projection = perspective(60.0, width / float(height), 0.1, 100.0)
        self.ant_shader['u_projection'] = self.projection
        self.phero_shader['u_projection'] = self.projection

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.phero_shader.draw('triangle_strip')
        self.ant_shader.draw('lines')
        rect

    def on_timer(self, event):
        #rotate(self.model, 0.05, 0, 0, 1)
        self.ant_shader['u_model'] = self.model
        self.phero_shader['u_model'] = self.model
        self.update()

    def on_mouse_wheel(self, event):
        self.translate += event.delta[1] * 4
        self.translate = min(80, max(0, self.translate))
        self.view = np.eye(4, dtype=np.float32)

        self.view = self.view.dot(rotate(-self.translate, (1, 0, 0)))
        self.view = self.view.dot(translate((0, 0, -2.3)))

        self.ant_shader['u_view'] = self.view
        self.phero_shader['u_view'] = self.view

        self.update()

    def show_fps(self, fps):
        print(fps)


def start_view(fps):
    c = Canvas()
    c.measure_fps(1, c.show_fps)
    c.show()
    app.run()
