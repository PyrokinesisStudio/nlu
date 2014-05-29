import sys
import os

dirs = [d for d, _, _ in os.walk("src")]

# If nlu is not in path, and if this is running from 
# nlu/examples/platformer/sprycle, the following should make nlu 
# available within this demo:
dirs.append("../../../..") 

dirs = [d for d in dirs if not "__pycache__" in d]

cwd = os.getcwd()
for d in dirs:
	sys.path.append(os.path.join(cwd, d))

def init():
	pass
