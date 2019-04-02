import pymesh
from pyobb.obb import OBB
import numpy as np
import sys
from scipy.spatial import ConvexHull

'''
pyobb.obb

OBB()
Fields
- centroid: the OBB center
- min: the OBB point with the smallest XYZ components
- max: the OBB point with the largest XYZ components
- points: the 8 points of the OBB
- extents: the extents of the OBB in the XYZ-axis
- rotation: the rotation matrix of the OBB

Methods to generate OBB
- build_from_triangles(points, faces)
- build_from_points(points)
- build_from_covariance_matrix(convariance_matrix, points)

'''

def getOBB(objFile):
	mesh = pymesh.load_mesh(objFile)
	obb = convertMeshToObb(mesh)
	return obb

def convertMeshToObb(mesh):
	obb = OBB.build_from_triangles(mesh.vertices, mesh.faces.flatten())
	return obb

def convertObbToMesh(obb):
	points = np.array(obb.points)
	hull = ConvexHull(points)
	indices = hull.simplices
	mesh = pymesh.form_mesh(points, indices)
	return mesh

def checkCollision(obb1, obb2):
	mesh1 = convertObbToMesh(obb1)
	mesh2 = convertObbToMesh(obb2)

	reshaped = mesh1.vertices.T
	minX1 = np.amin(reshaped[0])
	maxX1 = np.amax(reshaped[0])
	minY1 = np.amin(reshaped[1])
	maxY1 = np.amax(reshaped[1])
	minZ1 = np.amin(reshaped[2])
	maxZ1 = np.amax(reshaped[2])

	reshaped = mesh2.vertices.T
	minX2 = np.amin(reshaped[0])
	maxX2 = np.amax(reshaped[0])
	minY2 = np.amin(reshaped[1])
	maxY2 = np.amax(reshaped[1])
	minZ2 = np.amin(reshaped[2])
	maxZ2 = np.amax(reshaped[2])

	# simple box collision detection found from
	# https://www.cbcity.de/simple-3d-collision-detection-with-python-scripting-in-blender
	intersectX = (maxX1 >= minX2 and maxX1 <= maxX2) or (maxX2 >= minX1 and maxX2 <= maxX1)
	print("intersectX")
	print(intersectX)
	intersectY = (maxY1 >= minY2 and maxY1 <= maxY2) or (maxY2 >= minY1 and maxY2 <= maxY1)
	print("intersectY")
	print(intersectY)
	intersectZ = (maxZ1 >= minZ2 and maxZ1 <= maxZ2) or (maxZ2 >= minZ1 and maxZ2 <= maxZ1)
	print("intersectZ")
	print(intersectZ)
	return intersectX and intersectY and intersectZ



if __name__ == '__main__':
	file = sys.argv[1]
	file2 = sys.argv[2]
	obb2 = getOBB(file2)
	obb = getOBB(file)
	print(checkCollision(obb, obb2))
	#mesh = convertObbToMesh(obb)
	#pymesh.save_mesh("box.obj", mesh)