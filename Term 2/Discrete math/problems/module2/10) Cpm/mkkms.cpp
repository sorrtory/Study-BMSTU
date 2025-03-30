#include <string>
#include <iostream>
#include <vector>
#include <map>
#include <queue>
#include <set>

using namespace std;
const int inf = 1e9;

map<string, set<string>> redEdges;

struct Vertex
{
    string color = "black";
    int weight;
    vector<string> descendens;
    vector<string> ancestors;
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
    // g[currentNode].color = "blue";
    redEdges[currentNode].clear();
    for (auto &&i : g[currentNode].descendens)
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
        // paintItBlue(currentNode, g);
    }
    else
    {
        g[currentNode].color = "red";
        for (auto &&i : p[currentNode])
        {
            // redEdges[currentNode].push_back(i);
            redEdges[i].insert(currentNode);
            paintItRed(i, endNode, p, g);
        }
    }
}

void paintItBlack(graph_T &g)
{
    redEdges.clear();
    for (auto &&i : g)
        i.second.color = "black";
}

void paintItForRed(graph_T &g)
{
    for (auto &&i : g)
        if (i.second.color != "red")
            i.second.color = "black";
}

string firstNotBlue(string currentNode, map<string, vector<string>> p, graph_T &g)
{
    for (auto &&i : g[currentNode].descendens)
        if (g[i].color != "blue")
            return i;
    for (auto &&i : p[currentNode])
        return firstNotBlue(i, p, g);
    return "";
}

bool isFromRedEdges(string a, string b)
{
    for (auto &&i : redEdges[a])
        if (i == b)
            return true;
    return false;
}

string dfs(string v, string p, map<string, bool> &used, graph_T &g)
{
    if (used[v])
    {
        cout << "Graph has a cycle, namely:" << endl;
        return v;
    }
    used[v] = true;
    for (auto u : g[v].descendens)
    {
        if (u != p)
        {
            string k = dfs(u, v, used, g);
            if (k != "")
            {
                cout << v << endl;
                if (k == v)
                    exit(0);
                return k;
            }
        }
    }
    return "";
}

int paint(string startNode, string endNode, int maxSum, graph_T &g)
{
    if (g[startNode].color == "blue")
    {
        paintItBlue(startNode, g);
        return -1;
    }

    queue<string> q;
    string v;
    q.push(startNode);

    map<string, int> d;
    map<string, vector<string>> p;

    for (auto i : g)
        d[i.first] = -1;
    d[startNode] = g[startNode].weight;
    // d[startNode] = 0;
    while (!q.empty())
    {
        v = q.front();
        q.pop();
        for (string u : g[v].descendens)
        {
            // cout << u << " ";

            if (d[u] != -1 && d[u] <= d[v])
            {
                
                paintItBlue(u, g);

                for (auto &&i : g[v].ancestors)
                    for (auto j = g[i].descendens.begin(); j < g[i].descendens.end(); j++)
                        if (*j == u)
                            g[i].descendens.erase(j);

                // bool shouldBlue = true;
                // for (auto &&i : g[u].ancestors){
                //     for (auto &&j : g[i].descendens)
                //     {

                //     }

                // }

                // for (auto &&i : g[u].ancestors)
                // {
                //     cout << i << " ";
                //     // if (d[i] == -1)
                //     // {
                //     //     shouldBlue = false;
                //     //     break;
                //     // }
                //     if (d[u] <= d[i])
                //     {
                //         shouldBlue = true;
                //     }
                //     else
                //     {
                //         shouldBlue = false;
                //         break;
                //     }
                // }
                // cout << u << " " << shouldBlue << endl;

                // map<string, bool> used;

                // for (auto i : g)
                //     used[i.first] = false;
                // for (auto &&i : g[u].ancestors)
                // {
                //     if (!used[i])
                //     {
                //         string m = dfs(v, "", used, g);
                //         if (m != "")
                //         {
                //             paintItBlue(m, g);
                //         }
                //     }
                // }

                // continue;
            }

            // if (d[u] != -1 && d[v] != -1 && d[u] <= d[v] || u == v)
            // {
            //     // if (d[u] != -1 && d[u] <= d[v])
            //     // g[u].color = "blue";'
            //     bool shouldBlue = true;
            //     cout << " aboba " << u;
            //     for (auto &&i : g[u].ancestors)
            //     {
            //         if (d[i] == -1){
            //             cout << i << " " << endl;
            //             shouldBlue = false;
            //             break;
            //         }

            //     }
            //     if (shouldBlue)
            //         paintItBlue(u, g);
            // }
            if (d[u] < d[v] + g[u].weight && g[u].color != "blue")
                p[u].clear();

            if (d[u] <= d[v] + g[v].weight && g[u].color != "blue")
            {

                q.push(u);

                // d[u] = d[v] + g[v].weight;
                d[u] = d[v] + g[u].weight;
                p[u].push_back(v);
            }
        }
    }

    // d[endNode] += g[endNode].weight;

    // for (auto &&i : p)
    // {
    //     cout << i.first << ": ";
    //     for (auto &&j : i.second)
    //     {
    //         cout << j << "|";
    //     }
    //     cout << endl;
    // }
    // cout << d["E485"] << d["E260"] << " -> " << d["E148"] << " pososi " << startNode << " | " << endNode << endl;
    // cout << g["E986"].color << " and " << g["E260"].color << " -> " << g["E148"].color << " color " << endl;

    // if (g[endNode].color == "blue")
    // {
    //     string firstNB = firstNotBlue(endNode, p, g);
    //     if (firstNB == "")
    //         return -1;

    //     paintItRed(firstNB, startNode, p, g);
    //     return d[firstNB] + g[firstNB].weight;
    // }
    if (g[endNode].color == "blue"){
        return -1;
    }
    if (d[endNode] == maxSum)
    {
        paintItForRed(g);
        paintItRed(endNode, startNode, p, g);
    }

    if (d[endNode] > maxSum)
    {
        // cout << "AGAAAA|||||||||";
        paintItBlack(g);
        // cout << g["CutCabbage"].color << endl;
        paint(startNode, endNode, d[endNode], g);
        paintItRed(endNode, startNode, p, g);
        // cout << g["CutCabbage"].color << "!2" << endl;
    }

    return d[endNode];
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
            {
                g[lastNode].descendens.push_back(node);
                g[node].ancestors.push_back(lastNode);
            }

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
                maxSum = paintedSum;
            }
            // cout << paintedSum << " ";
        }
    }

    // for (auto &&i : redEdges)
    // {
    //     cout << i.first << ": ";
    //     for (auto &&j : i.second)
    //     {
    //         cout << j << " ";
    //     }
    //     cout << endl;
    // }
    // exit(0);
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

    // g.erase("");
    for (auto &&i : g)
    {

        for (auto &&j : i.second.descendens)
        {
            cout << "  " << i.first << " -> " << j;

            // if (i.second.color == "blue" || (i.second.color == "red" && g[j].color == "red" && isFromRedEdges(i.first, j)))
            if (i.second.color == "blue"  || (isFromRedEdges(i.first, j) && g[j].color != "blue"))
            {
                cout << " [color = " << i.second.color << "]";
            }
            cout << endl;
        }
    }
    cout << "}" << endl;
}
