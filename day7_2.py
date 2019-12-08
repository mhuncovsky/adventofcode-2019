import itertools
from collections import deque

DEBUG = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class IntCode:
    def __init__(self, memory, input_buffer):
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
        self.input_buffer = input_buffer
        self.output_buffer = deque()
        self.last_instruction_address = None
        self.done = False

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
        self.last_instruction_address = self.ip
        self.ip += 1
        inp = self.get_input()
        if inp is not None:
            self.memory[self.get_parameter_address()] = inp
            self.last_instruction_address = None

    def get_input(self):
        if len(self.input_buffer):
            return self.input_buffer.popleft()
        return None

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
        self.done = True

    def run_program(self, noun, verb):
        self.memory[1] = noun
        self.memory[2] = verb
        return self.run()

    def run(self, inputs):
        self.input_buffer.extend(inputs)
        self.running = True
        while self.running:
            self.tick()
        return self.output_buffer

    def tick(self):
        if self.last_instruction_address is not None:
            self.ip = self.last_instruction_address
        dprint(f'INSTRUCTION POINTER: {self.ip}')
        opcode = self.memory[self.ip] % 100
        self.parameter_modes += [int(d) for d in str(self.memory[self.ip])[:-2]]
        dprint(f'OPCODE: {opcode} ({self.opcodes.get(opcode).__name__}), PRM_MODES={self.parameter_modes!r}')
        self.opcodes.get(opcode)()


class Amp(IntCode):
    def __init__(self, memory, input_buffer, phase):
        super().__init__(memory, input_buffer)
        self.phase = phase
        self.input_buffer.appendleft(phase)


def get_amp_output(mem, phases):
    global amps
    inb = deque([0])
    amps = []
    for p in phases:
        amp = Amp(mem, inb, p)
        amps.append(amp)
        inb = amp.output_buffer
    amps[-1].output_buffer = amps[0].input_buffer
    while not all(amp.done for amp in amps):
        for amp in amps:
            amp.tick()
    return amps[-1].output_buffer.popleft()


def solve(input_data):
    permutations = list(itertools.permutations([5, 6, 7, 8, 9]))
    outputs = [get_amp_output(input_data, p) for p in permutations]
    return max(outputs)


example_1 = (
    [3, 26, 1001, 26, -4, 26, 3, 27, 1002, 27, 2, 27, 1, 27, 26, 27, 4, 27, 1001, 28, -1, 28, 1005, 28, 6, 99, 0, 0, 5],
    [9, 8, 7, 6, 5],
)
assert get_amp_output(*example_1) == 139629729

example_2 = (
    [3, 52, 1001, 52, -5, 52, 3, 53, 1, 52, 56, 54, 1007, 54, 5, 55, 1005, 55, 26, 1001, 54, -5, 54, 1105, 1, 12, 1, 53,
     54, 53, 1008, 54, 0, 55, 1001, 55, 1, 55, 2, 53, 55, 53, 4, 53, 1001, 56, -1, 56, 1005, 56, 6, 99, 0, 0, 0, 0, 10],
    [9, 7, 8, 5, 6],
)
assert get_amp_output(*example_2) == 18216


with open('day7_input.txt', 'r') as f:
    input_data = [int(x) for x in f.read().strip().split(',')]

print(f'MAX OUTPUT: {solve(input_data)}')
