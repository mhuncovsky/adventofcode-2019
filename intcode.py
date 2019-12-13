import abc
from collections import deque


class IO(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __len__(self):
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass

    @abc.abstractmethod
    def add(self, item):
        pass

    @abc.abstractmethod
    def pop(self):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def extend(self, iterable):
        pass


class DequeIO(IO):

    def __init__(self, input_values=None):
        self.deque = deque() if input_values is None else deque(input_values)

    def __len__(self):
        return len(self.deque)

    def __iter__(self):
        return iter(self.deque)

    def add(self, item):
        self.deque.append(item)

    def pop(self):
        return self.deque.popleft()

    def clear(self):
        self.deque.clear()

    def extend(self, iterable):
        self.deque.extend(iterable)


class IntCode:
    DEBUG = False

    @classmethod
    def dprint(cls, *args, **kwargs):
        if cls.DEBUG:
            print(*args, **kwargs)

    def __init__(self, memory, input_buffer: IO = None, output_buffer: IO = None):
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
        self.input_buffer = input_buffer if input_buffer is not None else DequeIO()
        self.output_buffer = output_buffer if output_buffer is not None else DequeIO()
        self.relative_base = 0
        self.last_instruction_address = None
        self.done = False
        self.waiting_for_input = False

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
        self.dprint(f'GET PARAMETER ADDRESS: mode={parameter_mode}, memory_value={self.read_memory(self.ip)}, address={address}')
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
            self.dprint(f'JT(a={a}, b={b}) DO JUMP')
        else:
            self.dprint(f'JT(a={a}, b={b}) DON\'T JUMP')

    def jump_if_false(self):
        self.ip += 1
        a = self.get_parameter_address()
        b = self.get_parameter_address()
        if not self.read_memory(a):
            self.ip = self.read_memory(b)
            self.dprint(f'JF(a={a}, b={b}) DO JUMP')
        else:
            self.dprint(f'JF(a={a}, b={b}) DON\'T JUMP')

    def less_than(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        self.dprint(f'LT(a={a}, b={b}, c={c})')
        self.memory[c] = int(self.read_memory(a) < self.read_memory(b))

    def equals(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        self.dprint(f'EQ(a={a}, b={b}, c={c})')
        self.memory[c] = int(self.read_memory(a) == self.read_memory(b))

    def input(self):
        self.last_instruction_address = self.ip
        self.ip += 1
        inp = self.get_input()
        if inp is not None:
            self.memory[self.get_parameter_address()] = inp
            self.last_instruction_address = None
            self.waiting_for_input = False
        else:
            self.waiting_for_input = True

    def get_input(self):
        if len(self.input_buffer):
            return self.input_buffer.pop()
        return None

    def output(self):
        self.ip += 1
        output = self.read_memory(self.get_parameter_address())
        self.do_output(output)
        self.dprint(f'OUTPUT: {output}')

    def do_output(self, output):
        self.output_buffer.add(output)

    def add(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        self.dprint(f'ADD(a={a}, b={b}, c={c})')
        self.memory[c] = self.read_memory(a) + self.read_memory(b)

    def mul(self):
        self.ip += 1
        a, b, c = (
            self.get_parameter_address(),
            self.get_parameter_address(),
            self.get_parameter_address(),
        )
        self.dprint(f'MUL(a={a}, b={b}, c={c})')
        self.memory[c] = self.read_memory(a) * self.read_memory(b)

    def halt(self):
        self.running = False
        self.done = True

    def run_program(self, noun, verb):
        self.memory[1] = noun
        self.memory[2] = verb
        return self.run()

    def run(self, inputs=None):
        if inputs is not None:
            self.input_buffer.extend(inputs)
        self.running = True
        while self.running:
            self.tick()
        out = tuple(self.output_buffer)
        self.output_buffer.clear()
        return out

    def run_until_out(self, inputs=None, n_out=1):
        if inputs is not None:
            self.input_buffer.extend(inputs)
        while len(self.output_buffer) < n_out:
            self.tick()
            if self.waiting_for_input:
                break
        if self.waiting_for_input:
            out = None
        else:
            out = tuple(self.output_buffer) if n_out > 1 else self.output_buffer.pop()
            self.output_buffer.clear()
        return out

    def tick(self):
        if self.last_instruction_address is not None:
            self.ip = self.last_instruction_address
        self.dprint(f'INSTRUCTION POINTER: {self.ip}')
        opcode = self.read_memory(self.ip) % 100
        self.parameter_modes += [int(d) for d in str(self.read_memory(self.ip))[:-2]]
        self.dprint(f'OPCODE: {opcode} ({self.opcodes.get(opcode).__name__}), PRM_MODES={self.parameter_modes!r}')
        self.opcodes.get(opcode)()
