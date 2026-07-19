#include <stdio.h>

#include "formatter.h"
#include "lexer.h"

int yyparse(yyscan_t scanner, struct Formatter *formatter);

int main(int argc, char **argv)
{
    FILE *input = stdin;
    yyscan_t scanner;
    struct Extra extra;
    struct Formatter formatter;
    int result;

    if (argc > 2) {
        fprintf(stderr, "Usage: %s [input.bas]\n", argv[0]);
        return 2;
    }

    if (argc == 2) {
        input = fopen(argv[1], "r");
        if (input == NULL) {
            perror(argv[1]);
            return 2;
        }
    }

    if (init_scanner(input, &scanner, &extra) != 0) {
        fputs("Cannot initialize scanner\n", stderr);
        if (input != stdin) {
            fclose(input);
        }
        return 2;
    }

    formatter_init(&formatter);
    result = yyparse(scanner, &formatter);
    destroy_scanner(scanner);

    if (input != stdin) {
        fclose(input);
    }

    return result == 0 ? 0 : 1;
}
