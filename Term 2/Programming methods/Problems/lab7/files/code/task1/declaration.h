#ifndef DECLARATION_H
#define DECLARATION_H
#include <iostream>

class Stack
{
private:
    int capacity;
    int size;
    float *data;

public:
    Stack(); // Конструктор
    Stack(const Stack& stk); // Конструктор копирования
    virtual ~Stack(); // Деструктор
    Stack& operator=(const Stack& counter); // Оператор присваивания

    int getSize();
    void add(float x);
    void doubleCapacity();
    float* get(int i);
    float top();
    void addition();
    void subtraction();
    void multiplication();
};


#endif
