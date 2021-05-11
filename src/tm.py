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
import websockets
import io

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

	def draw_canvas(self):
		fig = plt.figure(figsize = (10, 8))
		lon = self.glc[:,0]
		lat = self.glc[:,1]
	
		plt.plot(lon, lat,color = 'black')
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

	async def draw(self, steps):
		state_vector = np.zeros(self.dim)
		state_vector[3065] = 1.0;

		transition_matrix1 = np.copy(self.transition_matrix)

		if not HEADLESS:
			lake = self.draw_canvas()

		for i in range (1, steps):
			if HEADLESS:
				lake = self.draw_canvas()

			t = sparse.csr_matrix(state_vector) * sparse.csr_matrix(transition_matrix1)
			transition_matrix1 = sparse.csr_matrix(self.transition_matrix) * sparse.csr_matrix(transition_matrix1)
			t = t.todense()

			lake[self.islake_row, self.islake_col] = t
			plt.pcolor(self.olon, self.olat, lake, cmap = 'BuGn', shading = 'auto')

			if HEADLESS:
				data = io.StringIO()
				plt.savefig(data, format="svg")
				print(f"Sending {i} of {steps - 1}")
				await self.websocket.send(data.getvalue())

			else:
				plt.pause(0.05)

async def process(websocket, path, md):
	md.websocket = websocket
	async for message in websocket:
		print(message)
		await md.draw(20)

if __name__ == "__main__":
	md = MatrixDraw()
	print("initialized")

	if HEADLESS:
		handler = functools.partial(process, md = md)
		start_server = websockets.serve(handler, "127.0.0.1", 5678)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	else:
		asyncio.run(md.draw(20))

