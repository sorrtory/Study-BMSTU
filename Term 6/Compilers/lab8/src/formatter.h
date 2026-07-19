#ifndef FORMATTER_H
#define FORMATTER_H

struct Formatter {
    int indent;
    int modules;
};

void formatter_init(struct Formatter *formatter);
void formatter_begin_module(struct Formatter *formatter, const char *line);
void formatter_begin_block(struct Formatter *formatter, const char *line);
void formatter_else(struct Formatter *formatter);
void formatter_end_block(struct Formatter *formatter, const char *line);
void formatter_line(const struct Formatter *formatter, const char *line);

char *text_copy(const char *text);
char *text_format(const char *format, ...);
char *text_join(char *left, const char *separator, char *right);

#endif
