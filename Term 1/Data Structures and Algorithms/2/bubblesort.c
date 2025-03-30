#include <stdio.h>

void bubblesort(unsigned long nel,
                int (*compare)(unsigned long i, unsigned long j),
                void (*swap)(unsigned long i, unsigned long j))
{

    if (nel > 0)
    {
        for (size_t i = 0; i < nel - 1; i++)
        {

            if (i % 2 == 0)
            {
                // -->
                for (size_t j = i / 2; j < nel - 1 - i / 2; j++)
                {
                    if (compare(j, j + 1) > 0)
                    {
                        swap(j, j + 1);
                    }
                }
            }
            else
            {
                // <--
                for (size_t j = nel - 1 - i / 2; j > i / 2; j--)
                {
                    if (compare(j, j - 1) < 0)
                    {
                        swap(j, j - 1);
                    }
                }
            }
        }
    }
}

int z[] = {1, -1, -9, 3232, -12232, 22, 10000, -100, 15, 64};

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

    bubblesort(sizeof(z) / sizeof(int), *compare, *swap);
    for (size_t i = 0; i < sizeof(z) / sizeof(int); i++)
    {
        printf("%d ", z[i]);
    }
}