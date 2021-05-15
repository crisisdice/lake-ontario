import asyncio
import matplotlib.cm as mpcm
import matplotlib.colors as mpcol
import numpy as np
import scipy.io
import scipy.sparse as sparse

class MatrixDraw:
	def __init__(self, settings):
		try:
			self.dim = settings["dimension"]
			self.steps = settings["steps"]
			self.sensitivity = settings["sensitivity"]
			self.cmap = mpcm.get_cmap(settings["colormap"])
			self.norm = mpcol.Normalize(vmin=self.sensitivity, vmax=self.sensitivity * 10)

			transition_matrix = np.array(scipy.io.loadmat(settings["dir"])['M'])
			self.transition_matricies = self.init_transition_matricies(transition_matrix)
		except KeyError:
			raise ValueError("Missing setting in matrix settings")

	def init_transition_matricies(self, transition_matrix):
		initial_transition_matrix = np.copy(transition_matrix)
		matricies = {}

		for power in range(1, self.steps):
			iteration = sparse.csr_matrix(transition_matrix) * sparse.csr_matrix(initial_transition_matrix)
			matricies[str(power)] = iteration
			initial_transition_matrix = iteration
		return matricies

	def get_color(self, weight):
		rgba = self.cmap(self.norm(weight), bytes=True)
		return  f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})"

	def get_state_vector(self, node_id):
		sv = np.zeros(self.dim)
		sv[int(node_id)] = 1.0
		return sv

	def validate_matrix_request(self, node, season):
		valid_node = type(node) == int and node > -1 and node < self.dim
		valid_season = season in [ "spring", "summer", "fall", "winter"]

		if not valid_node or not valid_season:
			raise ValueError()

	async def draw_frame(self, state_vector, iteration):
		tm = self.transition_matricies[str(iteration)]
		values = (sparse.csr_matrix(state_vector) * sparse.csr_matrix(tm)).todense().A1
		await asyncio.sleep(0.5)
		return [ { "id": str(i), "color": self.get_color(values[i]) } for i in range(len(values)) if values[i] > self.sensitivity ]


