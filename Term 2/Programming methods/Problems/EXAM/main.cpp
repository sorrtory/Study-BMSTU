#include <string>
#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <cctype>

using namespace std;

string strip(string line)
{
    string out = "";
    for (auto &&i : line)
    {
        if (i != ' ')
        {
            out += i;
        }
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
    fileOUT.open("ifs.txt", ios_base::app);
    if (fileIN.is_open() && fileOUT.is_open())
    {
        size_t i = 1;
        while (getline(fileIN, line))
        {
            line = strip(line);
            if (line.size() >= 4 && line[0] == 'i' && line[1] == 'f')
            {
                // line = line.erase(0, 2);
                // strip(line);
                // line.erase(0, 1);
                // for (size_t j = 0; j < line.size(); j++)
                // {
                //     if (line[j] == ')')
                //     {
                //         lines.push_back(ifData);
                //         break;
                //     } else
                //     {
                //         ifData += line[j];
                //     }

                // }
                fileOUT << "file: " << (string)path.filename() << " line:" << i << endl;
            }
            i += 1;
        }
    }

    for (auto &&i : lines)
    {
    }

    fileIN.close();
    fileOUT.close();
}

int main(int argc, char const *argv[])
{
    fstream fileOUT;
    fileOUT.open("ifs.txt", ios::out);
    fileOUT.close();
    if (argc == 1)
    {
        filesystem::path path = "./fullOfC/";

        for (const auto &entry : std::filesystem::directory_iterator(path))
        {
            filesystem::path file = entry;
            if (file.extension() == ".c")
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
                if (file.extension() == ".c")
                    handleFile(file);
            }
        }
    }
}
