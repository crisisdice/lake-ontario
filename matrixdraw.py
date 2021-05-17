from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from numpy import array, copy, shape, zeros
from scipy.io import loadmat
from scipy.sparse import csr_matrix

class MatrixDraw:
	def __init__(self, settings, store):
		self.store = store
		self.dim = settings["dim"]
		self.steps = settings["steps"]
		self.sensitivity = settings["sensitivity"]
		self.cmap = get_cmap(settings["colormap"])
		self.norm = Normalize(vmin=self.sensitivity, vmax=self.sensitivity * 10)

	def validate_matrix_request(self, node, season, intensity):
		valid_node = type(node) == int and node > -1 and node < self.dim
		valid_season = season in [ "spring", "summer", "fall", "winter"]
		valid_intensity = type(intensity) == int and intensity % 2 == 0 and intensity > 0 and intensity < 11

		if not valid_node or not valid_season:
			raise ValueError()

	def get_state_vector(self, node_id, intensity):
		sv = zeros(self.dim)
		sv[int(node_id)] = 1.0

		return sv

	def draw_frame(self, state_vector, season, iteration):
		tm = self.store.retrieve(season, iteration)
		values = (csr_matrix(state_vector) * tm).todense().A1

		get_color = lambda weight: (rgba := self.cmap(self.norm(weight), bytes=True), f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})")[-1]

		return [ { "id": str(i), "color": get_color(values[i]) } for i in range(len(values)) if values[i] > self.sensitivity ]

