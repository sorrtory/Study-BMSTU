#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

struct Elem
{
    struct Elem *next;
    char *word;
};

/*
    Функция bsort(list)
    • принимает однонаправленный (односвязный) список, представленный
      указателем на свой первый элемент (NULL представляет пустой список)
    • и возвращает список из тех же элементов, упорядоченных в порядке
      возрастания длин строк.

    Односвязный список, в отличие от кольцевого двусвязного, не имеет
    выделенного служебного «головного» звена.
*/
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
    return (a_len < b_len) || ((a_len == b_len) && (strcmp(a, b) < 0));
}

struct Elem *bsort(struct Elem *list)
{
    struct Elem *t = NULL;
    while (t != list)
    {
        struct Elem *bound = t;
        t = list;
        struct Elem *i = list;

        while (i->next && i->next->next != NULL)
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

#define MEM(p) must_be_not_null((p), #p, __FILE__, __LINE__)

static void *must_be_not_null(void *p, const char *expr,
                              const char *file, int line)
{
    if (p)
        return p;

    fprintf(stderr, "%s:%d: '%s' returns NULL\n", file, line, expr);
    abort();
}

struct Buffer
{
    char *str;
    size_t len;
    size_t capacity;
};

#define BUFFER_INIT \
    {               \
        NULL, 0, 0  \
    }

static void buffer_free(struct Buffer *buffer)
{
    free(buffer->str);
}

static void buffer_add_char(struct Buffer *buffer, char ch)
{
    if (buffer->capacity == 0)
    {
        buffer->capacity = 16;
        buffer->str = MEM(malloc(buffer->capacity));
    }
    else if (buffer->len + 1 == buffer->capacity)
    {
        buffer->capacity = 3 * buffer->capacity / 2;
        buffer->str = MEM(realloc(buffer->str, buffer->capacity));
    }

    buffer->str[buffer->len++] = ch;
    buffer->str[buffer->len] = '\0';
}

#define randint(limit) (rand() % (limit))

#define VOWELS "aeiouy"
#define NVOWELS 6
#define CONSONANTS "bcdfghjklmnpqrstvwxz"
#define NCONSONANTS 20

static struct Elem *gen_list(struct Buffer *buffer, size_t nwords)
{
    struct Elem *items = MEM(calloc(nwords, sizeof(items[0])));
    size_t generated = 0;

    while (generated < nwords)
    {
        switch (randint(13))
        {
        case 0:
            if (buffer->len != 0 && buffer->str[buffer->len - 1] != '\0')
            {
                buffer_add_char(buffer, '\0');
                ++generated;
            }
            break;

        case 1:
        case 2:
        case 3:
            buffer_add_char(buffer, VOWELS[randint(NVOWELS)]);
            break;

        case 4:
        case 5:
        case 6:
            buffer_add_char(buffer, CONSONANTS[randint(NCONSONANTS)]);
            break;

        case 7:
        case 8:
        case 9:
            buffer_add_char(buffer, VOWELS[randint(NVOWELS)]);
            buffer_add_char(buffer, CONSONANTS[randint(NCONSONANTS)]);
            break;

        case 10:
        case 11:
        case 12:
            buffer_add_char(buffer, CONSONANTS[randint(NCONSONANTS)]);
            buffer_add_char(buffer, VOWELS[randint(NVOWELS)]);
            break;
        }
    }

    char *word = buffer->str;
    for (size_t i = 0; i < nwords; ++i)
    {
        items[i].next = (i != nwords - 1) ? &items[i + 1] : NULL;
        items[i].word = word;
        word += strlen(word) + 1;
    }

    return items;
}

static int words_compare(const void *va, const void *vb)
{
    const char *const *a = va;
    const char *const *b = vb;
    int res = (int)strlen(*a) - (int)strlen(*b);

    if (res == 0)
        res = (int)(*a - *b);

    return res;
}

static bool is_cyclic(struct Elem *list)
{
    if (list == NULL)
        return false;

    struct Elem *achilles = list, *tortoise = list;

    do
    {
        achilles = achilles->next;
        if (achilles != NULL)
            achilles = achilles->next;
        tortoise = tortoise->next;
    } while (achilles != NULL && achilles != tortoise);

    return achilles != NULL;
}

static int test(size_t nwords)
{
    printf("test(%zu):\n", nwords);

    // init
    int failed = 0;
    struct Buffer buffer = BUFFER_INIT;
    struct Elem *list = gen_list(&buffer, nwords);
    char **sample = MEM(calloc(nwords, sizeof(sample[0])));

    printf("Source list:\n");
    for (size_t i = 0; i < nwords; ++i)
    {
        printf("#%zu (%p): \"%s\" (%p)\n",
               i, &list[i], list[i].word, list[i].word);
    }

    for (size_t i = 0; i < nwords; ++i)
        sample[i] = list[i].word;
    qsort(sample, nwords, sizeof(sample[0]), words_compare);

    // call
    struct Elem *result = bsort(list);

    // check
    if (is_cyclic(result))
    {
        printf("ERROR: result list is cyclic!\n");
        size_t i = 0;
        struct Elem *p = result, *first = NULL;
        do
        {
            printf("#%zu (%p): ", i, p);
            fflush(stdout);
            printf("%s (%p)%s\n", p->word, p->word, p == first ? "same of #0" : "");
            if (!first)
                first = p;
            ++i;
            p = p->next;
        } while (p != first);

        failed = 1;
        goto CLEANUP;
    }

    size_t i = 0;
    struct Elem *p = result;
    while (i < nwords && p != NULL)
    {
        char *w1 = sample[i], *w2 = p->word;
        printf("#%zu (%p): expected \"%s\" (%p), actual \"%s\" (%p) - %s\n",
               i, p, w1, w1, w2, w2, w1 == w2 ? "Ok" : "FAIL!");
        if (w1 != w2)
            failed = 1;

        ++i;
        p = p->next;
    }

    if (i == nwords && p != NULL)
    {
        printf("ERROR: there are unexpected items at end of the list:\n");
        while (p != NULL)
        {
            printf("#%zu (%p): \"%s\" (%p)\n", i, p, p->word, p->word);
            ++i;
            p = p->next;
        }
        failed = 1;
    }
    else if (i < nwords && p == NULL)
    {
        printf("ERROR: %zu words are lost!\n", nwords - i);
        failed = 1;
    }

    // cleanup
CLEANUP:
    printf("\n");
    free(sample);
    free(list);
    buffer_free(&buffer);
    return failed;
}

int test_empty(void)
{
    struct Elem *result = bsort(NULL);

    if (result != NULL)
    {
        printf("bsort(NULL) must be a NULL, but got %p\n", result);
        return 1;
    }

    return 0;
}

int main()
{
    srand(time(NULL));
    int fails = 0;

    fails += test(1);
    fails += test(5);
    fails += test(10);
    fails += test(20);
    fails += test(50);
    fails += test(100);
    fails += test(200);
    fails += test(500);

    fails += test_empty();

    return fails == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}

/* vim: set sw=0 ts=4 noet: */