import trimesh as tri
from os import listdir, makedirs
from os.path import isfile, isdir, join, exists
import pymesh
import pandas as pd
import trimesh_obb as obb
import numpy as np
import sys

cleanMeshDir = "clean_mesh"
meshDir = "last_examples"
 
def insideMesh(part, chair):
	chairPoints = chair.vertices.tolist()
	b = [point.tolist() in chairPoints for point in part.vertices]
	m = np.array(b)
	return m.all()

def saveMesh(row, chair):
	directory = join(cleanMeshDir, chair, "meshes")
	if not exists(directory):
		makedirs(directory)
	pMesh = obb.convertObbToMesh(row['mesh'])
	pymesh.save_mesh(join(directory, row['file'].replace(" ", "")), pMesh)


def createCleanMeshParts(chair):
	chairPath = join(meshDir, chair)
	meshes = pd.DataFrame()
	meshes['file'] = listdir(join(chairPath, "meshes"))
	chairMesh = None
	chairFile = None
	for f in listdir(chairPath):
		if (f.endswith('.obj')) and not ('skeleton' in f):
			chairFile = f
			chairMesh = tri.load_mesh(join(chairPath, f))

	meshes['mesh'] = meshes['file'].apply(lambda f: tri.load_mesh(join(chairPath, "meshes", f)))
	mask = meshes['mesh'].apply(insideMesh, chair=chairMesh)
	clean_mesh = meshes.where(mask).dropna()
	clean_mesh.apply(saveMesh, chair=chair, axis=1)
	chairPymesh = obb.convertObbToMesh(chairMesh)
	pymesh.save_mesh(join(cleanMeshDir, chair, chairFile), chairPymesh)

if __name__ == '__main__':
	chairType = None
	if len(sys.argv) > 1:
		chairType = sys.argv[1]
		createCleanMeshParts(chairType)
	else:
		for chairType in listdir(meshDir):
			createCleanMeshParts(chairType)