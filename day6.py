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
example2 = '''COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN'''
example2_orbit_transfers = 4

with open('day6_input.txt', 'r') as f:
    part_1 = f.read()


def find_path(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath:
                return newpath
    return None


def find_shortest_path(graph, start, end):
    shortest_paths = {start: None}
    current_node = start
    visited = set()

    while current_node != end:
        visited.add(current_node)
        destinations = graph[current_node]

        for next_node in destinations:
            if next_node not in shortest_paths:
                shortest_paths[next_node] = current_node

        next_destinations = [node for node in shortest_paths if node not in visited]
        current_node = next_destinations[0]

    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node]
        current_node = next_node

    return path[::-1]


def make_graph(input_string):
    orbit_data = input_string.splitlines()
    orbits = {}
    for body, satelite in (entry.split(')') for entry in orbit_data):
        if body not in orbits:
            orbits[body] = []
        if satelite not in orbits:
            orbits[satelite] = []
        orbits[body].append(satelite)
        orbits[satelite].append(body)
    return orbits


def solve(string):
    graph = make_graph(string)
    paths = [find_path(graph, 'COM', body) for body in graph]
    return sum(len(x)-1 for x in paths)


def solve2(string):
    graph = make_graph(string)
    path = find_shortest_path(graph, 'YOU', 'SAN')
    return len(path) - 3


assert solve(example) == example_orbits
assert solve2(example2) == example2_orbit_transfers

print(f'[PART 1] TOTAL NUMBER OF ORBITS: {solve(part_1)}')  # 1831 IS WRONG, 130681 OK
print(f'[PART 2] ORBIT TRANSFERS NEEDED: {len(find_shortest_path(make_graph(part_1), "YOU", "SAN")) - 3}')
