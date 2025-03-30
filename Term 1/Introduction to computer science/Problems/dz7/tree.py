#!/usr/bin/python3
import os
import sys

def get_args_2(l):
    path = os.path.dirname(__file__)
    dirs_mode = False
    out_mode = False
    out_file = "./tree.out"
    out_mode1 = False
    i = 1
    while len(l) != i:
        
        if l[i] == "-d":
            dirs_mode = True
        elif l[i] == "-o":
            out_mode = True  
            out_mode1 = True 
        else:
            if out_mode1:
                out_file = l[i]
                out_mode1 = False
            else:
                path = l[i]
        i += 1
    
    return path, dirs_mode, out_mode, out_file
    

def get_args():
    if len(sys.argv) == 1:
        print("Путь не указан, путь заменен на текущую папку")
        return os.path.dirname(__file__), False, False, "./tree.out"
    else:
        return get_args_2(sys.argv)

    
        
def print_str(name, level, printing_file=False, out_mode=False):
    if printing_file:
        str = " |--- " * (level-1) + " |- "
    else:
        str = " |--- " * level 
    
    if out_mode:
        out_mode.write(str + name + "\n")
    else:
        print(str + name)


if __name__ == "__main__":
    path, dirs_mode, out_mode, out_file = get_args()
    if path[-1] == "/":
        path = path[:-1]

    if not (os.path.exists(path) and os.path.isdir(path) and os.access(path, os.R_OK)):
        print("Неправильные аргументы!")
    else:
        if out_mode:
            out_mode = open(out_file, "w")

        level = 0
        level_start = path.count("/")
        count_files = 0
        count_dirs = 0
        print_str(path, level, False, out_mode)

        for adress, dirs, files in os.walk(path):
            level = adress.count("/") - level_start 

            count_dirs += len(dirs)
            count_files += len(files)

            # Вывод названия текущей папки 
            if level != 0:
                # if not dirs_mode:  # Вывод отступа
                #     print_str("", level, False, out_mode)
                print_str(os.path.basename(adress), level, False, out_mode)

            # Вывод названий файлов в текущей папке
            if len(files) > 0 and not dirs_mode:
                for j in sorted(files):
                    print_str(j, level+1, True, out_mode)
            
                    
        papka_tail = "s"
        if count_dirs == 1:
            papka_tail = ""
        file_tail = "s"
        if count_files == 1:
            file_tail = ""
        if dirs_mode:
            print_str(f"\n{count_dirs} dir{papka_tail}", 0, False, out_mode)
        else:
            print_str(f"\n{count_dirs} dir{papka_tail}, {count_files} file{file_tail}", 0, False, out_mode)
            
        if out_mode:
            out_mode.close()

