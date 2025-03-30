#ifndef NUMS_H
#define NUMS_H

#include <vector>
#include <cmath>
#include <iostream>

using namespace std;


struct Triplet
{
    int *data;
    Triplet(){data = new int[3];}
    Triplet(int a, int b, int c) : Triplet(){ data[0] = a; data[1] = b; data[2] = c; }
    Triplet(const Triplet& trp): Triplet(trp.data[0], trp.data[1], trp.data[2]){}
    ~Triplet(){if (data) delete[] data;}
    int* operator*(){return data;}  
    Triplet& operator=(const Triplet& trp) {
        if (this == &trp) return *this;
        delete[] data;
        data = new int[3];
        copy(trp.data, trp.data + 3, data);
        return *this;
    }  
};


class MyIterator
{
  Triplet* p;
public:
  MyIterator(Triplet* x) :p(x) {}
  MyIterator(const MyIterator& mit) : p(mit.p) {}
  MyIterator& operator++() {++p;return *this;}
  MyIterator operator++(int) {MyIterator tmp(*this); operator++(); return tmp;}
  bool operator==(const MyIterator& rhs) const {return p==rhs.p;}
  bool operator!=(const MyIterator& rhs) const {return p!=rhs.p;}
  
  Triplet& operator*() {return *p;}
  Triplet* operator->() {return p;}
};



class Nums
{
public: 
    typedef MyIterator iterator;

private:
    vector<int> values;
    Triplet* iterStore;
    size_t iterSize = 0; 
    bool condition(const int a, const int b, const int c){
        bool isMet = false;
        int x = max(max(a, b), max(b, c));
        if (x == a)
            isMet = (pow(a, 2) == pow(b, 2) + pow(c, 2));
        if (x == b)
            isMet = (pow(b, 2) == pow(a, 2) + pow(c, 2));
        if (x == c)
            isMet = (pow(c, 2) == pow(a, 2) + pow(b, 2));
        
        return isMet;
    }
    void updateStore(){
        vector<Triplet> str;
        for (size_t i = 0; i < values.size() - 2; i++)
            for (size_t j = i+1; j < values.size() - 1; j++)
                for (size_t k = j+1; k < values.size(); k++)
                    if (condition(values[i], values[j], values[k]))
                        str.push_back(Triplet {values[i], values[j], values[k]});

        iterSize = str.size();
        iterStore = new Triplet[iterSize];
        copy(str.begin(), str.end(), iterStore);
    }
    
public:
    Nums(initializer_list<int> xs): values(xs) {updateStore();};
    ~Nums(){ if (iterStore) delete [] iterStore;}
    iterator begin() { return MyIterator(iterStore); }
    iterator end() { return MyIterator(iterStore + iterSize); }

};


#endif