# GIMPLE IR Dump

Решение первой лабораторной: GCC-плагин регистрирует свой `GIMPLE_PASS`
после построения SSA и вручную печатает части GIMPLE/IR через `printf`.

Плагин выводит:

- базовые блоки;
- блоки-предшественники и блоки-последователи;
- PHI-функции;
- `GIMPLE_ASSIGN`, `GIMPLE_COND`, `GIMPLE_CALL`, `GIMPLE_RETURN`;
- арифметические и логические операции;
- обращения к памяти: `ARRAY_REF`, `MEM_REF`, `COMPONENT_REF`, `ADDR_EXPR`.

Запуск:

```sh
make test
```

Очистка сгенерированных файлов:

```sh
make clean
```
