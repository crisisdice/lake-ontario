import matplotlib.cm as mpcm
import matplotlib.colors as mpcol
import numpy as np
import scipy.io
import scipy.sparse as sparse

import asyncio
import functools as f
import json
import websockets
import websockets.exceptions as wse

class MatrixDraw:
	def __init__(self):
		self.sensitivity = 0.01
		self.steps = 30
		self.cmap = mpcm.get_cmap("BuGn")
		self.norm = mpcol.Normalize(vmin=self.sensitivity, vmax=self.sensitivity * 10)

		transition_matrix = np.array(scipy.io.loadmat("data/Mtrans.mat")['M'])	
		self.transition_matricies = self.init_transition_matricies(transition_matrix)

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
		sv = np.zeros(4732)
		sv[int(node_id)] = 1.0
		return sv

	async def draw_frame(self, state_vector, iteration):
		tm = self.transition_matricies[str(iteration)]
		values = (sparse.csr_matrix(state_vector) * sparse.csr_matrix(tm)).todense().A1

		await asyncio.sleep(0.5)
		return [ { "id": str(i), "color": self.get_color(values[i]) } for i in range(len(values)) if values[i] > self.sensitivity ]

	async def handle(self, body, websocket):
		sv = md.get_state_vector(body["node"])

		for step in range (1, self.steps):
			task = asyncio.create_task(self.draw_frame(sv, step))
			await websocket.send(json.dumps({ "nodes": await task }))

async def handler(websocket, path, md):
	try:
		message = await websocket.recv()
		body = json.loads(message)
		print(f"Processing {message}")
		await md.handle(body, websocket)
	except wse.ConnectionClosedError:
		print("Client closed connection")

if __name__ == "__main__":
	md = MatrixDraw()
	print("Initialized")

	start_server = websockets.serve(f.partial(handler, md = md), "127.0.0.1", 5678)
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

