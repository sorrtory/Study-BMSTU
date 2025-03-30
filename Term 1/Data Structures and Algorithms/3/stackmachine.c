#include <stdio.h>
#include <stdlib.h>

struct Stack { 
    int top; 
    size_t cap; 
    long long* data; 
}; 


struct Stack* InitStack(size_t n){
    struct Stack *s = (struct Stack*)malloc(sizeof(struct Stack));
    s->data = (long long*)malloc(sizeof(long long) * n);
    s->cap = n;
    s->top = 0;
    return s;
}

int StackEmpty(struct Stack* s){
    return s->top == 0;
}

void Push(struct Stack* s, int x){
    if (s->top == s->cap)
    {
        // printf("Переполнение\n");
        s->data = (long long *)realloc(s->data, (s->top + 1) * sizeof(long long));
        s->cap = s->top + 1;
        Push(s, x);
    }
    else
    {   
        // printf("Добавочка\n");
        s->data[s->top] = x;
        s->top += 1;
    }
}

long long Pop(struct Stack* s){
    if (StackEmpty(s))
    {
        // printf("Опустошение");
    }
    else
    {   
        s->top -= 1;
        return s->data[s->top];
    }
}

long long Top(struct Stack* s){
    if (StackEmpty(s))
    {
        printf("Опустошение");
    }
    else
    {   
        return s->data[s->top - 1];
    }
}
void main(){
    struct Stack* s = InitStack(1);
    char str[10];
    int x = 0;
    long long a = 0, b = 0;
    scanf("%s", str);
    while (str[0] != 'E')
    {
        if (str[0] == 'C')
        {   
            scanf("%d", &x);
            Push(s, x);
        }
        else if (str[0] == 'A')
        {   
            a = Pop(s);
            b = Pop(s);
            Push(s, a+b);
        }
        else if (str[0] == 'S' && str[1] == 'U')
        {   
            a = Pop(s);
            b = Pop(s);
            Push(s, a-b);
        }
        else if (str[0] == 'M' && str[1] == 'U')
        {   
            a = Pop(s);
            b = Pop(s);
            Push(s, a*b);
        }
        else if (str[0] == 'D' && str[1] == 'I')
        {   
            a = Pop(s);
            b = Pop(s);
            Push(s, a/b);
        }
        else if (str[0] == 'M' && str[1] == 'A')
        {   
            a = Pop(s);
            b = Pop(s);
            if (a > b)
            {
                Push(s, a);
            }
            else
            {
                Push(s, b);
            }
        }
        else if (str[0] == 'M' && str[1] == 'I')
        {   
            a = Pop(s);
            b = Pop(s);
            if (a < b)
            {
                Push(s, a);
            }
            else
            {
                Push(s, b);
            }
        }
        else if (str[0] == 'N')
        {   
            x = Pop(s);
            Push(s, -x);
        }
        else if (str[0] == 'D' && str[1] == 'U')
        {   
            x = Pop(s);
            Push(s, x);
            Push(s, x);
        }
        else if (str[0] == 'S' && str[1] == 'W')
        {   
            a = Pop(s);
            b = Pop(s);
            Push(s, a);
            Push(s, b);
        }
        scanf("%s", str);
    }
    printf("%lld\n", Pop(s));
    
    free(s->data);
    free(s);
}