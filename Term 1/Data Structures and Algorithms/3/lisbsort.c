#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MINIMUM -2147483647

struct Elem
{
    struct Elem *next;
    char *word;
};

typedef struct Elem SingleLinkedList;

struct Elem *InitSingleLinkedList()
{
    struct Elem *l = (struct Elem *)malloc(sizeof(struct Elem));
    l->next = NULL;
    l->word = "";
    return l;
}

void InsertBeforeHead(struct Elem **l, char *x)
{
    struct Elem *y = (struct Elem *)malloc(sizeof(struct Elem));
    y->word = x;
    y->next = *l;
    *l = y;
}

void InsertAfterTail(struct Elem **l, char *x){
    struct Elem *y = (struct Elem *)malloc(sizeof(struct Elem));
    y->word = "";
    y->next = NULL;
    
    struct Elem **l_pointer = l;
    while ((*l_pointer)->next != NULL)
    {
        l_pointer = &((*l_pointer)->next);
    }
    (*l_pointer)->word = x;
    (*l_pointer)->next = y;
}

void ListDisplay(SingleLinkedList *l)
{
    while (l != NULL)
    {   
        if (strcmp(l->word, ""))
        {
            printf("%s", l->word);
            if (l->next != NULL)
            {
                printf(" ");
            }
        }
        l = l->next;
    }
    printf("\n");
}

void ListClean(SingleLinkedList *l, int n)
{
    for (size_t i = 0; i < n; i++)
    {
        SingleLinkedList *l_prev = l;
        l = l->next;
        free(l_prev);
    }
    free(l);
}

void swap(struct Elem *a, struct Elem *b)
{
    char *old_a_word = a->word;
    a->word = b->word;
    b->word = old_a_word;
}

int compare(char *a, char *b)
{
    int a_len = strlen(a);
    int b_len = strlen(b);
    return (a_len < b_len);
}

struct Elem *bsort(struct Elem *list)
{
    struct Elem *t = NULL;
    while (t != list)
    {
        struct Elem *bound = t;
        t = list;
        struct Elem *i = list;

        while (i->next != NULL)
        {

            if (compare(i->next->word, i->word))
            {
                swap(i->next, i);
                t = i;
            }

            i = i->next;
        }
    }
    return list;
}

void main()
{
    // int n = 7;
    // char *arr[] = {"ba", "a", "bo", "123", "zzzzz", "ba", "a"};
    int n = 0;
    SingleLinkedList *l = InitSingleLinkedList();
    char str[1001];
    fgets(str, 1001, stdin);
    char *istr = strtok(str, "\n ");
    while (istr != NULL)
    {
        if (istr != "" && istr != " " && istr != "\n")
        {
            InsertAfterTail(&l, istr);
            n += 1;
        }
        istr = strtok(NULL, "\n ");
    }

    l = bsort(l);
    ListDisplay(l);
    ListClean(l, n);
}