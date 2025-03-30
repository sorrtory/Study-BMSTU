#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define m 'z' - 'a' + 1

struct trie
{
    int v;
    struct trie *parent;
    struct trie *arcs[m];
};

struct node
{
    struct trie *x;
    int i;
};

struct trie *InitTrie()
{
    struct trie *t = (struct trie *)malloc(sizeof(struct trie));
    t->v = 0;
    t->parent = NULL;
    // t->arcs = (struct trie **)malloc(m * sizeof(struct trie *));
    for (size_t i = 0; i < m; i++)
    {
        t->arcs[i] = NULL;
    }

    return t;
}

struct node *Descend(struct trie *t, char *k, int insertmode)
{
    struct trie *x = t;
    int i = 0;
    int k_len = strlen(k);
    struct trie *y;
    while (i < k_len)
    {
        // y = x->arcs[k[i]];
        if (x->arcs[k[i]] != NULL)
        {
            y = x->arcs[k[i]];
        }
        // if (y == NULL)
        // {
        //     break;
        // }
        // if (insertmode)
        // {
        //     y->v += 1;
        // }
        // // 0x4a97358
        // x = y;
        i += 1;
    }
    struct node n = {x, i};
    struct node *np = &n;
    // struct node *n = {x, i};
    // n->x = x;
    // n->i = i;
    return np;
}

int MapEmpty(struct trie *t)
{
    if (t->arcs == NULL)
    {
        return 1;
    }

    if (t->v != 0)
    {
        return 0;
    }
    int i = 0;
    while (i < m)
    {
        if (t->arcs[i] != NULL)
        {
            return 0;
        }
        i += 1;
    }
    return 1;
}
// int MapSearch(struct trie *t, char *k)
// {
//     struct node *n = Descend(t, k);
//     return (n->i == strlen(k) && n->x->v != 0);
// }

// struct trie *Lookup(struct trie *t, char *k)
// {
//     struct node *n = Descend(t, k);
//     if (n->i != strlen(k) || n->x->v == 0)
//     {
//         printf("PANICAAAAAAAAAA");
//     }
//     return n->x;
// }

void Insert(struct trie *t, char *k, int v)
{
    int k_len = strlen(k);

    struct node *n = Descend(t, k, 1);
    printf("I1: %d\n", k_len);

    // if (n->i == strlen(k) && n->x->v != 0)
    // {
    //     printf("PANICAAAAAAAAAA");
    // }

    // while (n->i < k_len)
    // {
    //     struct trie *y = InitTrie();
    //     // y->v = n->x->v + 1;
    //     printf("Y>V: %d\n", y->v);
    //     printf("I: %d\n", n->i);
    //     n->x->arcs[k[n->i]] = y;
    //     y->parent = n->x;
    //     n->x = y;
    //     n->i += 1;
    // }
    // n->x->v = v;
}

// void Reassign(struct trie *t, char *k, int v)
// {
//     struct node *n = Descend(t, k);
//     if (n->i != strlen(k) || n->x->v == 0)
//     {
//         printf("PANICAAAAAAAAAA");
//     }
//     n->x->v = v;
// }

// void Delete(struct trie *t, char *k)
// {
//     struct node *n = Descend(t, k);
//     if (n->i != strlen(k) || n->x->v == 0)
//     {
//         printf("PANICAAAAAAAAAA");
//     }
//     n->x->v = 0;

//     while (n->x->parent != NULL && n->x->v != 0)
//     {
//         int j = 0;
//         while (j < m && n->x->arcs)
//         {
//             j += 1;
//         }
//         if (j < m)
//         {
//             break;
//         }

//         struct trie *y = n->x->parent;
//         n->i -= 1;
//         y->arcs[k[n->i]] = NULL;
//         free(n->x);
//         n->x = y;
//     }
// }

int TrieCount(struct trie *t, char *k)
{
    // struct node *n = Descend(t, k, 0);
    // return n->x->v;
    return 0;
    // return sizeof(n.x->arcs) / sizeof(struct trie *);
}

void TrieClean(struct trie *t)
{
    if (t != NULL)
    {
        for (size_t i = 0; i < sizeof(t->arcs) / sizeof(struct trie *); i++)
        {
            TrieClean(t->arcs[i]);
        }
    }

    free(t);
}

void TrieAdd(struct trie *t, char *k)
{
    for (size_t i = 0; i < strlen(k) - 1; i++)
    {
        char *k_slice;
        memcpy(k_slice, k, i);
        Insert(t, k_slice, 0);
    }

    Insert(t, k, 1);
}

void main()
{
    struct trie *t = InitTrie();
    Insert(t, "ab", 1);
    // Insert(t, "abc", 1);
    // Insert(t, "d", 1);
    printf("COUNT: %d\n", TrieCount(t, "a"));

    // char *k = (char *)malloc(100000);

    // char str[20];
    // scanf("%s", str);
    // while (strcmp(str, "END"))
    // {
    //     if (!strcmp(str, "INSERT"))
    //     {
    //         scanf("%s", k);
    //         if (MapEmpty(t))
    //         {
    //             printf("emptyboba\n");
    //             Insert(t, k, 1);
    //         }
    //         else
    //         {
    //             if (MapSearch(t, k))
    //             {
    //                 printf("Rboba\n");

    //                 Reassign(t, k, 1);
    //             }
    //             else
    //             {
    //                 printf("bobn\n");

    //                 TrieAdd(t, k);
    //             }
    //         }
    //     }

    //     if (!strcmp(str, "DELETE"))
    //     {
    //         scanf("%s", k);
    //         Delete(t, k);
    //     }

    //     if (!strcmp(str, "DELETE"))
    //     {
    //         scanf("%s", k);
    //         int p = TrieCount(t, k);
    //         printf("%d\n", p);
    //     }
    //     scanf("%s", str);
    // }
    // free(k);
    TrieClean(t);
}