from numpy import array, copy
from scipy.io import loadmat, savemat
from scipy.sparse import csr_matrix

class MatrixStore:
	def __init__(self):
		self.template = lambda season, power : f"data/{season}/{season}_{power}.mat"

	def seed(self, seasons, steps):
		for season in seasons:
			transition_matrix = array(loadmat(self.template(season, 1))['M'])
			multiplicand = copy(transition_matrix)
			
			for power in range(2, steps):
				result = csr_matrix(transition_matrix) * csr_matrix(multiplicand)
				self.store(result.toarray(), season, power)
				multiplicand = result

	def store(self, array, season, power):
		savemat(self.template(season, power), { 'M': array }, do_compression=True)

	def retrieve(self, season, power):
		return array(loadmat(self.template(season, power))['M'])

