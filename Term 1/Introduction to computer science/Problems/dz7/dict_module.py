import re

def get_tokens(data):
    tokens = []
    lines = data.split("\n")
    for line in range(len(lines)):
        line_data = lines[line]
        tail = 1
        words = re.split("[ ,.!?\"]", line_data)
        for word in words:
            tokens.append((word, line+1, line_data.find(word) + tail))
            tail += line_data.find(word) + len(word)
            line_data = line_data[line_data.find(word) + len(word):]
    return tokens

def get_dictionary(data):
    dictionary = ["", " ", "\n"]
    for line in data.split("\n"):
        for word in re.split("[ ,.!?\"]", line):
            dictionary.append(word)
    return dictionary

def add_dictionary(word, dict):
    if not word in dict:
        dict.append(word)
    return dict
     
