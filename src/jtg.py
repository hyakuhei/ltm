import json, subprocess, sys

from util import search, Dot

# XXX: This is ugly
ARCH = "High Level Architecture"


def drawRecursiveBoundaries(doc, boundaryKey, graph, drawnBoundaries=None):
    if drawnBoundaries is None:
        drawnBoundaries = {}

    return graph


# TODO: Smartlinks
def genGraph(doc, sceneName, compoundLinks=False, linkCounters=True, printLabels=True):

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

    _STYLES = {
        "boundary": 'color="Red"',
        "node": 'shape="box", margin="0.1", color="Grey", fontsize="13", fontname="Helvetica"',
        "link": 'fontsize="13", penwidth="1.2", arrowsize="0.8", fontname="Helvetica"',
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

                drawnActors[actor] = graph.newNode(
                    actor, parent=parentBoundary, style=_STYLES["node"]
                )

        linkCounter += 1

        flowLabel = ""
        if linkCounters == True:
            flowLabel = f"{linkCounter}."

        if printLabels == True:
            flowLabel = flowLabel + flow["data"]

        link = graph.newLink(
            drawnActors[flow["from"]],
            drawnActors[flow["to"]],
            label=flowLabel,
            style=_STYLES["link"],
        )

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

    doc["scenes"].insert(0, d)
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


def main(
    generateArchDiagram=True, markdown=False, printLabels=False, linkCounters=True
):
    doc = json.loads(sys.stdin.read())
    doc = prepDoc(doc)
    graph = None

    scenes = doc["scenes"]
    if generateArchDiagram == True:  # TODO: Make this a command line argument
        doc = addArchScene(doc)  # adds an ARCH scene to the doc

    for scene in doc["scenes"]:
        for sceneName in scene.keys():
            graph = genGraph(
                doc, sceneName, linkCounters=linkCounters, printLabels=printLabels
            )

            fileName = f"output/{sceneName}"
            with open(f"{fileName}.dot", "w") as f:
                if sceneName == ARCH:
                    f.write(graph.dot(compoundLinks=True))
                else:
                    f.write(graph.dot())

            _ = subprocess.run(
                ["dot", "-s100", "-Tpng", f"{fileName}.dot", f"-o{fileName}.png"],
                shell=False,
            )

            if markdown:
                print(f"## {sceneName}")
                print(f"![{sceneName}]({fileName.replace(' ', '%20')}.png)")
                if sceneName == ARCH and generateArchDiagram == True:
                    print("\n| Actor | Description |")
                    print("| --- | ---- |")
                    for actor in doc["actors"].keys():
                        print(f"| {actor} | {doc['actors'][actor]['description'] if 'description' in doc['actors'][actor] else '-'} |")
                    print("\n")

                if sceneName != ARCH:
                    print("\n| Id | From | To | Data |")
                    print("| --- | ---- | --- | ---- |")
                    ctr = 1
                    for flow in scene[sceneName]:
                        print(
                            f"| {ctr} | {flow['from']} | {flow['to']} | {flow['data']} |"
                        )
                        ctr += 1
                    print("\n")

                

if __name__ == "__main__":
    # TODO argument handling

    parms = {
        "generateArchDiagram": False,
        "markdown": False,
        "printLabels": False,
        "linkCounters": False,
    }

    if "-h" in sys.argv or "--help" in sys.argv:
        print("""
        Generate architecture diagrams and markdown reports from JSON files

        -h \t\t Print this help
        -arch \t\t Generate a summary high level architeciture diagram from the supplied scenes
        -markdown \t Generate Markdown output that inlcudes generated diagrams
        -label \t\t Include data strings in edge labels
        -number \t Number each dataflow
        """)
        sys.exit(0)

    if "-arch" in sys.argv:
        parms["generateArchDiagram"] = True
    
    if "-markdown" in sys.argv:
        parms["markdown"] = True
    
    if "-label" in sys.argv:
        parms["printLabels"] = True
    
    if "-number" in sys.argv:
        parms["linkCounters"] = True 
    
    main(**parms)

    
