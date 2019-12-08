import itertools
from collections import deque

DEBUG = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class IntCode:
    def __init__(self, memory):
        self.ip = 0
        self.memory = memory[:]
        self.parameter_modes = []
        self.running = False
        self.opcodes = {
            1: self.add,
            2: self.mul,
            3: self.input,
            4: self.output,
            5: self.jump_if_true,
            6: self.jump_if_false,
            7: self.less_than,
            8: self.equals,
            99: self.halt,
        }
        self.input_buffer = deque()
        self.output_buffer = deque()

    def get_parameter_address(self):
        try:
            parameter_mode = self.parameter_modes.pop()
        except IndexError:
            parameter_mode = 0

        if parameter_mode == 1:
            address = self.ip
        else:
            address = self.memory[self.ip]
        dprint(f'GET PARAMETER ADDRESS: mode={parameter_mode}, memory_value={self.memory[self.ip]}, address={address}')
        self.ip += 1
        return address

    def jump_if_true(self):
        self.ip += 1
        a = self.get_parameter_address()
        b = self.get_parameter_address()
        if self.memory[a]:
            self.ip = self.memory[b]
            dprint(f'JT(a={a}, b={b}) DO JUMP')
        else:
            dprint(f'JT(a={a}, b={b}) DON\'T JUMP')

    def jump_if_false(self):
        self.ip += 1
        a = self.get_parameter_address()
        b = self.get_parameter_address()
        if not self.memory[a]:
            self.ip = self.memory[b]
            dprint(f'JF(a={a}, b={b}) DO JUMP')
        else:
            dprint(f'JF(a={a}, b={b}) DON\'T JUMP')

    def less_than(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        dprint(f'LT(a={a}, b={b}, c={c})')
        self.memory[c] = int(self.memory[a] < self.memory[b])

    def equals(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        dprint(f'EQ(a={a}, b={b}, c={c})')
        self.memory[c] = int(self.memory[a] == self.memory[b])

    def input(self):
        self.ip += 1
        self.memory[self.get_parameter_address()] = self.get_input()

    def get_input(self):
        if len(self.input_buffer):
            return self.input_buffer.popleft()
        return int(input('INPUT: '))

    def output(self):
        self.ip += 1
        output = self.memory[self.get_parameter_address()]
        self.output_buffer.append(output)
        dprint(f'OUTPUT: {output}')

    def add(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        dprint(f'ADD(a={a}, b={b}, c={c})')
        self.memory[c] = self.memory[a] + self.memory[b]

    def mul(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        dprint(f'MUL(a={a}, b={b}, c={c})')
        self.memory[c] = self.memory[a] * self.memory[b]

    def halt(self):
        self.running = False

    def run_program(self, noun, verb):
        self.memory[1] = noun
        self.memory[2] = verb
        return self.run()

    def run(self, inputs):
        self.input_buffer.extend(inputs)
        self.running = True
        while self.running:
            dprint(f'INSTRUCTION POINTER: {self.ip}')
            opcode = self.memory[self.ip] % 100
            self.parameter_modes += [int(d) for d in str(self.memory[self.ip])[:-2]]
            dprint(f'OPCODE: {opcode} ({self.opcodes.get(opcode).__name__}), PRM_MODES={self.parameter_modes!r}')
            self.opcodes.get(opcode)()
        return self.output_buffer


class Amp(IntCode):
    def __init__(self, memory, phase):
        super().__init__(memory)
        self.phase = phase

    def run(self, inputs):
        inputs = [self.phase] + inputs
        return super().run(inputs)


def get_amp_output(memory, phase_settings):
    out = 0
    for ps in phase_settings:
        out = Amp(memory, ps).run([out]).popleft()
    return out


def solve(input_data):
    permutations = list(itertools.permutations([0, 1, 2, 3, 4]))
    outputs = [get_amp_output(input_data, p) for p in permutations]
    return max(outputs)


example_1 = [3, 15, 3, 16, 1002, 16, 10, 16, 1, 16, 15, 15, 4, 15, 99, 0, 0]
solution_1 = get_amp_output(example_1, [4, 3, 2, 1, 0])
print(f'EXAMPLE 1: {solution_1}')
assert solution_1 == 43210

example_2 = [3, 23, 3, 24, 1002, 24, 10, 24, 1002, 23, -1, 23, 101, 5, 23, 23, 1, 24, 23, 23, 4, 23, 99, 0, 0]
solution_2 = get_amp_output(example_2, [0, 1, 2, 3, 4])
print(f'EXAMPLE 2: {solution_2}')
assert solution_2 == 54321

example_3 = [3, 31, 3, 32, 1002, 32, 10, 32, 1001, 31, -2, 31, 1007, 31, 0, 33, 1002, 33, 7, 33, 1, 33, 31, 31, 1, 32,
             31, 31, 4, 31, 99, 0, 0, 0]
solution_3 = get_amp_output(example_3, [1, 0, 4, 3, 2])
print(f'EXAMPLE 3: {solution_3}')
assert solution_3 == 65210

with open('day7_input.txt', 'r') as f:
    input_data = [int(x) for x in f.read().strip().split(',')]

print(f'MAX OUTPUT: {solve(input_data)}')


