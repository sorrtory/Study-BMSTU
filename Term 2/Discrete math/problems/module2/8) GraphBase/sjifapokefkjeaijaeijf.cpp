#include <iostream>
#include <stack>
#include <set>
#include <vector>

using namespace std;

struct Node
{
    int T1;
    int comp;
    int low;
    set<int> arcs;
};

struct Node2
{
    bool based = true;
    int minNodeIndex = -1;
    set<int> arcs;
};

typedef vector<Node> graph_T;
typedef vector<Node2> graph2_T;

int time_ = 1;
int count = 1;

void VisitVertex_Tarjan(graph_T &G, int v, stack<int> &s)
{
    G[v].T1 = G[v].low = time_;
    time_ += 1;
    s.push(v);

    for (auto &&u : G[v].arcs)
    {
        if (G[u].T1 == 0)
            VisitVertex_Tarjan(G, u, s);
        if ((G[u].comp == 0) && G[v].low > G[u].low)
            G[v].low = G[u].low;
    }
    if (G[v].T1 == G[v].low)
    {
        int u = s.top();
        do
        {
            u = s.top();
            s.pop();
            G[u].comp = count;
        } while (u != v);
        count += 1;
    }
}
void Tarjan(graph_T &G)
{
    for (auto &&v : G)
        v.T1 = v.comp = 0;

    stack<int> s;
    for (int v = 0; v < G.size(); v++)
        if (G[v].T1 == 0)
            VisitVertex_Tarjan(G, v, s);
}

// 22
// 33
//  0  8     1  3     1 10     2 11     2 13     3 14
//  4  6     4 16     5 17     6 19     8  1     8  9
//  9  0     9  2    10  1    10  4    11 12    12  2
// 12  4    13  5    13 12    14 15    15  3    15  6
// 16  4    16  7    17  7    17 18    18  5    19  6
// 20 21    21 18    21 20
int main()
{
    int n, m;
    cin >> n >> m;
    graph_T g(n);

    int u, v;
    for (size_t i = 0; i < m; i++)
    {
        cin >> u >> v;
        g[u].arcs.insert(v);
    }
    Tarjan(g);

    graph2_T g_condensed(count);
    for (int i = 0; i < n; i++)
    {
        Node &node = g[i];

        if (g_condensed.at(node.comp).minNodeIndex == -1)
            g_condensed.at(node.comp).minNodeIndex = i;

        for (auto &&neigbour : node.arcs)
        {
            if (g[neigbour].comp != node.comp)
            {
                g_condensed.at(node.comp).arcs.insert(g[neigbour].comp);
                g_condensed.at(g[neigbour].comp).based = false;
            }
        }
    }
    for (auto i = g_condensed.begin() + 1; i != g_condensed.end(); i++)
        if (i->based)
            cout << i->minNodeIndex << " ";
    cout << endl;
    return 0;
}