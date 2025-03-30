/*
Вариант 19
Абсолютный путь к каталогу в файловой системе UNIX с операциями:
1. получение количества каталогов в пути;
2. получение ссылки на i-тый каталог в пути, считая от корня;
3. добавление имени каталога в конец пути;
4. получение количества файлов в каталоге (для этого требуется разобрать-
ся, как получить оглавление каталога).
*/

#include "implementation.cpp"

#include <string>
#include <iostream>
#include <filesystem>

PathToDir addPath(PathToDir &Pth, std::string path){
    return PathToDir(Pth.path + path);
}

int main()
{
    PathToDir Pth("/home/chinalap/");
    std::cout << "Number of dirs: " << Pth.getNumberOfDirsInPath() << std::endl;
    Pth.addDir("Документы");
    std::cout << "The forth dir: " << Pth.getDir(4) << std::endl;
    PathToDir Pth2 = Pth;
    std::cout << "Number of dirs: " << Pth2.getNumberOfDirsInPath() << std::endl;
    Pth = addPath(Pth2, "YIMP_labs/lab7/files/code/task2");
    std::cout << "Number of files: " << Pth.getNumberOfFiles() << std::endl;

}