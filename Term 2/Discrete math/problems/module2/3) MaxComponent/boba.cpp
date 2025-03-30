#include <iostream>
#include <vector>
#include <queue>
#include <set>

using namespace std;

typedef vector<vector<int>> graph_T;

struct component
{
    vector<int> nodes;
    int minNode = 1000001;
    size_t nodesNumber = 0;
    size_t edgesNumber = 0;
};

bool isFrom(int node, vector<int> nodes)
{
    for (auto &&i : nodes)
    {
        if (i == node)
        {
            return true;
        }
    }
    return false;
}

int main()
{
    int n;
    int m;
    cin >> n >> m;

    graph_T graph(n);
    queue<pair<int, int>> graphRaw;

    int u, v;
    for (size_t i = 0; i < m; i++)
    {
        cin >> u >> v;

        graph[u].push_back(v);
        graph[v].push_back(u);
        graphRaw.push(make_pair(u, v));
    }

    int compMatch[n]{};
    int num = 1;
    vector<component> components;
    for (int v = 0; v < n; v++)
    {
        if (!compMatch[v])
        {
            queue<int> q;
            q.push(v);
            compMatch[v] = num;
            while (!q.empty())
            {
                int cur = q.front();
                q.pop();
                for (int neighbor : graph[cur])
                {
                    if (!compMatch[neighbor])
                    {
                        compMatch[neighbor] = num;
                        q.push(neighbor);
                    }
                }
            }
            components.push_back(component{});
            num += 1;
        }
        int compIndex = compMatch[v] - 1;
        components.at(compIndex).nodes.push_back(v);
        components.at(compIndex).nodesNumber += 1;
        components.at(compIndex).minNode = min(components.at(compIndex).minNode, v);
        components.at(compIndex).edgesNumber += graph[v].size();
    }

    int biggestComponentIndex = 0;
    for (int compIndex = 0; compIndex < num - 1; compIndex++)
    {

        if (components.at(compIndex).nodesNumber > components.at(biggestComponentIndex).nodesNumber)
        {
            biggestComponentIndex = compIndex;
        }
        else if (components.at(compIndex).nodesNumber == components.at(biggestComponentIndex).nodesNumber)
        {
            if (components.at(compIndex).edgesNumber > components.at(biggestComponentIndex).edgesNumber)
            {
                biggestComponentIndex = compIndex;
            }
            else if (components.at(compIndex).edgesNumber == components.at(biggestComponentIndex).edgesNumber)
            {
                if (components.at(compIndex).minNode == components.at(biggestComponentIndex).minNode)
                {
                    biggestComponentIndex = compIndex;
                }
            }
        }
    }
    
    cout << "graph {" << endl;
    set<int> biggestNodes;
    for (int i : components.at(biggestComponentIndex).nodes)
        biggestNodes.insert(i);
    
    for (int i = 0; i < n; i++)
    {
        cout << "   " << i;
        if (biggestNodes.count(i))
        {
            cout << " [color=\"red\"]";
        }
        cout << endl;
    }

    while (!graphRaw.empty())
    {
        cout << "   " << graphRaw.front().first << " -- " << graphRaw.front().second;
        if (biggestNodes.count(graphRaw.front().first))
        {
            cout << " [color=\"red\"]";
        }
        cout << endl;
        graphRaw.pop();
    }
    cout << "}" << endl;
    return 0;
}