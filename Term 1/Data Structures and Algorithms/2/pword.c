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

void KMPSubst(char *S, char*T){
    int *π = Prefix(S);
    int q = 0, k = 0;

    size_t len_T = strlen(T);
    size_t len_S = strlen(S);

    while (k < len_T)
    {
        while (q > 0 && S[q] != T[k])
        {
            q = π[q-1];
        }

        if (S[q] == T[k])
        {
            q++;
        }
        if (q == 0)
        {   
            printf("no");
            free(π);
            return;
        }
        k++;
    }

    printf("yes");
    free(π);
    
}

int main(int argc, char** argv){
    char *S = argv[1];
    char *T = argv[2];
    // char *S = "bo1";
    // char *T = "bobo";
    KMPSubst(S, T);
    return 0;
}