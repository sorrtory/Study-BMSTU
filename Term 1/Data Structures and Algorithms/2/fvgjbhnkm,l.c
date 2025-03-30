#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct word_and_len
{
    char *str;
    int len;
};

void csort(char *src, char *dest)
{
    struct word_and_len *words = (struct word_and_len *)malloc(501 * sizeof(struct word_and_len));

    char new_src[strlen(src)];
    memcpy(new_src, src, strlen(src) + 1);

    char *word = strtok(new_src, " ");
    int n = 0;
    while (word != NULL)
    {
        words[n].str = word;
        words[n].len = strlen(word);
        word = strtok(NULL, " ");
        n++;
    }

    int count[n];
    for (size_t i = 0; i < n; i++)
    {
        count[i] = 0;
    }

    int i = 0, j = 0;
    while (j < n)
    {
        i = j + 1;
        while (i < n)
        {
            if (words[i].len < words[j].len)
            {

                count[j] += 1;
            }
            else
            {
                count[i] += 1;
            }
            i++;
        }
        j++;
    }

    int k = 0;
    int m = 0;
    int prevlen = 0;
    while (k != n)
    {
        if (count[k] == m)
        {
            // printf("WORD: %s count[k]: %d m: %d|", words[m].str, count[k], k);
            memcpy(dest + prevlen, words[k].str, words[k].len);
            prevlen += words[k].len;

            memcpy(dest + prevlen, " ", 1);

            prevlen += 1;
            k = 0;
            m++;
        }
        else
        {
            k++;
        }
    }
    memcpy(dest + prevlen - 1, "", 1);

    free(words);
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

enum
{
    MAX_WORD_LEN = 12,
    NVOWELS = 6,
    NCONSONANTS = 20
};

static const char VOWELS[] = "aeiouy";
static const char CONSONANTS[] = "bcdfghjklmnpqrstvwxz";

static int randint(int limit)
{
    return (int)(rand() / ((double)RAND_MAX + 1) * limit);
}

#define RANDLETTER(type) (type[randint(N##type)])

struct Word
{
    char letters[MAX_WORD_LEN];
    size_t len;
    size_t spaces_after;
    size_t order;
};

static void init_word(struct Word *word, size_t order)
{
    size_t len = MAX_WORD_LEN / 2 + randint(MAX_WORD_LEN / 2);
    size_t i = 0;

    while (i < len - 2)
        switch (randint(4))
        {
        case 0:
            word->letters[i++] = RANDLETTER(VOWELS);
            break;

        case 1:
            word->letters[i++] = RANDLETTER(CONSONANTS);
            break;

        case 2:
            word->letters[i++] = RANDLETTER(CONSONANTS);
            word->letters[i++] = RANDLETTER(VOWELS);
            break;

        case 3:
            word->letters[i++] = RANDLETTER(VOWELS);
            word->letters[i++] = RANDLETTER(CONSONANTS);
            break;
        }
    word->letters[i] = '\0';

    word->len = i;
    word->spaces_after = 1 + randint(5);
    word->order = order;
}

static int word_compare(const void *vleft, const void *vright)
{
    const struct Word *left = vleft;
    const struct Word *right = vright;

    return left->len != right->len
               ? (int)left->len - (int)right->len
               : (int)left->order - (int)right->order;
}

static int random_test(size_t nwords)
{
    // init
    struct Word words[nwords];
    size_t source_len = 0, dest_len = 0;

    for (size_t i = 0; i < nwords; ++i)
    {
        init_word(&words[i], i);
        source_len += words[i].len + words[i].spaces_after;
        dest_len += words[i].len + 1;
    }

    source_len -= words[nwords - 1].spaces_after;
    dest_len -= 1;

    char *source = MEM(malloc(source_len + 1));
    char *dest = MEM(malloc(dest_len + 1));
    char expected[dest_len + 1];

    // init destination buffer with garbage
    for (size_t i = 0; i < dest_len + 1; ++i)
        dest[i] = 1 + randint(255);

    char *p = source;
    for (size_t i = 0; i < nwords; ++i)
    {
        memcpy(p, words[i].letters, words[i].len);
        p += words[i].len;
        if (i != nwords - 1)
        {
            for (size_t j = 0; j < words[i].spaces_after; ++j)
                *p++ = ' ';
        }
    }
    *p = '\0';

    printf("Source string:\n(%s)\n", source);

    qsort(words, nwords, sizeof(words[0]), word_compare);

    p = expected;
    for (size_t i = 0; i < nwords; ++i)
    {
        memcpy(p, words[i].letters, words[i].len);
        p += words[i].len;
        *p++ = ' ';
    }
    p[-1] = '\0';

    printf("Expected result:\n(%s)\n", expected);
    fflush(stdout);

    char source_copy[source_len + 1];
    strcpy(source_copy, source);

    // call
    csort(source, dest);

    // check
    printf("Result after sorting:\n(%s)\n", dest);
    int mismatched_result = strcmp(dest, expected) != 0;
    if (mismatched_result)
        printf("TEST FAILED! Strings are not equal!\n\n");

    int source_touched = memcmp(source, source_copy, source_len + 1);
    if (source_touched)
        printf("TEST FAILED! Source string is changed!\n\n");

    int failed = mismatched_result || source_touched;
    if (!failed)
        printf("Test passed!\n\n");

    free(dest);
    free(source);
    return failed;
}

int main()
{
    int failed = 0;

    failed += random_test(1);
    failed += random_test(2);
    failed += random_test(3);
    failed += random_test(10);
    failed += random_test(30);
    failed += random_test(10 + randint(10));
    failed += random_test(200);

    return failed == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}

/* vim: set sw=0 ts=4 noet: */