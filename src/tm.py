HEADLESS = True

import scipy.io
import matplotlib

if HEADLESS:
	matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sparse
import math

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
		self.depth = np.loadtxt("data/odepth.dat")
		self.olon = np.loadtxt("data/olon.dat")
		self.olat = np.loadtxt("data/olat.dat")
		self.islake_row = (np.loadtxt("data/islake_row.dat") - 1).astype(int)
		self.islake_col = (np.loadtxt("data/islake_col.dat") - 1).astype(int)
		self.glc = np.loadtxt("data/GLcoast.dat")
		self.transition_matrix = np.array(scipy.io.loadmat("data/Mtrans.mat")['M'])
		self.dim = np.shape(self.transition_matrix)[0]

	def draw_lake(self, iteration=None):
		lon = self.glc[:,0]
		lat = self.glc[:,1]
	
		plt.plot(lon, lat, color = 'black')
		plt.xlim([np.amin(self.olon) - 0.25, np.amax(self.olon) + 0.25])
		plt.ylim([np.amin(self.olat) - 0.2, np.amax(self.olat) + 0.2])
	
		title = 'Lake Ontario'

		if iteration:
			title = title + f" {iteration * 2} days"

		plt.title(title)
	
		lake = np.ones(np.shape(self.depth)) * 0.0
		lake[self.depth == 0] = np.nan

		return lake

	def draw_mask(self):
		mask = np.ones(np.shape(self.depth))
		mask[self.depth == 0] = 0.0

		return mask

	def test(self):
		sv = np.zeros(self.dim)
		x = 1 / self.dim

		for i in range(self.dim):
			sv[i] = x * i

		return sv

	def initcoord(self, lat, lng, mask):
#		X=np.zeros(self.dim)
#		X[123] = 1.0
#		return X

		[x,y]= self.lonlat2xy(lat, lng)
		ii=math.floor(x/2000);
		jj=math.floor(y/2000);
		test=mask[ii,jj]
		
		if test==0:
			raise ValueError('Not in lake')
		else:
			D=np.zeros(np.shape(mask))
			D[ii,jj]=1.0
			X=D[self.islake_row, self.islake_col]   
		return(X)
	    
	def lonlat2xy(self, lat, lon):
		print(f" lon: {lon}, lat: {lat}")

		a=8.13204e1
		b=2.42939
		c=-1.33486
		d=0.0
		e=-1.76688
		f=1.11101e2
		g=0.0
		h=4.85416e-1
		rlon=-79.819996
		rlat=43.16554
		
		Dlon=lon-rlon
		Dlat=lat-rlat
		x = a*Dlon + b*Dlat + c*np.multiply(Dlon,Dlat) + d*np.power(Dlon,2)
		y = e*Dlon + f*Dlat + g*np.multiply(Dlon,Dlat) + h*np.power(Dlon,2)
		x=x*1000
		y=y*1000
		
		return(x,y)    

	async def draw(self, state_vector, steps, message=None, websocket=None):
		if not HEADLESS:
			fig = plt.figure(figsize = (10, 8))
			lake = self.draw_lake()

		transition_matrix_copy = np.copy(self.transition_matrix)

		for i in range (1, steps):
			if HEADLESS:
				#task = asyncio.create_task(self.draw_frame_async(transition_matrix_copy, state_vector))

				complete = await self.draw_frame_async(transition_matrix_copy, state_vector, i)

				transition_matrix_copy = complete[0]
				await websocket.send(complete[1].getvalue())
				mid = message["id"]				
				print(f"Sending {i} of {steps - 1} for {mid}")
			else:
				transition_matrix_copy = self.draw_frame(transition_matrix_copy, state_vector, lake, i)
				plt.pause(0.05)

	async def draw_frame_async(self, transition_matrix, state_vector, iteration):
		fig = plt.figure(figsize = (10, 8))
		lake = self.draw_lake(iteration)
		transition_matrix_copy = self.draw_frame(transition_matrix, state_vector, lake, iteration)
		data = io.StringIO()
		plt.savefig(data, format="svg")
		plt.close(fig)
		return (transition_matrix_copy, data)

	def draw_frame(self, transition_matrix, state_vector, lake, iteration):
		t = sparse.csr_matrix(state_vector) * sparse.csr_matrix(transition_matrix)
		transition_matrix_copy = sparse.csr_matrix(self.transition_matrix) * sparse.csr_matrix(transition_matrix)
		t = t.todense()

		lake[self.islake_row, self.islake_col] = t
		plt.pcolormesh(self.olon, self.olat, lake, cmap = 'BuGn', shading = 'auto')

		return transition_matrix_copy

async def process(websocket, path, md):
	try:
		message = await websocket.recv()
		print(f"Processing {message}")
		body = json.loads(message)

		mask = md.draw_mask()
		sv = md.initcoord(body["lat"], body["lng"], mask)
		await md.draw(sv, 20, body, websocket)
	except wse.ConnectionClosedError:
		print("Client closed connection")
	except ValueError:
		pass
		

if __name__ == "__main__":
	md = MatrixDraw()
	print("Initialized")

	if HEADLESS:
		handler = functools.partial(process, md = md)
		start_server = websockets.serve(handler, "127.0.0.1", 5678)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	else:
		mask = md.draw_mask()
		#sv = md.initcoord(43.6, -78.2, mask)
		sv = md.test()
		asyncio.run(md.draw(sv, 20))

