# Lab 2 - Simple LLVM IR generator

This small program prints LLVM IR for the function:

```
int main() {
    return 353 + 48;
}
```

Build:

```sh
make -C lab2
```

Run:

```sh
./lab2/simple_compiler
```

The program uses the LLVM C++ API to build a module with the `main` function,
then prints the generated LLVM IR to stdout.
