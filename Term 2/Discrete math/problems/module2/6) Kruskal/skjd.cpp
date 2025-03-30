#include <iostream>
#include <cmath>
#include <algorithm>
#include <vector>
#include <iomanip>

using namespace std;

int dsu_get(int v, int *p)
{
    return (v == p[v]) ? v : (p[v] = dsu_get(p[v], p));
}

void dsu_unite(int a, int b, int *p)
{
    a = dsu_get(a, p);
    b = dsu_get(b, p);
    if (rand() & 1)
        swap(a, b);
    if (a != b)
        p[a] = b;
}

float myRound(float x)
{
    int dx = x * 1000;
    float ddx = 0;
    if (dx % 10 >= 5)
        ddx = float(dx + 10) / 1000;
    else
        ddx = float(dx) / 1000;
    return (float)(int)(ddx * 100) / 100;
}
struct Point
{
    int x;
    int y;
};

struct Edge
{
    int from, to;
    float weight;
};

float dist(Point a, Point b)
{
    return sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2));
}
int main()
{
    int n, en;
    cin >> n;
    en = n * (n - 1) / 2;
    Point points[n];
    int x, y;
    for (size_t i = 0; i < n; i++)
    {
        cin >> x >> y;
        points[i].x = x;
        points[i].y = y;
    }

    vector<Edge> edges;
    for (int i = 0; i < n - 1; i++)
        for (int j = i + 1; j < n; j++)
            edges.push_back(Edge{i, j, dist(points[i], points[j])});

    sort(edges.begin(), edges.end(), [](Edge a, Edge b)
         { return a.weight < b.weight; });

    double res = 0;
    int p[n];

    for (int i = 0; i < n; i++)
        p[i] = i;
    for (auto [a, b, w] : edges)
    {
        if (p[a] != p[b])
        {
            res += w;
            int old_id = p[b], new_id = p[a];
            for (int j = 0; j < n; ++j)
                if (p[j] == old_id)
                    p[j] = new_id;
        }
    }
    cout << setprecision(2) << fixed;
    cout << myRound(res) << endl;
    return 0;
}