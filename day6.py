from collections import defaultdict

example = '''COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L'''
example_orbits = 42

with open('day6_input', 'r') as f:
    part_1 = f.read()


def find_path(graph, start, end, path=None):
    if path is None:
        path=[]
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath:
                return newpath
    return None


def make_graph(input_string):
    orbit_data = input_string.splitlines()
    orbits = {}
    for body, satelite in (entry.split(')') for entry in orbit_data):
        if body not in orbits:
            orbits[body] = []
        if satelite not in orbits:
            orbits[satelite] = []
        orbits[body].append(satelite)
    return orbits


def solve(string):
    graph = make_graph(string)
    paths = [find_path(graph, 'COM', body) for body in graph]
    return sum(len(x)-1 for x in paths)


assert solve(example) == example_orbits
print(f'[PART 1] TOTAL NUMBER OF ORBITS: {solve(part_1)}')  # 1831 IS WRONG
