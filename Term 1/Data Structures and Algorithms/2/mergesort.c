#include <stdio.h>
#include <stdlib.h>

void InsertSort(int low, int high, int *a)
{
    int i = low, elem, loc;
    while (i <= high)
    {
        elem = a[i];
        loc = i - 1;
        while (loc >= 0 && abs(a[loc]) > abs(elem))
        {
            a[loc + 1] = a[loc];
            loc--;
        }
        a[loc + 1] = elem;
        i++;
    }    
}

void Merge(int k, int l, int m, int *P)
{
    int T[m - k + 1];
    int i = k;
    int j = l + 1;
    int h = 0;

    while (h < (m - k + 1))
    {
        if (j <= m && (i == (l + 1) || abs(P[j]) < abs(P[i])))
        {
            T[h] = P[j];
            j++;
        }
        else
        {
            T[h] = P[i];
            i++;
        }
        h++;
    }

    for (size_t i = 0; i < h; i++)
    {
        P[k + i] = T[i];
    }
}

void MergeSortRec(int low, int high, int *P)

{

    if (high - low + 1 < 5)
    {
        InsertSort(low, high, P);
    }
    else
    {
        if (low < high)
        {
            int med = (low + high) / 2;
            MergeSortRec(low, med, P);
            MergeSortRec(med + 1, high, P);
            Merge(low, med, high, P);
        }
    }
}

void MergeSort(int n, int *P)
{
    MergeSortRec(0, n - 1, P);
}

void main()
{
    int n = 0;
    scanf("%d", &n);

    int arr[n];
    for (size_t i = 0; i < n; i++)
    {
        scanf("%d", &arr[i]);
    }

    MergeSort(n, arr);

    for (size_t i = 0; i < n; i++)
    {
        printf("%d ", arr[i]);
    }
}