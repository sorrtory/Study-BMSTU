#!/usr/bin/python3 
import argparse
import os
import sys
import re

def wc(text, args, file_name=None):
    data = []
    data.append(text.count("\n"))
    data.append(len([i for i in re.split("\s+", text) if i != ""]))
    data.append(len(text.encode("utf-8")))
    data.append(len(text))

    
    out = []

    if args.option_l:
        out.append(data[0])
    if args.option_w:
        out.append(data[1])
    if args.option_c:
        out.append(data[2])
    if args.option_m:
        out.append(data[3])

    if len(out) == 0:
        out = data[:3]
    
    if file_name:
        return [*[str(i) for i in out], file_name]
    else:
        return [str(i) for i in out]



def print_table(data):
    igogo = [i for i in data[0][:-1]]
    mx = [len(str(i)) for i in data[0]]
    for x in data[1:]:
        for i in range(len(x)):
            if i != len(x) - 1:
                igogo[i] = str(int(igogo[i]) + int(x[i]))
            mx[i] = max(mx[i], len(str(x[i])))
    
    igogo.append("итого")
    if len(data) != 1:
        mx[i] = max(mx[i], len("игого"))
        data = [*data, igogo]

    for x in data:
        line = ""
        for i in range(len(x)):
            line += " " + x[i] + " " * (mx[i] - len(x[i]))
        print(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="wc [ПАРАМЕТР]… [ФАЙЛ]…")
    parser.add_argument("-c", help="напечатать количество байт", dest="option_c", action="store_true")
    parser.add_argument("-m", help="напечатать количество символов", dest="option_m", action="store_true")
    parser.add_argument("-l", help="напечатать количество новых строк", dest="option_l", action="store_true")
    parser.add_argument("-w", help="напечатать количество слов", dest="option_w", action="store_true")
    parser.add_argument("files", help="список файлов", nargs="*", default=None) 

    args = parser.parse_args()
    
    # Использование: wc [ПАРАМЕТР]… [ФАЙЛ]…
    # Печатает число символов новой строки, слов и байт для каждого ФАЙЛА и
    # итоговую строку, если было задано несколько ФАЙЛОВ. Словом считается
    # последовательность символов ненулевой длины, отделённая пробельным символом.

    # Если ФАЙЛ не задан или задан как -, читает стандартный ввод.
    #   -c, --bytes            напечатать количество байт
    #   -m, --chars            напечатать количество символов
    #   -l, --lines            напечатать количество новых строк
    #   -w, --words            напечатать количество слов


    if len(args.files) != 0:
        data = []
        
        for file in args.files:
            if not (os.path.isfile(file) and os.access(file, os.R_OK)):
                print("Проблемы с указанными файлами:", file, file=sys.stderr)
                # sys.exit(1)
            else:
                with open(file, "r") as f:
                    data.append(wc(f.read(), args, file))
        print_table(data)
                   
    else:
        data = ""
        try:
            while 1:
                data += input() + "\n"
        except EOFError:
            print("\t".join(wc(data, args)))
        except KeyboardInterrupt:
            pass
            
        
