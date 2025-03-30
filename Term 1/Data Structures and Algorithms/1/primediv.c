#include <stdio.h>
#include <math.h>

long long abss(long long x){

    return (x >= 0) ? x : -x;    
}

void main(){
    long long x = 0;
    scanf("%lld", &x);

    long long ax = abss(x);
    int fac_len = (long long)sqrt(ax);
    
    int factors[fac_len];
    factors[0] = 0; factors[1] = 0;
    for (size_t i = 2; i <= fac_len; i++)
    {
        factors[i] = 1;
    }
    

    for (size_t i = 2; (i*i) <= fac_len; i++)
    {
        if (factors[i])
        {   
            for (size_t j = i*i; j <= fac_len; j+=i)
            {
                factors[j] = 0;
            }
            
        }

    }
    long long max_factor = ax;
    for (size_t i = 0; i <= sqrt(max_factor); i++)
    {   
        if (factors[i] && max_factor % i == 0)
        {   
            long long temp_factor = max_factor;
            // printf("tf %lld\n", temp_factor);
            while (temp_factor % i == 0)
            {
                temp_factor /= i;
            }

            if (temp_factor == 1)
            {
                max_factor = i;
            }
            else{
                max_factor /= i;
            }

            i = 0;
        }
        
    }
    
    printf("%lld", max_factor);

}