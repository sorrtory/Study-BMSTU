#include <stdio.h>

int set_init(int set_len){
    int Set = 0; 
    int num = 0;
    for (size_t i = 0; i < set_len; i++)
    {   
        scanf("%d", &num);
        Set = Set | (1 << num);
    }
    return Set;
}



void main(){
    int a_len = 0;
    scanf("%d", &a_len);
    int A = set_init(a_len);

    int b_len = 0;
    scanf("%d", &b_len);
    int B = set_init(b_len);

    int C = A & B;

    for (size_t i = 0; i < 32; i++)
    {
        if ((C & (1 << i)) != 0){
            printf("%d ", i);
        }
    }
    

    
}