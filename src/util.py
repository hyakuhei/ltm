"""Utility module for the ltm project

* search - search a nested dict for value. Return list of keys
* Dot - A dotFile renderer
"""

from typing import Union


def search(parent: dict, searchValue, path: list = None):
    """Search through nested dictionaries and lists looking for a value.


    Args:
        parent (dict): The first dictionary to start searching
        searchValue (variable): The value being searched for
        path (list, optional): The paths that have been searched. Defaults to None.

    Returns:
        list[keys]: List containing keys in required to traverse to the searched value
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


class Dot:
    def __init__(self):
        self._nodes = []
        self._subgraphs = []
        self._edges = []
        self._idCounter = 0
        """
        A few rules.
        1. A node can only belong to 0..1 subgraphs
        2. A subgraph can only belong to 0..1 subgraphs
        """

    def newSubgraph(
        self, label: str = "", parent: dict = None, style: str = 'color="Coral1"'
    ) -> dict:
        """Create a new subgraph

        Args:
            label (str, optional): Label for the subgraph. Defaults to "".
            parent (dict, optional): Make this subgraph a child of the parent. Defaults to None.

        Returns:
            dict: subgraph
        """
        if parent is not None:
            assert parent in self._subgraphs
            assert parent["nodetype"] == "subgraph"

        self._idCounter += 1
        newSub = {
            "id": self._idCounter,
            "label": label,
            "parent": parent,
            "nodetype": "subgraph",
            "style": style,
        }
        self._subgraphs.append(newSub)
        return newSub

    def newNode(
        self,
        label: str = "",
        parent: dict = None,
        style: str = 'shape="box", margin="0.1", color="Grey"',
    ) -> dict:
        """Create a new node

        Args:
            label (str, optional): A label for the node. Defaults to "".
            parent (dict, optional): Make this node a child of a parent subgraph. Defaults to None. Defaults to None.

        Returns:
            dict: [description]
        """
        if parent is not None:
            assert parent in self._subgraphs
            assert parent["nodetype"] == "subgraph"

        self._idCounter += 1
        node = {
            "id": self._idCounter,
            "label": label,
            "parent": parent,
            "nodetype": "node",
            "style": style,
        }
        self._nodes.append(node)
        return node

    def newLink(
        self,
        nodeA: dict,
        nodeB: dict,
        label: str = "",
        style: str = 'fontsize="10",penwidth="1.2",arrowsize="0.8"',
    ) -> dict:
        """Create a new link between nodes or subgraphs

        Creates a directional link from nodeA to nodeB
        Nodes can be subgraphs
        The naming is not helpful

        Args:
            nodeA (dict): Node or subgraph
            nodeB (dict): Node or subgraph
            label (str, optional): Label for the link. Defaults to "".

        Returns:
            dict: [description]
        """
        link = {"from": nodeA, "to": nodeB, "label": label, "style": style}
        self._edges.append(link)
        return link

    def recurse(self, item: dict, s: list, depth: int = 1, parent: dict = None):
        """Append dot formatted strings to s

        strings are immutable in python, you can't pass a string to this function
        instead you pass a list `s` each recursive call appends strings to `s`
        later those can be joined to make one big string.

        Args:
            item (dict): The node or subgraph to recurse
            s (list): a list of strings that this method will append to
            depth (int, optional): Used to track depth in the tree and format identation. Defaults to 1.
            parent (dict, optional): The parent of item, if it has one. Defaults to None.
        """
        openBrace = "{"
        closeBrace = "}"
        tab = "    "

        if item["nodetype"] == "subgraph":
            # Write the opening for this subgraph
            s.append(f"{tab*depth}subgraph cluster{item['id']} {openBrace}")
            s.append(f'{tab*depth}label="{item["label"]}";')
            s.append(f'{tab*depth}{item["style"]};')

            # Gather any nodes/subgraphs that are children of this subgraph
            children = [x for x in self._nodes if x["parent"] == item] + [
                x for x in self._subgraphs if x["parent"] == item
            ]

            for child in children:
                self.recurse(child, s, depth=depth + 1)

            s.append(f"{tab*depth}{closeBrace}")

        if item["nodetype"] == "node":
            s.append(
                f'{tab*depth}node{item["id"]} [label="{item["label"]}" {item["style"]}];'
            )

    def dot(self, compoundLinks=False) -> str:
        """Generate a string of the dot graph

        Args:
            compundLinks (bool): The node or

        Returns:
            str: string representing the graph in dot format
        """
        # Every subgraph with no parent is the root of it's own tree
        # Every node with no parent is the root of it's own tree
        dotStrings = []

        dotStrings.append("digraph G {")
        dotStrings.append("compound=true;")
        dotStrings.append('rankdir="LR"')

        for sub in [x for x in self._subgraphs if x["parent"] == None]:
            self.recurse(sub, dotStrings)

        for node in [x for x in self._nodes if x["parent"] == None]:
            self.recurse(sub, dotStrings)

        if compoundLinks == True:
            # Compound links _over-rides_ styling
            lookup = {}
            edgesToDraw = []

            # First do a pass to count the repeated edges (between any two nodes)
            for edge in self._edges:
                if (edge["from"]["id"], edge["to"]["id"]) in lookup:
                    lookup[(edge["from"]["id"], edge["to"]["id"])]["count"] += 1
                elif (edge["to"]["id"], edge["from"]["id"]) in lookup:
                    lookup[(edge["to"]["id"], edge["from"]["id"])]["count"] += 1
                else:
                    lookup[(edge["from"]["id"], edge["to"]["id"])] = {
                        "count": 1,
                        "edge": edge,
                    }

            # List a new set of edges, only one for each node
            # Double ended when required
            # Thicker when there's more connections
            for x in lookup.keys():
                modifiedEdge = lookup[x][
                    "edge"
                ].copy()  # Edges are provided by the user, don't modify them
                modifiedEdge["label"] = ""
                style = f'fontsize="10", penwidth="{1.2 * lookup[x]["count"]}", arrowsize="0.8"'
                if lookup[x]["count"] > 1:
                    modifiedEdge["style"] = f"dir=both, {style}"
                else:
                    modifiedEdge["style"] = style

                edgesToDraw.append(modifiedEdge)
        else:
            edgesToDraw = self._edges

        # Write the links
        for edge in edgesToDraw:
            # example: node1->node2 [label="meep" fontsize="10",penwidth="1.2",arrowsize="0.8"];
            s = f'node{edge["from"]["id"]}->node{edge["to"]["id"]} [label="{edge["label"]}" {edge["style"]}];'

            dotStrings.append(s)

        dotStrings.append("}")
        return "\n".join(dotStrings)

    # XXX: Remove
    def test(self):
        graph = Dot()
        mainContainer = graph.newSubgraph("Main Container")
        a1 = graph.newSubgraph("a1", parent=mainContainer)
        a2 = graph.newSubgraph("a2", parent=a1)
        a3 = graph.newNode("a3", parent=a2)

        b1 = graph.newSubgraph("b1", parent=mainContainer)
        b2 = graph.newSubgraph("b1", parent=b1)
        b3 = graph.newNode("b3", parent=b2)

        graph.newLink(b3, a3, label="OMG WHZT?")
        graph.newLink(a3, b3, label="I KNOW RIGHT!")

        print(graph.dot(compoundLinks=True))


# XXX: Remove
if __name__ == "__main__":
    Dot().test()
