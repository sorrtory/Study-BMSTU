import string
import random

def get_string(length):
    s = ""
    for _ in range(length):
        s += random.choice(string.printable[:95])
    return s

def get_strings(length, number):
    l = []
    for _ in range(number):
        l.append(get_string(length))
    return l

def make_strings(length, number):
    for i in range(1, number+1):
        # print(f"{i}) {get_string(length)}")
        print(get_string(length))
