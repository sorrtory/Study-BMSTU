#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char *argv[])
{

    int n = 0;

    for (size_t i = 0; argv[i] != 0; i++)
    {
        n++;
    }

    if (n != 4)
    {
        printf("Usage: frame <height> <width> <text>");
    }
    else
    {
        int height = atoi(argv[1]);
        int width = atoi(argv[2]) + 1;
        int text_len = strlen(argv[3]);

        if (width - 3 < text_len || height < 3)
        {
            printf("Error");
        }
        else
        {

            int word_height = (height - 1) / 2;
            int word_width = (width - text_len - 1) / 2;
            int k = 0;
            for (size_t i = 1; i < width * height + 1; i++)
            {
                if (i % width == 0)
                {
                    printf("\n");
                }

                else if (i < width || i > width * (height - 1) || i % width == 1 || i % width == width - 1)
                {

                    printf("*");
                }
                else if (k != text_len && i / width == word_height && i % width > word_width)
                {
                    printf("%c", argv[3][k]);
                    k++;
                }
                else
                {
                    printf(" ");
                }
            }
        }
    }
    return 0;
}