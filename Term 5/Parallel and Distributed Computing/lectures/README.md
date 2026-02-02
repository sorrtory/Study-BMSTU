# Distributed computing and concurrency course

## Lab 1

Parallelization of the algorithm for computing the product of two matrices.

### Rust concurrency items

- Channels - mpsc - Multi-producer, single-consumer FIFO queue communication primitives
- Threads
- Mutexes + RwLocks
- Condvars - conditional variables for signaling between threads
- Atomics - atomic types for lock-free programming
- Arc - Atomic Reference Counting (shared_ptr + async)
- Barriers - in thread waitgroups
- Thread Local Storage - thread_local! - duplicate data for each thread

## Lab 2

Parallel implementation of solving a system of linear algebraic equations using MPI

### Installing OpenMPI

On Ubuntu-based systems, you can install OpenMPI using the following command:

```bash
# Usually pre-installed build tools
sudo apt install gcc g++ build-essential

# Install clang (because rust llvm)
# https://github.com/rsmpi/rsmpi/issues/1
sudo apt install clang libclang-dev


# ~168MB
sudo apt install openmpi-bin libopenmpi-dev # openmpi-doc
```

### Running

```bash
# C check
# Compile with mpicc
mpicc hello.c -o hello
# Run with mpirun
mpirun -np 4 ./hello

# Install mpi crate
cargo add mpi

# Build and run
cargo build --release
mpirun -np 2 target/release/lab2
```

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

## Lab4

```bash
cargo run
```

## Lab5

```bash
cargo run
```

### Resources

- [Medium tutorial with ssh folders](https://medium.com/@ayshenesirli5/installing-open-mpi-for-ubuntu-31328b01f20b)
