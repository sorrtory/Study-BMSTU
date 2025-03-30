#include <stdio.h>

int _log2(int k)
{
  int i = 0;
  while (k > 0)
  {
    k /= 2;
    i++;
  }
  return i - 1;
}

int main(void)
{
  printf("%d", _log2(255));
  return 0;
}