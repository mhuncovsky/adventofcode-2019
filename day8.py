PART1_WIDTH = 25
PART1_HEIGHT = 6


def solve(string, width, height):
    grouped_by_width = zip(*((iter(string),) * width * height))
    fewest_zeroes_line = min(grouped_by_width, key=lambda x: x.count('0'))

    return fewest_zeroes_line.count('1') * fewest_zeroes_line.count('2')


with open('day8_input.txt', 'r') as f:
    data = f.read().strip()

print(f'PART 1: {solve(data, PART1_WIDTH, PART1_HEIGHT)}')
