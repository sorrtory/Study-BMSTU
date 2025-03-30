#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define MINIMUM -2147483648



int max(int a, int b){
    if (a > b)
    {
        return a;
    }
    else
    {
        return b;
    }
}


int query(int *T , int v, int l , int r, int a, int b){
    if (l > r)
    {
        return MINIMUM;
    }
    if (l == a && r == b){
        return T[v];
    }
    else
    {
        int m = (a+b)/2;
        if (r <= m)
        {
            return query(T, 2*v, l, r, a, m);
        }
        else if (l > m)
        {
            return query(T, 2*v+1, l, r, m+1, b);
        }
        else
        {
            return max(query(T, 2*v, l, m, a, m), query(T, 2*v+1, m+1, r, m+1, b));
        }
    }
}

int SegmentTree_Query(int *T , int n , int l , int r ){
    return query(T, 1, l , r, 0, n-1);
}
void build(int *nums, int v, int a, int b, int *T){
    if (a == b)
    {
        T[v] = nums[a];
        
    }
    else
    {
        int m = (a+b)/2;
        build(nums, 2*v, a, m, T);
        build(nums, 2*v + 1, m+1, b, T);
        T[v] = max(T[2*v], T[2*v + 1]);

    }
    
}
int * SegmentTree_Build(int *nums, int n){
    int * T = (int *)malloc(n * sizeof(int) * 4);
    build(nums, 1, 0, n - 1, T);
    return T;
}

void update(int v, int i, int new_val, int a, int b, int * T){
    if (a == b)
    {
        T[v] = new_val;
    }
    else
    {
        int m = (a+b)/2;
        if (i <= m)
        {
            update(v*2, i, new_val, a, m, T);
        }
        else
        {
            update(v*2 + 1, i, new_val, m+1, b, T);
        }
        T[v] = max(T[v*2], T[v*2+1]);
    }
}

void SegmentTree_Update(int i, int new_val, int n, int * T){
    update(1, i, new_val, 0, n - 1, T);
}

void main()
{

    int n = 0;
    scanf("%d", &n);

    int nums[n];

    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &nums[i]);
    }
    int *T = SegmentTree_Build(nums, n);

    char str[4];
    int l = 0, r = 0, i = 0, v = 0;
    scanf("%s", str);
    while (str[0] != 'E')
    {
        if (str[0] == 'U')
        {   
            scanf("%d", &i);
            scanf("%d", &v);
            SegmentTree_Update(i, v, n, T);

            
        }
        else if (str[0] == 'M')
        {
            scanf("%d", &l);
            scanf("%d", &r);
            printf("%d\n", SegmentTree_Query(T, n, l, r));

        }
        scanf("%s", str);
    }
    free(T);
}