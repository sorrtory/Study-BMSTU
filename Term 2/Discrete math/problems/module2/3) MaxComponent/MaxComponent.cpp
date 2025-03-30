#include <iostream>
#include <vector>
#include <queue>
#include <set>
#include <algorithm>
#include <tuple>

using namespace std;

struct Edge {
    int u, v;
};

void bfs(int start, const vector<vector<int>>& adj, vector<bool>& visited, set<int>& component, vector<Edge>& edges) {
    queue<int> q;
    q.push(start);
    visited[start] = true;
    component.insert(start);

    while (!q.empty()) {
        int node = q.front();
        q.pop();
        for (int neighbor : adj[node]) {
            edges.push_back({node, neighbor});
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                component.insert(neighbor);
                q.push(neighbor);
            }
        }
    }
}

int main() {
    int N, M;
    cin >> N >> M;

    vector<vector<int>> adj(N);
    vector<Edge> allEdges;

    for (int i = 0; i < M; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
        allEdges.push_back({u, v});
    }

    vector<bool> visited(N, false);
    vector<set<int>> components;
    vector<vector<Edge>> componentEdges;

    for (int i = 0; i < N; ++i) {
        if (!visited[i]) {
            set<int> component;
            vector<Edge> edges;
            bfs(i, adj, visited, component, edges);
            components.push_back(component);
            componentEdges.push_back(edges);
        }
    }

    int maxComponentIdx = 0;
    for (int i = 1; i < components.size(); ++i) {
        if (components[i].size() > components[maxComponentIdx].size() || 
            (components[i].size() == components[maxComponentIdx].size() && componentEdges[i].size() > componentEdges[maxComponentIdx].size()) ||
            (components[i].size() == components[maxComponentIdx].size() && componentEdges[i].size() == componentEdges[maxComponentIdx].size() && *components[i].begin() < *components[maxComponentIdx].begin())) {
            maxComponentIdx = i;
        }
    }

    set<int>& largestComponent = components[maxComponentIdx];
    vector<Edge>& largestComponentEdges = componentEdges[maxComponentIdx];

    cout << "graph G {" << endl;
    for (int i = 0; i < N; ++i) {
        if (largestComponent.count(i)) {
            cout << "  " << i << " [color=red];" << endl;
        } else {
            cout << "  " << i << ";" << endl;
        }
    }

    set<pair<int, int>> edgeSet;
    for (const auto& edge : allEdges) {
        int u = edge.u;
        int v = edge.v;
        if (u > v) swap(u, v);
        edgeSet.insert({u, v});
    }

    for (const auto& edge : edgeSet) {
        int u = edge.first;
        int v = edge.second;
        if (largestComponent.count(u) && largestComponent.count(v)) {
            cout << "  " << u << " -- " << v << " [color=red];" << endl;
        } else {
            cout << "  " << u << " -- " << v << ";" << endl;
        }
    }

    cout << "}" << endl;

    return 0;
}