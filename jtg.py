import json, tempfile, subprocess, sys

from util import search
from gvgen import *

ARCH = "High Level Architecture"

def _fileSafeString(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit()]).rstrip()


def writeDot(graph, filename):
    with open(filename, "w") as f:
        graph.dot(fd=f)


def drawRecursiveBoundaries(doc, boundaryKey, graph, drawnBoundaries=None):
    if drawnBoundaries is None:
        drawnBoundaries = {}

    return graph


def genGraph(doc, sceneName, useSmartLinks=False, linkCounters=True):
    sceneToDraw = None
    for sceneDict in doc["scenes"]:
        if sceneName in sceneDict:  # This is the correct scene
            sceneToDraw = sceneDict[sceneName]
            break

    # Prep the graph
    graph = GvGen()
    graph.smart_mode = 1 if useSmartLinks else 0
    drawnBoundaries = {}
    drawnActors = {}
    linkCounter = 0

    graph.styleAppend("Boundary", "color", "red")

    graph.styleAppend("Actor", "shape", "box")

    graph.styleAppend("Flow", "fontsize", 10)                

    # Loop through and draw any actors/boundaries we need
    for flow in sceneToDraw:
        for actor in [flow["to"], flow["from"]]:
            if actor not in drawnActors:  # it's not been drawn yet
                path = search(doc["boundaries"], actor)
                if path is None:
                    drawnActors[actor] = graph.newItem(actor)
                else:
                    rpath = [x for x in path if x != "actors" and x!= "boundaries"]
                    parentBoundary = None

                    for key in rpath:
                        if key not in drawnBoundaries:
                            drawnBoundaries[key] = graph.newItem(key, parentBoundary)
                            graph.styleApply("Boundary", drawnBoundaries[key])
                            parentBoundary = drawnBoundaries[key]
                        else:
                            parentBoundary = drawnBoundaries[key]
                    drawnActors[actor] = graph.newItem(actor, parentBoundary)

        linkCounter += 1
        flowLabel = (
            flow["data"] if linkCounters == False else f"{linkCounter} {flow['data']}"
        )
        link = graph.newLink(
            drawnActors[flow["from"]], drawnActors[flow["to"]], label=flowLabel
        )
        graph.styleApply("Flow", link)

    return graph


def addArchScene(doc):
    archFlows = []

    for scene in doc["scenes"]:
        for k in scene.keys():
            for flow in scene[k]:
                directionalLink = (flow["from"], flow["to"])
                if directionalLink not in archFlows:
                    archFlows.append(directionalLink)

    d = {ARCH: []}

    for f in archFlows:  # f is a tuple (from, to)
        d[ARCH].append({"from": f[0], "to": f[1], "data": ""})

    doc["scenes"].append(d)
    return doc


def search(parent, searchValue, path=None):
    """
    Search through nested dictionaries and lists looking for a value.
    Return the parameterized keys (or indexes) to reach that value
    """
    if path == None:
        path = []

    res = None
    foundKey = None

    for key, value in parent.items():
        if searchValue in value:
            if isinstance(value, list):
                path.append(key)
                return path
            else:
                path.append(key)
                return path
        else:
            if isinstance(value, dict):
                childPath = path[:]
                childPath.append(key)
                foundPath = search(parent[key], searchValue, path=childPath)
                if (
                    foundPath != None
                ):  # only break the loop if we've found what we were looking for
                    return foundPath

    return None


# Sets up the doc with some extra references that make graph
# traversal easier
def prepDoc(doc):
    # for boundary in doc["boundaries"].keys():
    # Setup each doc[actors][n] with links to the boundary it should be in
    # for actor in doc["boundaries"][boundary]:
    #    doc["actors"][actor]["boundary"] = boundary

    # Prepare boundary chains for actors
    for actor in doc["actors"].keys():
        path = search(doc["boundaries"], actor)
    return doc

def main(generateArchDiagram=True):
    doc = json.loads(sys.stdin.read())
    doc = prepDoc(doc)
    graph = None

    if generateArchDiagram == True:  # TODO: Make this a command line argument
        doc = addArchScene(doc)  # adds an ARCH scene to the doc

    for scene in doc["scenes"]:
        for sceneName in scene.keys():
            if sceneName == ARCH:
                graph = genGraph(doc, sceneName, useSmartLinks=True, linkCounters=False)
            else:
                graph = genGraph(doc, sceneName)

            with tempfile.NamedTemporaryFile(mode="r+", suffix=".dot") as fp:
                graph.dot(fd=fp)
                fp.seek(
                    0
                )  # Rewind back to the start of the file. Even though later we pass the fp.name,
                _ = subprocess.run(
                    ["dot", "-s100", "-Tpng", fp.name, f"-ooutput/{sceneName}.png"]
                )


if __name__ == "__main__":
    main()
