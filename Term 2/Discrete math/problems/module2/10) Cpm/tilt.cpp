#include <string>
#include <iostream>
#include <vector>
#include <map>
#include <queue>

using namespace std;
const int inf = 1e9;
map<string, int> bestd;
map<string, vector<string>> bestp;
map<string, int> d;
map<string, vector<string>> p;

struct Vertex
{
    string color = "black";
    int weight;
    vector<string> neighbours;
};

typedef map<string, Vertex> graph_T;

void split(string from, string *to, char c)
{
    size_t pos = 0;
    int i = 0;
    std::string from2 = from, token;
    int d = 0;
    while ((pos = from2.find(c)) != std::string::npos)
    {
        token = from.substr(d, pos);
        from2 = from2.substr(pos + 1);
        to[i] = token;
        d += pos + 1;
        i++;
    }
    token = from2.substr(0, pos);
    to[i] = token;
}

int count(string s, char c)
{
    int count = 0;

    for (int i = 0; i < s.size(); i++)
        if (s[i] == c)
            count++;

    return count;
}

void paintItBlue(string currentNode, graph_T &g)
{

    for (auto &&i : g[currentNode].neighbours)
    {
        if (g[i].color != "blue")
        {
            g[i].color = "blue";
            paintItBlue(i, g);
        }
    }
}
void paintItRed(string currentNode, string endNode, map<string, vector<string>> p, graph_T &g)
{
    if (g[currentNode].color == "blue")
    {
        paintItBlue(currentNode, g);
    }
    else
    {
        g[currentNode].color = "red";
    }
    for (auto &&i : p[currentNode])
        paintItRed(i, endNode, p, g);
}

void paintItBlack(graph_T &g)
{
    for (auto &&i : g)
        if (i.second.color != "blue")
            i.second.color = "black";
}

string firstNotBlue(string currentNode, map<string, vector<string>> p, graph_T &g)
{
    for (auto &&i : g[currentNode].neighbours)
        if (g[i].color != "blue")
            return i;
    for (auto &&i : p[currentNode])
        return firstNotBlue(i, p, g);
    return "";
}
int paint(string startNode, string endNode, int maxSum, graph_T &g)
{
    queue<string> q;
    string v;
    q.push(startNode);

    d.clear();
    p.clear();

    for (auto i : g)
        d[i.first] = -1;
    // d[startNode] = g[startNode].weight;
    d[startNode] = 0;

    while (!q.empty())
    {
        v = q.front();
        q.pop();
        for (string u : g[v].neighbours)
        {

            if (d[u] != -1 && d[u] <= d[v])
                // g[u].color = "blue";
                paintItBlue(u, g);

            if (d[u] < d[v] + g[u].weight && g[u].color != "blue")
                p[u].clear();

            if (d[u] <= d[v] + g[v].weight && g[u].color != "blue")
            {

                q.push(u);

                d[u] = d[v] + g[v].weight;
                p[u].push_back(v);
            }
        }
    }

    d[endNode] += g[endNode].weight;

    // for (auto &&i : p)
    // {
    //     cout << i.first << ": ";
    //     for (auto &&j : i.second)
    //     {
    //         cout << j << "|";
    //     }
    //     cout << endl;
    // }

    if (g[endNode].color == "blue")
    {
        string firstNB = firstNotBlue(endNode, p, g);
        if (firstNB == "")
            return -1;

        paintItRed(firstNB, startNode, p, g);
        return d[firstNB] + g[firstNB].weight;
    }

    if (d[endNode] == maxSum)
        paintItRed(endNode, startNode, p, g);

    if (d[endNode] > maxSum)
    {
        // cout << "AGAAAA|||||||||";
        paintItBlack(g);
        // cout << g["CutCabbage"].color << endl;
        paintItRed(endNode, startNode, p, g);
        // cout << g["CutCabbage"].color << "!2" << endl;
    }

    return d[endNode];
}

bool isGoodArc(string from, string to, graph_T &g)
{
    if (g[from].color == "blue")
        return true;

    for (auto &&i : bestp[to])
        if (i == from)
            return true;
    return false;
}
int main()
{
    // don't skip the whitespace while reading
    //   std::cin >> std::noskipws;

    string s = "", line;
    while (getline(cin, line))
        for (auto &&i : line)
            if (i != ' ')
                s += i;

    int linesCount = count(s, ';') + 1;
    string lines[linesCount];
    split(s, lines, ';');

    graph_T g;
    map<string, bool> startNodes;
    map<string, bool> endNodes;

    for (size_t i = 0; i < linesCount; i++)
    {
        string node;
        int angleCount = count(lines[i], '<') + 1;
        string nodes[angleCount];
        split(lines[i], nodes, '<');

        string lastNode = "";
        for (size_t j = 0; j < angleCount; j++)
        {

            node = nodes[j].substr(0, nodes[j].find('('));

            if (count(nodes[j], '(') != 0)
            {
                g[node];
                g[node].weight = stoi(nodes[j].substr(nodes[j].find('(') + 1, nodes[j].find(')')));
            }
            if (lastNode != "")
                g[lastNode].neighbours.push_back(node);

            nodes[j] = node;
            lastNode = node;
        }
        startNodes[nodes[0]] = true;
        endNodes[nodes[angleCount - 1]] = true;
    }

    int maxSum = 0, paintedSum = 0;
    for (auto &&i : startNodes)
    {
        string nodei = i.first;
        for (auto &&j : endNodes)
        {

            string nodej = j.first;
            // cout << "Start: " << nodei << " End: " << nodej << " Max: " << maxSum << endl;

            paintedSum = paint(nodei, nodej, maxSum, g);
            if (paintedSum > maxSum)
            {
                bestd = d;
                bestp = p;
                maxSum = paintedSum;
            }
        }
    }

    cout << "digraph {" << endl;
    for (auto &&i : g)
    {
        cout << "  " << i.first << " [" << "label = \"" << i.first << "(" << i.second.weight << ")\"";
        if (i.second.color != "black")
        {
            cout << ", color = " << i.second.color;
        }
        cout << "]" << endl;
    }

    for (auto &&i : g)
    {

        for (auto &&j : i.second.neighbours)
        {
            cout << "  " << i.first << " -> " << j;
            if (i.second.color == g[j].color && i.second.color != "black" && isGoodArc(i.first, j, g))
            {
                cout << " [color = " << i.second.color << "]";
            }
            cout << endl;
        }
    }
    cout << "}" << endl;
}