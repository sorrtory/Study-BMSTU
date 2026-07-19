% Лабораторная работа 3.2 «Форматтер исходных текстов»
% 3 июня 2026 г.
% Александр Федуков, ИУ9-62Б

# Цель работы

Целью данной работы является приобретение навыков использования генератора
синтаксических анализаторов bison.

# Индивидуальный вариант

Диалект Бейсика

```
' Суммирование элементов массива
Function SumArray#(Values#(nValues%))
  SumArray# = 0
  For i% = 1 To nValues%
    SumArray# = SumArray# + Values#(i%)
  Next i%
End Function

' Вычисление многочлена по схеме Горнера
Function Polynom!(x!, coefs!(ncoefs%))
  Polynom! = 0
  For i% = 1 to ncoefs%
    ' длинные строки можно переносить знаком прочерка
    Polynom! = Polynom! * x! + _
        coefs!(i%)
  Next i%
End Function

' Вычисление многочлена x³ + x² + x + 1
Function Polynom1111!(x!)
  Dim coefs!(4)

  For i% = 1 To 4
    coefs!(i%) = 1
  Next i%

  Polynom1111! = Polynom!(x!, coefs!)
End Function

' Инициализация массива числами Фибоначчи
Sub Fibonacci(res&(n%))
  If n% >= 1 Then
    res&(1) = 1
  End If

  If n% >= 2 Then
    res&(2) = 1
  End If

  i% = 3
  Do While i% <= n%
    ' длинные строки можно переносить знаком прочерка
    res&(i%) = res&(i% - 1) _
      + res&(i% - 2)
    i% = i% + 1
  Loop
End Sub

' Склеивание элементов массива через разделитель: Join$(", ", words)
Function Join$(sep$, items$(count%))
  If count% >= 1 Then
    Join$ = items$(1)
  Else
    Join$ = ""
  End If

  For i% = 2 To count%
    Join$ = Join$ + sep$ + items$(i%)
  Next i%
End Function

Комментарии начинаются с апострофа ' и продолжаются до конца строки.

Переводы строк значимые. Длинные строки можно переносить знаком прочерка на конце строки.

Идентификаторы и ключевые слова не чувствительны к регистру.

В имени каждой переменной и каждой функции указывается её тип:
% — целое, & — длинное целое, ! — вещественное одинарной точности,
# — вещественное двойной точности, $ — строка.

Внутри функции неявно объявляется переменная с тем же именем, что и имя самой функции.
Её значение является возвращаемым значением функции.

И индексация массивов, и вызов функции записываются при помощи круглых скобок.
Отличить одно от другого на этапе синтаксического анализа невозможно, поэтому в дереве
они различаться не должны. Квадратные скобки в реализации не поддерживаются.

Цикл с условием может быть записан пятью способами:

Do While …      Do Until …      Do            Do                Do
  …               …               …             …                 …
Loop            Loop            Loop While …  Loop Until …      Loop

Первые две формы — циклы с предусловием (положительным и отрицательным), две другие —
с постусловием и, наконец, пятая — бесконечный цикл.
```

# Реализация

## main.c

```c
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
```

## lexer.h

```
#ifndef LEXER_H
#define LEXER_H

#include <stdio.h>

#ifndef YY_TYPEDEF_YY_SCANNER_T
#define YY_TYPEDEF_YY_SCANNER_T
typedef void *yyscan_t;
#endif

struct Extra {
    int cur_line;
    int cur_column;
};

int init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra);
void destroy_scanner(yyscan_t scanner);

#endif

```

## lexer.l

```
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
```

## parser.y

```
%{

#include <stdio.h>
#include <stdlib.h>

#include "formatter.h"
#include "lexer.h"

%}

%define api.pure full
%define parse.error detailed
%locations

%code requires {
struct Formatter;
}

%lex-param {yyscan_t scanner}
%parse-param {yyscan_t scanner}
%parse-param {struct Formatter *formatter}

%union {
    char *text;
}

%token <text> IDENT SUB_IDENT NUMBER STRING
%token NEWLINE INVALID
%token FUNCTION SUB END IF THEN ELSE FOR TO NEXT DO WHILE UNTIL LOOP DIM
%token GE LE NE

%left '=' '<' '>' GE LE NE
%left '+' '-'
%left '*' '/'
%precedence UMINUS

%type <text> header sub_header params_opt params param
%type <text> simple_stmt assignment dim_stmt call_stmt variable args_opt args expr

%destructor { free($$); } <text>

%{

int yylex(YYSTYPE *yylval, YYLTYPE *yylloc, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner,
             struct Formatter *formatter, const char *message);

%}

%%

program
    : newlines_opt modules
    ;

modules
    : module
    | modules module
    ;

module
    : function
    | sub
    ;

function
    : FUNCTION header newlines
      {
          char *line = text_format("Function %s", $2);
          formatter_begin_module(formatter, line);
          free(line);
          free($2);
          $2 = NULL;
      }
      statements END FUNCTION
      {
          formatter_end_block(formatter, "End Function");
      }
      newlines_opt
    ;

sub
    : SUB sub_header newlines
      {
          char *line = text_format("Sub %s", $2);
          formatter_begin_module(formatter, line);
          free(line);
          free($2);
          $2 = NULL;
      }
      statements END SUB
      {
          formatter_end_block(formatter, "End Sub");
      }
      newlines_opt
    ;

header
    : IDENT '(' params_opt ')'
      {
          $$ = text_format("%s(%s)", $1, $3);
          free($1);
          free($3);
      }
    ;

sub_header
    : SUB_IDENT '(' params_opt ')'
      {
          $$ = text_format("%s(%s)", $1, $3);
          free($1);
          free($3);
      }
    ;

params_opt
    : %empty                    { $$ = text_copy(""); }
    | params                    { $$ = $1; }
    ;

params
    : param                     { $$ = $1; }
    | params ',' param          { $$ = text_join($1, ", ", $3); }
    ;

param
    : IDENT                     { $$ = $1; }
    | IDENT '(' IDENT ')'
      {
          $$ = text_format("%s(%s)", $1, $3);
          free($1);
          free($3);
      }
    ;

statements
    : %empty
    | statements statement newlines
    ;

statement
    : simple_stmt
      {
          formatter_line(formatter, $1);
          free($1);
      }
    | if_stmt
    | for_stmt
    | do_stmt
    ;

simple_stmt
    : assignment                { $$ = $1; }
    | dim_stmt                  { $$ = $1; }
    | call_stmt                 { $$ = $1; }
    ;

assignment
    : variable '=' expr
      {
          $$ = text_format("%s = %s", $1, $3);
          free($1);
          free($3);
      }
    ;

dim_stmt
    : DIM variable
      {
          $$ = text_format("Dim %s", $2);
          free($2);
      }
    ;

call_stmt
    : variable                 { $$ = $1; }
    ;

if_stmt
    : IF expr THEN newlines
      {
          char *line = text_format("If %s Then", $2);
          formatter_begin_block(formatter, line);
          free(line);
          free($2);
          $2 = NULL;
      }
      statements if_tail
    ;

if_tail
    : END IF
      {
          formatter_end_block(formatter, "End If");
      }
    | ELSE newlines
      {
          formatter_else(formatter);
      }
      statements END IF
      {
          formatter_end_block(formatter, "End If");
      }
    ;

for_stmt
    : FOR variable '=' expr TO expr newlines
      {
          char *line = text_format("For %s = %s To %s", $2, $4, $6);
          formatter_begin_block(formatter, line);
          free(line);
          free($2);
          $2 = NULL;
          free($4);
          $4 = NULL;
          free($6);
          $6 = NULL;
      }
      statements NEXT variable
      {
          char *line = text_format("Next %s", $11);
          formatter_end_block(formatter, line);
          free(line);
          free($11);
      }
    ;

do_stmt
    : DO do_body
    ;

do_body
    : newlines
      {
          formatter_begin_block(formatter, "Do");
      }
      statements LOOP do_tail
    | WHILE expr newlines
      {
          char *line = text_format("Do While %s", $2);
          formatter_begin_block(formatter, line);
          free(line);
          free($2);
          $2 = NULL;
      }
      statements LOOP
      {
          formatter_end_block(formatter, "Loop");
      }
    | UNTIL expr newlines
      {
          char *line = text_format("Do Until %s", $2);
          formatter_begin_block(formatter, line);
          free(line);
          free($2);
          $2 = NULL;
      }
      statements LOOP
      {
          formatter_end_block(formatter, "Loop");
      }
    ;

do_tail
    : %empty
      {
          formatter_end_block(formatter, "Loop");
      }
    | WHILE expr
      {
          char *line = text_format("Loop While %s", $2);
          formatter_end_block(formatter, line);
          free(line);
          free($2);
      }
    | UNTIL expr
      {
          char *line = text_format("Loop Until %s", $2);
          formatter_end_block(formatter, line);
          free(line);
          free($2);
      }
    ;

variable
    : IDENT                     { $$ = $1; }
    | IDENT '(' args_opt ')'
      {
          $$ = text_format("%s(%s)", $1, $3);
          free($1);
          free($3);
      }
    ;

args_opt
    : %empty                    { $$ = text_copy(""); }
    | args                      { $$ = $1; }
    ;

args
    : expr                      { $$ = $1; }
    | args ',' expr             { $$ = text_join($1, ", ", $3); }
    ;

expr
    : variable                  { $$ = $1; }
    | NUMBER                    { $$ = $1; }
    | STRING                    { $$ = $1; }
    | '(' expr ')'
      {
          $$ = text_format("(%s)", $2);
          free($2);
      }
    | '-' expr %prec UMINUS
      {
          $$ = text_format("-%s", $2);
          free($2);
      }
    | expr '+' expr             { $$ = text_join($1, " + ", $3); }
    | expr '-' expr             { $$ = text_join($1, " - ", $3); }
    | expr '*' expr             { $$ = text_join($1, " * ", $3); }
    | expr '/' expr             { $$ = text_join($1, " / ", $3); }
    | expr '=' expr             { $$ = text_join($1, " = ", $3); }
    | expr '<' expr             { $$ = text_join($1, " < ", $3); }
    | expr '>' expr             { $$ = text_join($1, " > ", $3); }
    | expr GE expr              { $$ = text_join($1, " >= ", $3); }
    | expr LE expr              { $$ = text_join($1, " <= ", $3); }
    | expr NE expr              { $$ = text_join($1, " <> ", $3); }
    ;

newlines_opt
    : %empty
    | newlines
    ;

newlines
    : NEWLINE
    | newlines NEWLINE
    ;

%%

void yyerror(YYLTYPE *loc, yyscan_t scanner,
             struct Formatter *formatter, const char *message)
{
    (void)scanner;
    (void)formatter;
    fprintf(stderr, "Syntax error at %d:%d: %s\n",
            loc->first_line, loc->first_column, message);
}
```

## formatter.h

```c
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
```

## formatter.c

```c
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
```

# Тестирование

Входные данные

```
' Суммирование элементов массива
Function SumArray#(Values#(nValues%))
SumArray#=0
For i%=1 To nValues%
SumArray#=SumArray#+Values#(i%)
Next i%
End Function

' Вычисление многочлена по схеме Горнера
Function Polynom!(x!,coefs!(ncoefs%))
Polynom!=0
For i%=1 to ncoefs%
Polynom!=Polynom!*x!+_
coefs!(i%)
Next i%
End Function

Function Polynom1111!(x!)
Dim coefs!(4)

For i%=1 To 4
coefs!(i%)=1
Next i%

Polynom1111!=Polynom!(x!,coefs!)
End Function

Sub Fibonacci(res&(n%))
If n%>=1 Then
res&(1)=1
End If
If n%>=2 Then
res&(2)=1
End If
i%=3
Do While i%<=n%
res&(i%)=res&(i%-1)+res&(i%-2)
i%=i%+1
Loop
End Sub

Function Join$(sep$,items$(count%))
If count%>=1 Then
Join$=items$(1)
Else
Join$=""
End If
For i%=2 To count%
Join$=Join$+sep$+items$(i%)
Next i%
End Function
```

Вывод на `stdout`

```
Function SumArray#(Values#(nValues%))
  SumArray# = 0
  For i% = 1 To nValues%
    SumArray# = SumArray# + Values#(i%)
  Next i%
End Function

Function Polynom!(x!, coefs!(ncoefs%))
  Polynom! = 0
  For i% = 1 To ncoefs%
    Polynom! = Polynom! * x! + coefs!(i%)
  Next i%
End Function

Function Polynom1111!(x!)
  Dim coefs!(4)
  For i% = 1 To 4
    coefs!(i%) = 1
  Next i%
  Polynom1111! = Polynom!(x!, coefs!)
End Function

Sub Fibonacci(res&(n%))
  If n% >= 1 Then
    res&(1) = 1
  End If
  If n% >= 2 Then
    res&(2) = 1
  End If
  i% = 3
  Do While i% <= n%
    res&(i%) = res&(i% - 1) + res&(i% - 2)
    i% = i% + 1
  Loop
End Sub

Function Join$(sep$, items$(count%))
  If count% >= 1 Then
    Join$ = items$(1)
  Else
    Join$ = ""
  End If
  For i% = 2 To count%
    Join$ = Join$ + sep$ + items$(i%)
  Next i%
End Function
```

Входные данные

```
Sub Loops(n%)
Do
n%=n%-1
Loop
Do Until n%=0
n%=n%-1
Loop
Do
n%=n%-1
Loop While n%>0
Do
n%=n%-1
Loop Until n%=0
End Sub
```

Вывод на `stdout`

```
Sub Loops(n%)
  Do
    n% = n% - 1
  Loop
  Do Until n% = 0
    n% = n% - 1
  Loop
  Do
    n% = n% - 1
  Loop While n% > 0
  Do
    n% = n% - 1
  Loop Until n% = 0
End Sub
```

Входные данные

```
Function Broken#()
  Broken# = 1 +
End Function
```

Вывод ошибки

```
Function Broken#()
Syntax error at 2:16: syntax error, unexpected NEWLINE
```

# Вывод

В ходе работы был реализован форматтер диалекта Бейсика. Flex использован для
лексического анализа: он выделяет ключевые слова, идентификаторы, числа, строки и
значимые переводы строк. Bison использован для описания грамматики программы и
выполнения действий необходимых для форматирования при разборе.
В результате программа приводит
исходный текст к единому виду и сообщает об ошибках синтаксиса.
