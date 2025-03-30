#include <iostream>
#include <set>
#include <vector>
#include <iterator>

#define DEEP 10

using namespace std;

class ArithmeticProgression {
public:
    int start;
    int step;
    
    ArithmeticProgression(int s, int st) : start(s), step(st) {}

};

class ProgressionSet {
private:
    vector<ArithmeticProgression> progressions;
    set<int> all_numbers;

public:
    void add_progression(int start, int step) {
        progressions.emplace_back(start, step);
        for (int i = 0; i < DEEP; ++i) { 
            all_numbers.insert(start + i * step);
        }
    }

    class ConstIterator {
    private:
        set<int>::iterator iter;
    
    public:
        ConstIterator(set<int>::iterator it) : iter(it) {}
        
        const int& operator*() const {
            return *iter;
        }

        ConstIterator& operator++() {
            ++iter;
            return *this;
        }

        bool operator!=(const ConstIterator& other) const {
            return iter != other.iter;
        }
    };

    ConstIterator begin() const {
        return ConstIterator(all_numbers.begin());
    }

    ConstIterator end() const {
        return ConstIterator(all_numbers.end());
    }
};

int main() {
    ProgressionSet pset;
    pset.add_progression(1, 2);  
    pset.add_progression(2, 3);  

    for (ProgressionSet::ConstIterator it = pset.begin(); it != pset.end(); ++it) {
        cout << *it << " ";
    }

    return 0;
}
