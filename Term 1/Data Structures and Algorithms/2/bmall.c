#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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

int * Delta1(char *S, int size){
    int *D = (int *)malloc(size * sizeof(int));
    int a = 0;
    int len_S = strlen(S);
    while (a < size)
    {
        D[a] = len_S;
        a++;
    }
    int j = 0;
    while (j < len_S){
        D[S[j] - 33] = len_S - j - 1;
        j++;
    }
    
    return D;
}

int * Delta2(char *S){
    int n = strlen(S);
    int *D = (int *)malloc(n * sizeof(int));

    int *Sig = Suffix(S);
    int i = 0;
    int t = Sig[0];
    while (i < n)
    {   

        while (t < i)
        {
            t = Sig[t+1];
            // printf("INFINITY?");

        }
        D[i] = -i + t + n;
        i++;
    }
    i = 0;
    while (i < n - 1)
    {
        t = i;
        while (t < n - 1)
        {   
            t = Sig[t+1];
            if (S[i] != S[t])
            {
                D[t] = -(i+1) + n;
            }
        }
        i++;
    }
    free(Sig);
    return D;
}

void BMSubst(char *S, int size, char *T){
    int len_S = strlen(S);
    int len_T = strlen(T);
    int *D1 = Delta1(S, size);
    int *D2 = Delta2(S);
    int k = len_S - 1, i = 0;
    while (k < len_T)
    {
        i = len_S - 1;
        while (T[k] == S[i])
        {
            if (i == 0)
            {
                printf("%d ", k);
                break;
            }
            i--;
            k--;
        }
        k += (D1[T[k] - 33] > D2[i]) ? D1[T[k] - 33] : D2[i];
    }
    free(D1);
    free(D2);
}

int main(int argc, char** argv){
    char *S = argv[1];
    char *T = argv[2];
    // char *S = "BHrBH";
    // char *T = "QBHrBWQBHrJQKBHr3BNOBHrBWBHrBHQBHUBWBUBzBHrBHr7BHrB5BHrs";
    BMSubst(S, 126 - 33 + 1, T);
    return 0;
}