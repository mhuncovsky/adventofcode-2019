import itertools
from collections import deque

DEBUG = False
DEBUG_PAINT = False
STEP = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def dp(*args, **kwargs):
    if DEBUG_PAINT:
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


UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_VECTOR = [UP, RIGHT, DOWN, LEFT]
DIRECTION_NAME = ['UP', 'RIGHT', 'DOWN', 'LEFT']


class PaintBot:
    def __init__(self, intcode: IntCode):
        self.intcode = intcode
        self.position = (0, 0)
        self.direction = 0
        self.black_panels = set()
        self.white_panels = set()
        self.painted_panels = set()

    def turn_left(self):
        self.direction = 3 if self.direction == 0 else self.direction - 1

    def turn_right(self):
        self.direction = (self.direction + 1) % 4

    def current_tile_color(self):
        if self.position in self.white_panels:
            return 1
        if self.position in self.black_panels:
            return 0
        self.black_panels.add(self.position)
        return 0

    def paint_white(self):
        try:
            self.black_panels.remove(self.position)
        except KeyError:
            pass
        self.white_panels.add(self.position)
        dp(f'PAINT {self.position[0]},{self.position[1]} WHITE')

    def paint_black(self):
        try:
            self.white_panels.remove(self.position)
        except KeyError:
            pass
        self.black_panels.add(self.position)
        dp(f'PAINT {self.position[0]},{self.position[1]} BLACK')

    def move(self):
        x, y = self.position
        dx, dy = DIRECTION_VECTOR[self.direction]
        self.position = (x+dx, y+dy)
        dp(f'MOVE {DIRECTION_NAME[self.direction]} {x},{y} --> {x+dx},{y+dy}')

    def step(self):
        self.intcode.input_buffer.append(self.current_tile_color())

        while not self.intcode.done and not len(self.intcode.output_buffer):
            self.intcode.tick()

        if len(self.intcode.output_buffer):
            color = self.intcode.output_buffer.popleft()
            dp(f'[COLOR] OUTPUT: {color}')
            self.painted_panels.add(self.position)
            if color:
                self.paint_white()
            else:
                self.paint_black()

        while not self.intcode.done and not len(self.intcode.output_buffer):
            self.intcode.tick()

        if len(self.intcode.output_buffer):
            move = self.intcode.output_buffer.popleft()
            dp(f'[MOVE] OUTPUT: {move}')
            if move:
                self.turn_right()
            else:
                self.turn_left()
            self.move()

    def run(self):
        while not self.intcode.done:
            self.step()
            if STEP:
                input()


with open('day11_input.txt', 'r') as f:
    input_data = [int(c) for c in f.read().split(',')]

ic = IntCode(memory=input_data, input_buffer=deque())
bot = PaintBot(ic)
bot.run()

print(f'PAINTED AT LEAST ONCE: {len(bot.painted_panels)}')