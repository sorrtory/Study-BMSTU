// Найти все файлы с расширением «html» в указанном каталоге, для каждого файла построить три множества заголовков типа h1, h2 и h3 и сохранить объединённые множества заголовков разного типа из всех файлов в файлах h1.txt, h2.txt и h3.txt в текущем каталоге. Каждый заголовок в сформированном файле должен располагаться в отдельной строке, для чего может потребоваться удаление из заголовка символов перевода строки. Кроме того, заголовки должны быть отсортированы лексикографически. Заголовки в HTML-файле задаются тегами «h1», «h2» и «h3».
// Например:

// <h1>Введение</h1>

// Работоспособность программы нужно проверить на наборе HTML-файлов, загруженных из интернета.

#include <string>
#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <cctype>
#include <algorithm>

using namespace std;
vector<string> h1;
vector<string> h2;
vector<string> h3;

// // Comparator Function
// bool myCmp(string s1, string s2)
// {

//     // If size of numeric strings
//     // are same the put lowest value
//     // first
//     if (s1.size() == s2.size()) {
//         return s1 < s2;
//     }

//     // If size is not same put the
//     // numeric string with less
//     // number of digits first
//     else {
//         return s1.size() < s2.size();
//     }
// }

bool stringCmp(string s1, string s2)
{
    if (s1.size() != s2.size())
        return s1.size() < s2.size();
    else
    {
        for (size_t i = 0; i < s1.size(); i++)
        {
            if (s1[i] < s2[i])
                return true;
            if (s1[i] > s2[i])
                return false;
        }
        return true;
    }
}
void writeHeaders()
{
    sort(h1.begin(), h1.end(), stringCmp);
    sort(h2.begin(), h2.end(), stringCmp);
    sort(h3.begin(), h3.end(), stringCmp);

    fstream fileH1, fileH2, fileH3;
    fileH1.open("h1.txt", ios::out);
    fileH2.open("h2.txt", ios::out);
    fileH3.open("h3.txt", ios::out);
    if (fileH1.is_open() && fileH2.is_open() && fileH3.is_open())
    {
        for (auto &&i : h1)
            fileH1 << i << endl;
        for (auto &&i : h2)
            fileH2 << i << endl;
        for (auto &&i : h3)
            fileH3 << i << endl;
    }
    fileH1.close();
    fileH2.close();
    fileH3.close();
}

void handleFile(filesystem::path path)
{
    cout << "Found file: " << filesystem::absolute(path) << endl;

    string line;
    fstream fileIN;
    fileIN.open(path, ios::in);

    if (fileIN.is_open())
    {
        bool inChevrons = false;
        int headerType = 0;
        string chevronsContent = "";
        while (getline(fileIN, line))
        {
            for (auto &&i : line)
            {

                switch (i)
                {
                case '<':
                    inChevrons = true;
                    break;
                case '>':
                    inChevrons = false;
                    if (chevronsContent == "/h1")
                        headerType = 0;
                    if (chevronsContent == "/h2")
                        headerType = 0;
                    if (chevronsContent == "/h3")
                        headerType = 0;

                    if (chevronsContent == "h1")
                    {
                        headerType = 1;
                        h1.push_back("");
                    }

                    if (chevronsContent == "h2")
                    {
                        headerType = 2;
                        h2.push_back("");
                    }
                    if (chevronsContent == "h3")
                    {
                        headerType = 3;
                        h3.push_back("");
                    }

                    chevronsContent = "";
                    break;
                default:
                    if (inChevrons)
                        chevronsContent += tolower(i);
                    else
                    {
                        if (headerType == 1)
                            h1.at(h1.size() - 1) += i;
                        if (headerType == 2)
                            h2.at(h2.size() - 1) += i;
                        if (headerType == 3)
                            h3.at(h3.size() - 1) += i;
                    }
                    break;
                }
            }
        }
    }
    fileIN.close();
}

int main(int argc, char const *argv[])
{
    if (argc == 1)
    {
        filesystem::path path = "./FullOfHTML/";
        for (const auto &entry : std::filesystem::directory_iterator(path))
        {
            filesystem::path file = entry;
            if (file.extension() == ".html")
                handleFile(file);
        }
        writeHeaders();
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
                if (file.extension() == ".html")
                    handleFile(file);
            }
            writeHeaders();
        }
    }
}