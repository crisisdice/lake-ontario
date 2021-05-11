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

	async def draw(self, steps):
		X = np.zeros(self.dim)
		X[3065] = 1.0;

		fig = plt.figure(figsize = (10, 8))
		lon = self.glc[:,0]
		lat = self.glc[:,1]

		plt.plot(lon, lat,color = 'black')
		plt.xlim([np.amin(self.olon)-0.25, np.amax(self.olon)+0.25])
		plt.ylim([np.amin(self.olat)-0.2, np.amax(self.olat)+0.2])
		plt.title('Lake Ontario')

		PD = np.ones(np.shape(self.depth))*0.0
		PD[self.depth == 0] = np.nan
		mask = np.ones(np.shape(self.depth))
		mask[self.depth == 0] = 0.0
		PD[self.depth == 0] = np.nan

		transition_matrix1 = np.copy(self.transition_matrix)
		masking = (self.depth>0)

		for i in range (1, steps):
			t = sparse.csr_matrix(X) * sparse.csr_matrix(transition_matrix1)
			transition_matrix1 = sparse.csr_matrix(self.transition_matrix) * sparse.csr_matrix(transition_matrix1)
			t = t.todense()

			PD[self.islake_row, self.islake_col] = t
			plt.pcolor(self.olon, self.olat, PD, cmap = 'BuGn')

			if self.websocket is not None:
				data = io.StringIO()
				plt.savefig(data, format="svg")
				print(f"Sending {i} of {steps}")
				await self.websocket.send(data.getvalue())

			else:
				plt.pause(0.05)

async def process(websocket, path, md):
	md.websocket = websocket
	coords = await websocket.recv()
	print(coords)
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

