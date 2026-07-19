#include "formatter.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void out_indent(int indent)
{
    int i;

    for (i = 0; i < indent; ++i) {
        fputs("  ", stdout);
    }
}

static void out_line(int indent, const char *line)
{
    out_indent(indent);
    puts(line);
}

static void out_of_memory(void)
{
    fputs("Out of memory\n", stderr);
    exit(1);
}

void formatter_init(struct Formatter *formatter)
{
    formatter->indent = 0;
    formatter->modules = 0;
}

void formatter_begin_module(struct Formatter *formatter, const char *line)
{
    if (formatter->modules > 0) {
        putchar('\n');
    }

    formatter->modules += 1;
    out_line(formatter->indent, line);
    formatter->indent += 1;
}

void formatter_begin_block(struct Formatter *formatter, const char *line)
{
    out_line(formatter->indent, line);
    formatter->indent += 1;
}

void formatter_else(struct Formatter *formatter)
{
    formatter->indent -= 1;
    out_line(formatter->indent, "Else");
    formatter->indent += 1;
}

void formatter_end_block(struct Formatter *formatter, const char *line)
{
    formatter->indent -= 1;
    out_line(formatter->indent, line);
}

void formatter_line(const struct Formatter *formatter, const char *line)
{
    out_line(formatter->indent, line);
}

char *text_copy(const char *text)
{
    char *result = strdup(text);

    if (result == NULL) {
        out_of_memory();
    }

    return result;
}

char *text_format(const char *format, ...)
{
    va_list args;
    va_list copy;
    int length;
    char *result;

    va_start(args, format);
    va_copy(copy, args);
    length = vsnprintf(NULL, 0, format, copy);
    va_end(copy);

    if (length < 0) {
        va_end(args);
        out_of_memory();
    }

    result = malloc((size_t)length + 1);
    if (result == NULL) {
        va_end(args);
        out_of_memory();
    }

    vsnprintf(result, (size_t)length + 1, format, args);
    va_end(args);
    return result;
}

char *text_join(char *left, const char *separator, char *right)
{
    char *result = text_format("%s%s%s", left, separator, right);

    free(left);
    free(right);
    return result;
}
