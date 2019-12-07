INPUT_MAX = 99
DESIRED_VALUE = 19690720

def intcode(memory):
    ip = 0
    while ip < len(memory):
        if memory[ip] == 99:
            break
        else:
            a = memory[ip+1]
            b = memory[ip+2]
            c = memory[ip+3]
            if memory[ip] == 1:
                memory[c] = memory[a] + memory[b]
            elif memory[ip] == 2:
                memory[c] = memory[a] * memory[b]
        ip += 4
    return memory

def run_program(memory, noun, verb):
    memory[1] = noun
    memory[2] = verb
    return intcode(memory)[0]

def brute_force(memory, d):
    for noun in range(INPUT_MAX + 1):
        for verb in range(INPUT_MAX + 1):
            if d == run_program(memory[:], noun, verb):
                return 100 * noun + verb
    
memory = [1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,6,19,1,9,19,23,1,6,23,27,1,10,27,31,1,5,31,35,2,6,35,39,1,5,39,43,1,5,43,47,2,47,6,51,1,51,5,55,1,13,55,59,2,9,59,63,1,5,63,67,2,67,9,71,1,5,71,75,2,10,75,79,1,6,79,83,1,13,83,87,1,10,87,91,1,91,5,95,2,95,10,99,2,9,99,103,1,103,6,107,1,107,10,111,2,111,10,115,1,115,6,119,2,119,9,123,1,123,6,127,2,127,10,131,1,131,6,135,2,6,135,139,1,139,5,143,1,9,143,147,1,13,147,151,1,2,151,155,1,10,155,0,99,2,14,0,0]
print(f'FIRST TASK:  {run_program(memory[:], 12, 2)}')
print(f'SECOND TASK: {brute_force(memory, DESIRED_VALUE)}')
