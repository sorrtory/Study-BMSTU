#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void swap(size_t i, size_t j, void *base, size_t width)
{
    void *old = malloc(width);
    memcpy(old, ((char *)base + i * width), width);
    memcpy(((char *)base + i * width), ((char *)base + j * width), width);
    memcpy(((char *)base + j * width), old, width);
    free(old);
}

void heapify(int (*compare)(const void *a, const void *b), size_t i, size_t n, void *base, size_t width)
{
    int l = 0, r = 0, j = i;
    while (1 == 1)
    {
        l = 2 * i + 1;
        r = l + 1;
        j = i;

        if (l < n && compare((char *)base + i * width, (char *)base + l * width) < 0)
        {
            i = l;
        }
        if (r < n && compare((char *)base + i * width, (char *)base + r * width) < 0)
        {
            i = r;
        }
        if (i == j)
        {
            break;
        }

        swap(i, j, base, width);
    }
}

void buildheap(int (*compare)(const void *a, const void *b), size_t nel, void *base, size_t width)
{
    int i = nel / 2 - 1;
    while (i >= 0)
    {
        heapify(compare, i, nel, base, width);
        i--;
    }
}

void hsort(void *base, size_t nel, size_t width,
           int (*compare)(const void *a, const void *b))
{
    buildheap(compare, nel, base, width);
    int i = nel - 1;
    while (i > 0)
    {
        swap(0, i, base, width);
        heapify(compare, 0, i, base, width);
        i--;
    }
}

int compare(const void *a, const void *b)
{
    int count_a = 0;
    int k = 0;
    char *a_pointer = *(char **)a;
    while (*(a_pointer + k))
    {
        if (*(a_pointer + k) == 'a')
        {
            count_a++;
        }

        k++;
    }

    int count_b = 0;
    k = 0;
    char *b_pointer = *(char **)b;
    while (*(b_pointer + k))
    {
        if (*(b_pointer + k) == 'a')
        {
            count_b++;
        }

        k++;
    }

    return count_a - count_b;
}

void main()
{
    int n = 0;
    scanf("%d", &n);

    char **str = (char **)malloc(n * sizeof(char *));

    for (size_t i = 0; i < n; i++)
    {
        str[i] = (char *)malloc(1000 * sizeof(char *));
        scanf("%s", str[i]);
    }

    hsort(str, n, sizeof(char *), compare);

    for (size_t i = 0; i < n; i++)
    {
        printf("%s\n", str[i]);
    }

    for (size_t i = 0; i < n; i++)
    {
        free(str[i]);
    }

    free(str);
}