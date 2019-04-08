import pymesh
from collections import namedtuple
from os import listdir
from os.path import isfile, isdir, join
import sys
import random
import math
import numpy as np
# import obb
import trimesh_obb

templates = []
parts = []
Template = namedtuple("Template", "dir templateParts")
TemplatePart = namedtuple("TemplatePart", "dir obj boundingBox")


def computeOBB(pymesh):
    trimesh = trimesh_obb.convertPymeshToTrimesh(pymesh);
    boundingBox = trimesh_obb.convertMeshToObb(trimesh)
    return boundingBox

def calculateDeformationCost(target, candidate):
    t, _, c = trimesh_obb.procrustesMatrixCost(candidate.boundingBox, target.boundingBox) 
    return t, c


def matchOBB(mesh, transform):
    t_candidate = trimesh_obb.convertPymeshToTrimesh(mesh).copy()
    t_candidate.apply_transform(transform)

    return pymesh.form_mesh(t_candidate.vertices, t_candidate.faces)

if __name__ == '__main__':
    randomTemplate = True
    templateDirName = ""
    if len(sys.argv) > 1:
        randomTemplate = False
        templateDirName = str(sys.argv[1])


    # Read all parts for all chairs and create the templates
    chairDirs = [f for f in listdir("last_examples") if isdir(join("last_examples", f))]
    for chairDir in chairDirs:
        newTemplate = Template(chairDir, [])
        chairMeshes = join("last_examples", chairDir, "meshes")
        chairParts = [f for f in listdir(chairMeshes) if isfile(join(chairMeshes, f))]
        for chairPart in chairParts:
            mesh = pymesh.load_mesh(chairMeshes + "/" + chairPart)
            boundingBox = computeOBB(mesh)
            newTemplatePart = TemplatePart(chairDir, chairPart, boundingBox)
            newTemplate.templateParts.append(newTemplatePart)
            parts.append(newTemplatePart)
        templates.append(newTemplate)

    selectedTemplate = None
    if randomTemplate:
        # Select a random template
        index = random.randint(0, len(templates)-1)
        selectedTemplate = templates[index]
    else:
        # Select the template specified by the user
        index = 0
        while selectedTemplate == None and index != len(templates):
            if templates[index].dir == templateDirName:
                selectedTemplate = templates[index]
            index += 1
        if selectedTemplate is None:
            print("Error: ", templateDirName, " is not valid.")
            sys.exit(0)
    print("selectedTemplate: ", selectedTemplate.dir)

    # For each part in that template, pick the part with the lowest deformation cost
    newMesh = None
    obbMesh = None
    for templatePart in selectedTemplate.templateParts:
        # Select the part that has the obb that best fits the obb of the template part
        selectedPart = None
        minDeformationCost = sys.float_info.max
        minTransform = None
        for part in parts:
            if part.dir != templatePart.dir:
                t, deformationCost = calculateDeformationCost(templatePart, part)
                if deformationCost < minDeformationCost:
                    minDeformationCost = deformationCost
                    selectedPart = part
                    minTransform = t

        selectedMesh = pymesh.load_mesh("last_examples/" + selectedPart.dir + "/meshes/" + selectedPart.obj)

        # FOR DEBUGING: Save the obb mesh
        boundingBox = templatePart.boundingBox
        selectedObb = trimesh_obb.convertObbToMesh(boundingBox);
        if obbMesh == None:
            obbMesh = selectedObb
        else :
            obbMesh = pymesh.merge_meshes([obbMesh, selectedObb])

        # transform the selectedMesh so the OBB matches the templatePart's OBB
        selectedMesh = matchOBB(selectedMesh, minTransform)

        # add the selectedMesh to the newMesh
        if newMesh == None:
            newMesh = selectedMesh
        else :
            # selectedMesh = connectPartToMesh(newMesh, selectedMesh)
            newMesh = pymesh.merge_meshes([newMesh, selectedMesh])

    pymesh.save_mesh("newChair.obj", newMesh);
    pymesh.save_mesh("obbChair.obj", obbMesh);
