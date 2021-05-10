HEADLESS = False

import scipy.io
import matplotlib

if HEADLESS:
	matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sparse

import asyncio
import websockets
import io

async def draw(websocket=None):
	mat = scipy.io.loadmat("data/Mtrans.mat")
	transition_matrix = mat['M']
	transition_matrix = np.array(transition_matrix)
	[nn,nn1] = np.shape(transition_matrix)
	X = np.zeros(nn)
	X[3065] = 1.0;
	
	T = 20 # number time steps 

	depth = np.loadtxt("data/odepth.dat")
	olon = np.loadtxt("data/olon.dat")
	olat = np.loadtxt("data/olat.dat")
	islake_row = np.loadtxt("data/islake_row.dat")
	islake_col = np.loadtxt("data/islake_col.dat")
	glc = np.loadtxt("data/GLcoast.dat")

	islake_row = islake_row-1
	islake_col = islake_col-1
	fig = plt.figure(figsize = (10, 8))
	lon = glc[:,0]
	lat = glc[:,1]

	plt.plot(lon, lat,color = 'black')
	plt.xlim([np.amin(olon)-0.25, np.amax(olon)+0.25])
	plt.ylim([np.amin(olat)-0.2, np.amax(olat)+0.2])
	plt.title('Lake Ontario')

	PD = np.ones(np.shape(depth))*0.0
	PD[depth == 0] = np.nan
	mask = np.ones(np.shape(depth))
	mask[depth == 0] = 0.0
	PD[depth == 0] = np.nan

	transition_matrix1 = np.copy(transition_matrix)

	islake_row = islake_row.astype(int)
	islake_col = islake_col.astype(int)

	masking = (depth>0)

	for i in range (1,T):
		t = sparse.csr_matrix(X) * sparse.csr_matrix(transition_matrix1)
		transition_matrix1 = sparse.csr_matrix(transition_matrix) * sparse.csr_matrix(transition_matrix1)

		t = t.todense()
		PD[islake_row,islake_col] = t
		plt.pcolor(olon,olat,PD,cmap = 'BuGn')

		if websocket is not None:
			data = io.StringIO()
			plt.savefig(data, format="svg")
			print(f"Sending {i} of {T}")
			await websocket.send(data.getvalue())

		if websocket is None:
			plt.pause(0.05)

async def process(websocket, path):
	args = await websocket.recv()
	print(args)
	await draw(websocket)

if __name__ == "__main__":
	if HEADLESS:
		start_server = websockets.serve(process, "127.0.0.1", 5678)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	else:
		asyncio.run(draw())

