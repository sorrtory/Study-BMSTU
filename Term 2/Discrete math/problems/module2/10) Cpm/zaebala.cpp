#include <string>
#include <iostream>
#include <vector>
#include <map>
#include <queue>
#include <set>
#include <stack>

using namespace std;

const int inf = 1e9;

map<string, set<string>> redEdges;
map<string, bool> startNodes;
map<string, bool> endNodes;

struct Vertex
{
    string color = "black";
    int weight;
    vector<string> descendens;
    vector<string> ancestors;

    int T1;
    int comp;
    int low;
};
typedef map<string, Vertex> graph_T;
graph_T g;
int maxSum = -1;

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

void paintItBlue(string currentNode)
{

    redEdges[currentNode].clear();
    for (auto &&i : g[currentNode].descendens)
    {
        if (g[i].color != "blue")
        {
            g[i].color = "blue";
            paintItBlue(i);
        }
    }
}

void paintItRed(string currentNode, string endNode, map<string, vector<string>> p)
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
            if (g[i].color != "blue")
                redEdges[i].insert(currentNode);

            paintItRed(i, endNode, p);
        }
    }
}

void paintItBlack()
{
    redEdges.clear();
    for (auto &&i : g)
        if (i.second.color != "blue")
            i.second.color = "black";
}

bool isFromRedEdges(string a, string b)
{
    for (auto &&i : redEdges[a])
        if (i == b)
            return true;
    return false;
}

int paint(string startNode, string endNode)
{
    if (g[startNode].color == "blue" || g[endNode].color == "blue")
        return -1;

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
            if (d[u] < d[v] + g[u].weight && g[u].color != "blue")
                p[u].clear();

            if (d[u] <= d[v] + g[u].weight && g[u].color != "blue")
            {
                q.push(u);
                d[u] = d[v] + g[u].weight;
                p[u].push_back(v);
            }
        }
    }
    if (d[endNode] == maxSum)
    {
        paintItRed(endNode, startNode, p);
    }

    if (d[endNode] > maxSum)
    {
        paintItBlack();
        paintItRed(endNode, startNode, p);
    }

    return d[endNode];
}

int time_ = 1;
int count_ = 1;

void VisitVertex_Tarjan(graph_T &G, string v, stack<string> &s)
{
    G[v].T1 = G[v].low = time_;
    time_ += 1;
    s.push(v);

    for (auto &&u : G[v].descendens)
    {
        if (G[u].T1 == 0)
            VisitVertex_Tarjan(G, u, s);
        if ((G[u].comp == 0) && G[v].low > G[u].low)
            G[v].low = G[u].low;
    }
    if (G[v].T1 == G[v].low)
    {
        string u = s.top();
        do
        {
            u = s.top();
            s.pop();
            G[u].comp = count_;
        } while (u != v);
        count_ += 1;
    }
}
void Tarjan(graph_T &G)
{
    for (auto &&v : G)
        v.second.T1 = v.second.comp = 0;

    stack<string> s;
    for (auto &&i : G)
        if (i.second.T1 == 0)
            VisitVertex_Tarjan(G, i.first, s);
}
string getFirstNotBlueAncestor(string n)
{
    for (auto &&i : g[n].ancestors)
        if (g[i].color != "blue")
            return i;

    for (auto &&i : g[n].ancestors)
        if (g[i].comp != g[n].comp)
            return getFirstNotBlueAncestor(i);

    return "";
}
int main()
{
    string s = "", line;
    while (getline(cin, line))
        for (auto &&i : line)
            if (i != ' ')
                s += i;

    int linesCount = count(s, ';') + 1;
    string lines[linesCount];
    split(s, lines, ';');

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

    Tarjan(g);
    vector<string> comps[count_];
    for (auto &&i : g)
        comps[i.second.comp].push_back(i.first);

    for (auto &&i : comps)
        if (i.size() != 1)
            for (auto &&j : i)
                paintItBlue(j);

    for (auto &&i : g)
        for (auto &&j : i.second.descendens)
            if (j == i.first)
            {
                paintItBlue(i.first);
                break;
            }

    for (auto i = startNodes.begin(); i != startNodes.end(); i++)
    {
        if (g[i->first].color == "blue")
            i->second = false;

        for (auto &&j : g[i->first].descendens)
            startNodes[j] = false;
    }

    map<string, bool> betterEndNodes;
    for (auto i = endNodes.begin(); i != endNodes.end(); i++)
    {
        if (g[i->first].color == "blue")
        {
            string nV = getFirstNotBlueAncestor(i->first);
            if (nV != "")
                betterEndNodes[nV] = true;
        }
        betterEndNodes[i->first] = true;
    }
    endNodes = betterEndNodes;

    int paintedSum = 0;
    for (auto &&st : startNodes)
    {
        if (st.second)
        {

            for (auto &&ed : endNodes)
            {
                if (ed.second)
                {
                    paintedSum = paint(st.first, ed.first);
                    if (paintedSum > maxSum)
                        maxSum = paintedSum;
                }
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

    // g.erase("");
    for (auto &&i : g)
    {

        for (auto &&j : i.second.descendens)
        {
            cout << "  " << i.first << " -> " << j;

            if (i.second.color == "blue" || (isFromRedEdges(i.first, j) && g[j].color != "blue"))
            {
                cout << " [color = " << i.second.color << "]";
            }
            cout << endl;
        }
    }
    cout << "}" << endl;
}
