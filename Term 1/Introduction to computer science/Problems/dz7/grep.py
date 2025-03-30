#!/usr/bin/python3

import argparse
import os
import sys
import re


def find(line, pattern, line_number, args, file_name=None):
    line_raw = line
    highlight = ""

    if args.option_i:
        line = line.lower()
        pattern = pattern.lower()

    if args.option_e:
        for match in re.finditer(pattern, line):
            highlight += " " * (match.start() - len(highlight)) + "^" * (match.end() - match.start())
    else:
        if pattern in line:
            while pattern in line:
                i = line.find(pattern)
                highlight += " " * i + "^" * len(pattern)
                line = line[i+len(pattern):]

    
    if highlight != "":
        line_out = line_raw

        if args.option_n:
            line_out = f"{line_number}) {line_out}"
            highlight = " " * (len(str(line_number)) + 2) + highlight
        
        if file_name != None:
            line_out = f"{file_name}: {line_out}"
            while line_out[-1] == "\n":
                line_out = line_out[:-1]
            highlight = " " * (len(str(file_name)) + 2) + highlight

        print(line_out)
        print(highlight)
        
        return 1
    else:
        return 0
        
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="grep [options] pattern [files]")
    parser.add_argument("-e", help="регулярное выражение", dest="option_e", action="store_true")
    parser.add_argument("-i", action="store_true", help="игнорировать различие регистра", dest="option_i")
    parser.add_argument("-m", help="остановиться после указанного ЧИСЛА совпавших строк", type = int, dest="option_m")
    parser.add_argument("-n", action="store_true", help="выводить номер строки", dest="option_n")
    parser.add_argument("pattern", help="шаблон поиска")
    parser.add_argument("files", help="список файлов", nargs="*", default=None) 

    args = parser.parse_args()

    # grep [options] pattern [files]

    # -e регулярное выражение
    # -i игнорировать различие регистра
    # -m остановиться после указанного ЧИСЛА совпавших строк
    # -n Выводить номер строки

    if len(args.files) != 0:
        count = 0
        for file in args.files:
            if not (os.path.isfile(file) and os.access(file, os.R_OK)):
                print("Проблемы с указанными файлами", file=sys.stderr)
                sys.exit(1)
            else:
                with open(file, "r") as f:
                    lines = f.readlines()

                    for i in range(len(lines)):
                        if args.option_m:
                            count += find(lines[i], args.pattern, i + 1, args, file)
                            if count == args.option_m:
                                break
                        else:
                            find(lines[i], args.pattern, i + 1, args, file)
                        
                        
    else:
        try:
            count = 0
            i = 0
            while 1:
                line = input()
                if args.option_m:
                    count += find(line, args.pattern, i + 1, args)
                    if count == args.option_m:
                        break
                else:
                    find(line, args.pattern, i + 1, args)
                i += 1
                
        except (EOFError, KeyboardInterrupt):
            print()
            
            

    

    


