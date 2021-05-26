import xml.etree.ElementTree as et
import numpy as np

class Data:
	def __init__(self):
		self.lon = np.loadtxt("data/olon.dat")
		self.lat = np.loadtxt("data/olat.dat")
		self.row = (np.loadtxt("data/islake_row.dat") - 1).astype(int)
		self.col = (np.loadtxt("data/islake_col.dat") - 1).astype(int)

		self.coords = [(self.lon[self.row[i]][self.col[i]], self.lat[self.row[i]][self.col[i]], i) for i in range(746) ]
		self.sorted = [node for node in self.coords]
		self.sorted.sort(key=lon_compare)

def lon_compare(e):
	return e[0]

def x_lon_compare(e):
	return float(e.attrib["d"].split(" ")[1])

def id_compare(e):
	return int(e.attrib["id"])

def sortchildrenby(parent, attr):
    parent[:] = sorted(parent, key=lambda child: int(child.get(attr)))

def get_children(root, sort=True):
	children = [ root[2][1][1][i] for i in range(746) ]

	if sort:
		children.sort(key = x_lon_compare)
	return children

def get_root():
	return et.parse("txml.svg").getroot()

def write(data, nodes, root):
	sortchildrenby(root[2][1][1], "id")
	f = open("output.svg", "w")
	f.write(et.tostring(root).decode())
	f.close()

def write_ids(nodes):
	for i in range(746):
		nodes[i].attrib["style"] = "fill:#0c0786;"
		nodes[i].attrib["id"] = str(data.sorted[i][2])

	nodes.sort(key = id_compare)
	#aproblems = [ 99, 148, 197, 246, 297, 401, 451, 500, 547, 630 ]	
#problems = [ 98, 147, 196, 245, 296, 400, 450, 499, 546, 629 ]

	#problems = [4278, 4216, 4143, 4065, 3982, 3890, 3788, 3679, 3567, 3451, 3334, 3216, 3096, 2975, 2853, 2730, 2604, 2478, 2351, 2222, 2089, 1954, 1820, 1686, 1558, 1432, 1305, 1180, 1056, 932, 808, 685, 562 ]

	#for i in range(10):
	#	nodes[problems[i]].attrib["id"] = str(problems[-1 - i])

if __name__ == "__main__":
	data = Data()
	root = get_root()
	nodes = get_children(root, False)

	#write_ids(nodes)
	write(data, nodes, root)

