#include <stdio.h>
#include <stdlib.h>
#include <string.h>

unsigned long _binsearch(unsigned long nel, int (*compare)(unsigned long i), unsigned long L, unsigned long R)
{
    unsigned long n = L + (R - L) / 2;
    switch (compare(n))
    {
    case 1:
        if (n == R)
        {
            return nel;
        }
        else
        {
            return _binsearch(nel, compare, L, n);
        }
        break;
    case 0:
        return n;
        break;
    case -1:
        if (n == L)
        {
            return nel;
        }
        else
        {
            return _binsearch(nel, compare, n, R);
        }
        break;
    }
}

unsigned long binsearch(unsigned long nel, int (*compare)(unsigned long i))
{
    return _binsearch(nel, compare, 0, nel);
}

int comp(const int i)
{
    int a = 6;
    if (i < a)
    {
        return -1;
    }
    if (i == a)
    {
        return 0;
    }
    if (i > a)
    {
        return 1;
    }
}
void main()
{
    int num[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    unsigned long mx = binsearch(10, comp);
    // int mx = 10/3;
    printf("\nid: %d", mx);
}
