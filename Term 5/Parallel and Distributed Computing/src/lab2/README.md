# Distributed computing and concurrency course

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

### Resources

- [Medium tutorial with ssh folders](https://medium.com/@ayshenesirli5/installing-open-mpi-for-ubuntu-31328b01f20b)
