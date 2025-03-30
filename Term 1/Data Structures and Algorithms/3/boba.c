#include <stdio.h>
#include <stdlib.h>


struct Task {
    int low, high;
};

struct Stack { 
    int top; 
    size_t cap; 
    struct Task* data; 
}; 


struct Stack* InitStack(size_t n){
    struct Stack *s = (struct Stack*)malloc(sizeof(struct Stack));
    s->data = (struct Task*)malloc(sizeof(struct Task) * n);
    s->cap = n;
    s->top = 0;
    return s;
}

int StackEmpty(struct Stack* s){
    return s->top == 0;
}

void Push(struct Stack* s, struct Task x){
    if (s->top == s->cap)
    {
        printf("Переполнение");
    }
    else
    {
        s->data[s->top] = x;
        s->top += 1;
    }
}

struct Task Pop(struct Stack* s){
    if (StackEmpty(s))
    {
        printf("Опустошение");
    }
    else
    {
        s->top -= 1;
        return s->data[s->top];
    }
}


void print_arr(int *arr, size_t n){
    for (size_t i = 0; i < n; i++)
    {
        printf("%d ", arr[i]);
    }
    printf("\n");
}


void swap(int a, int b, int *arr){
    int old_a = arr[a];
    arr[a] = arr[b];
    arr[b] = old_a;
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


void quicksort(int *arr, int l, int r){
    size_t len = r;
    struct Stack *s = InitStack(len);
    struct Task t = {t.low = l, t.high = r};
    Push(s, t);
    int c = 0;
    while (!StackEmpty(s)){
        t = Pop(s);
        if (t.high - 1 <= t.low){
            continue;
        }
        int i = Partition(t.low, t.high-1, arr);
        printf("C: %d, I: %d, r: %d\n", c, i, t.high);
        
        struct Task t1 = {.low = t.low, .high=i};
        struct Task t2 = {.low = i+1, .high=t.high};
        Push(s, t1);
        Push(s, t2);
        c++;
    }
    printf("C: %d\n", c);
    free(s->data);
    free(s);
}



void main(){
    // int n = 0;
    // scanf("%d", &n);
    // int arr[n];
    // for (size_t i = 0; i < n; i++)
    // {
    //     scanf("%d", &arr[i]);
    // }
    
    int n = 10;
    int arr[] = {500, 479, -464, -56, -580, -328, 982, 263, 730, -439};

    quicksort(arr, 0, n);

    print_arr(arr, n);
    
}