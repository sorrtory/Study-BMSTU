def generate_words(states, transitions, outputs, start_state, max_length):
    result = set()
    
    def dfs(current_state, current_word, length):
        if length > max_length:
            return
        if current_word:
            result.add(current_word)
        for input_signal in range(len(transitions[0])):
            next_state = transitions[current_state][input_signal]
            output_signal = outputs[current_state][input_signal]
            if output_signal != '-':
                dfs(next_state, current_word + output_signal, length + 1)
            else:
                dfs(next_state, current_word, length + 1)
    
    dfs(start_state, '', 0)
    return sorted(result)

if __name__ == "__main__":
    import sys
    input = sys.stdin.read
    data = input().split()

    index = 0
    N = int(data[index])
    index += 1
    
    transitions = []
    for _ in range(N):
        transitions.append([int(x) for x in data[index:index+2]])
        index += 2
    
    outputs = []
    for _ in range(N):
        outputs.append([x if x != '-' else '-' for x in data[index:index+2]])
        index += 2
    
    q0 = int(data[index])
    index += 1
    M = int(data[index])
    
    words = generate_words(N, transitions, outputs, q0, M)
    print(" ".join(words))
