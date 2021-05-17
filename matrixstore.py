from numpy import array, copy, frombuffer, reshape
from scipy.io import loadmat
from scipy.sparse import csr_matrix

import redis
import os

class MatrixStore:
	def __init__(self, settings, remote):
		self.db = os.environ.get("REDIS_URL") if remote else redis.Redis()
		self.shape = (settings["dim"], settings["dim"])
		self.steps = settings["steps"]
		self.seasons = settings["seasons"]
		self.template = lambda season, power : f"{season}:{power}"

	def seed(self):
		file_name = lambda season : f'data/{season}.mat'

		for season in self.seasons:
			transition_matrix = array(loadmat(file_name(season))['M'])
			multiplicand = copy(transition_matrix)
			self.store(transition_matrix, season, 1)
			
			for power in range(2, self.steps):
				result = csr_matrix(transition_matrix) * csr_matrix(multiplicand)
				self.store(result.toarray(), season, power)
				multiplicand = result

	def store(self, array, season, power):
		key = self.template(season, power)
		self.db.set(key, array.tobytes())		

	def retrieve(self, season, power):
		key = self.template(season, power)
		array_bytes = self.db.get(key)
		return csr_matrix(frombuffer(array_bytes).reshape(*self.shape))

