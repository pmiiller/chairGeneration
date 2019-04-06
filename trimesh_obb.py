import numpy as np
import sys
import trimesh as tri
import pymesh
from os import listdir, path

'''
Trimesh OBB

https://trimsh.org/trimesh.html#github-com-mikedh-trimesh
Fields
- centroid: the OBB center
- vertices: the 8 points of the OBB
- extents: the extents of the OBB in the XYZ-axis
- principal_inertia_transform: the rotation matrix of the OBB


'''

def getOBB(objFile):
	mesh = tri.load_mesh(objFile)

	im_obb = mesh.bounding_box_oriented
	obb = tri.creation.box(im_obb.primitive.extents, im_obb.primitive.transform)
	return obb

def convertMeshToObb(mesh):
	im_obb = mesh.bounding_box_oriented
	obb = tri.creation.box(im_obb.primitive.extents, im_obb.primitive.transform)
	return obb

def convertObbToMesh(obb):
	points = obb.vertices
	indices = obb.faces
	mesh = pymesh.form_mesh(points, indices)
	return mesh

def convertPymeshToTrimesh(mesh):
	points = mesh.vertices
	faces = mesh.faces
	return tri.base.Trimesh(vertices=points, faces=faces)


def checkCollision(obb1, obb2):
	# CollisionManager is able to check any collisions internally/collision with a specific mesh
	# or with other collsionManagers
	coll = tri.collision.CollisionManager()
	coll.add_object("box1", obb1)
	coll.add_object("box2", obb2)
	return coll.in_collision_internal()


'''
Aligns mesh with another mesh using the principal axes of inertia
as a starting point and refined by ICP

Parameters:
	- mesh
	- other_mesh
	- sample = number of samples from mesh to align
	- scale = allow scaling transform
	- icp_first = icp iterations for the 9 possible combinations of sign flippage
	- icp_final = icp iterations for the closest candidate from the wider search

Returns:
	- homogenous transformation matrix to align mesh with otehr_mesh
	- average square distance

'''
def icpMatrixCost(mesh, other_mesh, samples=500, scale=True, icp_first=10, icp_final=50):
	return tri.registration.mesh_other(mesh, other_mesh, samples=samples, scale=scale, icp_first=icp_first, icp_final=icp_final)


'''
Perform  Procrustes' analysis. Finds transformation T mapping
	(a) the points of mesh to
	(b) the points of other_mesh
minimizing square sum distances between T*a and b

Parameters:
	- mesh
	- other_mesh
	- reflection = allow reflection transformations
	- translation = allow translations
	- scale = allow scalling
	- return_cost = whether to return cost

Returns:
	- homogenous transformation matrix to align mesh with otehr_mesh
	- transformed points (a)
	- cost of transformation
'''
def procrustesMatrixCost(mesh, other_mesh, reflection=True, translation=True, scale=True, return_cost=True):
	return tri.registration.procrustes(mesh.vertices, other_mesh.vertices, reflection=True, translation=True, scale=True, return_cost=True)




if __name__ == '__main__':
	chair_type = sys.argv[1]
	mesh_directory = path.join("last_examples", chair_type, "meshes")
	obbs = []

	for f in listdir(mesh_directory) :
		obbs.append(getOBB(path.join(mesh_directory, f)))
		# a = obb.convertPymeshToTrimesh(pymesh.load_mesh(path.join(mesh_directory, f)))

	scene = tri.scene.scene.append_scenes(obbs)
	scene.show()


	obb1 = obbs[0]
	obb2 = obbs[1]
	t, c = icpMatrixCost(obb1, obb2)
	# obb1.apply_transform(t)
	# scene = tri.scene.scene.append_scenes([obb1, obb2])
	# scene.show()
	print(t)
	print(c)
	t, p, c = procrustesMatrixCost(obb1, obb2)
	print(t)
	print(c)
	print(p)
