Исходные данные для выполнения лабораторной работы в операционной системе Linux представлены следующим набором
файлов:

- `pcom.pas` — исходный текст компилятора P5;
- `pcom` — исполнимая версия компилятора P5, полученная путём компиляции исходного текста компилятора
  с помощью `gpc` (GNU Pascal Compiler);
- `pint` — интерпретатор псевдокода, предназначенный для выполнения программ;
- `iso7185.pdf` — текст стандарта ISO 7185:1990[2](https://hw.iu9.bmstu.ru/submission?task_id=31231#fn2);
- `hello.pas` — программа, предназначенная для проверки работоспособности компилятора.

для компиляции программы `hello.pas` нужно выполнить команду

```
./pcom <hello.pas
```

> NEW FILE prr

для интерпретации полученного псевдокода нужно выполнить команды

(Интерпретатор `pint` считывает псевдокод из файла с именем `prd`)

```
mv prr prd
./pint
```

hello2.pas

```bash
program hello(output);

begin
   writeln('Hello, world', 7 // 3, 7 % 3)
end.
```

```bash
cp pcom.pas pcom2.pas
vi pcom2.pas # change 5348 div to //, mod to %
# create prr. prr is assembly of pcom2.pass
./pcom <pcom2.pas
mv prr prd
# run prd with hello.pas for stdin = compile hello2.pass with new compiler
./pint <hello2.pas
```
