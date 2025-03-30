#include <stdio.h>

void main(){
    int count = 0;
    scanf("%d", &count);
    
    int arr[count];

    for (size_t i = 0; i < count; i++)
    {   
        scanf("%d", &arr[i]);
    }
    
    int k = 0;
    scanf("%d", &k);

    long long sum = 0;

    for (size_t i = 0; i < k; i++)
    {   
        sum += arr[i];
    }
    
    long long max_sum = sum;

    for (size_t i = k; i < count; i++)
    {   
        sum = sum + arr[i] - arr[i-k];
        if (sum > max_sum)
        {
            max_sum = sum;
        }
    }

    printf("%lld", max_sum);
}