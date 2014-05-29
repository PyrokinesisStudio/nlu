import sys
import os

dirs = [d for d, _, _ in os.walk("src")]
dirs.append("sprycle/src")

# If nlu is not in path, and if this is running from 
# nlu/examples/platformer, the following should make nlu 
# available within this demo:
dirs.append("../../..") 

dirs = [d for d in dirs if not "__pycache__" in d]

cwd = os.getcwd()
for d in dirs:
        sys.path.append(os.path.join(cwd, d))

def init():
	"""
	The configuration logic should only run once, on initial import,
	so there's no need for this function to do anything, except serve as a
	controller entry point.

	It may seem like a good idea to simply import this from nlu.init, but that 
	ignores the possibility that nlu itself is outside the import path, and
	is therefore dependent on this config to properly amend sys.path

	"""
	pass
