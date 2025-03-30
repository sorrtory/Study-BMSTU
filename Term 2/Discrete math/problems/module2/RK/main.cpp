/*
Учебный план
На вход программы поступает число n — количество курсов (пронумерованных от 1 до n) и описание каждого курса в виде k c1 … ck — перечень курсов, предшествующих данному (если курсу ничего не предшествует, то строка состоит из числа ноль).

Если курсы образуют циклические зависимости, то следует вывести слово cycle, иначе — минимальное количество семестров, требуемых для чтения этих курсов (считаем, что число курсов в семестре неограничено).

Например, входные данные

10
0
1 1
1 2
1 3
1 4
1 4
1 6
1 7
0
3 3 5 9
*/

#include <iostream>
#include <vector>#include <iostream>
#include <vector>
#include <queue>

using namespace std;

bool topologicalSort(int n, const vector<vector<int>>& adj, vector<int>& semesterCount) {
    vector<int> inDegree(n, 0);
    for (const auto& neighbors : adj) {
        for (int neighbor : neighbors) {
            inDegree[neighbor]++;
        }
    }

    queue<int> q;
    for (int i = 0; i < n; ++i) {
        if (inDegree[i] == 0) {
            q.push(i);
            semesterCount[i] = 1; 
        }
    }

    int visitedCount = 0;

    while (!q.empty()) {
        int course = q.front();
        q.pop();
        visitedCount++;

        for (int neighbor : adj[course]) {
            inDegree[neighbor]--;
            if (inDegree[neighbor] == 0) {
                q.push(neighbor);
                semesterCount[neighbor] = semesterCount[course] + 1;
            }
        }
    }

    return visitedCount == n;
}

int main() {
    int n;
    cin >> n;
    vector<vector<int>> adj(n);

    for (int i = 0; i < n; ++i) {
        int k;
        cin >> k;
        if (k > 0) {
            adj[i].resize(k);
            for (int j = 0; j < k; ++j) {
                cin >> adj[i][j];
                adj[i][j]--; 
            }
        }
    }

    vector<int> semesterCount(n, 0);
    if (!topologicalSort(n, adj, semesterCount)) {
        cout << "cycle" << endl;
    } else {
        int maxSemester = 0;
        for (int count : semesterCount) {
            if (count > maxSemester) {
                maxSemester = count;
            }
        }
        cout << maxSemester << endl;
    }

    return 0;
}
#include <queue>

using namespace std;

bool topologicalSort(int n, const vector<vector<int>>& adj, vector<int>& semesterCount) {
    vector<int> inDegree(n, 0);
    for (const auto& neighbors : adj) {
        for (int neighbor : neighbors) {
            inDegree[neighbor]++;
        }
    }

    queue<int> q;
    for (int i = 0; i < n; ++i) {
        if (inDegree[i] == 0) {
            q.push(i);
            semesterCount[i] = 1; 
        }
    }

    int visitedCount = 0;

    while (!q.empty()) {
        int course = q.front();
        q.pop();
        visitedCount++;

        for (int neighbor : adj[course]) {
            inDegree[neighbor]--;
            if (inDegree[neighbor] == 0) {
                q.push(neighbor);
                semesterCount[neighbor] = semesterCount[course] + 1;
            }
        }
    }

    return visitedCount == n;
}

int main() {
    int n;
    cin >> n;
    vector<vector<int>> adj(n);

    for (int i = 0; i < n; ++i) {
        int k;
        cin >> k;
        if (k > 0) {
            adj[i].resize(k);
            for (int j = 0; j < k; ++j) {
                cin >> adj[i][j];
                adj[i][j]--; 
            }
        }
    }

    vector<int> semesterCount(n, 0);
    if (!topologicalSort(n, adj, semesterCount)) {
        cout << "cycle" << endl;
    } else {
        int maxSemester = 0;
        for (int count : semesterCount) {
            if (count > maxSemester) {
                maxSemester = count;
            }
        }
        cout << maxSemester << endl;
    }

    return 0;
}


