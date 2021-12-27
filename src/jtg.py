import json, subprocess, sys

from util import search, Dot

#This is ugly
ARCH = "High Level Architecture"

def drawRecursiveBoundaries(doc, boundaryKey, graph, drawnBoundaries=None):
    if drawnBoundaries is None:
        drawnBoundaries = {}

    return graph


# TODO: Smartlinks
def genGraph(doc, sceneName, compoundLinks=False, linkCounters=True):

    sceneToDraw = None
    for sceneDict in doc["scenes"]:
        if sceneName in sceneDict:  # This is the correct scene
            sceneToDraw = sceneDict[sceneName]
            break

    # Prep the graph
    graph = Dot()

    drawnBoundaries = {}
    drawnActors = {}
    linkCounter = 0

    # Left over from GvGen - need to implement some type of stying.
    # graph.styleAppend("Boundary", "color", "red")
    # graph.styleAppend("Actor", "shape", "box")
    # graph.styleAppend("Flow", "fontsize", 10)

    _STYLES = {
        'boundary':'color="Red"',
        'node':'shape="Box"',
        'link':'fontsize="10"'
    }

    graphContainer = graph.newSubgraph(sceneName, style='color="Black"')

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


def main(generateArchDiagram=True,markdown=False):
    doc = json.loads(sys.stdin.read())
    doc = prepDoc(doc)
    graph = None

    if generateArchDiagram == True:  # TODO: Make this a command line argument
        doc = addArchScene(doc)  # adds an ARCH scene to the doc
        doc["scenes"] # Arch scene is just all of the existing scenes, bundled into one big one and run with compoundLinks

    for scene in doc["scenes"]:
        for sceneName in scene.keys():
            graph = genGraph(doc, sceneName)

            fileName = f"output/{sceneName}"
            with open(f"{fileName}.dot", "w") as f:
                if sceneName == ARCH:
                    f.write(graph.dot(compoundLinks=True))
                else:
                    f.write(graph.dot())

            _ = subprocess.run(
                ["dot", "-s100", "-Tpng", f"{fileName}.dot", f"-o{fileName}.png"], shell=False
            )

            if markdown:
                print(f"## {sceneName}")
                print(f"![{sceneName}]({fileName}.png)")
                for flow in scene:
                    print(flow)


if __name__ == "__main__":
    #TODO argument handling
    main(generateArchDiagram=True, markdown=True)
