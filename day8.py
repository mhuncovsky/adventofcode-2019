PART1_WIDTH = 25
PART1_HEIGHT = 6
COLOR_BLACK = '0'
COLOR_WHITE = '1'
COLOR_TRANSPARENT = '2'


def checksum(string, width, height):
    grouped_by_width = zip(*((iter(string),) * width * height))
    fewest_zeroes_line = min(grouped_by_width, key=lambda x: x.count('0'))

    return fewest_zeroes_line.count('1') * fewest_zeroes_line.count('2')


with open('day8_input.txt', 'r') as f:
    data = f.read().strip()

print(f'[PART 1] CHECKSUM: {checksum(data, PART1_WIDTH, PART1_HEIGHT)}')


def get_layers(string, width, height):
    return tuple(zip(*((iter(string),) * width * height)))


def combine_colors(colors):
    for color in colors:
        if color == COLOR_TRANSPARENT:
            continue
        else:
            return color
    return COLOR_TRANSPARENT


def combine_layers(layers):
    return tuple(combine_colors(colors) for colors in zip(*layers))


def print_image(image, width):
    int_image = (int(x) for x in image)
    for row in tuple(zip(*((iter(int_image),) * width))):
        print(''.join((' ', '#')[pixel] for pixel in row))


def solve(string, width, height):
    layers = get_layers(string, width, height)
    image = combine_layers(layers)
    return image


# EXAMPLE
assert solve('0222112222120000', 2, 2) == tuple('0110')

print('[PART 2] IMAGE:')
print_image(solve(data, PART1_WIDTH, PART1_HEIGHT), PART1_WIDTH)


