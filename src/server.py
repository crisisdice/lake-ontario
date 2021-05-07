import matplotlib.cm as mpcm
import matplotlib.colors as mpcol
import numpy as np
import scipy.io
import scipy.sparse as sparse

import asyncio
import functools
import json
import websockets
import websockets.exceptions as wse

class MatrixDraw:
	def __init__(self):
		self.transition_matrix = np.array(scipy.io.loadmat("data/Mtrans.mat")['M'])
		self.dim = np.shape(self.transition_matrix)[0]
		self.cmap = mpcm.get_cmap("BuGn")
		self.sensitivity = 0.01

	def get_color(self, weight):
		norm = mpcol.Normalize(vmin=self.sensitivity, vmax=self.sensitivity * 10)
		rgba = self.cmap(norm(weight), bytes=True)

		return  f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})"

	def get_state_vector(self, node_id):
		sv = np.zeros(self.dim)
		sv[int(node_id)] = 1.0
		return sv

	async def draw(self, state_vector, steps, websocket):
		transition_matrix_copy = np.copy(self.transition_matrix)

		for i in range (1, steps):
			task = asyncio.create_task(self.draw_frame(transition_matrix_copy, state_vector))
			complete = await task

			transition_matrix_copy = complete[0]
			response = { "nodes": complete[1] }

			await websocket.send(json.dumps(response))

	async def draw_frame(self, transition_matrix, state_vector):
		vector = sparse.csr_matrix(state_vector) * sparse.csr_matrix(transition_matrix)
		transition_matrix_copy = sparse.csr_matrix(self.transition_matrix) * sparse.csr_matrix(transition_matrix)
		values = vector.todense().A1

		nodes = [ { "id": str(i), "color": self.get_color(values[i]) } for i in range(len(values)) if values[i] > self.sensitivity ]
		return (transition_matrix_copy, nodes)

async def process(websocket, path, md):
	try:
		message = await websocket.recv()
		print(f"Processing {message}")
		body = json.loads(message)
		sv = md.get_state_vector(body["node"])
		await md.draw(sv, 30, websocket)
	except wse.ConnectionClosedError:
		print("Client closed connection")

if __name__ == "__main__":
	md = MatrixDraw()
	print("Initialized")

	handler = functools.partial(process, md = md)
	start_server = websockets.serve(handler, "127.0.0.1", 5678)

	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

