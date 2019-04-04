import pymesh
from collections import namedtuple
from os import listdir
from os.path import isfile, isdir, join
import sys
import random
import numpy as np
import obb

templates = []
parts = []
Template = namedtuple("Template", "dir templateParts")
TemplatePart = namedtuple("TemplatePart", "dir obj boundingBox")


def computeOBB(mesh):
    boundingBox = obb.convertMeshToObb(mesh);
    return boundingBox

def calculateDeformationCost(target, candidate):
    # right now just simply returns the distance between the centroids
    # TODO need to come up with a better deformation cost function
    # think, how would you transform one box into another

    centroidDistance = np.linalg.norm(target.boundingBox.centroid - candidate.boundingBox.centroid)
    extentsDistance = np.linalg.norm(target.boundingBox.extents - candidate.boundingBox.extents)

    return centroidDistance + extentsDistance

def matchOBB(target, candidate, mesh):
    translation = target.boundingBox.centroid - candidate.boundingBox.centroid

    a = np.array([[1,0,0,translation[0]],
              [0,1,0,translation[1]],
              [0,0,1,translation[2]],
              [0,0,0,1]])

    newVertices = np.ndarray(mesh.vertices.shape, mesh.vertices.dtype)
    for index, vertex in enumerate(mesh.vertices):

        homVertex = np.array([vertex[0], vertex[1], vertex[2], 1])
        transformedVertex = np.matmul(a, homVertex)
        newVertices[index] = np.array([transformedVertex[0], transformedVertex[1], transformedVertex[2]]) / transformedVertex[3]

    return pymesh.form_mesh(newVertices, mesh.faces)

def connectPartToMesh(mesh, part):
    # ensures basic connectivity
    # there is probably a better way to connect
    pointDistances = pymesh.distance_to_mesh(mesh, part.vertices)
    minSquaredDistance = sys.float_info.max
    closestPointMesh = None
    closestPointPart = None

    # enumerate the minimum squared distances
    for index, pointDistance in enumerate(pointDistances[0]):
        # find the minimum squared distance and the corresponding point pair
        if pointDistance < minSquaredDistance:
            minSquaredDistance = pointDistance
            closestPointMesh = pointDistances[2][index]
            closestPointPart = part.vertices[index]

    connectionTranslation = closestPointMesh - closestPointPart

    newVertices = np.ndarray(part.vertices.shape, part.vertices.dtype)
    for index, vertex in enumerate(part.vertices):
        newVertices[index] = vertex + connectionTranslation

    return pymesh.form_mesh(newVertices, selectedMesh.faces)


# Read all parts for all chairs and create the templates
chairDirs = [f for f in listdir("last_examples") if isdir(join("last_examples", f))]
for chairDir in chairDirs:
    newTemplate = Template(chairDir, [])
    chairMeshes = "last_examples/" + chairDir + "/meshes"
    chairParts = [f for f in listdir(chairMeshes) if isfile(join(chairMeshes, f))]
    for chairPart in chairParts:
        mesh = pymesh.load_mesh(chairMeshes + "/" + chairPart)
        boundingBox = computeOBB(mesh)
        newTemplatePart = TemplatePart(chairDir, chairPart, boundingBox)
        newTemplate.templateParts.append(newTemplatePart)
        parts.append(newTemplatePart)
    templates.append(newTemplate)

# Select a random template
index = random.randint(0, len(templates)-1)
selectedTemplate = templates[index]

print("selectedTemplate: ", selectedTemplate.dir)

# For each part in that template, pick the part with the lowest deformation cost
newMesh = None
obbMesh = None
for templatePart in selectedTemplate.templateParts:

    # Select the part that has the obb that best fits the obb of the template part
    selectedPart = None
    minDeformationCost = sys.float_info.max
    for part in parts:
        if part.dir != templatePart.dir:
            deformationCost = calculateDeformationCost(templatePart, part)
            if deformationCost < minDeformationCost:
                minDeformationCost = deformationCost
                selectedPart = part
    selectedMesh = pymesh.load_mesh("last_examples/" + selectedPart.dir + "/meshes/" + selectedPart.obj)

    # transform the selectedMesh so the OBB matches the templatePart's OBB
    selectedMesh = matchOBB(templatePart, selectedPart, selectedMesh)

    # add the selectedMesh to the newMesh
    if newMesh == None:
        newMesh = selectedMesh
    else :
        # selectedMesh = connectPartToMesh(newMesh, selectedMesh)
        newMesh = pymesh.merge_meshes([newMesh, selectedMesh])


    # FOR DEBUGING: Save the obb mesh
    boundingBox = templatePart.boundingBox
    selectedObb = obb.convertObbToMesh(boundingBox);
    if obbMesh == None:
        obbMesh = selectedObb
    else :
        obbMesh = pymesh.merge_meshes([obbMesh, selectedObb])


pymesh.save_mesh("newChair.obj", newMesh);
pymesh.save_mesh("obbChair.obj", obbMesh);
