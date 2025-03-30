#include <stdio.h>

unsigned long peak(unsigned long nel,
                   int (*less)(unsigned long i, unsigned long j))
{

    if (nel == 1 || less(0, 1) == 0)
    {
        return 0;
    }
    else if (less(nel - 1, nel - 2) == 0)
    {
        return nel - 1;
    }
    else
    {
        for (size_t i = 1; i < nel - 2; i++)
        {
            if (less(i, i - 1) == 0 && less(i, i + 1) == 0)
            {
                return i;
                break;
            }
        }
    }
}
// int num[10] = {3, 5, 3, 4, 5, 6, 3, 8, 9, 7};
int num[] = {} int less(const int i, const int j)
{
    if (num[i] < num[j])
    {
        return 1;
    }

    else
    {
        return 0;
    }
}
void main()
{
    unsigned long mx = peak(1, less);
    // int mx = 10/3;
    printf("\nid: %lld", mx);
}