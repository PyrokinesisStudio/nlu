import string
import mathutils as mt
from bge import logic, render
from bge import events as ev
from nlu import game

class Keyboard:

	string_const = {c: ord(c) for c in string.printable}
	string_const.update({
		"left": ev.LEFTARROWKEY,
		"right": ev.RIGHTARROWKEY,
		"up": ev.UPARROWKEY,
		"down": ev.DOWNARROWKEY,
		"enter": ev.ENTERKEY,
		"back": ev.BACKSPACEKEY,
		"space": ev.SPACEKEY,
		"rctrl": ev.RIGHTCTRLKEY,
		"lctrl": ev.LEFTCTRLKEY
	})
	string_const["INVERSE"] = {v: k for k, v in string_const.items()}


	def __init__(self,
			kx_dev=logic.keyboard,
			string_const=None):

		self.kx_dev = kx_dev

		if not string_const:
			string_const = Keyboard.string_const

		self.string_const = string_const
		self.const_string = string_const["INVERSE"]

	def key_hit(self, key, status=logic.KX_INPUT_JUST_ACTIVATED):
		key = self.string_const[key]
		return self.kx_dev.events[key] == status

	def key_down(self, key):
		return self.key_hit(key, logic.KX_INPUT_ACTIVE)

	def key_up(self, key):
		return self.key_hit(key, logic.KX_INPUT_JUST_RELEASED)
	
	def hit_key(self):
		activated = logic.KX_INPUT_JUST_ACTIVATED
		for key, status in self.kx_dev.active_events.items():
			if status == activated:
				return self.const_string[key]

		return None

class Mouse(Keyboard):

	string_const = {
		"left": ev.LEFTMOUSE,
		"right": ev.RIGHTMOUSE,
		"middle": ev.MIDDLEMOUSE,
		"wheel_up": ev.WHEELUPMOUSE,
		"wheel_down": ev.WHEELDOWNMOUSE,
		"x": ev.MOUSEX,
		"y": ev.MOUSEY
	}
	string_const["INVERSE"] = {v: k for k, v in string_const.items()}

	def __init__(self):
		super().__init__(logic.mouse, Mouse.string_const)

		name_keymeth = {name: getattr(self, name) 
				for name in dir(self) 
				if "key" in name}

		for n, fn in name_keymeth.items():
			setattr(self, n.replace("key", "btn"), fn)

	def show(self):
		render.showMouse(1)
	
	def hide(self):
		render.showMouse(0)
	
	def hit_obj(self):
		core = game.scene.core
		return core.sensors["mouse"].hitObject
	
	def ray_source(self):
		core = game.scene.core
		return core.sensors["mouse"].raySource

	def ray_target(self):
		core = game.scene.core
		return core.sensors["mouse"].rayTarget

	@property
	def position(self):
		return mt.Vector(logic.mouse.position)

	@position.setter
	def position(self, vec):
		logic.mouse.position = tuple(vec)

	@property
	def position_pix(self):
		core = game.scene.core
		return mt.Vector(core.sensors["mouse"].position)

	@position_pix.setter
	def position_pix(self, vec):
		render.setMousePosition(*[int(v) for v in vec])


keyboard = Keyboard()
mouse = Mouse()
