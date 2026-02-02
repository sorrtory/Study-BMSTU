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
