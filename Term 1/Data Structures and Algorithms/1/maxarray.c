#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int maxarray(void *base, size_t nel, size_t width,
             int (*compare)(void *a, void *b))
{
    void *mx = malloc(width);
    int index = 0;

    memcpy(mx, base, width);
    for (size_t i = 1; i < nel; i++)
    {
        void *value = (void *)((size_t)base + width * i);

        if (compare(value, mx) > 0)
        {
            memcpy(mx, value, width);
            index = i;
        }
    }

    free(mx);
    return index;
}

int comp(const int *i, const int *j)
{
    return *i - *j;
}
void main()
{
    int num[10] = {
        1, 3, 6, 5, 8, 7, 9, 6, 2, 0};
    int mx = maxarray(num, 10, sizeof(int), comp);
    printf("\nid: %d  vlu:%d", mx, num[mx]);
}

