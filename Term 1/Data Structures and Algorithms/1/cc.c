#include <stdbool.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int strdiff(char *a, char *b)
{

    int minlen = 0;
    if (strlen(a) >= strlen(b))
    {
        minlen = strlen(b) + 1;
    }
    else
    {
        minlen = strlen(a) + 1;
    }

    int same_count = 0;
    for (size_t i = 0; i < minlen; i++)
    {
        int j = a[i] ^ b[i];

        if (j == 0)
        {
            same_count += 8;
        }
        else
        {
            int k = 0;
            j = abs(j);
            while (j != 0)
            {
                if (j % 2 == 1)
                {
                    same_count += k;
                    break;
                }
                k++;
                j /= 2;
            }
            break;
        }
    }

    if (strlen(a) == strlen(b) && minlen * 8 == same_count)
    {
        return -1;
    }
    else
    {
        return same_count;
    }
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

char *mystrdup(const char *str)
{
    size_t size = strlen(str) + 1;
    char *result = malloc(size);
    if (result)
        memcpy(result, str, size);
    return result;
}

static int lower_bit(unsigned char c)
{
    return (c == 0 || c & 1) ? 0 : 1 + lower_bit(c >> 1);
}

#define swap_bit(str, bit_no) ((str)[(bit_no) / 8] ^= 1u << ((bit_no) % 8))

static int test_task(void)
{
    int res = strdiff("aa", "ai");
    if (res != 11)
    {
        printf("Strings are \"aa\" and \"ai\", expected 11 but got %d\n", res);
        return 1;
    }
    return 0;
}

static const char sample[] = "The quick brown fox jumps over the lazy dog";

static int test_swap_bit(int bit_no)
{
    int failed = 0;
    char *str1 = MEM(mystrdup(sample));
    char *str2 = MEM(mystrdup(sample));

    swap_bit(str2, bit_no);

    int res = strdiff(str1, str2);
    if (res != bit_no)
    {
        printf("Strings are \"%s\" and \"%s\", expected %d but got %d\n",
               str1, str2, bit_no, res);
        failed = 1;
    }

    free(str2);
    free(str1);
    return failed;
}

static char *cut(char *str, int pos)
{
    str[pos] = '\0';
    char *copy = MEM(mystrdup(str));
    free(str);
    return copy;
}

static int test_cut_str(int pos, bool left)
{
    int failed = 0;
    char *str1 = MEM(mystrdup(sample));
    char *str2 = MEM(mystrdup(sample));

    if (left)
        str1 = cut(str1, pos);
    else
        str2 = cut(str2, pos);

    int expected = pos * 8 + lower_bit(sample[pos]);
    int res = strdiff(str1, str2);

    if (res != expected)
    {
        printf("Strings are \"%s\" and \"%s\", expected %d but got %d\n",
               str1, str2, expected, res);
        failed = 1;
    }

    free(str2);
    free(str1);
    return failed;
}

static int test_eq(void)
{
    int failed = 0;
    char *str1 = MEM(mystrdup(sample));
    char *str2 = MEM(mystrdup(sample));

    int res = strdiff(str1, str2);

    if (res != -1)
    {
        printf("Strings are equal: \"%s\" and \"%s\", expected -1 but got %d\n",
               str1, str2, res);
        failed = 1;
    }

    free(str1);
    free(str2);
    return failed;
}

int main()
{

    // '�', 'T'

    int bad = 0;
    bad += test_task();

    bad += test_swap_bit(0);
    bad += test_swap_bit(1);
    bad += test_swap_bit(6);

    bad += test_swap_bit(7); // zxc

    bad += test_swap_bit(8);

    bad += test_swap_bit(15); // zxc

    bad += test_swap_bit(16);
    bad += test_swap_bit(42);
    bad += test_swap_bit(42 * 8);
    bad += test_swap_bit(42 * 8 + 6);

    bad += test_cut_str(0, true);
    bad += test_cut_str(1, true);
    bad += test_cut_str(10, true);
    bad += test_cut_str(20, true);
    bad += test_cut_str(42, true);

    bad += test_cut_str(0, false);
    bad += test_cut_str(1, false);
    bad += test_cut_str(10, false);
    bad += test_cut_str(20, false);
    bad += test_cut_str(42, false);

    bad += test_eq();

    return bad ? EXIT_FAILURE : EXIT_SUCCESS;
}

/* vim: set sw=0 ts=4 noet: */
