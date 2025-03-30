#include <stdio.h>

const int get_null(int *arr1, int *arr2, int count){
    int null = -2147483648;
    int bad = 1;
    
    while (bad)
    {   
        bad = 0;
        for (size_t i = 0; i < count; i++)
        {
            if (arr1[i] == null || arr2[i] == null)
            {
                bad = 1;
            }        
        }
        null++;
    }
    return null;
}

void main(){
    static int count = 8;

    int a[count];
    scanf("%d %d %d %d %d %d %d %d", &a[0], &a[1], &a[2], &a[3], &a[4], &a[5], &a[6], &a[7]);
    
    
    int b[count];
    scanf("%d %d %d %d %d %d %d %d", &b[0], &b[1], &b[2], &b[3], &b[4], &b[5], &b[6], &b[7]);


    const int null = get_null(a, b, count);
    int bigbad = 0, smallbad = 1;
    
    for (size_t i = 0; i < count; i++)
    {   
        smallbad = 1;
        for (size_t j = 0; j < count; j++)
        {
            if (a[j] == b[i])
            {
                a[j] = null;
                smallbad = 0;
                break;
            }
            
        }
        if (smallbad){
            bigbad = 1;
            break;
        }
        
    }
    
    if (bigbad){
        printf("no");
    }
    else
    {
        printf("yes");
    }
    

    
}