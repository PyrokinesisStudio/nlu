from nlu import game

class Transporting(game.Component):

	def __init__(self, gobj):
		super().__init__(gobj)

		self.terminus = None # Set by FireBall

		self.collision = self.gobj.n_sensors["collision"]

	# States
	def transport(self):
		gobj = self.collision.obj_hit("Player")
		if gobj:
			gobj.worldPosition = self.terminus.worldPosition
			gobj.worldPosition.z += 0.5
			gobj.setLinearVelocity([0, 0, 6])


class Growing(game.Component):
	
	def __init__(self, gobj):
		super().__init__(gobj)

		self.cont = self.gobj.controllers["Python1"]
		self.act = self.cont.actuators[1]

	def grow(self):
		act = self.cont.actuators[0]
		self.cont.activate(act)
		self.state = "idle"
	
	def burrow(self):
		self.gobj["frame"] = 0
		self.act.framePropName = "frame"
		self.cont.activate(self.act)
		self.state = "end"
	
	def end(self):
		if self.gobj["frame"] == self.act.frameEnd:
			self.gobj.end()
	
		

class Pipe(game.GameObject):

	def __init__(self, **kwargs):
		super().__init__()

		self.trans = Transporting(self)
		self.growing = Growing(self)

		self.components = [self.trans, self.growing]

	# Public
	def burrow(self):
		self.growing.state = "burrow"

	def grow(self):
		self.growing.state = "grow"

	@property
	def terminus(self, pipe):
		return self.trans.terminus

	@terminus.setter
	def terminus(self, pipe):
		self.trans.terminus = pipe
		self.trans.state = "transport"



def init(cont):
	if not "init" in cont.owner:
		Pipe(gobj=cont.owner)

def main(cont):
	cont.owner.main()
