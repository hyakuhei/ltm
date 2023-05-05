import json, subprocess, sys, os

from util import search, prepDoc, addArchScene


def genMMGraph(
    doc, sceneName, compoundLinks=False, linkCounters=True, printLabels=True
):

    sceneToDraw = None
    for sceneDict in doc["scenes"]:
        if sceneName in sceneDict:  # This is the correct scene
            sceneToDraw = sceneDict[sceneName]
            break

    for flow in sceneToDraw:
        for actor in [flow["to"], flow["from"]]:
            # set parent boundary
            pass


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
            # Generate a mermaid sourcefile
            mm = """
            sequenceDiagram
                Alice->>John: Hello John, how are you?
                John-->>Alice: Great!
                Alice-)John: See you later!
            """

            # Write the mermaid sourcefile
            try:
                fileName = f"output/{sceneName}"
                with open(f"{fileName}.mm", "w") as f:
                    f.write(mm)
            except Exception as e:
                print(e)

            # Call the mermaid CLI (expecting Docker) to generate the file
            # docker run --rm -u `id -u`:`id -g` -v `pwd`:/data minlag/mermaid-cli --input /data/temp_test.md
            _ = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-u",
                    f"{os.geteuid()}:{os.getegid()}",
                    "-v",
                    f"{os.getcwd()}:/data",
                    "minlag/mermaid-cli",
                    "--input",
                    f"/data/{fileName}.mm",
                ]
            )


if __name__ == "__main__":
    # TODO argument handling

    parms = {
        "generateArchDiagram": False,
        "markdown": False,
        "printLabels": False,
        "linkCounters": False,
    }

    if "-h" in sys.argv or "--help" in sys.argv:
        print(
            """
        Generate architecture diagrams and markdown reports from JSON files

        -h \t\t Print this help
        -arch \t\t Generate a summary high level architeciture diagram from the supplied scenes
        -markdown \t Generate Markdown output that inlcudes generated diagrams
        -label \t\t Include data strings in edge labels
        -number \t Number each dataflow
        """
        )
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
