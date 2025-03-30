#include <stdio.h>

int vol = 0;

void find_sums(long long current_sum, size_t j, size_t len_nums, int *nums){

    if (current_sum && !(current_sum & (current_sum - 1)))
    {   
        vol++;
    }

    for (size_t i = j + 1; i < len_nums; i++)
    {   
        find_sums(current_sum + nums[i], i, len_nums, nums);
    }

    
}


void main()
{
    int n = 0;
    scanf("%d", &n);

    int nums[24];
    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &nums[i]);
    }
    
    for (size_t i = 0; i < n; i++)
    {
        find_sums(nums[i], i, n, nums);

    }

    printf("%d", vol);
}