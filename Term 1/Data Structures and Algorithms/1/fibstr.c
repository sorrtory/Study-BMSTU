#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char *fibstr(int n)
{
    if (n == 1)
    {
        char *s = (char *)calloc(2, sizeof(char));
        strcpy(s, "");
        strcpy(s, "a");

        return s;
    }
    else if (n == 2)
    {
        char *s = (char *)calloc(2, sizeof(char));
        strcpy(s, "");
        strcpy(s, "b");

        return s;
    }
    else
    {

        char *s1 = fibstr(n - 2);

        char *s2 = fibstr(n - 1);
        char *s = (char *)calloc(strlen(s1) + strlen(s2) + 1, sizeof(char));

        strcpy(s, "");
        strcat(s, s1);
        strcat(s, s2);

        free(s1);
        free(s2);

        return s;
    }
}

int main(void)
{
    int n = 0;
    scanf("%d", &n);

    char *str = fibstr(n);
    printf("%s", str);

    free(str);

    return 0;
}