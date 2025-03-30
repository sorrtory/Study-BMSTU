#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

int * Prefix(char *S){
    int n = strlen(S);
    int *Pi = (int *)malloc(n * sizeof(int));
    for (size_t i = 0; i < n; i++)
    {
        Pi[i] = 0;
    }
    int i = 1;
    int t = 0;
    while (i < n)
    {
        while (t > 0 && S[t] != S[i])
        {
            t = Pi[t - 1];
        }
        if (S[t] == S[i])
        {
            t++;
        }
        Pi[i] = t;
        i++;
    }
    return Pi;
}


int main(int argc, char** argv){
    char *str = argv[1];
    // char *str = "aa10";
    int *Pi = Prefix(str);
    // for (size_t i = 0; i < strlen(str); i++)
    // {
    //     printf("%d ", Pi[i]);
    // }
    int i = 1, n = 0, k = 0, find = 0;
    while(i < strlen(str) + 1)
    {   
        n = i * 2 - 1;
        k = 2;
        while (n  < strlen(str) && i <= Pi[n])
        {            
            printf("%d %d\n", n + 1, k);
            find = 1;
            n += i;
            k++;
        }

        if (find)
        {
            i = n;
            find = 0;
        }
        i++;
    }

    free(Pi);
    return 0;
    
}