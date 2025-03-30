#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int char_cmp(const void *x, const void *y)

{
    printf("%s", *(char **)x);
    puts("NIGGERS\n");
    return strcmp(*(char **)x, *(char **)y);
}

void main()
{
    int n = 0;
    scanf("%d\n", &n);

    char **strings = calloc(1000, sizeof(char *));

    for (size_t i = 0; i < n; i++)
    {
        fgets(strings[i], 1000, stdin);
        strcpy(strings[i], strtok(strings[i], "\n"));
        // scanf("%s", &strings[i]);
    }

    // for (size_t i = 0; i < n; i++)
    // {
    //     printf("%s ", strings[i]);
    // }

    qsort(strings, n, sizeof(char *), char_cmp);

    puts("AFTER NIGGERS\n");
    for (size_t i = 0; i < n; i++)
    {
        printf("%s ", strings[i]);
    }
    free(strings);
    /*
    3
    cursed
    zxc
    sedenka
    */
    // zxcursedenka
}