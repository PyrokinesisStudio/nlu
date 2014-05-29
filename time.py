import time

class Timer:

	def __init__(self, delta=1):
		
		self.delta = delta
		self.restart()
	
	# Public:
	def done(self):
		
		time_now = time.time()
		if (time_now - self.time_last) > self.delta:
			self.time_last = time_now
			return True

		return False

	def restart(self):
		self.time_last = time.time()
