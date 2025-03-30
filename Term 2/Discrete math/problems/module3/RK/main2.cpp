// <div style="width: 100%; height: 75px; position: static; top: 0px; left: 0px; background-color: yellow">
//     Превед!
// </div>

#include <iostream>
#include <vector>
#include <queue>

using namespace std;

template <typename INTYPE, typename OUTTYPE>
class MealyMachine
{

public:
    vector<vector<INTYPE>> D; // переходы
    vector<OUTTYPE> F;        // выходы
    int n, m, q0;             // количество состояний автомата n, размер входного алфавита m, нач состояние q0

    MealyMachine(int n, int m, int q0)
    {
        vector<vector<INTYPE>> D(n, vector<INTYPE>(m));
        this->D = D;

        vector<OUTTYPE> F(n);
        this->F = F;

        this->n = n;
        this->m = m;
        this->q0 = q0;
    }

    void graphviz()
    {
        cout << "digraph {\n\trankdir = LR\n";
        for (size_t j = 0; j < n; j++)
        {
            string clr = F[j] ? ", color = \"red\"" : ", color = \"black\"";

            for (size_t i = 0; i < m; i++)
                cout << "\t" << j << " -> " << D[j][i] << " [label = \"" << (char)('a' + i) << "\"" << clr << "]\n";
        }
        cout << "}\n";
    }
};

int main(int argc, char const *argv[])
{
    int n, m;
    cin >> m >> n;

    int q0;
    cin >> q0;

    string signal;

    // MM1
    MealyMachine<int, bool> MM1(n, m, q0);
    for (size_t i = 0; i < n; i++)
    {
        cin >> signal;
        if (signal == "+")
            MM1.F[i] = true;

        for (size_t j = 0; j < m; j++)
            cin >> MM1.D[i][j];
    }
    // MM2
    cin >> n >> q0;
    MealyMachine<int, bool> MM2(n, m, q0);
    for (size_t i = 0; i < n; i++)
    {
        cin >> signal;
        if (signal == "+")
            MM2.F[i] = true;

        for (size_t j = 0; j < m; j++)
            cin >> MM2.D[i][j];
    }

    queue<int> q;
    queue<int> q1;

    q.push(MM1.q0);
    q1.push(MM2.q0);

    vector<int> d(MM1.n, -1);
    d[MM1.q0] = 0;

    while (!q.empty() && !q1.empty())
    {
        int v = q.front();
        q.pop();

        int v1 = q1.front();
        q1.pop();

        cout << v << " " << v1 << endl;
        if (MM1.F[v] != MM2.F[v1])
        {
            cout << d[v] << endl;
            return 0;
        }

        for (size_t i = 0; i < MM1.m; i++)
        {
            if (d[i] == -1)
            {
                q.push(MM1.D[v][i]);
                q1.push(MM2.D[v1][i]);
                d[MM1.D[v][i]] = d[v] + 1;
            }
        }
    }

    cout << "=" << endl;

    // MM1.graphviz();
    // MM2.graphviz();
    return 0;
}
