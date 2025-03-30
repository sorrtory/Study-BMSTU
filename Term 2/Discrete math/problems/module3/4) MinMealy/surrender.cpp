#include <iostream>
#include <vector>

using namespace std;

class DSU
{
public:
    vector<int> parent;
    vector<int> rank; // depth

    DSU(int v)
    {
        for (size_t i = 0; i < v; i++)
        {
            parent.push_back(i);
            rank.push_back(0);
        }

        // parent[v] = v;
        // rank[v] = 0;
    }

    int find_set(int v)
    {
        if (v == parent[v])
            return v;
        return parent[v] = find_set(parent[v]);
    }

    void union_sets(int a, int b)
    {
        a = find_set(a);
        b = find_set(b);
        if (a != b)
        {
            if (rank[a] < rank[b])
                swap(a, b);
            parent[b] = a;
            if (rank[a] == rank[b])
                ++rank[a];
        }
    }
};

template <typename INTYPE, typename OUTTYPE>
class MealyMachine
{

public:
    vector<vector<INTYPE>> D;  // переходы
    vector<vector<OUTTYPE>> F; // выходы
    int n, m, q0;              // количество состояний автомата n, размер входного алфавита m, номер начального состояния q0

    vector<vector<INTYPE>> canonD;  // переходы
    vector<vector<OUTTYPE>> canonF; // выходы
    MealyMachine(int n, int m, int q0)
    {
        vector<vector<INTYPE>> D(n, vector<INTYPE>(m));
        this->D = D;
        this->canonD = D;

        vector<vector<OUTTYPE>> F(n, vector<OUTTYPE>(m));
        this->F = F;
        this->canonF = F;

        this->n = n;
        this->m = m;
        this->q0 = q0;
    }
    void graphviz()
    {
        canonic();

        cout << "digraph {\n\trankdir = LR\n";

        for (size_t j = 0; j < n; j++)
            for (size_t i = 0; i < m; i++)
                cout << "\t" << j << " -> " << canonD[j][i] << " [label = \"" << (char)('a' + i) << "(" << canonF[j][i] << ")\"]\n";
        cout << "}\n";
    }
    void dfs(int q, vector<int> &canon)
    {
        static int qCount = 0;
        canon[q] = qCount;
        qCount += 1;
        for (size_t xIndex = 0; xIndex < this->m; xIndex++)
            if (canon[this->D[q][xIndex]] == -1)
                dfs(this->D[q][xIndex], canon);
    }
    void canonic()
    {
        vector<int> canon(n, -1);
        dfs(q0, canon);

        for (size_t i = 0; i < n; i++)
        {
            for (size_t j = 0; j < m; j++)
                this->canonD[canon[i]][j] = canon[this->D[i][j]];
            for (size_t j = 0; j < m; j++)
                this->canonF[canon[i]][j] = this->F[i][j];
        }
    }

    void Split1(int &m, vector<int> &π)
    {
        m = n;
        DSU Q(n);
        for (size_t q1 = 0; q1 < n - 1; q1++)
        {
            for (size_t q2 = q1 + 1; q2 < n; q2++)
            {
                if (Q.find_set(q1) != Q.find_set(q2))
                {
                    bool eq = true;
                    for (size_t i = 0; i < this->m; i++)
                    {
                        if (F[q1][i] != F[q2][i])
                        {
                            eq = false;
                            break;
                        }
                    }
                    if (eq)
                    {
                        Q.union_sets(q1, q2);
                        m -= 1;
                    }
                }
            }
        }
        for (size_t i = 0; i < n; i++)
        {
            π[i] = Q.find_set(i);
        }
    }
    void Split(int &m, vector<int> &π)
    {
        m = n;
        DSU Q(n);
        for (size_t q1 = 0; q1 < n - 1; q1++)
        {
            for (size_t q2 = q1 + 1; q2 < n; q2++)
            {
                if (π[q1] == π[q2] && Q.find_set(q1) != Q.find_set(q2))
                {
                    bool eq = true;
                    for (size_t i = 0; i < this->m; i++)
                    {

                        if (π[D[q1][i]] != π[D[q2][i]])
                        {
                            eq = false;
                            break;
                        }
                    }
                    if (eq)
                    {
                        Q.union_sets(q1, q2);
                        m -= 1;
                    }
                }
            }
        }
        for (size_t i = 0; i < n; i++)
        {
            π[i] = Q.find_set(i);
        }
    }
    MealyMachine<INTYPE, OUTTYPE> AufenkampHohn()
    {
        int m1, m2;
        vector<int> π(n);
        Split1(m1, π);
        while (1)
        {
            Split(m2, π);
            if (m1 == m2)
            {
                break;
            }
            m1 = m2;
        }
        MealyMachine<INTYPE, OUTTYPE> MM(m1, m, -1);
        int q1;
        vector<int> Qold(n);
        vector<int> Qnew(n);
        int c = 0;
        for (size_t i = 0; i < n; i++)
        {
            q1 = π[i];
            if (q1 == i)
            {
                Qold[c] = i;
                Qnew[i] = c;
                c++;
            }
        }

        for (size_t i = 0; i < m1; i++)
        {
            for (size_t j = 0; j < m; j++)
            {
                MM.D[i][j] = Qnew[π[D[Qold[i]][j]]];
                MM.F[i][j] = F[Qold[i]][j];
            }
        }
        MM.q0 = Qnew[π[q0]];
        return MM;
    }
};

int main()
{
    int n, m;
    cin >> n >> m;

    int q0;
    cin >> q0;

    int num;
    string signal;
    MealyMachine<int, string> MM(n, m, q0);
    for (auto &&i : MM.D)
        for (auto &&j : i)
            cin >> j;

    for (auto &&i : MM.F)
        for (auto &&j : i)
            cin >> j;
    MealyMachine<int, string> MMM = MM.AufenkampHohn();
    MMM.graphviz();
}