import io

from util import search, Dot

import graphviz


# XXX: This is ugly
ARCH = "High Level Architecture"


def drawRecursiveBoundaries(doc, boundaryKey, graph, drawnBoundaries=None):
    if drawnBoundaries is None:
        drawnBoundaries = {}

    return graph


# TODO: Smartlinks
def genGraph(doc, sceneName, compoundLinks=False, number=True, label=True):

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
        if number == True:
            flowLabel = f"{linkCounter}."

        if label == True:
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


def render(
    doc,
    outputDir,
    generateArchDiagram=True,
    report=False,
    label=False,
    number=True,
    title="High Level Architecture"
):
    doc = prepDoc(doc)
    graph = None

    report_fd = None
    if report == True:
        report_fd = open(f"{outputDir}/report.md", 'w')

    scenes = doc["scenes"]
    if generateArchDiagram == True:  # TODO: Make this a command line argument
        doc = addArchScene(doc)  # adds an ARCH scene to the doc

    for scene in doc["scenes"]:
        for sceneName in scene.keys():
            graph = genGraph(
                doc, sceneName, number=number, label=label
            )

            fileName = f"{outputDir}/{sceneName}"
            if sceneName == title:
                graph.write(fileName, compoundLinks=True)
            else:
                graph.write(fileName)

            graphviz.render("dot", "png", fileName).replace("\\", "/")

            if report:
                report_fd.write(f"## {sceneName}\n")
                report_fd.write(f"![{sceneName}]({sceneName.replace(' ', '%20')}.png)\n")
                if sceneName == title and generateArchDiagram == True:
                    report_fd.write("\n| Actor | Description |\n")
                    report_fd.write("| --- | ---- |\n")
                    for actor in doc["actors"].keys():
                        report_fd.write(
                            f"| {actor} | {doc['actors'][actor]['description'] if 'description' in doc['actors'][actor] else '-'} |\n"
                        )
                    report_fd.write("\n\n")

                if sceneName != title:
                    report_fd.write("\n| Id | From | To | Data |\n")
                    report_fd.write("| --- | ---- | --- | ---- |\n")
                    ctr = 1
                    for flow in scene[sceneName]:
                        report_fd.write(
                            f"| {ctr} | {flow['from']} | {flow['to']} | {flow['data']} |\n"
                        )
                        ctr += 1
                    report_fd.write("\n")
                
    if report_fd is not None:
        report_fd.close()
