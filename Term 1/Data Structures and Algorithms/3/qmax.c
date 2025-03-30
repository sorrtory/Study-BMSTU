#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//////////// DOUBLE STACK ////////////////////
struct DoubleStack
{
    int *data;
    int cap;
    int top1;
    int top2;

    int *max_values;
};

struct DoubleStack *InitDoubleStack(int n)
{
    struct DoubleStack *s = (struct DoubleStack *)malloc(sizeof(struct DoubleStack));
    s->data = (int *)malloc(n * sizeof(int));
    s->max_values = (int *)malloc(n * sizeof(int));
    s->cap = n;
    s->top1 = 0;
    s->top2 = n - 1;
    return s;
}

void StackClean(struct DoubleStack *s)
{
    free(s->data);
    free(s->max_values);
    free(s);
}

int StackEmpty1(struct DoubleStack *s)
{
    return s->top1 == 0;
}

int StackEmpty2(struct DoubleStack *s)
{
    return s->top2 == s->cap - 1;
}

int max(int a, int b)
{
    if (a > b)
    {
        return a;
    }
    else
    {
        return b;
    }
}

void Push1(struct DoubleStack *s, int x);
void Push2(struct DoubleStack *s, int x);
int Pop1(struct DoubleStack *s);
int Pop2(struct DoubleStack *s);

void DoubleStackCopy(struct DoubleStack *s1, struct DoubleStack *s2)
{
    struct DoubleStack *s2_temp = InitDoubleStack(s2->cap);

    // Get reversed s2
    while (!StackEmpty1(s2))
    {
        Push1(s2_temp, Pop1(s2));
    }

    while (!StackEmpty2(s2))
    {
        Push2(s2_temp, Pop2(s2));
    }

    // Clone to s1
    while (!StackEmpty1(s2_temp))
    {
        Push1(s1, Pop1(s2_temp));
    }

    while (!StackEmpty2(s2_temp))
    {
        Push2(s1, Pop2(s2_temp));
    }

    StackClean(s2_temp);
}

void StackExtend(struct DoubleStack *s)
{
    struct DoubleStack *s_temp = InitDoubleStack(s->cap * 2);
    DoubleStackCopy(s_temp, s);
    s->data = (int *)realloc(s->data, s->cap * 2 * sizeof(int));
    s->max_values = (int *)realloc(s->max_values, s->cap * 2 * sizeof(int));
    s->top2 = s->cap * 2 - (s->cap - s->top2);
    s->cap *= 2;
    DoubleStackCopy(s, s_temp);
    StackClean(s_temp);
}
void Push1(struct DoubleStack *s, int x)
{
    if (s->top2 < s->top1)
    {
        // printf("Переполнение 1\n");
        StackExtend(s);
        Push1(s, x);
    }
    else
    {
        if (s->top1 == 0)
        {
            s->max_values[s->top1] = x;
        }
        else
        {
            s->max_values[s->top1] = max(s->max_values[s->top1 - 1], x);
        }

        s->data[s->top1] = x;
        s->top1 += 1;
    }
}

void Push2(struct DoubleStack *s, int x)
{

    if (s->top2 < s->top1)
    {
        printf("Переполнение 2\n");
        StackExtend(s);
        Push2(s, x);
    }
    else
    {
        if (s->top2 == s->cap - 1)
        {
            s->max_values[s->top2] = x;
        }
        else
        {
            s->max_values[s->top2] = max(s->max_values[s->top2 + 1], x);
        }

        s->data[s->top2] = x;
        s->top2 -= 1;
    }
}
int Pop1(struct DoubleStack *s)
{
    if (StackEmpty1(s))
    {
        printf("Опустошение 1");
    }
    else
    {
        s->top1 -= 1;
        return s->data[s->top1];
    }
}

int Pop2(struct DoubleStack *s)
{
    if (StackEmpty2(s))
    {
        printf("Опустошение 2");
    }
    else
    {
        s->top2 += 1;
        return s->data[s->top2];
    }
}

//////////// QUEUE ////////////////////
typedef struct DoubleStack QueueOnStack;

QueueOnStack *InitQueueOnStack(int n)
{
    return InitDoubleStack(n);
}
int QueueEmpty(QueueOnStack *s)
{
    return StackEmpty1(s) && StackEmpty2(s);
}

void Enqueue(QueueOnStack *s, int x)
{
    Push1(s, x);
}
int Dequeue(QueueOnStack *s)
{
    if (StackEmpty2(s))
    {
        while (!StackEmpty1(s))
        {
            Push2(s, Pop1(s));
        }
    }
    return Pop2(s);
}
int QueueMax(QueueOnStack *s)
{
    int mx1 = -2100000000;
    int mx2 = -2100000000;
    if (s->top1 != 0)
    {
        mx1 = s->max_values[s->top1 - 1];
    }
    if (s->top2 != s->cap - 1)
    {
        mx2 = s->max_values[s->top2 + 1];
    }
    return max(mx1, mx2);
}
void main()
{
    QueueOnStack *q = InitQueueOnStack(10000);
    int x = 0;
    char str[20];
    scanf("%s", str);
    while (strcmp(str, "END"))
    {
        if (!strcmp(str, "ENQ"))
        {
            scanf("%d", &x);
            Enqueue(q, x);
        }
        else if (!strcmp(str, "DEQ"))
        {
            x = Dequeue(q);
            printf("%d\n", x);
        }
        else if (!strcmp(str, "EMPTY"))
        {
            if (QueueEmpty(q))
            {
                printf("true\n");
            }
            else
            {
                printf("false\n");
            }
        }
        else if (!strcmp(str, "MAX"))
        {
            x = QueueMax(q);
            printf("%d\n", x);
        }
        scanf("%s", str);
    }

    free(q->data);
    free(q->max_values);
    free(q);
}