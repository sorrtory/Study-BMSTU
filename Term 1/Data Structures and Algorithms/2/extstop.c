#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int * Suffix(char *S){
    int n = strlen(S);
    int *Sig = (int *)malloc(n * sizeof(int));
    for (size_t i = 0; i < n; i++)
    {
        Sig[i] = n - 1;
    }
    int t = n - 1;
    Sig[t] = n - 1;
    int i = n - 2;
    while (i >= 0)
    {
        while (t < n - 1 && S[t] != S[i])
        {
            t = Sig[t + 1];
        }
        if (S[t] == S[i])
        {
            t--;
        }
        Sig[i] = t;
        i--;
    }
    return Sig;
}

int ** Delta1(char *S, int size){
    int len_S = strlen(S);

    int **D = malloc(len_S * sizeof(int *));
    for (size_t i = 0; i < len_S; i++)
    {
        D[i] = malloc(size * sizeof(int));
    }

    int a = 0, b = 0;

    while (b < len_S)
    {
        a = 0;
        while (a < size)
        {
            D[b][a] = len_S;
            a++;
        }
        b++;
    }
    

    int j = 0, i = 0;
    while (j < len_S){
        i = 0;
        while (i < size && j != 0)
        {
            D[j][i] = D[j-1][i];
            i++;
        }
        
        D[j][S[j] - 33] = len_S - j - 1;
        j++;
    }
    
    return D;
}


void BMSubst(char *S, int size, char *T){
    int len_S = strlen(S);
    int len_T = strlen(T);
    int **D1 = Delta1(S, size);
    int k = len_S - 1, i = 0, printed = 0;
    while (k < len_T)
    {
        i = len_S - 1;
        while (T[k] == S[i])
        {
            if (i == 0)
            {
                printf("%d ", k);
                printed = 1;
                k = len_T;
                break;
            }
            i--;
            k--;
        }
        k += (D1[i][T[k] - 33] > len_S - i) ? D1[i][T[k] - 33] : len_S - i;
    }

    for (size_t i = 0; i < len_S; i++)
    {
        free(D1[i]);
    }
    free(D1);

    if (printed == 0)
    {
        printf("%d", len_T);
    }
    
}

int main(int argc, char** argv){
    // char *S = argv[1];
    // char *T = argv[2];
    char *S = "bo";
    char *T = "abobabobobobo";
    BMSubst(S, 126 - 33 + 1, T);
}