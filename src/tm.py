import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sparse

def draw():
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

	islake_row = islake_row-1
	islake_col = islake_col-1

	glc = np.loadtxt("data/GLcoast.dat")

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
		plt.savefig(f"pic/test{i}.svg")
		plt.pause(0.05)

if __name__ == "__main__":
	draw()
	
