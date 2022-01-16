grammar = """
    start: command+

    command: describe
           | include 
           | scene      
           | boundary
           | dataflow
           
    describe: "describe" SPACE WORD ":" SPACE ESCAPED_STRING

    include: "include" SPACE WORD

    boundary: "boundary" SPACE ESCAPED_STRING ":" [ WORD+ | ESCAPED_STRING+ ]

    dataflow: pitcher SPACE catcher ":"[SPACE][ flow | protocol ]
    pitcher: WORD
    catcher: WORD
    flow: ESCAPED_STRING
    protocol: WORD "(" [ protocol | flow ]")"

    scene: "scene:"[SPACE]ESCAPED_STRING

    SPACE: " "

    STRING: ESCAPED_STRING

    //
    // Names (Variables)
    //
    LCASE_LETTER: "a".."z"
    UCASE_LETTER: "A".."Z"
    DELIM_CHAR: ("/"|"-"|"_"|".")


    LETTER: UCASE_LETTER | LCASE_LETTER | DELIM_CHAR | DIGIT
    WORD: LETTER+

    %import common.DIGIT
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

import util

parser = Lark(grammar)

doc = {"actors": {}, "boundaries": {}, "scenes": []}

globalContext = {"currentScene": "UNSET", "boundaryNameCache": []}
_sceneMap = {}


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
        """Visitor Function"""
        self._addActor(tree)

    def catcher(self, tree):
        """Visitor Function"""
        self._addActor(tree)

    def include(self, tree):
        """Visitor Function"""
        pass

    def scene(self, tree):
        """Visitor Function"""
        sceneName = str(tree.children[1]).strip('"\\')
        globalContext["currentScene"] = sceneName
        if sceneName not in _sceneMap:
            scene = {sceneName: []}
            doc["scenes"].append(scene)
            _sceneMap[sceneName] = scene[
                sceneName
            ]  # Look up the right scene in the [] of scenes

    def describe(self, tree):
        """Visitor Function"""
        #print(f"Visited {tree}")

        describedActor = None

        for child in tree.children:
            if child.type == "WS":
                continue
            if child.type == "WORD":
                # This is the name of the actor we wish to describe
                assert describedActor is None
                assert str(child) in doc["actors"]
                describedActor = doc["actors"][str(child)]
            if child.type == "ESCAPED_STRING":
                assert describedActor is not None
                describedActor['description'] = str(child).strip('"\\')

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
        # doc["scenes"][globalContext["currentScene"]].append(flow)

    def _getBoundary(self, target, theDict=None):
        if theDict == None:
            theDict = doc["boundaries"]

        for k in theDict.keys():
            if k == target:
                return theDict
            else:
                if "boundaries" in theDict:
                    return self._getBoundary(target, theDict[k])

    def _moveBoundary(
        self,
        childKey: str,
        newParentKey: str,
        childDict: dict = None,
        parentDict: dict = None,
        searchDict: dict = None,
    ):
        """
        Walk the assembled boundaries looking for the one to be moved and the location to move it to
        @childKey - the name of the boundary to move
        @newParentKey - the name of the boundary that the @childKey will be moved under
        @childDict - Memo of which dictionary has the @childKey in it
        @parentDict - Memo of which dictionary has the @newParentKey in it
        @searchDict -  The dictionary we are searching
        """
        if searchDict == None:
            searchDict = doc["boundaries"]

        if newParentKey in searchDict:
            parentDict = searchDict

        if childKey in searchDict:
            childDict = searchDict

        # Both dicts have been found
        if parentDict != None and childDict != None:
            parentDict[newParentKey]["boundaries"][childKey] = childDict[childKey]
            del childDict[childKey]
            return
        else:
            for child in list(searchDict.keys()):
                if (
                    child in searchDict
                ):  # We need this check, because a previous iteration might have deleted the entry
                    self._moveBoundary(
                        childKey,
                        newParentKey,
                        childDict,
                        parentDict,
                        searchDict[child]["boundaries"],
                    )

    def nestBoundary(self, childKey: str, newParentKey: str):
        self._moveBoundary(childKey, newParentKey)

    def boundary(self, tree):
        # print(tree.children)

        thisBoundary = None

        for child in tree.children:
            if child.type == "WS":
                continue  # Skip to next child

            if child.type == "ESCAPED_STRING":
                # If this is the first escaped string, it's the boundary being declared
                # and we set 'thisBoundary'
                # If this is not the first escaped string, it's an instruction to nest.
                # This will overwrite the previous boundary if one existed with the same name
                if thisBoundary == None:
                    thisBoundary = str(child).strip('"\\')
                    if thisBoundary not in globalContext["boundaryNameCache"]:
                        doc["boundaries"][thisBoundary] = {
                            "actors": [],
                            "boundaries": {},
                        }
                        globalContext["boundaryNameCache"].append(thisBoundary)
                else:  # We've got a boundary to nest
                    # You can't declare boundaries this way, only nest them
                    # That means this is an instruction to _move_ an existing boundary
                    nestedBoundary = str(child).strip('"\\')
                    self.nestBoundary(
                        childKey=nestedBoundary, newParentKey=thisBoundary
                    )

            if child.type == "WORD":
                doc["boundaries"][thisBoundary]["actors"].append(str(child))


def test():
    with open("testInput.ltm", "r") as sample:
        # Parse the input file
        parseTree = parser.parse(sample.read())
        MyVisitor().visit_topdown(parseTree)
        print(json.dumps(doc, indent=4, sort_keys=True), end="")

        # Compare test input with hand crafted json
        with open("targetTestOutput.json", "r") as testTarget:
            testDoc = json.loads(testTarget.read())
            diff = DeepDiff(testDoc, doc)
            if diff == {}:
                pass
            else:
                print(diff)


def main():
    preparse = []
    for s in sys.stdin.readlines():
        if s.startswith("include"):
            path = s.split(" ")[-1]
            preparse.append(util.safeFileRead(path))
        else:
            preparse.append(s)
    
    preParsedString = "".join(preparse)

    parseTree = parser.parse(preParsedString)
    MyVisitor().visit_topdown(parseTree)
    print(json.dumps(doc, indent=4, sort_keys=True), end="")


if __name__ == "__main__":
    # test()
    main()
