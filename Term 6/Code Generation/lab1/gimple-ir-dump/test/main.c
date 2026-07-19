#include <stdio.h>

struct Pair {
    int first;
    int second;
};

static int add(int left, int right) {
    return left + right;
}

int main(void) {
    int a = 5;
    int b = 1;
    int c = a + b;
    int d = c * 2;
    int e = d - a;

    while (a < 10) {
        a = a + b;
    }

    if (e > 3) {
        b = b + 10;
    } else {
        b = b - 1;
    }

    int arr[3];
    arr[0] = 100;
    arr[1] = 200;
    arr[2] = arr[0] + arr[1];

    struct Pair pair;
    pair.first = arr[2];
    pair.second = add(pair.first, b);

    int value = 42;
    int *ptr = &value;
    int loaded = *ptr;

    printf("%d\n", pair.second + loaded);
    return 0;
}
