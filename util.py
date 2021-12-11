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
                if foundPath!= None: #only break the loop if we've found what we were looking for
                    return foundPath

    return None