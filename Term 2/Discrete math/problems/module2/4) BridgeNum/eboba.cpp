#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

typedef vector<vector<int>> graph_T;

void dfs(int v, bool used[], int h[], int d[], graph_T& g, int& counter, int p)
{
    used[v] = true;
    d[v] = h[v] = (p == -1 ? 0 : h[p] + 1);
    for (int u : g[v])
    {
        if (u != p)
        {
            if (used[u]) // если ребро обратное
                d[v] = min(d[v], h[u]);
            else
            { // если ребро прямое
                dfs(u, used, h, d, g, counter, v);
                d[v] = min(d[v], d[u]);
                if (h[v] < d[u])
                {
                    // если нельзя другим путем добраться в v или выше,
                    // то ребро (v, u) -- мост
                    // cout << v << "|" << u << endl;
                    counter += 1;
                }
            }
        }
    }
}

int main()
{
    int n;
    int m;
    cin >> n >> m;

    graph_T graph(n);

    int u, v;
    for (size_t i = 0; i < m; i++)
    {
        cin >> u >> v;

        graph[u].push_back(v);
        graph[v].push_back(u);
    }
    bool used[n]{};
    int h[n], d[n];
    fill(h, h+n, -1);
    fill(d, d+n, -1);
    int count = 0;
    for (size_t i = 0; i < n; i++)
        if (!used[i])
            dfs(i, used, h, d, graph, count, -1);

    cout << count;

    return 0;
}