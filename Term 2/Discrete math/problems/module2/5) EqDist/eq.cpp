#include <iostream>
#include <vector>
#include <queue>
#include <set>

using namespace std;

typedef vector<vector<int>> graph_T;

int main()
{
    int n, m;
    cin >> n >> m;

    graph_T graph(n);
    int u, v;
    for (size_t i = 0; i < m; i++)
    {
        cin >> u >> v;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    int k;
    cin >> k;

    int bearingIndex[k];
    int l;
    for (size_t i = 0; i < k; i++)
    {
        cin >> l;
        bearingIndex[i] = l;
    }

    if (k == 0)
        for (int i = 0; i < n; i++)
            cout << i << endl;
    else
    {
        set<int> goodNodes;
        int dst[k][n];
        bool used[n];

        for (size_t ind = 0; ind < k; ind++)
        {
            int i = bearingIndex[ind];
            for (size_t j = 0; j < n; j++)
            {
                dst[ind][j] = -1;
                used[j] = 0;
            }

            queue<int> q;
            q.push(i);
            used[i] = true;
            dst[ind][i] = 0;
            while (!q.empty())
            {
                int cur = q.front();
                q.pop();
                for (int neighbor : graph[cur])
                {
                    if (!used[neighbor])
                    {
                        q.push(neighbor);
                        used[neighbor] = true;
                        dst[ind][neighbor] = dst[ind][cur] + 1;
                    }
                }
            }
        }

        for (size_t i = 0; i < n; i++)
        {
            int dest = dst[0][i];
            if (dest == -1) break;
            
            int c = 1;
            for (size_t j = 1; j < k; j++)
                if (dst[j][i] == dest)
                    c += 1;
            if (c == k)
                goodNodes.insert(i);
        }

        if (goodNodes.empty())
            cout << "-";
        else
            for (int i : goodNodes)
                cout << i << " ";
    }
    cout << endl;
    return 0;
}