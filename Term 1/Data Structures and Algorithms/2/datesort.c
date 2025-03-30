#include <stdio.h>
#include <string.h>
#include <stdlib.h>



struct Date {
    int Day, Month, Year;
};

typedef struct Date Date;

void key(void *arr, int mode){
    Date* date = (Date *)arr;
    
}

void DistributionSort(int m, char *S, int n){
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
        count[i] = count[i-1] + count[i];
        i++;
    }
    
    char *D = (char *)malloc(n);
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
    
    return D; 
}

Date * RadixSort(){
    Date *arr = (Date *)malloc(n * sizeof(Date));
}

void main(){
    int n = 0;
    scanf("%d", n);
    Date *arr = (Date *)malloc(n * sizeof(Date));

    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &arr[i].Year);
        scanf("%d", &arr[i].Month);
        scanf("%d", &arr[i].Day);
    }
    
   
    DistributionSort('z' - 'a' + 1, str, n-1);

    for (size_t i = 0; i < n; i++)
    {
        printf("%04d %02d %02d", arr[i].Year, arr[i].Month, arr[i].Day);
    }
    
    free(arr);
}