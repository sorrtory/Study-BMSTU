#include <stdio.h>

static int add(int left, int right) {
    return left + right;
}

int main(void) {
    printf("Result: %d\n", add(2, 3));
    return 0;
}
