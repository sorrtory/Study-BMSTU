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

    MealyMachine(int n, int m)
    {
        vector<vector<INTYPE>> D(n, vector<INTYPE>(m));
        this->D = D;

        vector<vector<OUTTYPE>> F(n, vector<OUTTYPE>(m));
        this->F = F;

        this->n = n;
        this->m = m;
    }

    void graphviz()
    {
        cout << "digraph {\n\trankdir = LR\n";

        for (size_t j = 0; j < n; j++)
            for (size_t i = 0; i < m; i++)
                cout << "\t" << j << " -> " << D[j][i] << " [label = \"" << (char)('a' + i) << "(" << F[j][i] << ")\"]\n";
        cout << "}\n";
    }
};

int main(int argc, char const *argv[])
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
    MM.graphviz();
    return 0;
}
