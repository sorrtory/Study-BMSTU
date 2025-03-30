#include <iostream>
#include <algorithm>
#include <vector>
#include <queue>

using namespace std;

const int INF = 1e9 + 7;

typedef vector<vector<pair<int, int>>> graph_T;

int main()
{
    int n;
    int m;
    cin >> n >> m;

    graph_T graph(n);

    int u, v, w;
    for (size_t i = 0; i < m; i++)
    {
        cin >> u >> v >> w;

        graph[u].push_back(make_pair(v, w));
        graph[v].push_back(make_pair(u, w));
    }

    bool used[n];       
    int mst_weight = 0; 
    fill(used, used + n, false);
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> q;

    q.push({0, 0}); 

    while (!q.empty())
    {
        pair<int, int> c = q.top();
        q.pop();

        int dst = c.first, v = c.second;
        if (used[v])
            continue;

        used[v] = true;
        mst_weight += dst;
        for (pair<int, int> e : graph[v])
        {
            int u = e.first, len_vu = e.second;

            if (!used[u])
                q.push({len_vu, u});
        }
    }

    cout << mst_weight << endl;
    return 0;
}