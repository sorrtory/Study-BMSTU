#!/usr/bin/python3 

import argparse
import os
import sys
import dict_module

def print_table(data):
    mx = [len(str(i)) for i in data[0][0]]
    for file in data:
        for token in file:
            for i in range(len(token)):
                mx[i] = max(mx[i], len(str(token[i])))
    for file in data:
        for mistake in file:
            if len(mistake) == 3:
                line = f"{mistake[1]:>{mx[1]}}, {mistake[2]:>{mx[2]}}\t{mistake[0]:>{mx[0]}}"
            else:
                line = f"{mistake[3]:>{mx[3]}}: {mistake[1]:>{mx[1]}}, {mistake[2]:>{mx[2]}}\t{mistake[0]:>{mx[0]}}"
            print(line)

def find_bad_words(tokens, dictionary, file=None):
    out = []
    for token in tokens:
        if token[0] not in dictionary:
            if file:
                out.append([*token, file])
            else:
                out.append(token)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="./speller.py [СЛОВАРЬ] [ФАЙЛ]…  или [ТЕКСТ] | ./speller.py [ФАЙЛ]… " )

    pipemode = False
    if sys.stdin.isatty():
        parser.add_argument("dictionary", help="словарь")
    else:
        pipemode = True

    parser.add_argument("files", help="список файлов", nargs="+", default=None)

    args = parser.parse_args()


    dictionary = []
    if pipemode:
        dictionary = dict_module.get_dictionary(sys.stdin.read())
    else:
        with open(args.dictionary, "r") as f:
            dictionary = dict_module.get_dictionary(f.read())
    
    data = []
    if len(args.files) > 1:
        
        for file in args.files:
            if not (os.path.isfile(file) and os.access(file, os.R_OK)):
                print("Проблемы с файлом:", file, file=sys.stderr)
            else:
                with open(file, "r") as f:
                    data.append(find_bad_words(dict_module.get_tokens(f.read()), dictionary, file))
    else:
        file = args.files[0]
        if not (os.path.isfile(file) and os.access(file, os.R_OK)):
                print("Проблемы с файлом:", file, file=sys.stderr)
        else:
            with open(file, "r") as f:
                data.append(find_bad_words(dict_module.get_tokens(f.read()), dictionary))

    print_table(data)
               
