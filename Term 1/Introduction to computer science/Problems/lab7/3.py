#!/usr/bin/python3

import sys
from stringthings import make_strings


def check_params():
    return len(sys.argv) == 3 and sys.argv[1].isdigit() and sys.argv[2].isdigit()

if __name__ == "__main__":
    # Можно заполнять файлы тестовыми данными
    # make_strings(100, 10)

    if check_params():
        make_strings(int(sys.argv[1]), int(sys.argv[2]))
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "-e":
            print("./3.py 10 10")
        else:
            print("Переданы неверные параметры!")
    
