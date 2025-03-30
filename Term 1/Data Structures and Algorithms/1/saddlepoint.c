#include <stdio.h>

int get_col_min_index(int ref, int ref_x, int ref_y, int arr_x, int arr_y, int arr[arr_x][arr_y]){
    // Возвращаем индекс x минимального в столбце элемента
    int min = ref;
    int min_x = ref_x; 
    int tmp = 0;
    for (size_t i = 0; i < arr_x; i++)
    {   
        if (i != ref_y) // Не обращаемся дважды
        {
            tmp = arr[i][ref_x];
            
            if (tmp < min) 
            {
                min = tmp;
                min_x = i;
            }
        }    
    }
    return min_x;
    
}
int get_line_max_index(int ref, int ref_x, int ref_y, int arr_x, int arr_y, int arr[arr_x][arr_y]){
    // Возвращаем индекс y максимального в строке элемента
    int max = ref;
    int max_y = ref_x; 
    int tmp = 0;
    for (size_t i = 0; i < arr_y; i++)
    {   
        if (i != ref_x) // Не обращаемся дважды
        {   
            tmp = arr[ref_y][i];
            if (tmp > max) 
            {
                max = tmp;
                max_y = i;
            }
        }    
    }
    
    return max_y;
    
}

// void print_arr(int x, int y, int arr[x][y]){

//     for (size_t i = 0; i < x; i++)
//     {     
//         for (size_t j = 0; j < y; j++)
//         {   
//             printf("%3d ", arr[i][j]);
//         }
//         printf("\n");
//     }
// }

int main(){
    int x, y;
    
    scanf("%d", &x); 
    scanf("%d", &y);

    int arr[x][y];


    for (size_t i = 0; i < x; i++)
    {     
        for (size_t j = 0; j < y; j++)
        {   
            scanf("%d", &arr[i][j]);
        }
    }

    int saddlepoint_old_x = 0;
    int saddlepoint_old_y = 0;
    int saddlepoint_x = 0;
    int saddlepoint_y = 0;
    
    saddlepoint_x = get_line_max_index(arr[saddlepoint_y][saddlepoint_x], saddlepoint_x, saddlepoint_y, x, y, arr);
    
    int c = 1;
    while (c != 4)
    {   
        // printf("C:%d X:%d Y:%d\n", c, saddlepoint_x, saddlepoint_y);

        
        if (c % 2 == 1)
        {   
            saddlepoint_old_y = saddlepoint_y;
            saddlepoint_y = get_col_min_index(arr[saddlepoint_y][saddlepoint_x], saddlepoint_x, saddlepoint_y, x, y, arr); 
            // printf("NEWY:%d\n", saddlepoint_y);
            
            if (saddlepoint_x == saddlepoint_y)
            {
                printf("%d %d", saddlepoint_old_y, saddlepoint_x);
                break;
            }
            
        }
        else{
            saddlepoint_old_x = saddlepoint_x;
            saddlepoint_x = get_line_max_index(arr[saddlepoint_y][saddlepoint_x], saddlepoint_x, saddlepoint_y, x, y, arr);
            // printf("NEWX:%d\n", saddlepoint_x);
            // if (saddlepoint_y == saddlepoint_x)
            // {
            //     printf("%d %d", saddlepoint_old_x, saddlepoint_y);
            //     break;
            // }
        }

        c++;
        
    }

    if (c == 4)
    {
        printf("none");
    }
    
}