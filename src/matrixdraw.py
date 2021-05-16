from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from numpy import array, copy, shape, zeros
from scipy.io import loadmat
from scipy.sparse import csr_matrix

class MatrixDraw:
	def __init__(self, settings):
		transition_matrix = array(loadmat(settings["dir"])['M'])
		initial_transition_matrix = copy(transition_matrix)

		self.dim = shape(transition_matrix)[0]
		self.steps = settings["steps"]
		self.sensitivity = settings["sensitivity"]
		self.cmap = get_cmap(settings["colormap"])
		self.norm = Normalize(vmin=self.sensitivity, vmax=self.sensitivity * 10)
		self.transition_matricies = {}

		for power in range(1, self.steps):
			iteration = csr_matrix(transition_matrix) * csr_matrix(initial_transition_matrix)
			self.transition_matricies[str(power)] = iteration
			initial_transition_matrix = iteration
	
	def validate_matrix_request(self, node, season):
		valid_node = type(node) == int and node > -1 and node < self.dim
		valid_season = season in [ "spring", "summer", "fall", "winter"]

		if not valid_node or not valid_season:
			raise ValueError()

	def get_state_vector(self, node_id):
		sv = zeros(self.dim)
		sv[int(node_id)] = 1.0

		return sv

	def draw_frame(self, state_vector, iteration):
		tm = self.transition_matricies[str(iteration)]
		values = (csr_matrix(state_vector) * csr_matrix(tm)).todense().A1
		get_color = lambda weight: (rgba := self.cmap(self.norm(weight), bytes=True), f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})")[-1]
		
		return [ { "id": str(i), "color": get_color(values[i]) } for i in range(len(values)) if values[i] > self.sensitivity ]


