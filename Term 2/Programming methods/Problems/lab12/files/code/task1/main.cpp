// Варианты заданий для программ, которые нужно разработать в ходе выполнения данной лабораторной работы, приведены в таблицах 1–7.  Каждая программа должна принимать через аргумент командной строки путь к каталогу, в котором располагаются подлежащие обработке файлы.

// Найти все файлы с расширением «md» в указанном каталоге, и в тексте каждого файла пронумеровать заголовки целыми числами. Изменённые файлы следует сохранить в текущем каталоге. Заголовки в формате MarkDown обозначаются с помощью «подчёркивания» последовательностью знаков «=» или «−».
// Например:

// Введение
// ========

// Работоспособность программы нужно проверить на наборе предварительно составленных MD-файлов.

#include <string>
#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>

using namespace std;


bool LineSuitableForHeader(string line)
{
    return line != "" && line.find("- ") == string::npos;
}

bool LineAfterHeader(string line)
{
    char mode = '!';
    bool out = true;
    for (auto &&i : line)
    {
        switch (i)
        {
        case '=':
            if (mode == '!' || mode == '=')
                mode = '=';
            else
                out = false;
            break;
        case '-':
            if (mode == '!' || mode == '-')
                mode = '-';
            else
                out = false;
            break;
        default:
            out = false;
            break;
        }
        if (!out)
            break;
    }

    return out;
}

void handleFile(filesystem::path path)
{
    cout << "Found file: " << filesystem::absolute(path) << endl;

    string line;
    vector<string> lines;
    fstream fileIN, fileOUT;
    fileIN.open(path, ios::in);
    fileOUT.open(path.filename(), ios::out);

    if (fileIN.is_open() && fileOUT.is_open())
    {
        size_t i = 0;
        int headerCount = 0;
        string lastLine = "";
        while (getline(fileIN, line))
        {

            lines.push_back(line);
            if (line != "" && i != 0 && LineAfterHeader(lines[i]) && LineSuitableForHeader(lines[i - 1]))
                fileOUT << ++headerCount << ". ";

            i += 1;
            if (lines.size() != 1)
                fileOUT << lastLine << endl;
            
            lastLine = line;
        }
        fileOUT << lastLine << endl;
    }
    fileIN.close();
    fileOUT.close();
}


int main(int argc, char const *argv[])
{
    if (argc == 1)
    {
        filesystem::path path = "./FullOfMD/";

        for (const auto &entry : std::filesystem::directory_iterator(path))
        {
            filesystem::path file = entry;
            if (file.extension() == ".md")
                handleFile(file);
        }
    }
    else
    {
        for (size_t i = 1; i < argc; i++)
        {
            if (!std::filesystem::is_directory(argv[i]))
            {
                cerr << "Это не папка!" << endl;
                exit(0);
            }
            
            for (const auto &entry : std::filesystem::directory_iterator(argv[i]))
            {
                filesystem::path file = entry;
                if (file.extension() == ".md")
                    handleFile(file);
            }
        }
    }
}
