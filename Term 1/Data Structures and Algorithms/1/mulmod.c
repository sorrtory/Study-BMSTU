#include <stdio.h>
// #include <string.h>

unsigned long long gorner(unsigned long long cfs[], unsigned long long n, unsigned long long x0, unsigned long long m){
    unsigned long long sum = 0; unsigned long long last = cfs[0];
    for (unsigned long long i = 1; i < n; i++){
        sum = ((last * x0)%m + (cfs[i])%m)%m;
        last = sum;
    }

    return sum;
}

void main(){
    unsigned long long a=0, b=0, m=0, cfs[64] = {0};
    // memset(cfs, 0, sizeof cfs);
    
    scanf("%ld", &a);
    scanf("%ld", &b);
    scanf("%ld", &m);

    int i = 63;
    while (b != 0)
    {
        cfs[i] = (b % 2) * a;
        b = b / 2;
        i--;
    }

    printf("%ld", gorner(cfs, 64, 2, m));

}