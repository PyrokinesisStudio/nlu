from bge import render
from nlu import game

def draw_vec(source, vec, color=(0, 255, 0)):
	render.drawLine(source, source + vec, color)	

def display(val):
	core = game.scene.core()
	core["debug"] = str(val)
