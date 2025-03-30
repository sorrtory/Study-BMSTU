#include <iostream>
#include <vector>

using namespace std;

template <typename INTYPE, typename OUTTYPE>
class MealyMachine
{

public:
    vector<vector<INTYPE>> D;  // переходы
    vector<vector<OUTTYPE>> F; // выходы
    int n, m;                  // количество состояний автомата n, размер входного алфавита m,

    vector<vector<INTYPE>> canonD;  // переходы
    vector<vector<OUTTYPE>> canonF; // выходы
    MealyMachine(int n, int m)
    {
        vector<vector<INTYPE>> D(n, vector<INTYPE>(m));
        this->D = D;
        this->canonD = D;

        vector<vector<OUTTYPE>> F(n, vector<OUTTYPE>(m));
        this->F = F;
        this->canonF = F;

        this->n = n;
        this->m = m;
    }
};

void dfs(int q, const MealyMachine<int, string> &MM, vector<int> &canon)
{
    static int qCount = 0;
    canon[q] = qCount;
    qCount += 1;
    for (size_t xIndex = 0; xIndex < MM.m; xIndex++)
        if (canon[MM.D[q][xIndex]] == -1)
            dfs(MM.D[q][xIndex], MM, canon);
}

int main()
{
    int n, m;
    cin >> n >> m;

    int q0;
    cin >> q0;

    int num;
    string signal;
    MealyMachine<int, string> MM(n, m);
    for (auto &&i : MM.D)
        for (auto &&j : i)
            cin >> j;

    for (auto &&i : MM.F)
        for (auto &&j : i)
            cin >> j;

    vector<int> canon(n, -1);
    dfs(q0, MM, canon);

    for (size_t i = 0; i < n; i++)
    {
        for (size_t j = 0; j < m; j++)
            MM.canonD[canon[i]][j] = canon[MM.D[i][j]];
        for (size_t j = 0; j < m; j++)
            MM.canonF[canon[i]][j] = MM.F[i][j];
    }

    cout << n << endl;
    cout << m << endl;
    cout << 0 << endl;

    for (auto &&i : MM.canonD)
    {
        for (auto &&j : i)
        {
            cout << j << " ";
        }
        cout << endl;
    }

    for (auto &&i : MM.canonF)
    {
        for (auto &&j : i)
        {
            cout << j << " ";
        }
        cout << endl;
    }
    return 0;
}
