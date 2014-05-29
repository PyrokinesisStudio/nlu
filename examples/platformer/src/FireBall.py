from Pipe import Pipe
from nlu import game

class PipeSpawn(game.Component):

	def __init__(self, gobj, color, color_pipe):
		super().__init__(gobj)

		self.color = color
		self.color_pipe = color_pipe

		self.state = "spawn"
	
	# States
	def spawn(self):
		vel = self.gobj.getLinearVelocity()
		vel.magnitude = 0.25
		_, pos, _ = self.gobj.ray(vel)
		if pos:
			pipe = Pipe()

			if self.color == "orange":
				self.flip(pipe)

			pipe_old = self.color_pipe[self.color]
			if pipe_old:
				pipe_old.burrow()

			pipe.worldPosition = pos
			pipe.worldPosition.z -= 0.6
			pipe.grow()

			self.color_pipe[self.color] = pipe

			pipes = list(self.color_pipe.values())
			if not None in pipes:
				self.bind_pipes(pipes)

			self.gobj.end()
	
	# Private
	def flip(self, pipe):
		col = pipe.worldOrientation.col
		col[0] *= -1
		col[1] *= -1

	def bind_pipes(self, pipes):
		a, b = pipes

		a.terminus = b
		b.terminus = a
	

class FireBall(game.GameObject):

	def __init__(self, color, color_pipe, **kwargs):
		super().__init__()

		spawn = PipeSpawn(self, color, color_pipe)

		self.components = [spawn]

def init(cont):
	if not "init" in cont.owner:
		FireBall(gobj=cont.owner)

def main(cont):
	cont.owner.main()
