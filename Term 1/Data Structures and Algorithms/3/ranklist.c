#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct MapPair
{
    int k;
    char *v;
};

struct MapElem
{
    struct MapPair pair;
    struct MapElem **next;
    int *order;
};

struct MapElem *InitSkipList(int m)
{
    struct MapElem *l = (struct MapElem *)malloc(sizeof(struct MapElem));

    l->next = (struct MapElem **)malloc(sizeof(struct MapElem *) * m);
    int i = 0;
    while (i < m)
    {
        l->next[i] = NULL;
        i++;
    }

    l->order = (int *)malloc(sizeof(int) * m);
    i = 0;
    while (i < m)
    {
        l->order[i] = 0;
        i++;
    }

    l->pair.k = -1111111111;
    l->pair.v = NULL;
}

struct MapElem *Succ(struct MapElem *x)
{
    return x->next[0];
}

void Skip(struct MapElem *l, int m, int k, struct MapElem **p)
{

    struct MapElem *x = l;
    int i = m - 1;
    while (i >= 0)
    {
        while (x->next[i] != NULL && x->next[i]->pair.k < k)
        {
            x = x->next[i];
        }
        p[i] = x;
        i -= 1;
    }
}

int SkippyRank(struct MapElem *l, int m, int k)
{
    // struct MapElem **p = (struct MapElem **)malloc(sizeof(struct MapElem *));
    // Skip(l, m, k, p);
    // struct MapElem *x = Succ(p[0]);
    // if (x == NULL)
    // {
    //     printf("AAAAAA СПАСАЙТЕСЬ КТО МОЖЕТ MapSearchRank");
    //     return -1;
    // }
    // else
    // {
    //     return x->pair.k;
    // }
    // free(p);
    int rank = -1;

    if (k != -1111111111)
    {
        struct MapElem *x = l;
        rank = 0;
        int i = m - 1;
        while (i >= 0)
        {
            while (x->next[i] != NULL && x->next[i]->pair.k < k)
            {
                rank += x->order[i];
                x = x->next[i];
            }
            i -= 1;
        }
    }
    return rank;
}

char *Lookup(struct MapElem *l, int m, int k)
{
    // struct MapElem **p = (struct MapElem **)malloc(sizeof(struct MapElem *));
    struct MapElem *p[m];
    Skip(l, m, k, p);
    struct MapElem *x = Succ(p[0]);
    if (x == NULL || x->pair.k != k)
    {
        printf("AAAAAA СПАСАЙТЕСЬ КТО МОЖЕТ Lookup\n");
    }
    // free(p);
    return x->pair.v;
}

void Insert(struct MapElem *l, int m, int k, char *v)
{
    // Список указателей на другие элементы
    // struct MapElem **p = (struct MapElem **)malloc(sizeof(struct MapElem *));
    struct MapElem *p[m]; // Фиксированный, потому что малоковский не работает, наверное из-за указателей
    Skip(l, m, k, p);
    if (p[0]->next[0] != NULL && p[0]->next[0]->pair.k == k)
    {
        printf("AAAAAA СПАСАЙТЕСЬ КТО МОЖЕТ Insert\n");
    }

    // Создаем новый элемент x, заполняем значения и ранг
    struct MapElem *x = InitSkipList(m);
    // struct MapElem *x = (struct MapElem *)malloc(sizeof(struct MapElem));
    // x->next = (struct MapElem **)malloc(sizeof(struct MapElem *) * m);
    // x->order = (int)malloc(sizeof(struct MapElem *) * m);
    x->pair.k = k;
    x->pair.v = v;
    int rank = SkippyRank(l, m, p[0]->pair.k) + 1;
    // printf("\nCURRENT RANK: %d\n", rank);
    int r = rand() * 2;
    int i = 0, p_i_rank = 0;
    while (i < m && r % 2 == 0)
    {

        // Бежим, обновляем порядок и ранги
        x->next[i] = p[i]->next[i];
        p[i]->next[i] = x;

        p_i_rank = SkippyRank(l, m, p[i]->pair.k);
        // printf("RANKP_I: %d\n", p_i_rank);

        x->order[i] = p[i]->order[i] - (rank - p_i_rank) + 1;
        p[i]->order[i] = (rank - p_i_rank);

        i += 1;
        r /= 2;
    }

    // Чистим элементы за инсертом, двигаем ранги
    while (i < m)
    {
        x->next[i] = NULL;
        p[i]->order[i] += 1;
        i += 1;
    }
}

void MapElemClear(struct MapElem *l)
{

    free(l->next);
    free(l->order);
    if (l->pair.v != NULL)
    {
        free(l->pair.v);
    }

    free(l);
}

void Delete(struct MapElem *l, int m, int k)
{
    // struct MapElem **p = (struct MapElem **)malloc(sizeof(struct MapElem *));
    struct MapElem *p[m];
    Skip(l, m, k, p);

    struct MapElem *x = Succ(p[0]);
    if (x == NULL || x->pair.k != k)
    {
        printf("AAAAAA СПАСАЙТЕСЬ КТО МОЖЕТ Delete\n");
    }

    int i = 0;
    while (i < m && p[i]->next[i] == x)
    {
        // Сдвигаем нексты и ранги
        p[i]->next[i] = x->next[i];
        p[i]->order[i] += x->order[i] - 1;
        i += 1;
    }
    // Двигаем ранги за делитом
    while (i < m)
    {
        // x->next[i] = NULL;
        p[i]->order[i] -= 1;
        i += 1;
    }

    // Фришим удаленный x
    MapElemClear(x);
}

void ListClean(struct MapElem *l, int n)
{
    for (size_t i = 0; i <= n; i++)
    {
        struct MapElem *l_prev = l;
        l = l->next[0];
        MapElemClear(l_prev);
    }
    free(l);
}

void main()
{
    int k = 0;
    int m = 100;
    struct MapElem *l = InitSkipList(m);
    int n = 0;

    char str[20];
    scanf("%s", str);
    while (strcmp(str, "END"))
    {
        if (!strcmp(str, "INSERT"))
        {
            scanf("%d", &k);
            char *v = malloc(10);
            scanf("%s", v); // Нужно малокать, иначе лукап всегда дает посоеднюю строку
            Insert(l, m, k, v);
            n += 1;
        }
        else if (!strcmp(str, "LOOKUP"))
        {
            scanf("%d", &k);
            printf("%s\n", Lookup(l, m, k));
        }
        else if (!strcmp(str, "DELETE"))
        {
            scanf("%d", &k);
            Delete(l, m, k);
            n -= 1;
        }
        else if (!strcmp(str, "RANK"))
        {
            scanf("%d", &k);
            printf("%d\n", SkippyRank(l, m, k));
        }
        scanf("%s", str);
    }

    ListClean(l, n);
}
