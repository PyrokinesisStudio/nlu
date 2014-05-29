from bge import types, logic, types


class Scene:
	"""
	A wrapper for a KX_Scene, created mainly to provide a nicer api, in a more sensible structure.
	
	A default "scene" is available on this module, and can be used elsewhere via "game.scene".

	"""

	def __init__(self):
		self.scene_core = {}

	def __iter__(self):
		return iter(self.kx_scene.objects)

	@property
	def kx_scene(self):
		return logic.getCurrentScene()

	@property
	def core(self):
		return self.scene_core[self.kx_scene]

	# Public
	def add(self, name):
		return self.kx_scene.addObject(name, self.core)

	def ray(self, src, vec):
		return self.core.rayCast(src + vec, src)

	def replace(self, name):
		self.kx_scene.replace(name)
	
	def overlay(self, name):
		logic.addScene(name)

	@property
	def scenes(self):
		return {s.name: s for s in logic.getSceneList()}

	@property
	def camera(self):
		return self.kx_scene.active_camera

	@camera.setter
	def camera(self, cam):
		self.kx_scene.active_camera = cam
	
	@property
	def objects(self):
		return self.kx_scene.objects

	@property
	def post_draw(self):
		return self.kx_scene.post_draw

	@post_draw.setter
	def post_draw(self, lst):
		self.kx_scene.post_draw = lst

scene = Scene()


class SenCollision:
	"""
	A more convenient collision detection structure, meant to wrap 
	a collision sensor with an unspecified filter (detects everything)

	"""

	def __init__(self, sensor):
		self.sensor = sensor

	# Public
	def obj_hit(self, name):
		for gobj in self.sensor.hitObjectList:
			if name == gobj.name[:len(name)]:
				return gobj

	def hit_obj(self):
		return self.sensor.hitObject


class GameObject(types.KX_GameObject):

	def __new__(cls, *args, **kwargs):
		"""
		GameObject(gobj=cont.owner) will reinstance owner to be of type GameObject.

		If the "gobj" keyword argument is ommited, an attempt will be made to create
		a new instance of an object with the same name as that of the class (it is assumed 
		this object exists). That new instance will then be reinstanced.

		With this, it is now also possible to provide various constructor arguments,
		for any subclass of GameObject:

		Bomb(x, y, time_to_boom)
		
		Or, if you want to reinstance an existing KX_GameObject:
		
		Bomb(x, y, time_to_boom, gobj=kx_bomb)

		In either case, the constructor for Bomb should look like this:
		
		def __init__(self, x, y, time_to_boom, **kwargs):
			super().__init__()

			# the rest of your init code ...

		"""
		if "gobj" in kwargs:
			gobj = kwargs["gobj"]
		else:
			gobj = scene.add(cls.__name__)

		return super().__new__(cls, gobj)

	def __init__(self):
		# The first controller is assumed to run init, which would run even for already
		# reinstanced objects. The existence of this property is used to avoid a double
		# reinstancing.
		self["init"] = True;

		# The second controller is assumed to run main, and is used as active.
		# All relevant sensors and actuators (used by the object) should connect to it.
		self.cont = self.controllers[1]

		# Crate a more convenient collision sensor.
		# n_sensors could store additional alternatives, for additional sensor types,
		# but I don't think there's a need for anything beyond collision.
		# (the name "sensors" denotes an already existing property, hence "n_sensors")
		self.n_sensors = {s.name: SenCollision(s) 
				for s in self.cont.sensors 
				if type(s) == types.KX_TouchSensor}

		# I use link groups to specify instances of any given master object.
		# The following code merges properties defined on the link group object (usually an Empty)
		# with those on the actual spawned instance, along with replicating whatever parent/child
		# relationships exist on the link group, so that they're inherited by the spawned instance.
		group = self.groupObject
		if group:
			for name in group.getPropertyNames():
				self[name] = group[name]
			if group.parent:
				self.setParent(group.parent)
			for c in group.children:
				c.setParent(self)


		self.components = []

		# If you want to suspend all logic execution: gobj.main = gobj.idle
		self.main = self.run

		
	# Public
	def idle(self):
		pass

	def run(self):
		for c in self.components:
			c.main()
	
	def ray(self, vec):
		return scene.ray(self.position, vec)

	def ray_cut(self, vec):
		hit, pos, _ = self.ray(vec)

		return (hit, mt.Vector(pos) - self.worldPosition if hit else None)

	def align_axis_to_vec(self, axis, vec):
		if isinstance(axis, str):
			axis = {'x':0, 'y':1, 'z':2}[axis]

		self.alignAxisToVect(vec, axis)
	
	def end(self):
		self.endObject()


class Component:

	def __init__(self, gobj):
		self.gobj = gobj

		self.state = "idle"
	
	def idle(self):
		pass

	@property
	def state(self):
		return self.main.__name__

	@state.setter
	def state(self, state_name):
		self.main = getattr(self, state_name)



def end():
	logic.endGame()
