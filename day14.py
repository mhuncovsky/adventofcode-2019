

def parse_rule(s):
    inputs, output = s.split(' => ')
    inputs = [x.split() for x in inputs.split(', ')]
    inputs = [(int(a), b) for a, b in inputs]
    output = (int(output.split()[0]), output.split()[1])
    return inputs, output
       

class Reaction:
    def __init__(self, s):
        ins, out = parse_rule(s)
        self.requirements = {name: count for count, name in ins}
        self.count, self.name = out

    def make(self, n=1):
        return {k: v * n for k, v in self.requirements.items()}, self.count * n


class Reactor:
    def __init__(self, s):
        self.reactions = {}
        for line in s.splitlines():
            reaction = Reaction(line)
            self.reactions[reaction.name] = reaction
        self.storage = {}

    def make_one(self, name, n=1):
        required, made_count = self.reactions[name].make(n)
        for item, count in required.items():
            self.storage[item] = self.storage.get(item, 0) - count
        self.storage[name] = self.storage.get(name, 0) + made_count

    def make(self, name, base_resource='ORE', n=1):
        self.make_one(name, n=n)
        while any(v < 0 for k, v in self.storage.items() if k != base_resource):
            for k in list(self.storage.keys()):
                if k != base_resource and self.storage[k] < 0:
                    to_make = abs(self.storage[k])
                    cycles = max(to_make // self.reactions[k].count, 1)
                    self.make_one(k, n=cycles)


def solve1(s):
    r = Reactor(s)
    r.make('FUEL')
    while any(v < 0 for k, v in r.storage.items() if k != 'ORE'):
        for k in list(r.storage.keys()):
            if k != 'ORE' and r.storage[k] < 0:
                r.make(k)
    return abs(r.storage.get('ORE'))

def solve2(s):
    ore = 1000000000000    
    r = Reactor(s)
    r.storage['ORE'] = ore    
    r.make('FUEL')
    ore_one_cycle = ore - r.storage['ORE']
    while r.storage['ORE'] >= ore_one_cycle:
        r.make('FUEL', n=max(r.storage['ORE']//ore_one_cycle, 1))
    return r.storage.get('FUEL')

if __name__ == '__main__':
    with open('day14.txt', 'r') as f:
        inp = f.read()

    print(f'Part 1: {solve1(inp)}')
    print(f'Part 2: {solve2(inp)}')
    
