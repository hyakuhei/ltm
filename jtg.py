import json, tempfile, subprocess, sys

from gvgen import *

ARCH = "High Level Architecture"


def main():
    pass

def _fileSafeString(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit()]).rstrip()

def writeDot(graph, filename):
    with open(filename, "w") as f:
        graph.dot(fd=f)

def drawRecursiveBoundaries(doc, boundaryKey, graph, drawnBoundaries = None):
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
                if "boundary" not in doc["actors"][actor]:
                    drawnActors[actor] = graph.newItem(actor)
                else:
                    boundary = doc["actors"][actor]["boundary"]
                    if boundary not in drawnBoundaries:
                        drawnBoundaries[boundary] = graph.newItem(boundary)
                        graph.styleApply("Boundary", drawnBoundaries[boundary])

                    drawnActors[actor] = graph.newItem(actor, drawnBoundaries[boundary])
                graph.styleApply("Actor", drawnActors[actor])

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
                print(f"Found {searchValue} in a list: {key}")
                path.append(key)
                return path
            else:
                print(f"Found {searchValue} in a dict")
                path.append(key)
                return path
        else:
            if isinstance(value, dict):
                childPath = path[:]
                childPath.append(key)
                foundPath = search(parent[key], searchValue, path=childPath)
                if foundPath!= None: #only break the loop if we've found what we were looking for
                    return foundPath

    return None

# Sets up the doc with some extra references that make graph
# traversal easier
def prepDoc(doc):
    #for boundary in doc["boundaries"].keys():
        # Setup each doc[actors][n] with links to the boundary it should be in
        #for actor in doc["boundaries"][boundary]:
        #    doc["actors"][actor]["boundary"] = boundary

    # Prepare boundary chains for actors
    for actor in doc["actors"].keys():
        path = search(doc["boundaries"], actor)
        print(f"{actor} in {path}")
    #print(f"Found 'Ordering': {path}")
    return doc


def test():
    graphDotFiles = {}
    with open("targetTestOutput.json", "r") as jt:
        doc = json.loads(jt.read())
        doc = prepDoc(doc)

        for scene in doc["scenes"]:
            for sceneName in scene.keys():
                graph = genGraph(doc, sceneName)
                """
                Create a temporary file and have the GvGen graph write to that temporary file
                Execute graphviz to render the temporary file into a PNG 
                """
                with tempfile.NamedTemporaryFile(mode="r+", suffix=".dot") as fp:
                    graph.dot(fd=fp)
                    fp.seek(
                        0
                    )  # Rewind back to the start of the file. Even though later we pass the fp.name,
                    _ = subprocess.run(
                        ["dot", "-s100", "-Tpng", fp.name, f"-o{sceneName}.png"]
                    )
                    _ = subprocess.run(["open", f"{sceneName}.png"])


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
    # test()
