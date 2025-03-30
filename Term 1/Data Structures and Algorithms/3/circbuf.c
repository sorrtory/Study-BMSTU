#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Queue
{
    int *data;
    int cap;
    int count;
    int head;
    int tail;
};

struct Queue *InitQueue(int n)
{
    struct Queue *q = (struct Queue *)malloc(sizeof(struct Queue));
    q->data = (int *)malloc(n * sizeof(int));
    q->cap = n;
    q->count = 0;
    q->head = 0;
    q->tail = 0;
    return q;
}

int QueueEmpty(struct Queue *q)
{
    return q->count == 0;
}

int Dequeue(struct Queue *q)
{
    if (QueueEmpty(q))
    {
        printf("Опустошение");
    }
    else
    {
        int x = q->data[q->head];
        q->head += 1;
        if (q->head == q->cap)
        {
            q->head = 0;
        }
        q->count -= 1;
        return x;
    }
}
void Enqueue(struct Queue *q, int x);

// int Getqueue(struct Queue *q, int depth)
// {
//     return q->data[q->head + depth];
// }

void QueueCopy(struct Queue *q1, struct Queue *q2)
{
    int n = q2->count;
    for (size_t i = 0; i < n; i++)
    {
        Enqueue(q1, Dequeue(q2));
    }
}
void Enqueue(struct Queue *q, int x)
{
    if (q->count == q->cap)
    {
        // printf("Переполнение\n");
        struct Queue *q_temp = InitQueue(q->cap * 2);
        QueueCopy(q_temp, q);
        Enqueue(q_temp, x);
        q->data = (int *)realloc(q->data, (q->cap * 2) * sizeof(int));
        q->cap *= 2;
        QueueCopy(q, q_temp);
        free(q_temp->data);
        free(q_temp);
    }
    else
    {

        q->data[q->tail] = x;
        q->tail += 1;
        if (q->tail == q->cap)
        {
            q->tail = 0;
        }
        q->count += 1;
    }
}
void main()
{
    struct Queue *q = InitQueue(4);
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
        scanf("%s", str);
    }
    free(q->data);
    free(q);
}