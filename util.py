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

    def getNodes(self, label):
        """
        Return a list of nodes that have the provided label
        """
        return [x for x in self._nodes if x["label"] == label]

    def getSubgraph(self, label):
        """
        Return a list of subgraphs that have the provided label
        """
        return [x for x in self._subgraphs if x["label"] == label]

    def newSubgraph(self, label="Anonymous", parent=None):
        if parent is not None:
            assert parent in self._subgraphs

        self._idCounter += 1
        newSub = {
            "id": self._idCounter,
            "label": label,
            "parent": parent,
            "nodetype": "subgraph",
        }
        self._subgraphs.append(newSub)
        return newSub

    def newNode(self, label="Anonymous", parent=None):
        if parent is not None:
            assert parent in self._subgraphs

        self._idCounter += 1
        node = {
            "id": self._idCounter,
            "label": label,
            "parent": parent,
            "nodetype": "node",
        }
        self._nodes.append(node)
        return node

    def newLink(self, nodeA, nodeB, label=None):
        link = {"from": nodeA, "to": nodeB, "label": label}
        self._edges.append(link)
        return link

    def recurse(self, item, s, depth=1, parent=None):
        openBrace = "{"
        closeBrace = "}"
        tab = "    "

        if item["nodetype"] == "subgraph":
            # Write the opening for this subgraph
            s.append(f"{tab*depth}subgraph cluster{item['id']} {openBrace}")
            s.append(f'{tab*depth}label="{item["label"]}";')

            # Gather any nodes/subgraphs that are children of this subgraph
            children = [x for x in self._nodes if x["parent"] == item] + [
                x for x in self._subgraphs if x["parent"] == item
            ]

            for child in children:
                self.recurse(child, s, depth=depth + 1)

            s.append(f"{tab*depth}{closeBrace}")

        if item["nodetype"] == "node":
            s.append(f'{tab*depth}node{item["id"]} [label="{item["label"]}"];')

    def dot(self):
        # Every subgraph with no parent is the root of it's own tree
        # Every node with no parent is the root of it's own tree
        dotStrings = []

        dotStrings.append("digraph G {")
        dotStrings.append("compound=true;")

        for sub in [x for x in self._subgraphs if x["parent"] == None]:
            self.recurse(sub, dotStrings)

        for node in [x for x in self._nodes if x["parent"] == None]:
            self.recurse(sub, dotStrings)

        # return f"nodes: {self._nodes}" + f"\nsubgraphs: {self._subgraphs}"
        # Write the links
        edgeStyle = 'fontsize="10",penwidth="1.2",arrowsize="0.8"'
        for edge in self._edges:
            if edge["label"] != None:
                s = f'node{edge["from"]["id"]}->node{edge["to"]["id"]} [label="{edge["label"]}" {edgeStyle}];'
            else:
                s = f'node{edge["from"]["id"]}->node{edge["to"]["id"]} [{edgeStyle}];'

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

        graph.newLink(b3, a3, label="OMG WHZT")

        print(graph.dot())


# XXX: Remove
if __name__ == "__main__":
    Dot().test()
