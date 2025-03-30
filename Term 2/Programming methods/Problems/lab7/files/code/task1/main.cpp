/*
Вариант 9
Стековая машина, оперирующая вещественными числами, с операциями:
1. получение количества чисел в стеке;
2. добавление вещественного числа на стек;
3. получение ссылки на i-ое число, считая от вершины стека;
4. сложение, умножение и вычитание двух чисел на вершине стека (числа
удаляются со стека, результат добавляется в стек).
*/


#include "implementation.cpp"

void print_stack(Stack& stk, char n){
    int i = stk.getSize();
    std::cout << "Stk" << n << ": ";
    for (size_t i = 0; i < stk.getSize(); i++)
    {
        std::cout << *stk.get(i) << " ";        
    }
    std::cout << std::endl;

}

int main()
{
    Stack stk, stk2;
    stk.add(10);
    stk.add(9);
    stk.add(8);
    print_stack(stk, '1');
    print_stack(stk2, '2');
    stk2 = stk; // Assigment (purposely reversed)
    std::cout << "Assigment stk2 = stk" << std::endl;
    print_stack(stk2, '2');
    auto stk3 = stk; // Copy
    std::cout << "Copy stk to stk3" << std::endl;
    std::cout << "stk top: " << stk.top() << std::endl;
    stk2.multiplication();
    std::cout << "stk2 top: " << stk2.top() << std::endl;
    std::cout << "stk2 top: " << stk2.top() << std::endl;
    print_stack(stk, '1');
    print_stack(stk2, '2');
    print_stack(stk3, '3');
    return 0;
}
