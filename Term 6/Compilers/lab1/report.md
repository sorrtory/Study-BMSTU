% Лабораторная работа № 1.1. Раскрутка самоприменимого компилятора
% 16 февраля 2026 г.
% Александр Федуков, ИУ9-62Б

# Цель работы

Целью данной работы является ознакомление с раскруткой самоприменимых компиляторов на примере модельного
компилятора.

# Индивидуальный вариант

Компилятор P5. Заменить операторы div и mod на // и % соответственно.

# Реализация

Различие между файлами `pcom.pas` и `pcom2.pas`:

Я изменил количество зарезервированных слов в компиляторе, убрав `div` и `mod` из списка зарезервированных
слов. Я добавил новые операторы `//` и `%` в список операторов и связал их с соответствующими операциями
деления и остатка от деления через внутреннюю реализацию в компиляторе. Я также обновил таблицы символов и
операторов, чтобы учесть эти изменения.

```diff
--- src/pcom.pas	2026-02-16 12:38:54.711487807 +0300
+++ vm-shared/pcom2.pas	2026-02-16 16:47:35.000000000 +0300
@@ -326,7 +326,7 @@
    maxins     = 78;  { maximum number of instructions }
    maxids     = 250; { maximum characters in id string (basically, a full line) }
    maxstd     = 39;  { number of standard identifiers }
-   maxres     = 35;  { number of reserved words }
+   maxres     = 33;  { number of reserved words }
    reslen     = 9;   { maximum length of reserved words }
    varsqt     = 10;  { variable string quanta }
    prtlln     = 10;  { number of label characters to print in dumps }
@@ -1495,8 +1495,25 @@
          if not iscmte then nextch; goto 1
        end;
       special:
-        begin sy := ssy[ch]; op := sop[ch];
-          nextch
+        begin
+          if ch = '/' then
+            begin
+              nextch;  { consume first '/' }
+              if ch = '/' then
+                begin
+                  sy := mulop; op := idiv;
+                  nextch; { consume second '/' }
+                end
+              else
+                begin
+                  sy := mulop; op := rdiv;
+                end
+            end
+          else
+            begin
+              sy := ssy[ch]; op := sop[ch];
+              nextch
+            end
         end;
       chspace: sy := othersy
     end; (*case*)
@@ -5345,17 +5362,25 @@
       rw[ 1] := 'if       '; rw[ 2] := 'do       '; rw[ 3] := 'of       ';
       rw[ 4] := 'to       '; rw[ 5] := 'in       '; rw[ 6] := 'or       ';
       rw[ 7] := 'end      '; rw[ 8] := 'for      '; rw[ 9] := 'var      ';
-      rw[10] := 'div      '; rw[11] := 'mod      '; rw[12] := 'set      ';
-      rw[13] := 'and      '; rw[14] := 'not      '; rw[15] := 'nil      ';
-      rw[16] := 'then     '; rw[17] := 'else     '; rw[18] := 'with     ';
-      rw[19] := 'goto     '; rw[20] := 'case     '; rw[21] := 'type     ';
-      rw[22] := 'file     '; rw[23] := 'begin    '; rw[24] := 'until    ';
-      rw[25] := 'while    '; rw[26] := 'array    '; rw[27] := 'const    ';
-      rw[28] := 'label    '; rw[29] := 'repeat   '; rw[30] := 'record   ';
-      rw[31] := 'downto   '; rw[32] := 'packed   '; rw[33] := 'program  ';
-      rw[34] := 'function '; rw[35] := 'procedure';
-      frw[1] :=  1; frw[2] :=  1; frw[3] :=  7; frw[4] := 16; frw[5] := 23;
-      frw[6] := 29; frw[7] := 33; frw[8] := 34; frw[9] := 35; frw[10] := 36;
+      rw[10] := 'set      '; rw[11] := 'and      '; rw[12] := 'not      ';
+      rw[13] := 'nil      '; rw[14] := 'then     '; rw[15] := 'else     ';
+      rw[16] := 'with     '; rw[17] := 'goto     '; rw[18] := 'case     ';
+      rw[19] := 'type     '; rw[20] := 'file     '; rw[21] := 'begin    ';
+      rw[22] := 'until    '; rw[23] := 'while    '; rw[24] := 'array    ';
+      rw[25] := 'const    '; rw[26] := 'label    '; rw[27] := 'repeat   ';
+      rw[28] := 'record   '; rw[29] := 'downto   '; rw[30] := 'packed   ';
+      rw[31] := 'program  '; rw[32] := 'function '; rw[33] := 'procedure';
+
+      frw[1] :=  1;
+      frw[2] :=  1;
+      frw[3] :=  7;
+      frw[4] := 14;
+      frw[5] := 21;
+      frw[6] := 27;
+      frw[7] := 31;
+      frw[8] := 32;
+      frw[9] := 33;
+      frw[10]:= 34;  { maxres+1 }
     end (*reswords*) ;

     procedure symbols;
@@ -5363,33 +5388,34 @@
       rsy[ 1] := ifsy;      rsy[ 2] := dosy;      rsy[ 3] := ofsy;
       rsy[ 4] := tosy;      rsy[ 5] := relop;     rsy[ 6] := addop;
       rsy[ 7] := endsy;     rsy[ 8] := forsy;     rsy[ 9] := varsy;
-      rsy[10] := mulop;     rsy[11] := mulop;     rsy[12] := setsy;
-      rsy[13] := mulop;     rsy[14] := notsy;     rsy[15] := nilsy;
-      rsy[16] := thensy;    rsy[17] := elsesy;    rsy[18] := withsy;
-      rsy[19] := gotosy;    rsy[20] := casesy;    rsy[21] := typesy;
-      rsy[22] := filesy;    rsy[23] := beginsy;   rsy[24] := untilsy;
-      rsy[25] := whilesy;   rsy[26] := arraysy;   rsy[27] := constsy;
-      rsy[28] := labelsy;   rsy[29] := repeatsy;  rsy[30] := recordsy;
-      rsy[31] := downtosy;  rsy[32] := packedsy;  rsy[33] := progsy;
-      rsy[34] := funcsy;    rsy[35] := procsy;
+      rsy[10] := setsy;     rsy[11] := mulop;     rsy[12] := notsy;
+      rsy[13] := nilsy;     rsy[14] := thensy;    rsy[15] := elsesy;
+      rsy[16] := withsy;    rsy[17] := gotosy;    rsy[18] := casesy;
+      rsy[19] := typesy;    rsy[20] := filesy;    rsy[21] := beginsy;
+      rsy[22] := untilsy;   rsy[23] := whilesy;   rsy[24] := arraysy;
+      rsy[25] := constsy;   rsy[26] := labelsy;   rsy[27] := repeatsy;
+      rsy[28] := recordsy;  rsy[29] := downtosy;  rsy[30] := packedsy;
+      rsy[31] := progsy;    rsy[32] := funcsy;    rsy[33] := procsy;
       ssy['+'] := addop ;   ssy['-'] := addop;    ssy['*'] := mulop;
       ssy['/'] := mulop ;   ssy['('] := lparent;  ssy[')'] := rparent;
       ssy['$'] := othersy ; ssy['='] := relop;    ssy[' '] := othersy;
       ssy[','] := comma ;   ssy['.'] := period;   ssy['''']:= othersy;
       ssy['['] := lbrack ;  ssy[']'] := rbrack;   ssy[':'] := colon;
       ssy['^'] := arrow ;   ssy['<'] := relop;    ssy['>'] := relop;
-      ssy[';'] := semicolon; ssy['@'] := arrow;
+      ssy[';'] := semicolon; ssy['@'] := arrow; ssy['%'] := mulop;
     end (*symbols*) ;

     procedure rators;
       var i: integer;
     begin
-      for i := 1 to maxres (*nr of res words*) do rop[i] := noop;
-      rop[5] := inop; rop[10] := idiv; rop[11] := imod;
-      rop[6] := orop; rop[13] := andop;
+      for i := 1 to maxres do rop[i] := noop;
+        rop[5]  := inop;
+        rop[6]  := orop;
+        rop[11] := andop;   {now 'and' is rw[11] }
       for i := ordminchar to ordmaxchar do sop[chr(i)] := noop;
       sop['+'] := plus; sop['-'] := minus; sop['*'] := mul; sop['/'] := rdiv;
-      sop['='] := eqop; sop['<'] := ltop;  sop['>'] := gtop;
+      sop['%'] := imod;
+      sop['='] := eqop; sop['<'] := ltop;  sop['>'] := gtop;
     end (*rators*) ;

     procedure procmnemonics;
@@ -5488,6 +5514,7 @@
       chartp['<'] := chlt    ; chartp['>'] := chgt    ;
       chartp['{'] := chlcmt  ; chartp['}'] := special ;
       chartp['@'] := special ;
+      chartp['%'] := special;

       ordint['0'] := 0; ordint['1'] := 1; ordint['2'] := 2;
       ordint['3'] := 3; ordint['4'] := 4; ordint['5'] := 5;
```

Различие между файлами `pcom2.pas` и `pcom3.pas`:

Я заменил некоторые вхождения оператора `div` на `//` и оператора `mod` на `%` в исходном коде компилятора.

```diff
--- vm-shared/pcom2.pas	2026-02-16 16:47:35.000000000 +0300
+++ vm-shared/pcom3.pas	2026-02-16 16:50:10.000000000 +0300
@@ -1694,7 +1694,7 @@
   begin
     k := alignquot(fsp);
     l := flc-1;
-    flc := l + k  -  (k+l) mod k
+    flc := l + k  -  (k+l) % k
   end (*align*);

   procedure printtables(fb: boolean);
@@ -2967,7 +2967,7 @@
       end;

       procedure putic;
-      begin if ic mod 10 = 0 then writeln(prr,'i',ic:5) end;
+      begin if ic % 10 = 0 then writeln(prr,'i',ic:5) end;

       procedure gen0(fop: oprange);
       begin
@@ -3659,7 +3659,7 @@
                             if lsp^.form = scalar then error(399)
                             else
                               if string(lsp) then
-                                begin len := lsp^.size div charmax;
+                                begin len := lsp^.size // charmax;
                                   if default then
                                         gen2(51(*ldc*),1,len);
                                   gen2(51(*ldc*),1,len);
@@ -5329,7 +5329,7 @@
     (* note in the above reservation of buffer store for 2 text files *)
     ic := 3; eol := true; linecount := 0;
     ch := ' '; chcnt := 0;
-    mxint10 := maxint div 10;
+    mxint10 := maxint // 10;
     inputhdf := false; { set 'input' not in header files }
     outputhdf := false; { set 'output' not in header files }
     for i := 1 to 500 do errtbl[i] := false; { initialize error tracking }
```

# Тестирование

Тестовый пример:

```pascal
program hello(output);
begin
  writeln('Hello, world ', 7 // 3, ' ', 7 % 3)
end.
```

Вывод тестового примера на `stdout`

```
z@z-Standard-PC-Q35-ICH9-2009:~/Downloads/p5$ ./pint
P5 Pascal interpreter vs. 1.0

Assembling/loading program
Running program

Hello, world           2           1

program complete
```

При попытке использовать старый оператор `div` в `hello2.pas` с помощью `pcom2.pas` не получится
скомпилировать `hello2.pas` и будет выведено сообщение об ошибке. Однако если использовать новый оператор
`//`, тогда `hello2.pas` успешно скомпилируется.

```bash
z@z-Standard-PC-Q35-ICH9-2009:~/Downloads/p5$ ./pcom < pcom2.pas
P5 Pascal compiler vs. 1.0


     1       40 (*$c+,t-,d-,l-

Errors in program: 0
z@z-Standard-PC-Q35-ICH9-2009:~/Downloads/p5$ mv prr prd
z@z-Standard-PC-Q35-ICH9-2009:~/Downloads/p5$ ./pint <hello2.pas
P5 Pascal interpreter vs. 1.0

Assembling/loading program
Running program

P5 Pascal compiler vs. 1.0


     1       40 program hello(output);
     2       40 begin
     3        3   writeln('Hello, world ', 7 div 3, ' ', 7 % 3)
     3   ****                                  ^6,104^59
     4       19 end.

Errors in program: 3

Error numbers in listing:
-------------------------
  6  Illegal symbol
 59  Error in variable
104  Identifier not declared


program complete
z@z-Standard-PC-Q35-ICH9-2009:~/Downloads/p5$ ./pint <hello2.pas
P5 Pascal interpreter vs. 1.0

Assembling/loading program
Running program

P5 Pascal compiler vs. 1.0


     1       40 program hello(output);
     2       40 begin
     3        3   writeln('Hello, world ', 7 // 3, ' ', 7 % 3)
     4       24 end.

Errors in program: 0

program complete
```

# Вывод

В данной лабораторной работе была выполнена раскрутка самоприменимого компилятора P5. Были внесены изменения в
исходный код компилятора для замены операторов `div` и `mod` на `//` и `%` соответственно.

Были проведены тесты, которые показали успешную компиляцию и выполнение программы `hello2.pas` с
использованием новых операторов, в то время как использование старых операторов приводило к ошибкам
компиляции.

Я поработал с pascal, c его компилятором и интерпретатором. На практике применил раскрутку самоприменимого
компилятора, что позволило мне погрузиться в некоторые принципы работы компиляторов.
