import pymesh
from collections import namedtuple
from os import listdir, makedirs
from os.path import isfile, isdir, join, exists
import sys
import random
import math
import numpy as np
import trimesh as tri
import trimesh_obb
import createViews
import evaluate_sample
import operator
import pickle

Template = namedtuple("Template", "dir templateParts")
TemplatePart = namedtuple("TemplatePart", "dir obj boundingBox orientedExtents symmetries")

chairsDirectory = "clean_mesh"

def computeOBB(pymesh):
    trimesh = trimesh_obb.convertPymeshToTrimesh(pymesh);
    boundingBox = trimesh_obb.convertMeshToObb(trimesh)
    return boundingBox

def calculateDeformationCost(target, candidate):
    centroidDifference = target.boundingBox.centroid - candidate.boundingBox.centroid

    tarExtents = target.orientedExtents
    canExtents = candidate.orientedExtents
    extentsDifference = tarExtents - canExtents

    rotationTarget = np.delete(np.delete(target.boundingBox.bounding_box_oriented.primitive.transform, 3, 0), 3, 1)
    rotationCandidate = np.delete(np.delete(candidate.boundingBox.bounding_box_oriented.primitive.transform, 3, 0), 3, 1)
    rotationDifference = np.matmul(rotationCandidate, np.transpose(rotationTarget))
    rotationDifferenceTrace = np.trace(rotationDifference)
    if rotationDifferenceTrace > 3.0 :
        rotationDifferenceTrace = 3.0
    if rotationDifferenceTrace < -1.0 :
        rotationDifferenceTrace = -1.0
    rotationDistance = math.acos((rotationDifferenceTrace - 1.0) / 2.0)

    # Need to come up with a better function or a better way to tune the weights
    weights = [0.3, 0.3, 0.0, 0.4]
    t, c = calculateDeformationCostProcrustes(target, candidate)
    return np.sum(weights[0] * np.square(centroidDifference) + weights[1] * np.square(extentsDifference) + weights[2] * np.square(rotationDistance) + weights[3] * c)

def matchOBB(target, candidate, mesh):
    # Transforms the candidate mesh so its obb matches the obb of the target
    # Currently seems like only translation works well

    tarCent = target.boundingBox.centroid
    canCent = candidate.boundingBox.centroid
    tarExtents = target.orientedExtents
    canExtents = candidate.orientedExtents

    scaleExtents = tarExtents / canExtents;

    transform = np.array([[1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]])

    canToOrg = np.array([[1,0,0,-canCent[0]],
              [0,1,0,-canCent[1]],
              [0,0,1,-canCent[2]],
              [0,0,0,1]])

    # rotationCandidate = np.delete(np.delete(candidate.boundingBox.principal_inertia_transform, 3, 0), 3, 1)
    # rotationCandidate = np.delete(np.delete(candidate.boundingBox.apply_obb(), 3, 0), 3, 1)
    rotationCandidate = np.delete(np.delete(candidate.boundingBox.bounding_box_oriented.primitive.transform, 3, 0), 3, 1)
    canRotInv = np.array([[rotationCandidate[0][0],rotationCandidate[0][1],rotationCandidate[0][2],0],
              [rotationCandidate[1][0],rotationCandidate[1][1],rotationCandidate[1][2],0],
              [rotationCandidate[2][0],rotationCandidate[2][1],rotationCandidate[2][2],0],
              [0,0,0,1]])
    canRotInv = np.transpose(canRotInv)

    scale = np.array([[scaleExtents[0],0,0,0],
              [0,scaleExtents[1],0,0],
              [0,0,scaleExtents[2],0],
              [0,0,0,1]])

    # rotationTarget = np.delete(np.delete(target.boundingBox.principal_inertia_transform, 3, 0), 3, 1)
    # rotationTarget = np.delete(np.delete(target.boundingBox.apply_obb(), 3, 0), 3, 1)
    rotationTarget = np.delete(np.delete(target.boundingBox.bounding_box_oriented.primitive.transform, 3, 0), 3, 1)
    tarRot = np.array([[rotationTarget[0][0],rotationTarget[0][1],rotationTarget[0][2],0],
              [rotationTarget[1][0],rotationTarget[1][1],rotationTarget[1][2],0],
              [rotationTarget[2][0],rotationTarget[2][1],rotationTarget[2][2],0],
              [0,0,0,1]])
    # tarRot = np.transpose(tarRot)

    orgToTar = np.array([[1,0,0,tarCent[0]],
              [0,1,0,tarCent[1]],
              [0,0,1,tarCent[2]],
              [0,0,0,1]])

    transform = np.matmul(transform, orgToTar)
    transform = np.matmul(transform, tarRot)
    transform = np.matmul(transform, scale)
    transform = np.matmul(transform, canRotInv)
    transform = np.matmul(transform, canToOrg)

    newVertices = np.ndarray(mesh.vertices.shape, mesh.vertices.dtype)
    for index, vertex in enumerate(mesh.vertices):

        homVertex = np.array([vertex[0], vertex[1], vertex[2], 1])
        transformedVertex = np.matmul(transform, homVertex)
        newVertices[index] = np.array([transformedVertex[0], transformedVertex[1], transformedVertex[2]]) / transformedVertex[3]

    return pymesh.form_mesh(newVertices, mesh.faces)

def calculateDeformationCostProcrustes(target, candidate):
    t, _, c = trimesh_obb.procrustesMatrixCost(candidate.boundingBox, target.boundingBox)
    return t, c

def matchOBBProcrustes(mesh, transform):
    t_candidate = trimesh_obb.convertPymeshToTrimesh(mesh).copy()
    t_candidate.apply_transform(transform)

    return pymesh.form_mesh(t_candidate.vertices, t_candidate.faces)

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

def checkForSymmetry(part1, part2):
    part1Copy = part1.boundingBox.copy()
    part2Copy = part2.boundingBox.copy()

    reflectX = np.array([
        [-1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]])

    part1Copy.apply_transform(reflectX)

    center1 = np.array([
        [1,0,0,-part1Copy.centroid[0]],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]])

    center2 = np.array([
        [1,0,0,-part2Copy.centroid[0]],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]])

    part1Copy.apply_transform(center1)
    part2Copy.apply_transform(center2)

    closestPointsX = tri.proximity.ProximityQuery(part1Copy).vertex(part2Copy.vertices)
    diffrenceX = np.sum(closestPointsX[0])
    # print(diffrenceX)

    symmetryThreshold = 0.08
    symmetry = False
    if diffrenceX < symmetryThreshold:
        symmetry = True
    return symmetry

def loadTemplatesWithoutPickle():
    templates = []
    parts = []

    # Read all parts for all chairs and create the templates
    chairDirs = [f for f in listdir(chairsDirectory) if isdir(join(chairsDirectory, f))]
    for chairDir in chairDirs:
        print("Loading tempate from: " + chairDir)
        newTemplate = Template(chairDir, [])
        chairMeshes = chairsDirectory + "/" + chairDir + "/meshes"
        chairParts = [f for f in listdir(chairMeshes) if isfile(join(chairMeshes, f))]
        for chairPart in chairParts:
            mesh = pymesh.load_mesh(chairMeshes + "/" + chairPart)
            boundingBox = computeOBB(mesh)
            orientedExtents = tri.bounds.oriented_bounds(boundingBox)[1]
            newTemplatePart = TemplatePart(chairDir, chairPart, boundingBox, orientedExtents, [])
            newTemplate.templateParts.append(newTemplatePart)
            parts.append(newTemplatePart)

        # Find symmetries
        for templatePart1 in newTemplate.templateParts:
            for templatePart2 in newTemplate.templateParts:
                if templatePart1 != templatePart2:
                    symmetry = checkForSymmetry(templatePart1, templatePart2)
                    if symmetry:
                        print("\tSymmetry Detected: " + templatePart1.obj + " ; " + templatePart2.obj)
                        templatePart1.symmetries.append(templatePart2)

        templates.append(newTemplate)

    return [templates, parts]

def loadTemplates():
    templates = []
    parts = []

    try:
        with open("templates", 'rb') as f:
            templates, parts = pickle.load(f)
            print('Sucessfully found templates file')
            return [templates, parts]
    except:
        templates, parts = loadTemplatesWithoutPickleFile()
        with open('templates', 'wb') as f:
            pickle.dump([templates, parts], f)
        return [templates, parts]

def addToNewMesh(newMesh, selectedMesh):
    if newMesh == None:
        newMesh = selectedMesh
    else :
        # selectedMesh = connectPartToMesh(newMesh, selectedMesh)
        newMesh = pymesh.merge_meshes([newMesh, selectedMesh])
    return newMesh

def addToObbMesh(obbMesh, templatePart):
    boundingBox = templatePart.boundingBox
    selectedObb = trimesh_obb.convertObbToMesh(boundingBox);
    if obbMesh == None:
        obbMesh = selectedObb
    else :
        obbMesh = pymesh.merge_meshes([obbMesh, selectedObb])
    return obbMesh

def generateForTemplate(selectedTemplate, parts):
    # For each part in the selected template, pick the part with the lowest deformation cost
    newMesh = None
    obbMesh = None
    clustering = []
    doneCreation = False
    sampleChairBmp = "sample_chair/"
    if not exists(sampleChairBmp):
        makedirs(sampleChairBmp)
    max_iter = 5
    iterCreate = 0
    possibleMesh = []
    scores = []

    # open cluster file
    try:
        with open("clusterings", 'rb') as f:
            clustering = pickle.load(f)
            print('Sucessfully found clustering file')
        useCluster = True
    except:
        useCluster = False

    while (not doneCreation) and (iterCreate < max_iter):
        newMesh = None
        lastScore = 0.0
        templateParts = selectedTemplate.templateParts.copy()
        for templatePart in templateParts:
            # Select the part that has the obb that best fits the obb of the template part

            if useCluster == True:
                # find the closest cluster representative to the part and select a random cluster member
                selectedPart = None
                minDeformationCost = sys.float_info.max
                for cluster in clustering:
                    deformationCost = calculateDeformationCost(templatePart, cluster[0])
                    if deformationCost < minDeformationCost:
                        minDeformationCost = deformationCost
                        randomMember = random.randint(0,len(cluster)-1)
                        #print('len = ',len(cluster), ' rand = ',randomMember)
                        selectedPart = cluster[randomMember]
                    #print("cost: ",deformationCost, "mincost: ",minDeformationCost)


            else:
                # use a closest fitting part if there is no file for clusters
                selectedPart = None
                minDeformationCost = sys.float_info.max
                for part in parts:
                    if part.dir != templatePart.dir:
                        randN = random.uniform(0, 1)
                        deformationCost = calculateDeformationCost(templatePart, part) * randN
                        if deformationCost < minDeformationCost:
                            minDeformationCost = deformationCost
                            selectedPart = part
            selectedMesh = pymesh.load_mesh(chairsDirectory + "/" + selectedPart.dir + "/meshes/" + selectedPart.obj)

            # FOR DEBUGING: add the part to the obb mesh
            obbMesh = addToObbMesh(obbMesh, templatePart)

            # transform the selectedMesh so the OBB matches the templatePart's OBB
            selectedMesh = matchOBB(templatePart, selectedPart, selectedMesh)

            # add the selectedMesh to the newMesh
            newMesh = addToNewMesh(newMesh, selectedMesh)


            # check for symmetries and use that to fill in parts of the template
            for symmetry in templatePart.symmetries:
                if symmetry in templateParts:
                    canCent = templatePart.boundingBox.centroid
                    tarCent = symmetry.boundingBox.centroid

                    transform = np.array([[1,0,0,0],
                        [0,1,0,0],
                        [0,0,1,0],
                        [0,0,0,1]])

                    canToOrg = np.array([[1,0,0,-canCent[0]],
                        [0,1,0,-canCent[1]],
                        [0,0,1,-canCent[2]],
                        [0,0,0,1]])

                    reflectX = np.array([[-1,0,0,0],
                        [0,1,0,0],
                        [0,0,1,0],
                        [0,0,0,1]])

                    orgToTar = np.array([[1,0,0,tarCent[0]],
                        [0,1,0,tarCent[1]],
                        [0,0,1,tarCent[2]],
                        [0,0,0,1]])

                    transform = np.matmul(transform, orgToTar)
                    transform = np.matmul(transform, reflectX)
                    transform = np.matmul(transform, canToOrg)

                    newVertices = np.ndarray(selectedMesh.vertices.shape, selectedMesh.vertices.dtype)
                    for index, vertex in enumerate(selectedMesh.vertices):

                        homVertex = np.array([vertex[0], vertex[1], vertex[2], 1])
                        transformedVertex = np.matmul(transform, homVertex)
                        newVertices[index] = np.array([transformedVertex[0], transformedVertex[1], transformedVertex[2]]) / transformedVertex[3]

                    newFaces = selectedMesh.faces[:,::-1]
                    symmetricMesh = pymesh.form_mesh(newVertices, newFaces)
                    newMesh = addToNewMesh(newMesh, symmetricMesh)

                    templateParts.remove(symmetry)

        # creates views and scores
        possibleMesh.append(newMesh)
        pymesh.save_mesh("sample_mesh.obj", newMesh);
        createViews.createViews("sample_mesh.obj", 1, sampleChairBmp)
        score = evaluate_sample.main(sampleChairBmp)
        scores.append(score[0])
        # print(scores)
        iterCreate += 1

        doneCreation = score[0] >= 0.8
        if iterCreate >= max_iter:
            index = scores.index(max(scores))
            newMesh = possibleMesh[index]

    pymesh.save_mesh("obbChair.obj", obbMesh);
    return newMesh

def generateForTemplateProcrustes(selectedTemplate, parts):
    # For each part in the selected template, pick the part with the lowest deformation cost
    newMesh = None
    obbMesh = None
    for templatePart in selectedTemplate.templateParts:
        # Select the part that has the obb that best fits the obb of the template part
        selectedPart = None
        minDeformationCost = sys.float_info.max
        for part in parts:
            if part.dir != templatePart.dir:
                t, deformationCost = calculateDeformationCostProcrustes(templatePart, part)
                if deformationCost < minDeformationCost:
                    minDeformationCost = deformationCost
                    selectedPart = part
                    minTransform = t
        selectedMesh = pymesh.load_mesh("last_examples/" + selectedPart.dir + "/meshes/" + selectedPart.obj)

        # FOR DEBUGING: add the part to the obb mesh
        obbMesh = addToObbMesh(obbMesh, templatePart)

        # transform the selectedMesh using procrustes transform
        selectedMesh = matchOBBProcrustes(selectedMesh, minTransform)

        # add the selectedMesh to the newMesh
        newMesh = addToNewMesh(newMesh, selectedMesh)

    pymesh.save_mesh("obbChair.obj", obbMesh);
    return newMesh

if __name__ == '__main__':
    newBMPDir = 'new_chair_bmp/'
    newChairDir = 'new_chair_obj/'
    rankedChairDir = 'ranked_chair_obj/'

    randomTemplate = True
    doAll = False
    evalOnly = False
    templateDirName = ""
    if len(sys.argv) > 1:
        randomTemplate = False
        templateDirName = str(sys.argv[1])
        if templateDirName == "all":
            doAll = True
        elif templateDirName == "eval":
            scores = evaluate_sample.main(newBMPDir)
            fileList = listdir(newChairDir)
            fileList.sort()
            fileListBmp = listdir(newBMPDir)
            for i in range(0, int(len(fileListBmp) / 3)):
                index, value = max(enumerate(scores), key=operator.itemgetter(1))
                scoredChair = fileList.pop(index)
                scores = np.delete(scores, index)
                mesh = pymesh.load_mesh(newChairDir + scoredChair)
                pymesh.save_mesh(rankedChairDir + str(i + 1) + ".obj", mesh)
            sys.exit()
        elif templateDirName == "load":
            templates, parts = loadTemplatesWithoutPickle()
            with open('templates', 'wb') as f:
                pickle.dump([templates, parts], f)
            sys.exit()

    print("Beginning Generation Script")

    loadedTemplates = loadTemplates()
    templates = loadedTemplates[0]
    parts = loadedTemplates[1]
    print("Templates Loaded")

    if not doAll:
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
                print("Error: " + templateDirName + " is not valid.")
                sys.exit(0)
        print("Template Selected: " + selectedTemplate.dir)

        newMesh = generateForTemplate(selectedTemplate, parts)
        print("New Chair Generated")

        pymesh.save_mesh("newChair.obj", newMesh);

        createViews.createViews("newChair.obj", 1)

    else:
        chairCount = 1
        for index, template in enumerate(templates):
            print("Generating Chair for: " + template.dir)
            newMesh = generateForTemplate(template, parts)
            print("New Chair Generated")

            file = newChairDir + str(index + 1).zfill(4) + ".obj"
            pymesh.save_mesh(file, newMesh);
            createViews.createViews(file, chairCount)
            chairCount += 3

        scores = evaluate_sample.main(newBMPDir)
        fileList = listdir(newChairDir)
        fileList.sort()
        fileListBmp = listdir(newBMPDir)
        for i in range(0, int(len(fileListBmp) / 3)):
            index, value = max(enumerate(scores), key=operator.itemgetter(1))
            scoredChair = fileList.pop(index)
            scores = np.delete(scores, index)
            mesh = pymesh.load_mesh(newChairDir + scoredChair)
            pymesh.save_mesh(rankedChairDir + str(i + 1) + ".obj", mesh)
