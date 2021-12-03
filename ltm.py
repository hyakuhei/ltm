grammar = """
    start: command+

    command: dataflow   
           | scene      
           | boundary
           | nest

    boundary: "boundary" SPACE ESCAPED_STRING ":" [ WORD+ | ESCAPED_STRING+ ]

    dataflow: pitcher SPACE catcher ":"[SPACE][ flow | protocol ]
    pitcher: WORD
    catcher: WORD
    flow: ESCAPED_STRING
    protocol: WORD "(" [ protocol | flow ]")"
    nest: "nest" SPACE ESCAPED_STRING ":" ESCAPED_STRING+

    scene: "scene:"[SPACE]ESCAPED_STRING

    SPACE: " "

    STRING: ESCAPED_STRING

    %import common.WORD
    %import common.ESCAPED_STRING
    %import common.WS

    %ignore WS
"""

import json
import logging
import sys

from deepdiff import DeepDiff

from lark import Lark
from lark.visitors import Visitor_Recursive

parser = Lark(grammar)

doc = {"actors": {}, "boundaries": {}, "scenes": []}

globalContext = {"currentScene": "UNSET"}

_sceneMap = {}

# Use the boundary class to hold the boundary
# structure in memory as a tree
class Boundary():
    def __init__(self):
        self.parent=None
        self.children=[]
        self.actors=[]
        self.name=None

    def boundaryToDict(self, parent, boundaries=None):
        """
        For a given boundary, return a dict of the tree
        including and below this boundary
        """
        if boundaries == None:
            boundaries = {}

        if not self.name:
            return boundaries

        boundaries[self.name] = {
            "actors":self.actors
        }

        return boundaries

class MyVisitor(Visitor_Recursive):
    # This has to be run top-down.
    def _addActor(self, tree):
        if globalContext["currentScene"] == "UNSET":
            logging.error(
                'All Dataflows must belong to a scene. Hint: define a scene using: scene:"TheScene"'
            )

        if str(tree.children[0]) not in doc["actors"]:
            doc["actors"][str(tree.children[0])] = {}

    def pitcher(self, tree):
        self._addActor(tree)

    def catcher(self, tree):
        self._addActor(tree)

    def scene(self, tree):
        sceneName = str(tree.children[1]).strip('"\\')
        globalContext["currentScene"] = sceneName
        if sceneName not in _sceneMap:
            scene = {sceneName:[]}
            doc["scenes"].append(scene)
            _sceneMap[sceneName] = scene[sceneName] # Look up the right scene in the [] of scenes

    def dataflow(self, tree):
        flow = {}
        protocols = []
        parentProtocol = flow  # Flow is kind of always an anonymous protocol

        for sub in tree.iter_subtrees():
            if sub.data == "pitcher":
                flow["from"] = str(sub.children[0])
            if sub.data == "catcher":
                flow["to"] = str(sub.children[0])
            if sub.data == "protocol":
                # Nested protocol
                protocols.append(str(sub.children[0]))
            if sub.data == "flow":
                # Check to see if we have protocols that this should be nestled in
                parentProtocol["data"] = str(sub.children[0]).strip('"\\')

        protocols.reverse()
        for p in protocols:
            newProtocol = {"name": p}
            parentProtocol["protocol"] = newProtocol
            parentProtocol = newProtocol

        _sceneMap[globalContext["currentScene"]].append(flow)
        #doc["scenes"][globalContext["currentScene"]].append(flow)

    def nest(self, tree):
        """
        Nest is a command to re-order the way boundaries are nested
        It will take a boundary (and any of it's nested boundaries)
        And relocate it within (below) the specified boundaries
        """

        for child in tree.children:
            print(child)

    def _walkBoundaries(self, boundaryDict):
        for p in boundaryDict.keys():
            print(f"{p} contains {[x for x in boundaryDict[p]['boundaries']]}" )
        
    def moveBoundary(self, parent, mover):
        # Find mover in the existing doc structure
        self._walkBoundaries(parent)

    def boundary(self, tree):
        print(tree.children)        
    
        thisBoundary = None

        for child in tree.children:
            if child.type == "WS":
                continue # Skip to next child

            if child.type == "ESCAPED_STRING":
                # If this is the first escaped string, it's the boundary being declared
                # and we set 'thisBoundary'
                # If this is not the first escaped string, it's an instruction to nest.
                # This will overwrite the previous boundary if one existed with the same name 
                if thisBoundary == None:
                    thisBoundary = str(child).strip('"\\')
                    doc["boundaries"][thisBoundary] = {
                        "actors":[],
                        "boundaries":{}
                    }
                else: # We've got a boundary to nest
                    # You can't declare boundaries this way, only nest them
                    # That means this is an instruction to _move_ an existing boundary 
                    nestedBoundary = str(child).strip('"\\')
                    self.moveBoundary(doc["boundaries"],nestedBoundary)
                    
            
            if child.type == "WORD":
                doc["boundaries"][thisBoundary]["actors"].append(str(child))


    def boundary_OLD(self,tree):
        for child in tree.children[1:]:
            # First token should always b
            if child.type == "ESCAPED_STRING":
                thisBoundary = str(child).strip('"\\')
                if thisBoundary not in doc["boundaries"]:
                    doc["boundaries"][thisBoundary] = []
            elif child.type == "WORD":
                assert thisBoundary in doc["boundaries"]
                doc["boundaries"][thisBoundary].append(str(child))


## TODO: Add any additional enrichment magic (like say, required fields for a protocol)
def enrich(doc: dict):
    pass

#diagram as code
def dac(doc, engine: str = "dot"):
    pass

def test():
    with open("testInput.ltm", "r") as sample:
        # Parse the input file
        parseTree = parser.parse(sample.read())
        MyVisitor().visit_topdown(parseTree)
        print(json.dumps(doc, indent=4, sort_keys=True), end='')

        # Compare test input with hand crafted json
        with open("targetTestOutput.json", "r") as testTarget:
            testDoc = json.loads(testTarget.read())
            diff = DeepDiff(testDoc, doc)
            if diff == {}:
                pass
            else:
                print(diff)

def main():
    parseTree = parser.parse(sys.stdin.read())
    MyVisitor().visit_topdown(parseTree)
    # print(json.dumps(doc, indent=4, sort_keys=True), end='')

if __name__ == "__main__":
    # test()
    main()