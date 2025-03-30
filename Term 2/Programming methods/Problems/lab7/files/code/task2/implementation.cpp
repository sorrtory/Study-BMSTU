#include "declaration.h"
PathToDir::PathToDir(std::string pth){
    if (pth.back() != '/')
    {
        pth += '/';
    }
    path = pth;

    dirsNumber = std::count(path.begin(), path.end(), '/');
    dirs = new std::string[dirsNumber];

    dirs[0] = "/";
    pth = pth.substr(1);
    size_t pos = 0;
    int i = 1;
    while ((pos = pth.find('/')) != std::string::npos) {
        dirs[i] = pth.substr(0, pos);
        pth.erase(0, pos + 1);
        i += 1;
    }
}
PathToDir::PathToDir(const PathToDir &Pth){
    path = Pth.path;
    dirsNumber = Pth.dirsNumber;
    std::string *dirs_new = new std::string[Pth.dirsNumber];
    for (size_t i = 0; i < dirsNumber; i++)
    {
        dirs_new[i] = Pth.dirs[i];
    }
    dirs = dirs_new;
}
PathToDir::~PathToDir(){
    delete[] dirs;
    std::cout << "PathToDir was deleted" << std::endl;
}

PathToDir& PathToDir::operator=(const PathToDir& Pth)
{
    path = Pth.path;
    dirsNumber = Pth.dirsNumber;
    std::string *dirs_new = new std::string[Pth.dirsNumber];
    for (size_t i = 0; i < dirsNumber; i++)
    {
        dirs_new[i] = Pth.dirs[i];
    }
    dirs = dirs_new;
    return *this;
}

int PathToDir::getNumberOfDirsInPath(){
    return dirsNumber;
} 

std::string& PathToDir::getDir(int k){
    return *(dirs + k - 1);
}

void PathToDir::addDir(std::string dirName){
    *this = PathToDir(path + dirName + "/");
}

int PathToDir::getNumberOfFiles(){
    int counter = 0;
    for (const auto & entry : std::filesystem::directory_iterator(path)){
        if (!entry.is_directory()){
            counter += 1;
        }
    }
    return counter;
}