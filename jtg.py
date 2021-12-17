import json, subprocess, sys

from util import search, Dot

ARCH = "High Level Architecture"


def drawRecursiveBoundaries(doc, boundaryKey, graph, drawnBoundaries=None):
    if drawnBoundaries is None:
        drawnBoundaries = {}

    return graph


# TODO: Smartlinks
def genGraph(doc, sceneName, useSmartLinks=True, linkCounters=True):

    # XXX: Temporary over-ride to turn this off until smartlinks implemented
    if useSmartLinks == True:
        useSmartLinks = False

    sceneToDraw = None
    for sceneDict in doc["scenes"]:
        if sceneName in sceneDict:  # This is the correct scene
            sceneToDraw = sceneDict[sceneName]
            break

    # Prep the graph
    graph = Dot()

    # Left over from GvGen - I'll implement something like
    # this soon, so leaving here as a reminder.
    # graph.smart_mode = 1 if useSmartLinks else 0
    drawnBoundaries = {}
    drawnActors = {}
    linkCounter = 0

    # Left over from GvGen - need to implement some type of stying.
    # graph.styleAppend("Boundary", "color", "red")
    # graph.styleAppend("Actor", "shape", "box")
    # graph.styleAppend("Flow", "fontsize", 10)

    # graphContainer = graph.newItem("xxx")
    graphContainer = graph.newSubgraph("Window")
    # graphContainer = None

    # Loop through and draw any actors/boundaries we need
    for flow in sceneToDraw:
        for actor in [flow["to"], flow["from"]]:
            parentBoundary = graphContainer
            if actor not in drawnActors:  # it's not been drawn yet
                path = search(doc["boundaries"], actor)
                if path is not None:
                    rpath = [x for x in path if x != "actors" and x != "boundaries"]
                    for key in rpath:
                        if key in drawnBoundaries:
                            parentBoundary = drawnBoundaries[key]
                        else:
                            drawnBoundaries[key] = graph.newSubgraph(
                                key, parentBoundary
                            )
                            # Useful for understanding that stuff is being drawn in the right order
                            # if parentBoundary:
                            #    print(f"Drew {key} under {parentBoundary['properties']['label']}")
                            # else:
                            #    print(f"Drew {key} under {parentBoundary}")

                            # TODO: Replace when util supports Styling
                            # graph.styleApply("Boundary", drawnBoundaries[key])
                            parentBoundary = drawnBoundaries[key]

                drawnActors[actor] = graph.newNode(actor, parent=parentBoundary)

        linkCounter += 1
        flowLabel = (
            flow["data"] if linkCounters == False else f"{linkCounter} {flow['data']}"
        )
        link = graph.newLink(
            drawnActors[flow["from"]], drawnActors[flow["to"]], label=flowLabel
        )
        # graph.styleApply("Flow", link)

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


def main(generateArchDiagram=True, saveDot=False):
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

            fileName = f"output/{sceneName}"
            with open(f"{fileName}.dot", "w") as f:
                f.write(graph.dot())

            _ = subprocess.run(
                ["dot", "-s100", "-Tpng", f"{fileName}.dot", f"-o{fileName}.png"]
            )


if __name__ == "__main__":
    main(generateArchDiagram=False, saveDot=True)
