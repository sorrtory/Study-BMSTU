#include <stdio.h>
#include <string.h>
#include <stdlib.h>

unsigned long long max_fib(unsigned long long x){
    unsigned long long tfib = 0, tfib_2 = 0, tfib_1 = 1;

    while (tfib_1 <= x)
    {  
        tfib = tfib_2 + tfib_1;
        tfib_2 = tfib_1;
        tfib_1 = tfib;
    }
    return tfib_2;
}
unsigned long long len_fib(unsigned long long x){
    unsigned long long i = 0;
    unsigned long long tfib = 0, tfib_2 = 0, tfib_1 = 1;

    while (tfib_1 <= x)
    {  
        tfib = tfib_2 + tfib_1;
        tfib_2 = tfib_1;
        tfib_1 = tfib;
        i++;
    }
    return i;
}

unsigned long long fib_i(unsigned long long x){
    unsigned long long i = 0;
    unsigned long long tfib = 0, tfib_2 = 0, tfib_1 = 1;

    while (i != x)
    {  
        tfib = tfib_2 + tfib_1;
        tfib_2 = tfib_1;
        tfib_1 = tfib;
        i++;
    }
    return tfib;
}

void main(){
    unsigned long long x = 0;
    scanf("%ld", &x);
    
    if (x <= 1) {
        printf("%ld", x);
    }
    else
    {
        unsigned long long mb = max_fib(x);        
        unsigned long long i = len_fib(x) - 1;
        while (i > 0)
        {
            // printf("\n%ld %ld\n", fib_i(i), mb);
            if (mb == fib_i(i)){
                printf("1");
                x -= mb;
                mb = max_fib(x);
            }
            else{
                printf("0");
            }
            i--;
        }
    }
}