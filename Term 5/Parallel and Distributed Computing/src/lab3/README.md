# Distributed computing and concurrency course

## Lab3

### Installing OpenMP

GCC supports OpenMP out of the box.
For Clang, you may need to install additional packages.

Install OpenMP headers first

```bash
sudo apt-get install libomp-dev
```

### Running

```bash
# Compile with OpenMP support
gcc -fopenmp -o hello.out hello.c
./hello.out

# lab3
g++ -fopenmp lab3.cpp -o lab3.out
OMP_NUM_THREADS=8 ./lab3.out
```
