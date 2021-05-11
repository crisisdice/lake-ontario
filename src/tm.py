HEADLESS = True

import scipy.io
import matplotlib

if HEADLESS:
	matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sparse

import asyncio
import functools
import io
import json
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import websockets
import websockets.exceptions as wse

class MatrixDraw:
	def __init__(self):
		self.websocket = None
		self.depth = np.loadtxt("data/odepth.dat")
		self.olon = np.loadtxt("data/olon.dat")
		self.olat = np.loadtxt("data/olat.dat")
		self.islake_row = (np.loadtxt("data/islake_row.dat") - 1).astype(int)
		self.islake_col = (np.loadtxt("data/islake_col.dat") - 1).astype(int)
		self.glc = np.loadtxt("data/GLcoast.dat")
		self.transition_matrix = np.array(scipy.io.loadmat("data/Mtrans.mat")['M'])
		self.dim = np.shape(self.transition_matrix)[0]

	def draw_lake(self):
		lon = self.glc[:,0]
		lat = self.glc[:,1]
	
		plt.plot(lon, lat, color = 'black')
		plt.xlim([np.amin(self.olon) - 0.25, np.amax(self.olon) + 0.25])
		plt.ylim([np.amin(self.olat) - 0.2, np.amax(self.olat) + 0.2])
		plt.title('Lake Ontario')
	
		lake = np.ones(np.shape(self.depth)) * 0.0
		lake[self.depth == 0] = np.nan
		mask = np.ones(np.shape(self.depth))
		mask[self.depth == 0] = 0.0
		lake[self.depth == 0] = np.nan
	
		masking = (self.depth>0)

		return lake

	def get_state_vector(self, lat, lng):
		state_vector = np.zeros(self.dim)
		state_vector[3065] = 1.0;
		return state_vector

	async def draw(self, state_vector, steps, message=None):
		if not HEADLESS:
			fig = plt.figure(figsize = (10, 8))
			lake = self.draw_lake()

		transition_matrix_copy = np.copy(self.transition_matrix)

		for i in range (1, steps):
			if HEADLESS:
				fig = plt.figure(figsize = (10, 8))
				lake = self.draw_lake()

			t = sparse.csr_matrix(state_vector) * sparse.csr_matrix(transition_matrix_copy)
			transition_matrix_copy = sparse.csr_matrix(self.transition_matrix) * sparse.csr_matrix(transition_matrix_copy)
			t = t.todense()

			lake[self.islake_row, self.islake_col] = t
			plt.pcolor(self.olon, self.olat, lake, cmap = 'BuGn', shading = 'auto')

			if HEADLESS:
				data = io.StringIO()
				plt.savefig(data, format="svg")
				plt.close(fig)

				mid = message["id"]				

				print(f"Sending {i} of {steps - 1} for {mid}")
				await self.websocket.send(data.getvalue())

			else:
				plt.pause(0.05)

async def process(websocket, path, md):
	try:
		md.websocket = websocket
		
		message = await websocket.recv()
		print(f"Processing {message}")
		body = json.loads(message)
		sv = md.get_state_vector(body["lat"], body["lng"])
		await md.draw(sv, 10, body)
	except wse.ConnectionClosedError:
		print("Client closed connection")
		

if __name__ == "__main__":
	md = MatrixDraw()
	print("Initialized")

	if HEADLESS:
		handler = functools.partial(process, md = md)
		start_server = websockets.serve(handler, "127.0.0.1", 5678)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	else:
		sv = md.get_state_vector("-78", "43.5")
		asyncio.run(md.draw(sv, 20))

