#ifndef NUMBERS_H
#define NUMBERS_H

#include <iostream>     // std::cout
#include <iterator>     // std::iterator, std::input_iterator_tag
#include <vector>
#include <initializer_list>


class MyIterator
{
  int* p;
public:
  MyIterator(int* x) :p(x) {}
  MyIterator(const MyIterator& mit) : p(mit.p) {}
  MyIterator& operator++() {++p;return *this;}
  MyIterator operator++(int) {MyIterator tmp(*this); operator++(); return tmp;}
  bool operator==(const MyIterator& rhs) const {return p==rhs.p;}
  bool operator!=(const MyIterator& rhs) const {return p!=rhs.p;}
  int& operator*() {return *p;}
};

using namespace std;

inline string getBits(long long x)
{
    string s = "";
    while (x > 0)
    {
        s = to_string(x % 2) + s;
        x /= 2;
    }
    
    return s;
}

template <typename T>
class Numbers
{
private:
    vector<string> dataBits;
    T* store;
    size_t size;
    typedef T* iterator;
    typedef const T* const_iterator;

public:
    void add(T x);
    void updateIter();
    string get();
    Numbers(std::initializer_list<double> values);
    ~Numbers();
    iterator begin() { return &store[0]; }
    const_iterator begin() const { return &store[0]; }
    iterator end() { return &store[size]; }
    const_iterator end() const { return &store[size]; }
};
template <typename T>
Numbers<T>::~Numbers(){
    if (store)
    {
        delete[] store;
    }
    
}
template <typename T>
string Numbers<T>::get(){
    string s = "";
    for (auto &&i : dataBits)
        s += i;
    return s;
}

template <typename T>
void Numbers<T>::add(T x)
{
    dataBits.push_back(getBits(x));
    updateIter();
}

template <typename T>
Numbers<T>::Numbers(std::initializer_list<double> values)
{
    for (auto &&x : values)
        dataBits.push_back(getBits(x));
    updateIter();
    
}

template <typename T>
void Numbers<T>::updateIter()
{
    int c = 0;
    vector<int> nums;
    for (auto &&num : dataBits)
    {
        for (auto &&chr : num)
        {
            if (chr == '0')
                c += 1;
            else
            {   
                if (c != 0)
                    nums.push_back(c);
                c = 0;
            }
        }
    }
    if (c != 0)
        nums.push_back(c);
    
    size = nums.size();
    
    store = new int[size];
    copy(nums.begin(), nums.end(), store);

}

#endif