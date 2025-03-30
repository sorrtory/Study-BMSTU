#include <iostream>
#include <vector>
#include <set>
#include <unistd.h>
#include <algorithm>
#include <unordered_map>

using namespace std;

template <typename INTYPE, typename OUTTYPE>
class MealyMachine
{

public:
    vector<vector<INTYPE>> D;  // переходы
    vector<vector<OUTTYPE>> F; // выходы
    int n, m;                  // количество состояний автомата n, размер входного алфавита m,

    MealyMachine(int n, int m)
    {
        vector<vector<INTYPE>> D(n, vector<INTYPE>(m));
        this->D = D;

        vector<vector<OUTTYPE>> F(n, vector<OUTTYPE>(m));
        this->F = F;

        this->n = n;
        this->m = m;
    }

    void graphviz()
    {
        cout << "digraph {\n\trankdir = LR\n";

        for (size_t j = 0; j < n; j++)
            for (size_t i = 0; i < m; i++)
                cout << "\t" << j << " -> " << D[j][i] << " [label = \"" << (char)('a' + i) << "(" << F[j][i] << ")\"]\n";
        cout << "}\n";
    }
};

string getTail(const vector<string> &path, int qInPathIndex)
{

    string tail = "";
    for (auto i = qInPathIndex; i < path.size(); i++)
        if (path[i] != "-")
            tail += path[i];

    return tail;
}

string getWay(const vector<string> &way)
{
    string s = "";
    for (auto &&i : way)
        s += i + "|";
    return s;
}

int rfind(const vector<string> &myWay, string q)
{
    for (int i = myWay.size() - 1; i >= 0; i--)
        if (myWay[i] == q)
            return i;
    return -1;
}

void dfs(int q, const MealyMachine<int, string> &MM, vector<string> path, string pathNoMinus, vector<string> myWay, const int maxSize, set<string> possibleStringsInVertex[], unordered_map<string, bool> &visited)
{
    // static int count = 0;
    // count += 1;
    // cout << count << endl;
    cout << q << ": ";
    for (int i = 0; i < MM.n; i++)
    {
        cout << "|";
        for (auto &&j : possibleStringsInVertex[i])
        {
            cout << j << ";";
        }
        cout << "| ";
    }
    cout << endl;
    // cout << "path: ";
    // for (auto &&k : path)
    // {
    //     cout << k;
    // }
    // cout << " way: ";

    // for (auto &&k : myWay)
    // {
    //     cout << k;
    // }
    cout << endl;
    string sWay = getWay(myWay);
    if (pathNoMinus.size() > maxSize)
    {
        return;
    }

    possibleStringsInVertex[q].insert(pathNoMinus);

    int qInPathIndex = rfind(myWay, to_string(q));

    visited[sWay] = true;

    vector<string> myWay2(myWay);
    myWay2.push_back(to_string(q));

    // usleep(500);
    for (int i = 0; i < MM.m; i++)
    {
        vector<string> vect2(path);
        vect2.push_back(MM.F[q][i]);

        if (pathNoMinus.size() + 1 <= maxSize)
        {
            if (MM.F[q][i] == "-")
            {

                if (MM.D[q][i] != q) // prevent self λ
                {

                    if (qInPathIndex != -1) // update pathes of q λ descendant, if already visited q
                    {
                        // if (q == 4)
                        // {
                        //     cout << "akfrjnvfrkjfkvkdkdkvf";
                        // }
                        
                        string tail = getTail(path, qInPathIndex);
                        for (string base : possibleStringsInVertex[MM.D[q][i]])
                        {
                            if (base == "" || tail == "")
                            {
                                continue;
                            }

                            string based = base + tail;
                            while (based.size() <= maxSize)
                            {
                                cout << "ADD" << based << " by" << q << " with " << MM.F[q][i] << " to " << MM.D[q][i] << " base: "  << base << " tail: " << tail << "and path: ";
                                for (auto &&j : path)
                                {
                                    cout << j;
                                }
                                cout << " and way: ";
                                for (auto &&j : myWay)
                                {
                                    cout << j;
                                }
                                cout << endl;
                                possibleStringsInVertex[q].insert(based);
                                possibleStringsInVertex[MM.D[q][i]].insert(based);
                                based += tail;
                            }
                        }
                        // return;
                    }
                    else
                    {

                        // if (path.size() + 1 <= maxSize)
                        // {
                        for (string possiblePath : possibleStringsInVertex[q])
                        {
                            if (possibleStringsInVertex[MM.D[q][i]].find(possiblePath) == possibleStringsInVertex[MM.D[q][i]].end() && !(visited.count(sWay + to_string(q))))
                            {
                                // cout << "ME";
                                dfs(MM.D[q][i], MM, vect2, possiblePath, myWay2, maxSize, possibleStringsInVertex, visited);
                            }
                        }
                        // }
                    }
                }
            }
            else
            {
                for (string possiblePath : possibleStringsInVertex[q])
                {
                    if (possiblePath.size() + 1 <= maxSize)
                    {
                        if (possibleStringsInVertex[MM.D[q][i]].find(possiblePath + MM.F[q][i]) == possibleStringsInVertex[MM.D[q][i]].end() && !(visited.count(sWay + to_string(q))))
                        {
                            dfs(MM.D[q][i], MM, vect2, possiblePath + MM.F[q][i], myWay2, maxSize, possibleStringsInVertex, visited);
                        }
                    }
                }
            }
        }
    }
}

int main(int argc, char const *argv[])
{
    int N = 10, M, q0;
    string space;
    cin >> N;

    getline(cin, space);
    MealyMachine<int, string> MM(N, 2);
    for (auto &&i : MM.D)
        for (auto &&j : i)
            cin >> j;

    getline(cin, space);
    for (auto &&i : MM.F)
        for (auto &&j : i)
            cin >> j;

    getline(cin, space);

    cin >> q0;
    cin >> M;
    ////////////////////////////////////////
    MM.graphviz();

    set<string> possibleStringsInVertex[N];
    vector<string> path;
    // string pathNoMinus = "";
    vector<string> myWay;
    unordered_map<string, bool> visited;
    dfs(q0, MM, path, "", myWay, M, possibleStringsInVertex, visited);

    set<string> out;
    for (auto &&st : possibleStringsInVertex)
        for (auto &&i : st)
            if (i != "")
                out.insert(i);

    for (auto &&i : out)
        cout << i << " ";
    cout << endl;
    return 0;
}
