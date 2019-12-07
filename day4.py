# Your puzzle input is 206938-679128.
import re

codes = list(str(x) for x in range(206938, 679128 + 1))
pairs = ('00', '11', '22', '33', '44', '55', '66', '77', '88', '99')

def has_pairs(string):
    for pair in pairs:
        if pair in string:
            return True
    return False

def never_decreases(string):
    digits = [int(x) for x in string]
    return digits == sorted(digits)   

def has_pairs_but_not_part_of_larger_group(string):
    for pair in pairs:
        if pair in string:
            try:
                if string[string.index(pair)+2] != pair[0]:
                    return True
            except IndexError:
                return True
    return False

def solve_1(codes):
    return list(filter(lambda x: has_pairs(x) and never_decreases(x), codes))


codes_matching_part_1 = solve_1(codes)
codes_matching_part_2 = list(filter(has_pairs_but_not_part_of_larger_group, codes_matching_part_1))

print(f'PASSWORDS THAT MEET THE CRITERIA OF PART 1: {len(codes_matching_part_1)}')
print(f'PASSWORDS THAT MEET THE CRITERIA OF PART 2: {len(codes_matching_part_2)}')
