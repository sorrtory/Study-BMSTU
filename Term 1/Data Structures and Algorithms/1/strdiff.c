#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *int_to_bin(int n)
{
    char *str = (char *)calloc(9, sizeof(char));
    memset(str, '0', 8);

    int k = 0;
    
    while (n > 0)
    {   
        switch (n%2)
        {
        case 0:
            str[k] = '0';
            break;
        
        case 1:
            str[k] = '1';
            break;
        }
        n /= 2;
        k++;
    }
    return str;
    
}


int strdiff(char *a, char *b)
{

    int minlen = 0;
    if (strlen(a) >= strlen(b))
    {
        minlen = strlen(b) + 1;
    }
    else    
    {
        minlen = strlen(a) + 1;
    }

    int same_count = 0;
    for (size_t i = 0; i < minlen; i++)
    {
        char *a_i_bin = int_to_bin(a[i]);
        char *b_i_bin = int_to_bin(b[i]);
        
        size_t j = 0;
        while (j != 8 && a_i_bin[j] == b_i_bin[j])
        {   
            same_count++;
            j++;
        }
        
        free(a_i_bin);
        free(b_i_bin);

        if (j != 8)
        {
            break;
        }
    }

    if (strlen(a) == strlen(b) && minlen*8 == same_count)
    {
        return -1;
    }
    else{
        return same_count;
    }
}





int main()
{
    char  s1[] = "The quick brown fox jumps over the lazy dog";
    char  s2[] = "�he quick brown fox jumps over the lazy dog";
    
    printf("%d", strdiff(s1, s2));
    printf("\n");
    printf(int_to_bin('T'));
    printf("\n");
    printf(int_to_bin('�'));
    
    

    
}