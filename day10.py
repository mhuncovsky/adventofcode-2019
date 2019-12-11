import math
from collections import defaultdict


with open('day10_input.txt', 'r') as f:
    input_data = f.read()

with open('day10_example.txt', 'r') as f:
    example = f.read()


def get_asteriods(string):
    return [(x, y) for y, line in enumerate(string.splitlines()) for x, value in enumerate(line) if value == '#']


def get_line_of_sight(center, target):
    x, y = target[0] - center[0], target[1] - center[1]
    xy_gcd = math.gcd(x, y)
    return x / xy_gcd, y / xy_gcd


def count_los(center, asteroids):
    los = set()
    for asteroid in asteroids:
        if asteroid == center:
            continue
        los.add(get_line_of_sight(center, asteroid))
    return len(los)


def find_station(string):
    asteroids = get_asteriods(string)
    los_counts = [count_los(a, asteroids) for a in asteroids]
    return asteroids[los_counts.index(max(los_counts))], max(los_counts)


def solve(string):
    return find_station(string)[1]


assert ((11, 13), 210) == find_station(example)
print(f'BEST LOCATION CAN SEE {solve(input_data)} ASTEROIDS.')


def get_los2(center, target):
    x, y = target[0] - center[0], target[1] - center[1]
    return x, y


def angle(x, y):
    p = math.fmod(math.atan2(y, x), math.pi * 2)
    deg = math.degrees(p) - 90
    while deg < 0:
        deg += 360
    return deg


def normalize_los(los):
    x, y =  los
    xy_gcd = math.gcd(x, y)
    return x / xy_gcd, y / xy_gcd


center, _ = find_station(example)
asteroids = get_asteriods(example)
asteroids.remove(center)
los = [get_los2(center, a) for a in asteroids]
combined = list(zip(asteroids, los))
left = [(a, la) for a, la in combined if la[0] < 0]
middle = [(a, la) for a, la in combined if la[0] == 0]
right = [(a, la) for a, la in combined if la[0] > 0]


def screen(asteroid_data, reverse):
    a_by_los = defaultdict(list)
    for a, la in asteroid_data:
        a_by_los[normalize_los(la)].append((a, la))
    for k in a_by_los:
        a_by_los[k] = sorted(a_by_los[k], key=lambda x: x[1][1], reverse=reverse)
    sorted_by_x = sorted(a_by_los.keys(), key=lambda x: x[0], reverse=reverse)
    deleted = []
    for k in sorted_by_x:
        a, la = a_by_los[k].pop(0)
        deleted.append(a)
        asteroid_data.remove((a, la))
    return asteroid_data, deleted




assert ((5, 8), 33) == find_station('''......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####''')
assert ((1, 2), 35) == find_station('''#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.''')
assert ((6, 3), 41) == find_station('''.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..''')