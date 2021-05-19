from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from numpy import array, copy, max, shape, zeros
from scipy.sparse import csr_matrix

class MatrixDraw:
	def __init__(self, store):
		self.store = store

	def get_state_vector(self, node_id, intensity, dim):
		sv = zeros(dim)
		sv[int(node_id)] = 1.0

		return sv

	def draw_frame(self, state_vector, season, iteration, colormap):
		tm = self.store.retrieve(season, iteration)
		values = (csr_matrix(state_vector) * csr_matrix(tm)).todense().A1

		norm = Normalize(vmin=0, vmax=max(values))
		cmap = get_cmap(colormap)

		get_color = lambda weight: (rgba := cmap(norm(weight), bytes=True), f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})")[-1]

		return [ { "id": str(i), "color": get_color(values[i]) } for i in range(len(values)) if values[i] > 0 ]

