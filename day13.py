# 0 is an empty tile. No game object appears in this tile.
# 1 is a wall tile. Walls are indestructible barriers.
# 2 is a block tile. Blocks can be broken by the ball.
# 3 is a horizontal paddle tile. The paddle is indestructible.
# 4 is a ball tile. The ball moves diagonally and bounces off objects.
from collections import deque
from intcode import IntCode, DequeIO, IO

IntCode.DEBUG = False
EMPTY, WALL, BLOCK, PADDLE, BALL = range(5)


class Display(IO):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [0] * width * height
        self.offset = 0

    def __len__(self):
        return self.width * self.height

    def __iter__(self):
        while True:
            yield self.data[self.offset]
            self.update_offset()

    def update_offset(self):
        self.offset = (self.offset + 1) % len(self)

    def add(self, item):
        self.data[self.offset] = item
        self.update_offset()

    def pop(self):
        ret = self.data[self.offset]
        self.update_offset()
        return ret

    def print(self):
        lines = zip(*((iter(self.data),) * self.width))
        print('\n'.join(''.join(str(c) for c in line) for line in lines))


class ArcadeCabinet:
    def __init__(self, code):
        # self.display = display
        self.code = code
        self.intcode = IntCode(code, input_buffer=DequeIO(), output_buffer=DequeIO())

        self.tiles = []
        self.score = 0

    def reset(self):
        self.score = 0
        self.intcode = IntCode(self.code, input_buffer=DequeIO(), output_buffer=DequeIO())

    def run_and_count_block_tiles(self):
        while not self.intcode.done:
            while not self.intcode.done and len(self.intcode.output_buffer) < 3:
                self.intcode.tick()
            if self.intcode.done:
                break
            self.tiles.append(tuple(self.intcode.output_buffer))
            self.intcode.output_buffer.clear()

        return sum(1 for x, y, tile_id in self.tiles if tile_id == 2)

    def run(self):
        self.intcode.memory[0] = 2
        inp = 0
        ball_x = 0
        paddle_x = 0
        tiles = {}
        while not self.intcode.done:
            out = self.intcode.run_until_out([], 3)
            if out is None:
                self.intcode.input_buffer.add(inp)
                continue

            x, y, tid = out

            if tid == BALL:
                ball_x = x
            elif tid == PADDLE:
                paddle_x = x

            if (x, y) == (-1, 0):
                self.score = tid
                if BLOCK not in tiles.values():
                    return self.score
            else:
                tiles[(x, y)] = tid

            if ball_x == paddle_x:
                inp = 0
            elif ball_x > paddle_x:
                inp = 1
            else:
                inp = -1

            # display([(k[0], k[1], tiles[k]) for k in tiles])


def display(tiles):
    print()
    tid_by_pos = {(x, y): tid for x, y, tid in tiles}
    for y in range(max(y for x, y, tile in tiles) + 1):
        line = []
        for x in range(max(x for x, y, tile in tiles) + 1):
            tid = tid_by_pos.get((x, y), '.')
            if tid == PADDLE:
                line.append('=')
            elif tid == BALL:
                line.append('O')
            elif tid == BLOCK:
                line.append('B')
            elif tid == WALL:
                line.append('#')
            else:
                line.append('.')
        print(''.join(line))


with open('day13_input.txt', 'r') as f:
    input_data = [int(c) for c in f.read().split(',')]

ac = ArcadeCabinet(input_data)
print(f'[PART 1] BLOCK TILES: {ac.run_and_count_block_tiles()}')

ac.reset()
ac.run()
print(f'[PART 2] SCORE: {ac.score}')
