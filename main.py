import pymesh
from collections import namedtuple
from os import listdir
from os.path import isfile, isdir, join
import sys
import random

templates = []
parts = []
Template = namedtuple("Template", "dir templateParts")
TemplatePart = namedtuple("TemplatePart", "dir obj boundingBox")


def computeOBB(mesh):
    # do something
    return None

def calculateDeformationCost(targetOBB, candidateOBB):
    # do something
    return random.uniform(0.0, 10.0)


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
index = random.randint(0, len(templates))
selectedTemplate = templates[index]

# For each part in that template, pick the part with the lowest deformation cost
newMesh = None
for templatePart in selectedTemplate.templateParts:
    selectedPart = None
    minDeformationCost = sys.float_info.max
    for part in parts:
        if part.dir != templatePart.dir:
            deformationCost = calculateDeformationCost(templatePart, part)
            if deformationCost < minDeformationCost:
                minDeformationCost = deformationCost
                selectedPart = part
    selectedMesh = pymesh.load_mesh("last_examples/" + selectedPart.dir + "/meshes/" + selectedPart.obj)
    # should transform the selectedMesh so the OBB matches the templatePart's OBB
    if newMesh == None:
        newMesh = selectedMesh
    else :
        newMesh = pymesh.merge_meshes([newMesh, selectedMesh])

pymesh.save_mesh("newChair.obj", newMesh);
