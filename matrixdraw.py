from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from numpy import array, copy, frombuffer, shape, zeros
from scipy.io import loadmat
from scipy.sparse import csr_matrix

import numpy as np
import redis
import os

class MatrixDraw:
	def __init__(self, settings, remote):
		self.store = redis.from_url(os.environ.get("REDIS_URL")) if remote else redis.Redis()
		self.dim = settings["dim"]
		self.shape = (settings["dim"], settings["dim"])
		self.steps = settings["steps"]
		self.sensitivity = settings["sensitivity"]
		self.cmap = get_cmap(settings["colormap"])
		self.norm = Normalize(vmin=self.sensitivity, vmax=self.sensitivity * 10)
		self.transition_matricies = {}

		for season in settings["seasons"]:
			self.transition_matricies[season] = array(loadmat(f"data/{season}.mat")['M'])

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

	def draw_frame(self, state_vector, season, iteration, uid):
		M = self.transition_matricies[season]

		if iteration == 1:
			multiplicand = copy(M)
		else:
			multiplicand = frombuffer(self.store.get(uid)).reshape(*self.shape)

		t = csr_matrix(state_vector) * csr_matrix(multiplicand)
		multiplicand = csr_matrix(M) * csr_matrix(multiplicand)
		vector = t.todense()
		values = vector.A1

		self.store.set(uid, multiplicand.toarray().tobytes())

		norm = Normalize(vmin=0, vmax=np.max(vector))

		get_color = lambda weight, norm: (rgba := self.cmap(norm(weight), bytes=True), f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})")[-1]

		

		return [ { "id": str(i), "color": get_color(values[i], norm) } for i in range(len(values)) if values[i] > self.sensitivity ]

