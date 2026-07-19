# Hello World GCC Plugin

Первый пример из методички: GCC загружает shared library как плагин и
вызывает `plugin_init`. Никакого IR здесь еще нет, это проверка, что среда
сборки и `-fplugin` работают.

```sh
make test
```

Ожидаемый смысл вывода:

```text
Hello, GCC plugin!
Hello from compiled C program
```
