#include <stdio.h>

int get_closest_fib(int x)
{
    int last = 0;
    int current = 1;

    while (current + last < x)
    {

        current += last;

        last = current - last;
    }

    return x == 0 ? 0 : current;
}

void shellsort(unsigned long nel,
               int (*compare)(unsigned long i, unsigned long j),
               void (*swap)(unsigned long i, unsigned long j))
{

    for (size_t d = get_closest_fib(nel); d >= 1; d = get_closest_fib(d - 1))
    {

        for (size_t i = d; i < nel; ++i)
        {
            int j = i - d;
            while (j >= 0 && compare(j, j + d) > 0)
            {

                swap(j + d, j);
                j -= d;
            }
        }
    }
}

int z[] = {22, -3, 13, 3232, -12232, 1};

int compare(unsigned long i, unsigned long j)
{
    if (z[i] > z[j])
    {
        return 1;
    }
    if (z[i] < z[j])
    {
        return -1;
    }
    if (z[i] == z[j])
    {
        return 0;
    }
}

void swap(unsigned long i, unsigned long j)
{
    unsigned long old_i = z[i];
    z[i] = z[j];
    z[j] = old_i;
}

void main()
{
    shellsort(sizeof(z) / sizeof(int), *compare, *swap);

    for (size_t i = 0; i < sizeof(z) / sizeof(int); i++)
    {
        printf("%d ", z[i]);
    }
}