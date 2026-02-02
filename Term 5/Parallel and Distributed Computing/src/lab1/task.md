# Distributed computations and concurrency. Lab 1

Matrix multiplication

## Task

Lab 1 focuses on parallelizing the algorithm for multiplying two square matrices. The steps are:

1. Multiply two square matrices **A** and **B** of size _n_ using the standard algorithm:
   - Compute each element of matrix **C** as:  
     $c_{ij} = \sum_{k=1}^{n} a_{ik} \cdot b_{kj}$
2. Measure the computation time for the standard algorithm.
3. Compare the time when computing elements of matrix C by columns instead of rows.
4. Choose matrix sizes so that computation time is reasonable (not too short or too long).
5. Do not use library functions for matrix multiplication.
6. Divide the resulting matrix C into approximately equal rectangular submatrices.
7. Parallelize the program so that each thread computes its own submatrix.
   - Divide matrices A and B into groups of rows and columns for this purpose.
8. Test with different numbers of threads and measure computation time for each case.
9. Compare the results with the standard algorithm to verify correctness.
10. Pay attention to thread synchronization: the main thread should wait for all worker threads to finish.
11. If possible, evaluate the impact of process/thread priorities on computation time.
12. After presenting the program, prepare a report including:
    - Program listing
    - Device specifications
    - Computation times for both standard and parallel algorithms (as numbers and as a graph: x-axis = number of threads, y-axis = computation time)
    - If priority management is possible, compare computation times for different priorities.

## Notes
- Use Rust's standard library for threading. But rather than using `std::thread::spawn`, use a thread pool library like `rayon` or `threadpool` to manage threads more efficiently. MB `tokio`