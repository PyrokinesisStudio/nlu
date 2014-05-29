import pickle
import itertools as it
import bpy
from bge import events
from nlu import (
	game,
	inputs,
	geometry,
	time
)

def dump_to_textblock(frames, sprycle):
	b_sprycle = bpy.data.objects[sprycle.name]
	text_name = "frames_{:s}".format(sprycle.name)
	if text_name in bpy.data.texts:
		b_text = bpy.data.texts[text_name]
	else:
		b_text = bpy.data.texts.new(text_name)
	if not len(b_sprycle.game.controllers):
		bpy.ops.logic.controller_add(type="PYTHON", object=sprycle.name)
		b_sprycle.game.controllers[0].text = b_text
	b_text.clear()
	b_text.write(str(pickle.dumps(frames)))


class TexAnim(game.Component):
	
	def __init__(self, gobj, sprycle,
			cycle_frames=None,
			cycle=None,
			fps=10,
			cb_frame=None,
			cb_cycle=None):

		super().__init__(gobj)

		self.sprycle = sprycle
		self.sprycle_poly = geometry.Mesh(sprycle.meshes[0]).polygons[0]

		if cycle_frames:
			self.cycle_frames = cycle_frames
		else:
			data = eval(sprycle.controllers[0].script)
			self.cycle_frames = pickle.loads(data)

		self.cb_frame = cb_frame # fn()
		self.cb_cycle = cb_cycle # fn(cycle_name)

		cycles = list(self.cycle_frames.keys())
		if not cycle in cycles:
			cycle = cycles[0]

		self.timer = time.Timer()
		self.fps = fps

		self.active_cycle_name = None
		self.active_cycle = None
		self.cycle(cycle)

		self.velocity_factor = 5

		self.state = "animation"

	def play_next_frame(self):
		coords = next(self.active_cycle)
		self.sprycle_poly.tex_coords = coords

		if self.cb_frame:
			self.cb_frame()

	def face_direction(self, d):
		self.sprycle.localScale[0] = abs(self.sprycle.localScale[0]) * d

	# States
	def animation(self):
		if self.timer.done():
			self.play_next_frame()
	
	def animation_by_velocity(self):
		self.fps = self.fn_fps()
		self.animation()

	# Public
	def cycle(self, cycle_name):
		if cycle_name == self.active_cycle_name:
			return

		self.active_cycle_name = cycle_name

		self.active_cycle = it.cycle(self.cycle_frames[cycle_name])
		if self.cb_cycle:
			self.cb_cycle(cycle_name)

		self.timer.restart()
		self.play_next_frame()
	
	def auto(self, fn_fps):
		self.fn_fps = fn_fps
		self.state = "animation_by_velocity"

	@property
	def fps(self):
		return self._fps

	@fps.setter
	def fps(self, fps):
		if fps < 0:
			self.face_direction(-1)
		elif fps > 0:
			self.face_direction(1)
			
		self.timer.delta = 1/abs(fps) if fps else float("inf")

		self._fps = fps
	
class MouseControl(game.Component):

	def __init__(self, gobj, tex_anim, sprycle):
		super().__init__(gobj)

		self.tex_anim = tex_anim
		self.sprycle = sprycle

		self.state = "control_cycle"

	# States
	def control_cycle(self):
		mouse = inputs.mouse
		if mouse.btn_hit("left"):
			hit_obj = mouse.hit_obj()
			if hit_obj and "active" in hit_obj:
				cycle = hit_obj.name.split('.')[0]
				self.gobj["cycle"] = cycle
				self.tex_anim.cycle(cycle)

		if mouse.btn_down("left"):
			self.mp = mouse.position_pix
			self.fps = self.tex_anim.fps
			self.state = "control_frame"

	def control_frame(self):
		mouse = inputs.mouse
		if mouse.btn_down("left"):
			delta = mouse.position_pix - self.mp
			self.tex_anim.fps = self.fps + int(delta.x / 7)
			self.gobj["fps"] = self.tex_anim.fps
		else:
			self.state = "control_cycle"



class App(game.GameObject):
	
	def __init__(self, **kwargs):
		super().__init__()

		inputs.mouse.show()

		b_selected = bpy.context.active_object
		sprycle = self.sprycle(b_selected)

		self.planes = self.cycle_planes(sprycle)
		self.active_cycle = None # on_cycle
		self.active_plane = None # on_frame

		frames = self.cycle_frames(sprycle)
		dump_to_textblock(frames, sprycle)

		self["cycle"] = b_selected.name.split('.')[0]

		tex_anim = TexAnim(self, sprycle, frames, 
				self["cycle"], self["fps"],
				self.on_frame, self.on_cycle)

		mouse_control = MouseControl(self, tex_anim, sprycle)

		self.components = [tex_anim, mouse_control]

		for c in sprycle.children:
			c["active"] = True
			c.removeParent()

	def grouped_cplanes(self, sprycle):
		c_planes = sorted(sprycle.children, key=lambda x: x.name)
		groups = it.groupby(c_planes, key=lambda x: x.name.split('.')[0])
		return [(n, sorted(g, key=lambda x: x.worldPosition.x)) for n, g in groups]

	def cycle_frames(self, sprycle):
		obj_tex_coords = lambda o: geometry.Mesh(o.meshes[0]).polygons[0].tex_coords_lists
		return {n: list(map(obj_tex_coords, g)) for n, g in self.grouped_cplanes(sprycle)}

	def cycle_planes(self, sprycle):
		return {n: list(g) for n, g in self.grouped_cplanes(sprycle)}

	def on_cycle(self, cycle_name):
		self.active_cycle = it.cycle(self.planes[cycle_name])
	
	def on_frame(self):
		scale_factor = 1.2
		if self.active_plane:
			self.scale_factor(self.active_plane, 1/scale_factor)
		self.active_plane = next(self.active_cycle)
		self.scale_factor(self.active_plane, scale_factor)
	
	def scale_factor(self, gobj, factor):
		ls = self.active_plane.localScale
		self.active_plane.localScale = [i * factor for i in ls]
	
	def sprycle(self, b_selected):
		if b_selected.parent:
			sprycle_name = b_selected.parent.name
		else:
			sprycle_name = b_selected.name
		return self.scene.objects[sprycle_name]
		


def init(cont):
	
	App(gobj=cont.owner)

def main(cont):

	cont.owner.main()
