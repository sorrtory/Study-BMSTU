#include <stdio.h>
#include <stdlib.h>

// void swap(size_t i, size_t j, void *base, size_t width)
// {
//     void *old = malloc(width);
//     memcpy(old, ((char *)base + i * width), width);
//     memcpy(((char *)base + i * width), ((char *)base + j * width), width);
//     memcpy(((char *)base + j * width), old, width);
//     free(old);
// }

// void heapify(int (*compare)(const void *a, const void *b), size_t i, size_t n, void *base, size_t width)
// {
//     int l = 0, r = 0, j = i;
//     while (1 == 1)
//     {
//         l = 2 * i + 1;
//         r = l + 1;
//         j = i;

//         if (l < n && compare((char *)base + i * width, (char *)base + l * width) < 0)
//         {
//             i = l;
//         }
//         if (r < n && compare((char *)base + i * width, (char *)base + r * width) < 0)
//         {
//             i = r;
//         }
//         if (i == j)
//         {
//             break;
//         }

//         swap(i, j, base, width);
//     }
// }

struct ptr
{
    int index;
    int k;
    // int v;
};

struct q
{
    int cap;
    int count;
    struct ptr **heap;
};

void swap_ptr(struct ptr *ptr1, struct ptr *ptr2)
{
    struct ptr *ptr1_old = ptr1;
    ptr1 = ptr2;
    ptr2 = ptr1_old;
}

void Heapify(int i, int n, struct ptr **P)
{
    int l = 0, r = 0, j = i;
    while (1)
    {
        l = 2 * i + 1;
        r = l + 1;
        j = i;
        if (l < n && P[i]->k > P[l]->k)
        {
            i = l;
        }
        if (r < n && P[i]->k > P[r]->k)
        {
            i = r;
        }
        if (i == j)
        {
            break;
        }
        swap_ptr(P[i], P[j]);
        P[i]->index = i;
        P[j]->index = j;
    }
}

struct q *InitPriorityQueue(int n)
{
    struct q *q = (struct q *)malloc(sizeof(struct q));
    q->heap = (struct ptr **)malloc(sizeof(struct ptr *) * n);
    q->cap = n;
    q->count = 0;
    return q;
}

struct ptr *InitPtr(int n)
{
    struct ptr *ptr = (struct ptr *)malloc(sizeof(struct ptr));
    ptr->index = 0;
    ptr->k = n;
    return ptr;
}

void Insert(struct q *q, struct ptr *ptr)
{
    int i = q->count;
    if (i == q->cap)
    {
        printf("PEREPOLNENIYE");
    }
    else
    {
        q->count = i + 1;
        q->heap[i] = ptr;
        while (i > 0 && q->heap[(i - 1) / 2]->k < q->heap[i]->k)
        {
            swap_ptr(q->heap[(i - 1) / 2], q->heap[i]);
            q->heap[i]->index = i;
            i = (i - 1) / 2;
        }
        q->heap[i]->index = i;
        // printf("VAlue: %d, index: %d\n", q->heap[i]->k, q->heap[i]->index);
    }
}

struct ptr *ExtractMax(struct q *q)
{
    if (q->count == 0)
    {
        printf("ochered pusta");
    }
    else
    {
        struct ptr *ptr = q->heap[0];
        q->count -= 1;
        if (q->count > 0)
        {
            q->heap[0] = q->heap[q->count];
            q->heap[0]->index = 0;
            Heapify(0, q->count, q->heap);
        }
        return ptr;
    }
}

void PriorityQueueClean(struct q *q, int q_len)
{
    for (size_t i = 0; i < q_len; i++)
    {
        free(q->heap[i]);
    }
    free(q->heap);
    free(q);
}

void main()
{
    int k = 0;
    scanf("%d", &k);
    int q_len = 0;

    int n = 0;
    for (size_t i = 0; i < k; i++)
    {
        scanf("%d", &n);
        q_len += n;
    }

    int q_elem = 0;
    struct q *q = InitPriorityQueue(q_len);
    for (size_t i = 0; i < q_len; i++)
    {
        scanf("%d", &q_elem);
        Insert(q, InitPtr(q_elem));
    }

    for (size_t i = 0; i < q_len; i++)
    {
        printf("%d ", ExtractMax(q)->k);
    }

    PriorityQueueClean(q, q_len);
}