#include <iostream>
#include <vector>
#include <set>
#include <unistd.h>
#include <algorithm>
#include <unordered_map>
#include <queue>

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

string substractPathes(string longerPath, string shorterPath)
{
    // cout << longerPath << " and  " << shorterPath << endl;
    if (longerPath == "")
    {
        return "";
    }

    return longerPath.substr(shorterPath.size());
}

void printPath(vector<set<string>> pth)
{
    cout << "path: ";
    int q = 0;
    for (auto &&i : pth)
    {
        cout << q << "( ";
        for (auto &&j : i)
        {
            cout << "|" << j << "|;";
        }
        cout << " )";
        q++;
    }
    cout << endl;
}

int getMinPathSize(set<string> pth)
{
    auto m = ++pth.begin();
    return (*m).size();
}

vector<int> rightOrderToBFS(int currentNode, int des1, int des2, const vector<set<string>> &pathNominus)
{
    // begin from visited and self cycle
    vector<int> out;
    if (des1 == currentNode)
    {
        out = {0, 1};
    }
    else if (des2 == currentNode)
    {
        out = {1, 0};
    }
    else if (pathNominus[des1].size() != 1 && pathNominus[des2].size() != 1)
    {
        if (getMinPathSize(pathNominus[des1]) >= getMinPathSize(pathNominus[des2]))
        {
            out = {1, 0};
        }
        else
        {
            out = {0, 1};
        }
    }
    else if (pathNominus[des1].size() != 1)
    {
        out = {0, 1};
    }
    else if (pathNominus[des2].size() != 1)
    {
        out = {1, 0};
    }
    else
    {
        out = {0, 1};
    }

    return out;
}

void dfs(int current, int to, string path, vector<bool> &used, set<string> &out, const MealyMachine<int, string> &MM)
{
    if (current == to)
    {
        out.insert(path);
    }
    else
    {
        used[current] = true;
        for (int i = 0; i < MM.m; i++)
        {
            int u = MM.D[current][i];
            path = MM.F[current][i] == "-" ? path : path + MM.F[current][i];
            if (!used[u])
                dfs(u, to, path, used, out, MM);
        }
    }
}

void bfs(int startNode, const MealyMachine<int, string> &MM, const int maxPathSize)
{
    vector<set<string>> path(MM.n, set<string>{""});
    vector<set<string>> pathNominus(MM.n, set<string>{""});

    queue<int> q;
    q.push(startNode);

    while (!q.empty())
    {
        int currentNode = q.front();
        q.pop();
        cout << "currentNode: " << currentNode << " ";
        printPath(pathNominus);
        cout << rightOrderToBFS(currentNode, MM.D[currentNode][0], MM.D[currentNode][1], pathNominus)[0] << rightOrderToBFS(currentNode, MM.D[currentNode][0], MM.D[currentNode][1], pathNominus)[1];
        for (int i : rightOrderToBFS(currentNode, MM.D[currentNode][0], MM.D[currentNode][1], pathNominus))
        {
            // usleep(1000);
            int descendant = MM.D[currentNode][i];
            string signal = MM.F[currentNode][i];

            set<string> pathNominusCurrentNodeCopy(pathNominus[currentNode]);
            for (string currentNodePath : pathNominus[currentNode])
            {
                if (pathNominus[descendant].size() != 1 || descendant == currentNode) // visited before or self cycle
                {
                    if (descendant == currentNode)
                    {
                        if (signal == "-") // prevent infinite self cycle
                        {
                            continue;
                        }
                        else // add signal to every path
                        {
                            currentNodePath += signal;
                            while (currentNodePath.size() <= maxPathSize)
                            {
                                pathNominusCurrentNodeCopy.insert(currentNodePath);
                                currentNodePath += signal;
                            }
                        }
                    }
                    else
                    {
                        set<string> cyclePathes;
                        vector<bool> used(MM.n, false);
                        dfs(descendant, currentNode, "", used, cyclePathes, MM);
                        for (auto &&cycle : cyclePathes)
                        {
                            // set<string> pathNominusDescendantCopy(pathNominus[descendant]);
                            // for (auto &&descendantPath : pathNominus[descendant])
                            // {

                            // }
                            // cout << "|" << cycle << "|" << endl;
                        }

                        // if (signal != "-")
                        // {
                        //     currentNodePath += signal;
                        // }
                    }
                }
                else // not visited before
                {
                    if (currentNodePath == "" && pathNominus[currentNode].size() != 1)
                    {
                        continue;
                    }

                    path[descendant].insert(currentNodePath + signal);

                    if (signal == "-")
                    {
                        pathNominus[descendant].insert(currentNodePath);
                    }
                    else
                    {
                        pathNominus[descendant].insert(currentNodePath + signal);
                    }
                    // cout << currentNodePath + signal << endl;
                    q.push(descendant);
                }
            }

            if (pathNominus[currentNode].size() != pathNominusCurrentNodeCopy.size())
            {
                pathNominus[currentNode] = pathNominusCurrentNodeCopy;
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
    bfs(q0, MM, M);

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
5

    1 3 0 1 4 2 1 1 3 2

    y y -
    x
        x x
            z z
                z -

    2 5