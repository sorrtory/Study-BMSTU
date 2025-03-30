#define INITIALSTACKCAPACITY 5
#include "declaration.h"
Stack::Stack(){
    Stack::capacity = INITIALSTACKCAPACITY;
    Stack::data = new float[INITIALSTACKCAPACITY];
    Stack::size = 0;
}

Stack::~Stack(){
    delete[] data;
    std::cout << "Stack was deleted" << std::endl;
}

Stack& Stack::operator=(const Stack& stk)
{
    float* data_new = new float[stk.capacity];
    for (size_t i = 0; i < stk.size; i++)
    {
        data_new[i] = stk.data[stk.size - i - 1];
    }
    data = data_new;
    size = stk.size;
    capacity = stk.capacity;

    return *this;
}

Stack::Stack(const Stack &stk){
    float* data_new = new float[stk.capacity];
    for (size_t i = 0; i < stk.size; i++)
    {
        data_new[i] = stk.data[i];
    }
    data = data_new;
    size = stk.size;
    capacity = stk.capacity;
}

int Stack::getSize(){
    return this->size;
    
}

void Stack::doubleCapacity(){
    float * data_new = new float[this->capacity*2];
    for (size_t i = 0; i < this->size; i++)
    {
        data_new[i] = this->data[i];
    }
    delete[] this->data;
    this->data = data_new;
    this->capacity *= 2;
}

void Stack::add(float x){
    if (capacity <= size + 1)
        doubleCapacity();
    
    data[size] = x;
    size += 1;

}

float Stack::top() {
    if (size == 0)
    {
        std::cerr << "Stack is empty" << std::endl;
        return 0;
    }
    size -= 1;
    return data[size];
}

void Stack::addition(){
    Stack::add(Stack::top() + Stack::top());
}

void Stack::subtraction(){
    Stack::add(-Stack::top() + Stack::top());
}
void Stack::multiplication(){
    Stack::add(Stack::top() * Stack::top());

}

float* Stack::get(int i){
    if (size < i)
    {
        std::cerr << "Stack has not enough data" << std::endl;
        return NULL;
    }
    return &data[size - 1 - i];
}