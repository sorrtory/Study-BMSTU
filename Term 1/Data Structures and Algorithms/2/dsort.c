#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define STRING_SIZE 1000010

void DistributionSort(int m, char *S, int n)
{
    int count[m];
    for (size_t i = 0; i < m; i++)
    {
        count[i] = 0;
    }

    int j = 0;
    int k = 0;
    while (j < n)
    {
        k = S[j] - 'a';
        count[k]++;
        j++;
    }
    int i = 1;
    while (i < m)
    {
        count[i] = count[i - 1] + count[i];
        i++;
    }

    char *D = (char *)malloc(n + 1);
    j = n - 1;
    i = 0;
    while (j >= 0)
    {
        k = S[j] - 'a';
        i = count[k] - 1;
        count[k] = i;
        D[i] = S[j];
        j--;
    }
    D[n] = '\0';
    printf("%s\n", D);
    free(D);
}

int main()
{
    char *str = (char *)malloc(STRING_SIZE + 1);
    // encyclopedia
    fgets(str, STRING_SIZE, stdin);
    str[strlen(str) - 1] = '\0';

    DistributionSort('z' - 'a' + 1, str, strlen(str));

    free(str);
    return 0;
}