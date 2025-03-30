#ifndef DECLARATION_H
#define DECLARATION_H
#include <iostream>
#include <filesystem>
#include <string>
#include <algorithm>
class PathToDir
{
    friend PathToDir addPath(PathToDir &Pth, std::string path);
private:
    std::string path;
    int dirsNumber;
    std::string *dirs;

public:
    PathToDir(std::string path); // Конструктор
    PathToDir(const PathToDir& pth); // Конструктор копирования
    virtual ~PathToDir(); // Деструктор
    PathToDir& operator=(const PathToDir& counter); // Оператор присваивания

    int getNumberOfDirsInPath(); // получение количества каталогов в пути; 
    std::string& getDir(int k); // получение ссылки на i-тый каталог в пути, считая от корня; 
    void addDir(std::string dirName); // добавление имени каталога в конец пути;
    int getNumberOfFiles(); // получение количества файлов в каталоге (для этого требуется разобраться, как получить оглавление каталога). 

};


#endif
