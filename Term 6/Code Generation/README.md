# Генерация оптимального кода

<img align=right src="https://llvm.org/img/LLVMWyvernSmall.png" height="100px" width="100px">

Лабораторные работы по внутренним представлениям и оптимизациям в GCC и LLVM.

- [Lab 1](./lab1/) - GCC-плагин для вывода GIMPLE IR.
- [Lab 2](./lab2/) - генерация LLVM IR.
- [Lab 3](./lab3/) - компилятор простого языка в LLVM IR.
- [Lab 4](./lab4/) - построение CFG и SSA-формы.

## [Lab 1](./lab1/)

### Материалы

- [GCC Internals](./materials/lectures/02.GCC_internals.v1.pdf)
- [GCC Plugin API](./materials/gcc-plugins.pdf)

```bash
gcc --version
sudo apt install gcc-15-plugin-dev
gcc -print-file-name=plugin
```

### Info

```
.c/.cpp код
  ↓
парсинг
  ↓
внутреннее дерево GCC: GENERIC / GIMPLE
  ↓
SSA-форма
  ↓
оптимизации на GIMPLE
  ↓
RTL
  ↓
машинный код / объектный файл
```

- GIMPLE — упрощённое внутреннее представление программы в GCC.
  Например, сложные выражения разбиваются на простые инструкции.

- SSA — Static Single Assignment. Это форма, где каждая “версия” переменной присваивается один раз. Например, вместо одной переменной x внутри компилятора могут появиться x_1, x_2, x_3.

- Pass — проход компилятора. Это стадия, которая что-то делает с программой: строит SSA, оптимизирует, удаляет мёртвый код, анализирует функции и т.д.

```bash
gcc -O0 -fdump-tree-ssa -c test/main.c
gcc -O0 -fdump-tree-gimple -c test/main.c
```

## [Lab 2](./lab2/)

```bash
sudo apt install llvm-dev libclang-dev clang
```

## [Lab 3](./lab3/)

```bash
make -C lab3 run
```

```
прочитать текст
-> разбить на токены
-> разобрать в AST
-> сгенерировать LLVM IR
-> напечатать LLVM IR
```

honarable mention: 
- [ANTLR](https://github.com/antlr/antlr4)

## [Lab 4](./lab4/)

```bash
make -C lab4 run
```

## Additional tools

```
CMake = builds your project and manages linking
Bear  = helps tools understand an existing build

sudo apt install libzstd-dev 
```
