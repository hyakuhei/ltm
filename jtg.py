import json, io

from gvgen import *

def main():
    pass            

def _fileSafeString(filename):
    return("".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip())

def writeDot(graph, filename):
    with open(filename, 'w') as f:
        graph.dot(fd=f)

def genGraph(doc, sceneName):
    sceneToDraw = None
    for sceneDict in doc["scenes"]:
        if sceneName in sceneDict: # This is the correct scene
            sceneToDraw = sceneDict[sceneName]
            break

    # Prep the graph
    graph = GvGen()
    drawnBoundaries = {}
    drawnActors = {}

    # Loop through and draw any actors/boundaries we need
    for flow in sceneToDraw:
        for actor in [flow['to'], flow['from']]:
            if actor not in drawnActors: # it's not been drawn yet
                if "boundary" not in doc["actors"][actor]:
                    drawnActors[actor] = graph.newItem(actor)
                else:
                    boundary = doc["actors"][actor]["boundary"]
                    if boundary not in drawnBoundaries:
                        drawnBoundaries[boundary] = graph.newItem(boundary)
                    
                    drawnActors[actor] = graph.newItem(actor, drawnBoundaries[boundary])
        
        graph.newLink(drawnActors[flow['from']], drawnActors[flow['to']], label=flow['data'])      

    return graph

# Sets up the doc with some extra references that make graph 
# traversal easier
def prepDoc(doc):
    for boundary in doc["boundaries"].keys():
        # Setup each doc[actors][n] with links to the boundary it should be in
        for actor in doc["boundaries"][boundary]:
            doc["actors"][actor]["boundary"] = boundary

    return doc

def test():
    with open("targetTestOutput.json", 'r') as jt:
        doc = json.loads(jt.read())
        doc = prepDoc(doc)

        for scene in doc["scenes"]:
            for sceneName in scene.keys():
                graph = genGraph(doc, sceneName)
                writeDot(graph, f"{_fileSafeString(sceneName)}.dot")

            # Can always bounce these through a tempfile if needed
            
if __name__ == "__main__":
    # main()
    test()