import itertools
from collections import deque

DEBUG = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class IntCode:
    def __init__(self, memory, input_buffer):
        self.ip = 0
        self.memory = memory[:] + [0] * 1024 * 1024
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
            9: self.adjust_relative_base,
            99: self.halt,
        }
        self.input_buffer = input_buffer
        self.output_buffer = deque()
        self.relative_base = 0
        self.last_instruction_address = None
        self.done = False

    def get_parameter_address(self):
        try:
            parameter_mode = self.parameter_modes.pop()
        except IndexError:
            parameter_mode = 0

        if parameter_mode == 1:
            address = self.ip
        elif parameter_mode == 2:
            address = self.read_memory(self.ip) + self.relative_base
        else:
            address = self.read_memory(self.ip)
        dprint(f'GET PARAMETER ADDRESS: mode={parameter_mode}, memory_value={self.read_memory(self.ip)}, address={address}')
        self.ip += 1
        return address

    def adjust_relative_base(self):
        self.ip += 1
        parameter_address = self.get_parameter_address()
        self.relative_base += self.read_memory(parameter_address)

    def read_memory(self, address):
        if address < 0:
            return self.memory[0]
        return self.memory[address]

    def jump_if_true(self):
        self.ip += 1
        a = self.get_parameter_address()
        b = self.get_parameter_address()
        if self.read_memory(a):
            self.ip = self.read_memory(b)
            dprint(f'JT(a={a}, b={b}) DO JUMP')
        else:
            dprint(f'JT(a={a}, b={b}) DON\'T JUMP')

    def jump_if_false(self):
        self.ip += 1
        a = self.get_parameter_address()
        b = self.get_parameter_address()
        if not self.read_memory(a):
            self.ip = self.read_memory(b)
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
        self.memory[c] = int(self.read_memory(a) < self.read_memory(b))

    def equals(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        dprint(f'EQ(a={a}, b={b}, c={c})')
        self.memory[c] = int(self.read_memory(a) == self.read_memory(b))

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
        output = self.read_memory(self.get_parameter_address())
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
        self.memory[c] = self.read_memory(a) + self.read_memory(b)

    def mul(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        dprint(f'MUL(a={a}, b={b}, c={c})')
        self.memory[c] = self.read_memory(a) * self.read_memory(b)

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
        opcode = self.read_memory(self.ip) % 100
        self.parameter_modes += [int(d) for d in str(self.read_memory(self.ip))[:-2]]
        dprint(f'OPCODE: {opcode} ({self.opcodes.get(opcode).__name__}), PRM_MODES={self.parameter_modes!r}')
        self.opcodes.get(opcode)()


assert tuple(
    IntCode([109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99], deque()).run([])
) == (109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99)
assert len(str(IntCode([1102, 34915192, 34915192, 7, 4, 7, 99, 0], deque()).run([])[0])) == 16
assert IntCode([104, 1125899906842624, 99], deque()).run([])[0] == 1125899906842624

with open('day9_input.txt', 'r') as f:
    input_data = [int(x) for x in f.read().strip().split(',')]

print(f'BOOST KEYCODE: {IntCode(input_data, deque()).run([1])[0]}')
print(f'COORDINATES: {IntCode(input_data, deque()).run([2])[0]}')
