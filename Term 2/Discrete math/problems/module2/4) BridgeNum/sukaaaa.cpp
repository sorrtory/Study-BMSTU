#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

void dfs(int v, int parent, vector<vector<int>> &adj, vector<bool> &visited, vector<int> &disc, vector<int> &low, vector<pair<int, int>> &bridges, int &time)
{
    visited[v] = true;
    disc[v] = low[v] = ++time;
    // disc[v] = low[v] = (parent == -1 ? 0 : low[parent] + 1);
    // cout << parent << "parent ";
    for (int to : adj[v])
    {
        if (!visited[to])
        {
            dfs(to, v, adj, visited, disc, low, bridges, time);

            // Check if the subtree rooted at 'to' has a connection back to an ancestor of 'v'
            low[v] = min(low[v], low[to]);

            // If the lowest vertex reachable from subtree under 'to' is below 'v' in DFS tree, then 'v-to' is a bridge
            // cout << "d[u]: " << disc[v] << endl;
            // cout << "h[v]: " << low[to] << endl;
            // if (h[v] < d[u])
            if (low[to] > disc[v])
            {
                bridges.push_back({v, to});
            }
        }
        else if (to != parent)
        {
            // Update low value of 'v' for parent function calls
            low[v] = min(low[v], disc[to]);
        }
    }
}

int main()
{
    int N, M;
    cin >> N >> M;

    vector<vector<int>> adj(N);
    for (int i = 0; i < M; ++i)
    {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    vector<bool> visited(N, false);
    vector<int> disc(N, -1), low(N, -1);
    vector<pair<int, int>> bridges;
    int time = 0;

    for (int i = 0; i < N; ++i)
    {
        if (!visited[i])
        {
            dfs(i, -1, adj, visited, disc, low, bridges, time);
        }
    }

    cout << "Number of bridges: " << bridges.size() << endl;
    // for (auto bridge : bridges)
    // {
    //     cout << bridge.first << " " << bridge.second << endl;
    // }

    return 0;
}
