
#include <stdio.h>

long gorner(long cfs[], long n, long x0){
    long sum = 0; long last = cfs[0];
    for (long i = 1; i < n; i++){
        sum = last * x0 + cfs[i];
        last = sum;
    }

    return sum;
}
        


void main(){
    /*
    5
    -3
    -2 -2 -3 -2 3 -2
    */
    
    long n, x0;
    
    scanf("%ld", &n);
    scanf("%ld", &x0);
    
    n += 1;
    long cfs[n], cfs_d[n];

    for (long i = 0; i < n; i++){
        scanf("%ld", &cfs[i]);
        cfs_d[i] = cfs[i] * (n-i-1);
        
    }



    printf("%ld %ld", gorner(cfs, n, x0), gorner(cfs_d, n-1, x0));
    
}
