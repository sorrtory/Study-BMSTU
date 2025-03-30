#ifndef MYNUMBER_H
#define MYNUMBER_H
// Последовательность целых 32-разрядных чисел, понимаемая как одно большое двоичное число, с константным однонаправленным итератором по длинам непрерывных последовательностей нулевых битов в нём.
#include <iostream>
#include <vector>
#include <iterator>
#include <memory>

using namespace std;
class MyNumber
{
private:
    long long int x;
public:
    MyNumber(long long int x);
    string getBits();
};

MyNumber::MyNumber(long long int x)
{
    this->x = x;
}

inline string MyNumber::getBits()
{
    string s = "";
    while (x > 0)
    {
        s = to_string(x % 2) + s;
        x /= 2;
    }
    
    return s;
}
template<typename ValueType>
class Iterator: public std::iterator<std::output_iterator_tag, ValueType>
{
    friend class Numbers;
private:
    Iterator(ValueType* p);
// public:
//     using iterator_category = std::forward_iterator_tag;
//     using value_type = int;
//     using difference_type = int;
//     using pointer = int*;
//     using reference = int&;
public:

    Iterator(const Iterator &it);

    bool operator!=(Iterator const& other) const;
    bool operator==(Iterator const& other) const; //need for BOOST_FOREACH
    typename Iterator::reference operator*() const;
    Iterator& operator++();
    Iterator operator++(ValueType);
private:
    ValueType* p;
};

template<typename ValueType>
Iterator<ValueType>::Iterator(ValueType *p) :
    p(p)
{

}

template<typename ValueType>
Iterator<ValueType>::Iterator(const Iterator& it) :
    p(it.p)
{

}

template<typename ValueType>
bool Iterator<ValueType>::operator!=(Iterator const& other) const
{
    return p != other.p;
}

template<typename ValueType>
bool Iterator<ValueType>::operator==(Iterator const& other) const
{
    return p == other.p;
}

template<typename ValueType>
typename Iterator<ValueType>::reference Iterator<ValueType>::operator*() const
{
    return *p;
}

template<typename ValueType>
Iterator<ValueType> &Iterator<ValueType>::operator++()
{
    ++p;
    return *this;
}
template<typename ValueType>
Iterator<ValueType> Iterator<ValueType>::operator++(ValueType) {
    Iterator tmp(*this); 
    operator++(); 
    return tmp;
    }
class Numbers
{
private:
    vector<string> dataBits;
    std::unique_ptr<int[]> data;
    size_t size = 0;

public:

    void add(long long x);
    void zeroes();
    typedef Iterator<const int> const_iterator;
    Numbers(std::initializer_list<long long> values);

    const_iterator begin() const;
    const_iterator end() const;

};

void Numbers::add(long long x)
{
    dataBits.push_back(MyNumber(x).getBits());
    zeroes();
}

void Numbers::zeroes()
{
    int c = 0;
    vector<int> nums;
    for (auto &&num : dataBits)
    {
        for (auto &&chr : num)
        {
            if (chr == '0')
            {
                c += 1;
            } else
            {
                nums.push_back(c);
                c = 0;
            }
        }
    }
    copy(nums.begin(), nums.end(), data.get());
    size = nums.size();
}

Numbers::Numbers(std::initializer_list<long long> values)
{
    for (auto &&i : values)
    {
        add(i);        
    }
    
}

Numbers::const_iterator Numbers::begin() const
{
    return const_iterator(data.get());
}
Numbers::const_iterator Numbers::end() const
{
    return const_iterator(data.get() + size);
}
#endif