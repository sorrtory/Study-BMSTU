use rand::random_range;

use std::hash::{DefaultHasher, Hash, Hasher};
use std::io::Write;
use std::sync::{
    Arc,
    atomic::{AtomicBool, Ordering},
    mpsc::channel,
};
use std::thread;
use std::time::{Duration, Instant};

const MAX_N: usize = 1000; // Max size of the matrix
type Elem = i32; // Type of the matrix elements

#[derive(Clone)]
struct Matrix {
    rows: usize,
    cols: usize,
    data: Vec<Elem>,
    data_hash: u64,
}

impl Hash for Matrix {
    fn hash<H: Hasher>(&self, state: &mut H) {
        for value in &self.data {
            value.hash(state);
        }
    }
}

impl Matrix {
    /// Initialize a new matrix with given dimensions
    fn new(rows: usize, cols: usize) -> Self {
        assert!(rows <= MAX_N && cols <= MAX_N);
        Matrix {
            rows,
            cols,
            data: vec![0; rows * cols],
            data_hash: 0,
        }
    }

    /// Fill the matrix with random values
    fn fill(&mut self) {
        for i in 0..self.rows {
            for j in 0..self.cols {
                self.data[i * self.cols + j] = random_range(0..100);
            }
        }
    }

    /// Set the value at position (i, j)
    fn set(&mut self, i: usize, j: usize, value: Elem) {
        assert!(i < self.rows && j < self.cols);
        self.data[i * self.cols + j] = value;
    }

    /// Get the value at position (i, j)
    fn get(&self, i: usize, j: usize) -> Elem {
        assert!(i < self.rows && j < self.cols);
        self.data[i * self.cols + j]
    }

    /// Calculate and return the hash of the matrix data
    fn compute_hash(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

    /// Check the hash of the matrix data against the stored hash
    /// If the stored hash is 0, initialize it with the current hash
    fn check_hash(&mut self) {
        print!("Hash check: ");
        let new_hash = self.compute_hash();
        if self.data_hash == 0 {
            println!("Init");
            self.data_hash = new_hash;
        } else if self.data_hash == new_hash {
            println!("Ok");
        } else {
            println!("BAD");
        }
    }
}

// MatrixMultiplier have to live at least as long as A and B
struct MatrixMultiplier {
    A: Matrix, // First matrix
    B: Matrix, // Second matrix
    C: Matrix, // Result matrix
}

impl MatrixMultiplier {
    fn new(A: Matrix, B: Matrix) -> Self {
        assert!(A.cols == B.rows);
        let C = Matrix::new(A.rows, B.cols);
        MatrixMultiplier { A, B, C }
    }

    /// Row major order multiplication
    fn multiply_standard(&mut self) {
        println!("Matrix {}x{} standard ...", self.A.rows, self.B.cols);
        Self::_with_timer(|| {
            for A_row in 0..self.A.rows {
                for B_col in 0..self.B.cols {
                    let mut sum = 0;
                    for k in 0..self.A.cols {
                        sum += self.A.get(A_row, k) * self.B.get(k, B_col);
                    }
                    self.C.set(A_row, B_col, sum);
                }
            }
        });
        self.C.check_hash();
    }

    /// Column major order multiplication
    fn multiply_cols(&mut self) {
        println!("Matrix {}x{} column-wise ...", self.A.rows, self.B.cols);

        Self::_with_timer(|| {
            for B_col in 0..self.B.cols {
                for A_row in 0..self.A.rows {
                    let mut sum = 0;
                    for k in 0..self.B.rows {
                        sum += self.A.get(A_row, k) * self.B.get(k, B_col);
                    }
                    self.C.set(A_row, B_col, sum);
                }
            }
        });
        self.C.check_hash();
    }

    /// Concurrent multiplication using num_threads threads
    /// Each thread computes a chunk of elements of the result matrix
    /// Resulting matrix size must be divisible by num_threads
    fn multiply_concurrent(&mut self, num_threads: usize) {
        // Implement concurrent multiplication
        // let (chunks, remainder) = self.C.data.as_chunks_mut::<3>();
        println!(
            "Matrix {}x{} concurrent with {} threads ...",
            self.A.rows, self.B.cols, num_threads
        );
        assert!(num_threads > 0);
        assert!(num_threads <= self.C.data.len()); // No more threads than elements
        assert!(self.C.data.len() % num_threads == 0); // For simplicity require divisibility
        // Then all elements are equally spread per each thread
        let chunk_size = self.C.data.len() / num_threads;

        // Channel to send computed cell values from threads to main thread
        struct CellValue {
            i: usize,
            j: usize,
            value: Elem,
        }
        let (tx, rx) = channel::<CellValue>();

        // Clone A and B into Arcs to share between threads
        let A: Arc<Matrix> = Arc::new(self.A.clone());
        let B: Arc<Matrix> = Arc::new(self.B.clone());
        let mut handles = vec![];

        Self::_with_timer(|| {
            for thread_id in 0..num_threads {
                let tx_clone = tx.clone();
                let A_clone = A.clone();
                let B_clone = B.clone();

                // Determine the chunk of elements this thread will compute
                let start_element = thread_id * chunk_size;
                let end_element = start_element + chunk_size;
                let handle = thread::spawn(move || {
                    for index in start_element..end_element {
                        // Convert linear index to 2D indices
                        // Note: this is probably not the most efficient way
                        let i = index / B_clone.cols;
                        let j = index % B_clone.cols;

                        let mut sum = 0;
                        // Compute the value for C[i][j]
                        for k in 0..A_clone.cols {
                            sum += A_clone.get(i, k) * B_clone.get(k, j);
                        }
                        tx_clone.send(CellValue { i, j, value: sum }).unwrap();
                    }
                });
                handles.push(handle);
            }

            drop(tx); // Close the sending side

            // Multiple producers, single consumer
            // But we can have multiple consumers with mutex or crates like crossbeam
            for cell in rx.iter() {
                self.C.set(cell.i, cell.j, cell.value);
            }

            for handle in handles {
                handle.join().unwrap();
            }
        });
        self.C.check_hash();
    }

    /// Wrap a function with a timer that prints elapsed time every 100ms
    fn _with_timer<F, R>(f: F) -> R
    where
        F: FnOnce() -> R,
    {
        let start = Instant::now();
        let running = Arc::new(AtomicBool::new(true));

        // Clone the running flag for the timer thread
        let running_clone = running.clone();
        // Spawn a timer thread
        let handle = thread::spawn(move || {
            while running_clone.load(Ordering::Relaxed) {
                let elapsed = start.elapsed().as_secs_f32();
                print!("\rElapsed: {:.2} sec", elapsed);
                std::io::stdout().flush().unwrap();
                thread::sleep(Duration::from_millis(100));
            }
        });

        // Run the actual function
        let result = f();

        // Tell the timer to stop
        running.store(false, Ordering::Relaxed);

        // Wait for timer thread to finish
        handle.join().unwrap();

        // Final time print
        println!("\rTook: {:.2} sec", start.elapsed().as_secs_f32());

        result
    }
}

fn main() {
    let mut A = Matrix::new(MAX_N, MAX_N);
    A.fill();
    let mut B = Matrix::new(MAX_N, MAX_N);
    B.fill();

    let mut multiplier = MatrixMultiplier::new(A, B);
    multiplier.multiply_standard();
    println!();
    multiplier.multiply_cols();
    println!();
    multiplier.multiply_concurrent(2);
    println!();
    multiplier.multiply_concurrent(4);
    println!();
    multiplier.multiply_concurrent(8);
    println!();
    multiplier.multiply_concurrent(100);
    println!();
}

/// Unit tests for MatrixMultiplier
/// Multiplication of two 3x3 matrices with known result
#[cfg(test)]
mod tests {
    use super::*;
    const a: [Elem; 9] = [1, 2, 3, 4, 5, 6, 7, 8, 9]; // Left matrix
    const b: [Elem; 9] = [9, 8, 7, 6, 5, 4, 3, 2, 1]; // Right matrix
    const c: [Elem; 9] = [30, 24, 18, 84, 69, 54, 138, 114, 90]; // Expected result

    #[test]
    fn test_matrix_multiplier_by_row() {
        _with_expected(|multiplier| {
            multiplier.multiply_standard();
        });
    }

    #[test]
    fn test_matrix_multiplier_by_col() {
        _with_expected(|multiplier| {
            multiplier.multiply_cols();
        });
    }

    #[test]
    fn test_matrix_multiplier_concurrent() {
        _with_expected(|multiplier| {
            multiplier.multiply_concurrent(3);
        });
    }

    /// Helper function to create a MatrixMultiplier with predefined matrices and check the result
    fn _with_expected<F>(f: F)
    where
        F: FnOnce(&mut MatrixMultiplier),
    {
        let mut A = Matrix::new(3, 3);
        A.data = a.to_vec();
        let mut B = Matrix::new(3, 3);
        B.data = b.to_vec();
        let mut multiplier = MatrixMultiplier::new(A, B);
        f(&mut multiplier);
        assert_eq!(multiplier.C.data, c.to_vec());
    }
}
