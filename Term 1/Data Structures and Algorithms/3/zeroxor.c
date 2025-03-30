#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct MapPair
{
    int k;
    int v;
};

struct Elem
{
    struct Elem *next;
    struct MapPair pair;
};

typedef struct Elem SingleLinkedList;

int HASH(int i, int m)
{
    return abs(i) % m;
}

struct Elem *InitSingleLinkedList()
{
    struct Elem *l = (struct Elem *)malloc(sizeof(struct Elem));
    l->next = NULL;
    l->pair.k = 0;
    l->pair.v = 0;
    return l;
}

struct Elem *InsertBeforeHead(struct Elem *l, int k, int v)
{
    struct Elem *y = (struct Elem *)malloc(sizeof(struct Elem));
    y->pair.k = k;
    y->pair.v = v;
    y->next = l;
    l = y;
    return l;
}

struct Elem *ListSearch(SingleLinkedList *l, int k)
{
    // Находим значение по ключу
    struct Elem *x = l;
    while (x != NULL && x->pair.k != k)
    {
        x = x->next;
    }
    return x;
}

SingleLinkedList **InitHashTable(int m)
{
    SingleLinkedList **t = (SingleLinkedList **)malloc(sizeof(SingleLinkedList *) * m);
    for (size_t i = 0; i < m; i++)
    {
        t[i] = InitSingleLinkedList();
    }
    return t;
}

int Lookup(SingleLinkedList **t, int k, int m)
{
    struct Elem *p = ListSearch(t[HASH(k, m)], k);
    if (p == NULL)
    {
        printf("AAAAAAA ПАНИКАА LOOKUP\n");
        return 0;
    }
    else
    {
        return p->pair.v;
    }
}

void Insert(SingleLinkedList **t, int k, int v, int m)
{
    int i = HASH(k, m);
    if (ListSearch(t[i], k) != NULL)
    {
        printf("AAAAAAA ПАНИКАА INSERT\n");
    }
    else
    {
        t[i] = InsertBeforeHead(t[i], k, v);
    }
}

void ListClean(struct Elem *l)
{
    while (l != NULL)
    {
        struct Elem *l_prev = l;
        l = l->next;
        free(l_prev);
    }
    free(l);
}

void HashTableClean(SingleLinkedList **l, int m)
{
    for (size_t i = 0; i < m; i++)
    {
        ListClean(l[i]);
    }
    free(l);
}

void main()
{
    // int n = 6; // До 100_000
    // int a[] = {0, 14, 14, 2, 2, 0};
    int n = 0;
    scanf("%d", &n);

    int m = 111111; // Размер хеш таблицы
    SingleLinkedList **l = InitHashTable(m);

    int xors_0[n];
    for (size_t i = 0; i < n; i++)
    {
        xors_0[i] = 0;
    }

    long count = 0;
    int x = 0;
    int k = 0;
    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &k);
        // k = a[i];

        x = k ^ x;

        struct Elem *p = ListSearch(l[HASH(x, m)], x);
        if (p != NULL)
        {
            xors_0[i] = xors_0[p->pair.v] + 1;
        }
        l[HASH(x, m)] = InsertBeforeHead(l[HASH(x, m)], x, i);

        count += xors_0[i];
    }

    printf("%ld", count);
    HashTableClean(l, m);
    // int n = 0;
    // int arr[n];
    // scanf("%d", &n);
    // for (size_t i = 0; i < n; i++)
    // {
    //     scanf("%d", &arr[i]);
    // }
}