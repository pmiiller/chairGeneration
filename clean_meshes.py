import trimesh as tri
from os import listdir, makedirs
from os.path import isfile, isdir, join, exists
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
    mesh = obb.convertObbToMesh(row['mesh'])
    mesh.export(join(directory, row['file'].replace(" ", "")))

def createCleanMeshParts(chair):
    chairPath = join(meshDir, chair)
    meshes = pd.DataFrame()

    partsDir = [folder for folder in listdir(chairPath) if isdir(join(chairPath, folder))][0]

    meshes['file'] = [f for f in listdir(join(chairPath, partsDir)) if f.endswith('.obj')]
    chairMesh = None
    chairFile = None
    for f in listdir(chairPath):
    	if (f.endswith('.obj')) and not ('skeleton' in f):
    		chairFile = f
    		chairMesh = tri.load_mesh(join(chairPath, f))

    meshes['mesh'] = meshes['file'].apply(lambda f: tri.load_mesh(join(chairPath, partsDir, f)))
    mask = meshes['mesh'].apply(insideMesh, chair=chairMesh)
    clean_mesh = meshes.where(mask).dropna()
    clean_mesh.apply(saveMesh, chair=chair, axis=1)
    chairMesh = obb.convertObbToMesh(chairMesh)
    chairMesh.export(join(cleanMeshDir, chair, chairFile))

if __name__ == '__main__':
	chairType = None
	if len(sys.argv) > 1:
		chairType = sys.argv[1]
		createCleanMeshParts(chairType)
	else:
		for chairType in listdir(meshDir):
			createCleanMeshParts(chairType)
