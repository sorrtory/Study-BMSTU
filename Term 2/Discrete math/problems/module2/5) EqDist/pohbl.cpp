#include <iostream>
#include <vector>
#include <queue>
#include <set>

using namespace std;

typedef vector<vector<int>> graph_T;

struct Node
{
    bool isBear;
    int *bearDistances;
};

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
    Node nodes[n];
    for (size_t i = 0; i < n; i++)
    {
        nodes[i].bearDistances = new int[k];
        for (size_t j = 0; j < k; j++)
        {
            nodes[i].bearDistances[j] = -1;
        }
        nodes[i].isBear = false;
    }
    
    int bearingIndex[k];
    int l;
    for (size_t i = 0; i < k; i++)
    {
        cin >> l;
        bearingIndex[i] = l;
        nodes[i].isBear = true;
    }

    set<int> goodNodes;

    for (size_t i = 0; i < n; i++)
    {
        bool used[n];
        int dst[k];
        for (int i = 0; i < k; i++) // изначально заполним массив dst значением -1
            dst[i] = -1; // оно будет обозначать, что расстояние до этой вершины ещё неизвестно
        

        queue<int> q;
        q.push(i);
        used[i] = true;
        dst[i] = 0;
        while (!q.empty())
        {
            int cur = q.front(); // извлекаем из очереди текущую вершину
            q.pop();

            // Здесь должна быть обработка текущей вершины.

            for (int neighbor : graph[cur])
            { // добавляем всех непосещённых соседей.
                if (!used[neighbor])
                {
                    q.push(neighbor);
                    used[neighbor] = true;
                    dst[neighbor] = dst[cur] + 1;
                }
            }
        }
        int distance = -1;
        int dCounter = 0;
        for (int j = 0; j < k; j++)
        {
            if (dst[j] != -1)
                if (distance == -1)
                    distance = dst[i];
                else
                    if (dst[i] == distance)
                        dCounter += 1;
            else
                cout << "Vertex " << i + 1 << " cannot be reached from vertex " << i << endl;
            if (dCounter == k)
                goodNodes.insert(i);
        }
    }

    if (goodNodes.size())
        for (size_t i = 0; i < goodNodes.size(); i++)
            cout << i << endl;
    else
        cout << "-" << endl;

    return 0;
}