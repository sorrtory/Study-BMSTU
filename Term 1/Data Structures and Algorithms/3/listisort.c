#include <stdio.h>
#include <stdlib.h>
#define MINIMUM -2147483647

struct Elem
{
    struct Elem *prev, *next;
    int v;
};
typedef struct Elem Elem;
typedef Elem DoubleLinkedList;

DoubleLinkedList *InitDoubleLinkedList()
{
    Elem *l = (Elem *)malloc(sizeof(Elem));
    l->prev = l;
    l->next = l;
    l->v = MINIMUM;
    return l;
}

int ListEmpty(DoubleLinkedList *l)
{
    return l->next == l;
}

void InsertAfterTail(DoubleLinkedList *l, int v)
{
    // Но почему-то BeforeHead
    Elem *z = (Elem *)malloc(sizeof(Elem));
    z->next = l->next;
    z->prev = l;
    z->v = v;

    l->next->prev = z;
    l->next = z;
}

// Elem *GetElem(DoubleLinkedList *l, int depth)
// {
//     Elem *x = l;
//     for (size_t i = 0; i < depth; i++)
//     {
//         x = x->next;
//     }
//     return x;
// }

// void swap(DoubleLinkedList *l, int depth1, int depth2)
// {
//     int old_depth_1_v = GetElem(l, depth1)->v;
//     GetElem(l, depth1)->v = GetElem(l, depth2)->v;
//     GetElem(l, depth2)->v = old_depth_1_v;
// }

// void InsertSort(DoubleLinkedList *P)
// {
//     int i = 1;
//     while (GetElem(P, i) != P)
//     {
//         int loc = i - 1;
//         while (loc >= 0 && GetElem(P, loc + 1)->v < GetElem(P, loc)->v)
//         {
//             swap(P, loc + 1, loc);
//             loc--;
//         }
//         i++;
//     }
// }

void swap(Elem *a, Elem *b)
{
    int old_a_v = a->v;
    a->v = b->v;
    b->v = old_a_v;
}

void InsertSort(DoubleLinkedList *P)
{
    Elem *i = P->next->next;
    while (i != P)
    {
        Elem *loc = i->prev;
        while (loc != P && loc->next->v < loc->v)
        {
            swap(loc->next, loc);
            loc = loc->prev;
        }
        i = i->next;
    }
}

void ListDisplay(DoubleLinkedList *l)
{
    Elem *x = l->next;
    while (x != l)
    {
        printf("%d ", x->v);
        x = x->next;
    }
    printf("\n");
}

void ListClean(DoubleLinkedList *l, int n)
{
    Elem *x = l->next->next;
    for (size_t i = 0; i < n; i++)
    {
        free(x->prev);
        x = x->next;
    }
    free(l);
}

void main()
{
    // int n = 7;
    // int arr[] = {10, 9, 14, 9, 2, -1, 11};

    int n = 0;
    scanf("%d", &n);

    int arr[n];
    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &arr[i]);
    }

    DoubleLinkedList *l = InitDoubleLinkedList();
    for (size_t i = 0; i < n; i++)
    {
        InsertAfterTail(l, arr[i]);
    }
    // ListDisplay(l);
    InsertSort(l);
    ListDisplay(l);
    ListClean(l, n);
}
