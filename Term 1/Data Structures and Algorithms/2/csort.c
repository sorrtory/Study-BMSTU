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

int main()
{
    char str[1000];
    fgets(str, 1000, stdin);
    str[strlen(str) - 1] = '\0';
    char new_str[1000];
    csort(str, new_str);
    printf("%s", new_str);
    return 0;
}