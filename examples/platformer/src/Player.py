from nlu import game, inputs
from FireBall import FireBall
import mathutils as mt
from collections import defaultdict
import sprycle


class PipeShooting(game.Component):

	def __init__(self, gobj):
		super().__init__(gobj)

		inputs.mouse.show()

		self.color_pipe = {"green": None, "orange": None} # Filled by FireBall

		btn_color = {"left": "green", "right": "orange"}
		self.btn_color = defaultdict(lambda: None, btn_color)

		self.state = "shoot"
	
	# States
	def shoot(self):
		color = self.btn_color[inputs.mouse.hit_btn()]
		if color:
			self.fire(color, self.target_pos())
	
	# Private
	def fire(self, color, pos):
		vel = pos - self.gobj.worldPosition
		vel.magnitude = 10
		fb = FireBall(color, self.color_pipe)
		fb.worldPosition = self.gobj.worldPosition
		fb.setLinearVelocity(vel)
	
	def target_pos(self):
		vec = inputs.mouse.ray_source()
		vec.y = 0
		return vec

class AnimControl(game.Component):

	def __init__(self, gobj, movement, tex_anim):
		super().__init__(gobj)

		tex_anim.auto(lambda: self.gobj.getLinearVelocity().x * 5)
		self.tex_anim = tex_anim
		self.movement = movement

		self.state = "move"
	
	def move(self):
		if self.movement.on_ground():
			vx = self.gobj.getLinearVelocity().x
			if abs(vx) > 0.01:
				self.tex_anim.cycle("walk")
			else:
				self.tex_anim.cycle("stand")
		else:
			self.tex_anim.cycle("jump")

class Movement(game.Component):

	def __init__(self, gobj, on_ground):
		super().__init__(gobj)

		self.on_ground = on_ground

		self.speed = 3
		self.speed_air = self.speed / 2
		self.force_accel = 10
		self.force_accel_air = self.force_accel / 2
		self.force_jump = 350

		self.state = "move"

	# States
	def move(self):
		velocity, jump = self.control()
		if self.on_ground():
			velocity.magnitude = self.speed
			self.move_via_force(velocity, self.force_accel, jump)
		else:
			velocity.magnitude = self.speed_air
			self.move_via_force(velocity, self.force_accel_air, 0)
	
	def other(self):
		print(self.state)
		self.state = "move"
	
	# Private
	def control(self):
		kd = inputs.keyboard.key_down

		up_down = 0
		right_left = kd('d') - kd('a')

		velocity = mt.Vector((right_left, up_down))
		jump = inputs.keyboard.key_hit('w')

		return (velocity, jump)

	def move_via_force(self, velocity_target, force_accel, jump):
		if velocity_target.magnitude:
			velocity = self.gobj.getLinearVelocity(True).xy
			force_move = velocity_target - velocity
			force_move.magnitude = force_accel
			if velocity.magnitude > velocity_target.magnitude:
				if velocity_target * velocity > 0:
					force_move.magnitude = 0
			self.gobj.applyForce((force_move.x, force_move.y, 0), True)

		force_jump = jump * self.force_jump
		self.gobj.applyForce((0, 0, force_jump), True)


class Player(game.GameObject):
	
	def __init__(self, **kwargs):
		super().__init__()

		movement = Movement(self, self.on_ground)
		tex_anim = sprycle.TexAnim(self, self.children["Mario"])
		anim_control = AnimControl(self, movement, tex_anim)
		pipe_shooting = PipeShooting(self)

		self.components = [movement,
				tex_anim,
				anim_control,
				pipe_shooting]

	def on_ground(self):
		return self.n_sensors["collision"].hit_obj()


def init(cont):
	if not "init" in cont.owner:
		Player(gobj=cont.owner)

def main(cont):

	cont.owner.main()
