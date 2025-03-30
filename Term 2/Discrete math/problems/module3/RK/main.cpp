#include <iostream>
#include <vector>
#include <queue>
#include <string>
#include <unordered_set>

using namespace std;

struct Automaton {
    int M, N, q0;
    vector<bool> F;
    vector<vector<int>> D;
};

struct StatePair {
    int state1, state2, length;
};


int main() {
    Automaton A1, A2;
    
    cin >> A1.M >> A1.N >> A1.q0;

    A1.F.resize(A1.N);
    A1.D.resize(A1.N, vector<int>(A1.M));
    
    for (int i = 0; i < A1.N; ++i) {
        char final_state;
        cin >> final_state;
        A1.F[i] = (final_state == '+');
        for (int j = 0; j < A1.M; ++j) {
            cin >> A1.D[i][j];
        }
    }
    A2.M = A1.M;
    cin >> A2.N >> A2.q0;
    A2.F.resize(A2.N);
    A2.D.resize(A2.N, vector<int>(A2.M));
    
    for (int i = 0; i < A2.N; ++i) {
        char final_state;
        cin >> final_state;
        A2.F[i] = (final_state == '+');
        for (int j = 0; j < A2.M; ++j) {
            cin >> A2.D[i][j];
        }
    }
    
    queue<StatePair> q;
    unordered_set<string> visited;
    
    q.push({A1.q0, A2.q0, 0});
    visited.insert(to_string(A1.q0) + "," + to_string(A2.q0));
    
    while (!q.empty()) {
        StatePair current = q.front();
        q.pop();
        
        if (A1.F[current.state1] != A2.F[current.state2]) {
            cout << current.length << endl;
            return 0;
        }
        
        for (int i = 0; i < A1.M; i++) {
            int next_state1 = A1.D[current.state1][i];
            int next_state2 = A2.D[current.state2][i];
            string next_state_pair = to_string(next_state1) + "," + to_string(next_state2);
            
            if (visited.find(next_state_pair) == visited.end()) {
                q.push({next_state1, next_state2, current.length + 1});
                visited.insert(next_state_pair);
            }
        }
    }
    
    cout << "=" << endl;
    return 0;
}
