import numpy as np
import os, os.path
import trimesh as tri
from PIL import Image, ImageDraw



#axis = 0: x, side view
#axis = 1: y, top view
#axis = 2: z, front view
def averageTriangleDepth(triangle, v0, v1, v2, axis):

	v0Depth = v0[axis]
	v1Depth = v1[axis]
	v2Depth = v2[axis]

	averageDepth = (v0Depth+v1Depth+v2Depth)/3
	return averageDepth

def getDistOfTriangle(O, triangle, v0, v1, v2, axis):
	depth = averageTriangleDepth(triangle, v0, v1, v2, axis)

	dist = depth-O[axis]
	return abs(dist)


def getMesh(filename):
	return tri.load_mesh(filename)




def createViews(filename, chairCount, directory='new_chair_bmp/'):
	mesh = getMesh(filename)


	minX = mesh.vertices[0][0]
	maxX = minX

	minY = mesh.vertices[0][1]
	maxY = minY

	minZ = mesh.vertices[0][2]
	maxZ = minZ

	# find boundary of mesh
	for vertex in mesh.vertices:
		if vertex[0] < minX:
			minX = vertex[0]
		if vertex[0] > maxX:
			maxX = vertex[0]

		if vertex[1] < minY:
			minY = vertex[1]
		if vertex[1] > maxY:
			maxY = vertex[1]

		if vertex[2] < minZ:
			minZ = vertex[2]
		if vertex[2] > maxZ:
			maxZ = vertex[2]

	h = 224
	w = 224

	#x = -1 for side view
	#y = 1 for top view
	#z = -1 for front view
	O = np.array([-1., -1., 1.]) #Camera. For each of the 3 views, the other 2 axes are 0

	imgFront = Image.new('RGB', (h, w), "white")	#create white canvas
	imgSide = Image.new('RGB', (h, w), "white")	#create white canvas
	imgTop = Image.new('RGB', (h, w), "white")	#create white canvas

	#drawing canvas for each of the 3 views
	drawFront = ImageDraw.Draw(imgFront)
	drawSide = ImageDraw.Draw(imgSide)
	drawTop = ImageDraw.Draw(imgTop)


	count = 0

	minX -= 0.5
	maxX += 0.5
	minY -= 0.5
	maxY += 0.5
	minZ -= 0.5
	maxZ += 0.5

	#array for each triangle to store its points and color assigned to it
	dt = np.dtype([('p0X', int), ('p0Y', int),
				   ('p1X', int), ('p1Y', int),
				   ('p2X', int), ('p2Y', int), ('color', int)])
	# triFront = np.empty((mesh.num_faces), dtype = dt)
	# triTop = np.empty((mesh.num_faces), dtype = dt)
	# triSide = np.empty((mesh.num_faces), dtype = dt)
	triFront = np.empty((len(mesh.faces)), dtype = dt)
	triTop = np.empty((len(mesh.faces)), dtype = dt)
	triSide = np.empty((len(mesh.faces)), dtype = dt)

	for triangle in mesh.faces:
		v0 = mesh.vertices[triangle[0]]
		v1 = mesh.vertices[triangle[1]]
		v2 = mesh.vertices[triangle[2]]

		distX = getDistOfTriangle(O, triangle, v0, v1, v2, 0) #side
		distY = getDistOfTriangle(O, triangle, v0, v1, v2, 1) #front
		distZ = getDistOfTriangle(O, triangle, v0, v1, v2, 2) #top

		colorX = int(distX/2*255)
		colorY = int(distY/2*255)
		colorZ = int(distZ/2*255)

		p0X = (v0[0]- minX) * w/(maxX-minX)
		p0Y = (v0[1]- minY) * h/(maxY-minY)
		p0Z = (v0[2]- minZ) * h/(maxZ-minZ)

		p1X = (v1[0]- minX) * w/(maxX-minX)
		p1Y = (v1[1]- minY) * h/(maxY-minY)
		p1Z = (v1[2]- minZ) * h/(maxZ-minZ)

		p2X = (v2[0]- minX) * w/(maxX-minX)
		p2Y = (v2[1]- minY) * h/(maxY-minY)
		p2Z = (v2[2]- minZ) * h/(maxZ-minZ)

		triFront[count] = (p0X, h-p0Z, p1X, h-p1Z, p2X, h-p2Z, colorY)
		triTop[count] = (p0X, h-p0Y, p1X, h-p1Y, p2X, h-p2Y, colorZ)
		triSide[count] = (w-p0Y, h-p0Z, w-p1Y, h-p1Z, w-p2Y, h-p2Z, colorX)

		count += 1


	#sort triangles by shade of gray, so that darker triangles
	#are drawn last
	triFront = np.sort(triFront, order = 'color')
	triTop = np.sort(triTop, order = 'color')
	triSide = np.sort(triSide, order = 'color')


	#iterate through triangles starting with lightest shade
	# for i in range(mesh.num_faces-1, -1, -1):
	for i in range(len(mesh.faces)-1, -1, -1):
		drawTop.polygon([(triTop[i][0], triTop[i][1]),
						 (triTop[i][2], triTop[i][3]),
						 (triTop[i][4], triTop[i][5])],
						 fill = (triTop[i][6], triTop[i][6], triTop[i][6]))

		drawFront.polygon([(triFront[i][0], triFront[i][1]),
						 (triFront[i][2], triFront[i][3]),
						 (triFront[i][4], triFront[i][5])],
						 fill = (triFront[i][6], triFront[i][6], triFront[i][6]))

		drawSide.polygon([(triSide[i][0], triSide[i][1]),
						 (triSide[i][2], triSide[i][3]),
						 (triSide[i][4], triSide[i][5])],
						 fill = (triSide[i][6], triSide[i][6], triSide[i][6]))


	imgSide.save(directory + str(chairCount) + '.bmp')
	imgTop.save(directory + str(chairCount+1) + '.bmp')
	imgFront.save(directory + str(chairCount+2) + '.bmp')


if __name__ == '__main__':
	indir = 'new_chair_obj'
	fileList = os.listdir(indir)
	fileList.sort()
	print(fileList)

	chairCount = 1
	for chair in fileList:
		file = indir + '/' + chair

		createViews(file, chairCount)
		chairCount+=3
