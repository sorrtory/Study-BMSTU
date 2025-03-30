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
    return i % m;
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
        // printf("AAAAAAA ПАНИКАА LOOKUP\n");
        return 0;
    }

    return p->pair.v;
}

void Insert(SingleLinkedList **t, int k, int v, int m)
{
    int i = HASH(k, m);
    if (ListSearch(t[i], k) != NULL)
    {
        // printf("AAAAAAA ПАНИКАА INSERT\n");
        // return;
    }

    t[i] = InsertBeforeHead(t[i], k, v);
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
    int m = 0; // Размер хеш таблицы
    scanf("%d", &m);
    SingleLinkedList **l = InitHashTable(m);

    int k = 0, v = 0, i = 0;
    char str[20];
    scanf("%s", str);
    while (strcmp(str, "END"))
    {
        if (!strcmp(str, "ASSIGN"))
        {
            scanf("%d", &k);
            scanf("%d", &v);
            Insert(l, k, v, m);
        }
        else if (!strcmp(str, "AT"))
        {
            scanf("%d", &i);
            printf("%d\n", Lookup(l, i, m));
        }
        scanf("%s", str);
    }

    HashTableClean(l, m);
}