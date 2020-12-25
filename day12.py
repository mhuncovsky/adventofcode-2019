import re
import itertools
import math
from collections import deque

DEBUG = False
STEP = False

INPUT = '''<x=1, y=3, z=-11>
<x=17, y=-10, z=-8>
<x=-1, y=-15, z=2>
<x=12, y=-4, z=-4>'''


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def parse(s):
    bodies = []
    for x, y, z in re.findall(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)>', s):
        bodies.append(Body((int(x), int(y), int(z)), (0, 0, 0)))
    return bodies


class Body:
    def __init__(self, position, velocity):
        self.pos = list(position)
        self.vel = list(velocity)


class System:
    def __init__(self, s):
        self.bodies = parse(s)
        self.time = 0

    def apply_gravity(self):
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                pa = self.bodies[i].pos
                va = self.bodies[i].vel
                pb = self.bodies[j].pos
                vb = self.bodies[j].vel
                for k in range(len(pa)):
                    if pa[k] > pb[k]:
                        va[k] -= 1
                        vb[k] += 1
                    elif pa[k] < pb[k]:
                        va[k] += 1
                        vb[k] -= 1

    def apply_velocity(self):
        for body in self.bodies:
            for i in range(len(body.pos)):
                body.pos[i] += body.vel[i]

    def energy(self):
        potential = (sum(abs(x) for x in b.pos) for b in self.bodies)
        kinetic = (sum(abs(x) for x in b.vel) for b in self.bodies)
        return sum(p * k for p, k in zip(potential, kinetic))
    
    def step(self, count=1):
        for _ in range(count):
            self.apply_gravity()
            self.apply_velocity()
            self.time += 1

    def __str__(self):
        lines = ((
            f'pos=<x={body.pos[0]:>3d}, y={body.pos[1]:>3d}, z={body.pos[2]:>3d}>, '
            f'vel=<x={body.vel[0]:>3d}, y={body.vel[1]:>3d}, z={body.vel[2]:>3d}>') for body in self.bodies)
        return '\n'.join(lines)

                        
def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)


class System2:
    def __init__(self, s):
        self.bodies = parse(s)
        self.times = [0, 0, 0]

    def pos(self, axis):
        return tuple(b.pos[axis] for b in self.bodies)

    def vel(self, axis):
        return tuple(b.vel[axis] for b in self.bodies)

    def apply_gravity(self, axis):
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                pa = self.bodies[i].pos
                va = self.bodies[i].vel
                pb = self.bodies[j].pos
                vb = self.bodies[j].vel
                if pa[axis] > pb[axis]:
                    va[axis] -= 1
                    vb[axis] += 1
                elif pa[axis] < pb[axis]:
                    va[axis] += 1
                    vb[axis] -= 1

    def apply_velocity(self, axis):
        for body in self.bodies:
            body.pos[axis] += body.vel[axis]
    
    def step(self, axis=0, count=1):
        for _ in range(count):
            self.apply_gravity(axis)
            self.apply_velocity(axis)
            self.times[axis] += 1

    def __str__(self):
        lines = ((
            f'pos=<x={body.pos[0]:>3d}, y={body.pos[1]:>3d}, z={body.pos[2]:>3d}>, '
            f'vel=<x={body.vel[0]:>3d}, y={body.vel[1]:>3d}, z={body.vel[2]:>3d}>') for body in self.bodies)
        return '\n'.join(lines)
    


if __name__ == '__main__':
    import functools
    s = System(INPUT)
    s.step(1000)
    print(f'Part 1: {s.energy()}')

    s =  System2(INPUT)
    for axis in range(3):
        p0 = s.pos(axis)
        v0 = s.vel(axis)
        s.step(axis)
        while s.pos(axis) != p0 or s.vel(axis) != v0:
            s.step(axis)
    print(f'Part 2: {functools.reduce(lcm, s.times)}')
    
        
