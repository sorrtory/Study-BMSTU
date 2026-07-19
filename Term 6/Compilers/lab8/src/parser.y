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
