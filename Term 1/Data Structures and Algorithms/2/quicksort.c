#include <stdio.h>

void swap(int a, int b, int *arr){
    int old_a = arr[a];
    arr[a] = arr[b];
    arr[b] = old_a;
}

void SelectSort(int low, int high, int *P){
    int j = high, k = 0, i = 0;
    while (j > low)
    {
        k = j;
        i = j - 1;
        while (i >= low)
        {   
            if (P[k] < P[i])
            {
                k = i;
            }
            i--;
        }
        swap(j, k, P);
        j--;
    }
}

int Partition(int low, int high, int *P){
    int i = low, j = low;
    while (j < high)
    {   
        if (P[j] < P[high])
        {
            swap(i, j, P);
            i++;
        }
        j++;
    }
    swap(i, high, P);
    return i;
}

void QuickSortRec(int m, int low, int high, int *P){

    while (high - low > m)
    {
        int q = Partition(low, high, P);
        if ((high - q) > (q - low))
        {
            QuickSortRec(m, low, q - 1, P);
            low = q + 1;

        }
        else
        {
            QuickSortRec(m, q + 1, high, P);
            high = q - 1;
        }
    }
    SelectSort(low, high, P);
}

void QuickSort(int m, int n, int * P){
    QuickSortRec(m, 0, n - 1, P);
}

void main(){
    // int n = 10, m = 4;
    // int arr[] = {10, 0, -1, 9, 8, -40, 18, 44, 9, 15};
    int n = 0, m = 0;
    scanf("%d", &n);
    scanf("%d", &m);
    int arr[n];
    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &arr[i]);
    }

    QuickSort(m, n, arr);
    // SelectSort(n, arr);

    for (size_t i = 0; i < n; i++)
    {
        printf("%d ", arr[i]);
    }
    
}