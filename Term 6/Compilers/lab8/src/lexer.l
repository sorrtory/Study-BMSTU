%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"
%option caseless noinput nounput

%{

#include <stdlib.h>
#include <string.h>

#include "lexer.h"
#include "parser.tab.h"

#define YY_USER_ACTION                                                        \
    do {                                                                      \
        int i;                                                                \
        struct Extra *extra = yyextra;                                        \
        yylloc->first_line = extra->cur_line;                                 \
        yylloc->first_column = extra->cur_column;                             \
        for (i = 0; i < yyleng; ++i) {                                        \
            if (yytext[i] == '\n') {                                          \
                extra->cur_line += 1;                                         \
                extra->cur_column = 1;                                        \
            } else {                                                          \
                extra->cur_column += 1;                                       \
            }                                                                 \
        }                                                                     \
        yylloc->last_line = extra->cur_line;                                  \
        yylloc->last_column = extra->cur_column;                              \
    } while (0);

static char *copy_lexeme(const char *text)
{
    char *result = strdup(text);

    if (result == NULL) {
        fputs("Out of memory\n", stderr);
        exit(1);
    }

    return result;
}

%}

%%

[ \t\r]+                    ;
"'"[^\n]*                    ;
_[ \t]*("'"[^\n]*)?\n       ;
\n                          return NEWLINE;

function                    return FUNCTION;
sub                         return SUB;
end                         return END;
if                          return IF;
then                        return THEN;
else                        return ELSE;
for                         return FOR;
to                          return TO;
next                        return NEXT;
do                          return DO;
while                       return WHILE;
until                       return UNTIL;
loop                        return LOOP;
dim                         return DIM;

">="                        return GE;
"<="                        return LE;
"<>"                        return NE;

[(),=+\-*/<>]               return yytext[0];

\"([^\"\n]|\"\")*\"         {
                                yylval->text = copy_lexeme(yytext);
                                return STRING;
                            }

[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)? {
                                yylval->text = copy_lexeme(yytext);
                                return NUMBER;
                            }

[A-Za-z][A-Za-z0-9_]*[%&!#$] {
                                yylval->text = copy_lexeme(yytext);
                                return IDENT;
                            }

[A-Za-z][A-Za-z0-9_]*       {
                                yylval->text = copy_lexeme(yytext);
                                return SUB_IDENT;
                            }

.                           return INVALID;

%%

int init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra)
{
    extra->cur_line = 1;
    extra->cur_column = 1;

    if (yylex_init_extra(extra, scanner) != 0) {
        return 1;
    }

    yyset_in(input, *scanner);
    return 0;
}

void destroy_scanner(yyscan_t scanner)
{
    yylex_destroy(scanner);
}
