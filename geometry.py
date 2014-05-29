import mathutils as mt

class Mesh:

	def __init__(self, kx_mesh):

		# Public:
		self.polygons = [Polygon(kx_mesh.getPolygon(i)) 
				for i in range(kx_mesh.numPolygons)]
		pos_verts = {}
		for i in range(kx_mesh.getVertexArrayLength(0)):
			v = kx_mesh.getVertex(0, i)
			pos = tuple(v.XYZ)
			if pos in pos_verts:
				pos_verts[pos].append(v)
			else:
				pos_verts[pos] = [v]

		self.vertices = [Vertex(verts) for verts in pos_verts.values()]

class Polygon:
	
	def __init__(self, kx_polygon):

		kx_mesh = kx_polygon.getMesh()

		self.vertices = [kx_mesh.getVertex(0, kx_polygon.getVertexIndex(i)) 
				for i in range(kx_polygon.getNumVertex())]

	# Public:
	@property
	def tex_coords(self):
		return [v.getUV() for v in self.vertices]

	@tex_coords.setter
	def tex_coords(self, coords):
		for v, c in zip(self.vertices, coords):
			v.setUV(c)
	
	@property
	def tex_coords_lists(self):
		return [list(v.getUV()) for v in self.vertices]

class Vertex:

	def __init__(self, vertices):

		self.vertices = vertices
	
	# Public
	@property
	def position(self):
		return mt.Vector(self.vertices[0].XYZ)

	@position.setter
	def position(self, pos):
		for v in self.vertices:
			v.XYZ = list(pos)

	@property
	def uv(self):
		return self.vertices[0].getUV()

	@property
	def normal(self):
		normals = [mt.Vector(v.normal) for v in self.vertices]
		n = sum(normals, mt.Vector([0]*3))
		n.magnitude = 1
		return n
