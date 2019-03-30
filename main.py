import pymesh
from collections import namedtuple
from os import listdir
from os.path import isfile, isdir, join

templates = []
Template = namedtuple("Template", "dir templateParts")
TemplatePart = namedtuple("TemplatePart", "obj boundingBox")

def computeOBB(mesh):
    # do something
    return None

# Read all parts for all chairs and create the templates
chairDirs = [f for f in listdir("last_examples") if isdir(join("last_examples", f))]
for chairDir in chairDirs:
    newTemplate = Template(chairDir, []);
    chairMeshes = "last_examples/" + chairDir + "/meshes";
    chairParts = [f for f in listdir(chairMeshes) if isfile(join(chairMeshes, f))]
    for chairPart in chairParts:
        mesh = pymesh.load_mesh(chairMeshes + "/" + chairPart)
        boundingBox = computeOBB(mesh);
        newTemplatePart = TemplatePart(chairPart, boundingBox)
        newTemplate.templateParts.append(newTemplatePart)
    templates.append(newTemplate)

print(templates)
