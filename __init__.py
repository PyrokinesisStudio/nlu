from nlu import game

def init(cont):
	"""
	This function reifies game.scene

	It must run once, before anything else.

	"""
	owner = cont.owner
	kx_scene = owner.scene

	scene = game.scene
	scene.scene_core[kx_scene] = owner

def game_object(cont):
	game.GameObject(gobj=cont.owner)
