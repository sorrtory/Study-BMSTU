use mpi::Count;
use mpi::collective::SystemOperation;
use mpi::datatype::PartitionMut;
use mpi::traits::*;
use rand::prelude::*;
use std::time::Instant;

// забирает оперативки N*N*8 bytes
const N: usize = 16384;

// критерий остановки
const EPS: f64 = 1e-7;

// шаг в итерации
const TAU: f64 = 0.1 / N as f64;
// const TAU: f64 = -0.1 / N as f64;

// максимальное число итераций
const MAX_ITERS: usize = 2_000_000;

fn main() {
    // Инициализация MPI
    let universe = mpi::initialize().unwrap();
    let world = universe.world(); // коммуникатор всех процессов

    let rank = world.rank() as usize; // номер текущего процесса
    let p = world.size() as usize; // общее число процессов

    // Вычисляем, сколько строк у каждого процесса
    let base = N / p; // число строк на процесс
    let rem = N % p; // число процессов, получающих на 1 строку больше
    // 0..(rem-1) процессы получают по (base+1) строк
    // rem..(p) процессы получают по base строк

    // число строк, обрабатываемых текущим процессом
    let local_n = base + if rank < rem { 1 } else { 0 };
    // начальный номер строки для текущего процесса
    let start_row = rank * base + rank.min(rem);

    // counts/displs нужны для сборки b_full через all_gather_varcount_into
    let mut counts: Vec<Count> = vec![0; p]; // число элементов от каждого процесса
    let mut displs: Vec<Count> = vec![0; p]; // смещения для каждого процесса
    {
        let mut off: Count = 0;
        for r in 0..p {
            let cnt = (base + if r < rem { 1 } else { 0 }) as Count;
            counts[r] = cnt;
            displs[r] = off;
            off += cnt;
        }
    }

    // вектор из всех 1.0. он должен быть решением системы
    let x_true = vec![1.0_f64; N];

    // A_local — локальный блок строк матрицы A: local_n строк по N столбцов
    let mut a_local = vec![0.0_f64; local_n * N];

    // Заполняем A
    // Модельная задача с заданным решением: диагональные элементы = 2, остальные = 1
    for i_local in 0..local_n {
        let i_global = start_row + i_local;
        let row_offset = i_local * N;
        for j in 0..N {
            a_local[row_offset + j] = if i_global == j { 2.0 } else { 1.0 };
        }
    }

    // b_local = A_local * x_true
    // считаем локальный кусок вектора правой части
    let mut b_local = vec![0.0_f64; local_n];
    for i_local in 0..local_n {
        let row_offset = i_local * N;
        let mut sum = 0.0_f64;
        for j in 0..N {
            sum += a_local[row_offset + j] * x_true[j];
        }
        b_local[i_local] = sum;
    }

    // посчитаем полный вектор b
    // b дублируется во всех процессах: соберём b_full через Allgatherv
    let mut b_full = vec![0.0_f64; N];
    {
        // разбиваем b_full на части для каждого процесса
        let mut part_b = PartitionMut::new(&mut b_full[..], &counts[..], &displs[..]);
        // собираем полное b_full из локальных кусков b_local
        world.all_gather_varcount_into(&b_local[..], &mut part_b);
        // MPI_Allgatherv
    }

    // посчитаем ||b||_2
    let local_b2: f64 = b_local.iter().map(|v| v * v).sum();
    let mut global_b2 = 0.0_f64;
    world.all_reduce_into(&local_b2, &mut global_b2, SystemOperation::sum());
    let norm_b = global_b2.sqrt();

    // ------ Реализация итеративного метода

    // x хранится целиком в каждом процессе
    let mut x_n_full = vec![0.0_f64; N];
    let mut x_np1_full = vec![0.0_f64; N];
    let mut x_np1_local = vec![0.0_f64; local_n];

    // инициализируем rng
    let mut rng = StdRng::seed_from_u64(123456789); // фиксированный seed

    // инициализируем x0 как рандомные числа в диапазоне [-1, 1]
    for i in 0..N {
        x_n_full[i] = rng.gen_range(-1.0_f64..1.0_f64);
    }

    // Замер времени вычислений
    world.barrier();
    let t0 = Instant::now();

    let mut iters_done: usize = 0;
    let mut last_ratio: f64 = f64::INFINITY;

    // итерируемся, пока не привысим MAX_ITERS или не достигнем EPS
    for n_iter in 0..MAX_ITERS {
        let mut local_r2 = 0.0_f64;

        // вычисляем локальный кусок r и x_{n+1}
        for i_local in 0..local_n {
            // Ax_n для строки i_local:
            let row_offset = i_local * N;
            let mut ax = 0.0_f64;
            for j in 0..N {
                ax += a_local[row_offset + j] * x_n_full[j];
            }

            // r_i = (Ax_n)_i - b_i
            let i_global = start_row + i_local;
            let r_i = ax - b_full[i_global];

            local_r2 += r_i * r_i;

            // считаем x_{n+1} для этой строки
            let x_i_n = x_n_full[i_global];
            x_np1_local[i_local] = x_i_n - TAU * r_i;
        }

        let mut global_r2 = 0.0_f64;

        // собираем ||r||_2^2 по всем процессам как сумму локальных вкладов
        world.all_reduce_into(&local_r2, &mut global_r2, SystemOperation::sum());
        // MPI_Allreduce + MPI_SUM

        // вычисляем g(x_n) = ||r||_2 / ||b||_2
        last_ratio = global_r2.sqrt() / norm_b;
        iters_done = n_iter + 1;

        // собираем полный x_{n+1} во всех процессах из x_np1_local
        {
            let mut part_xnp1 = PartitionMut::new(&mut x_np1_full[..], &counts[..], &displs[..]);
            world.all_gather_varcount_into(&x_np1_local[..], &mut part_xnp1);
            // MPI_Allgatherv
        }

        // меняем указатели для следующей итерации
        std::mem::swap(&mut x_n_full, &mut x_np1_full);

        // проверяем условие остановки
        if last_ratio < EPS {
            break;
        }
    }

    // ждем завершения всех процессов
    world.barrier();
    // замеряем время
    let elapsed = t0.elapsed().as_secs_f64();

    // Вывод результатов
    if rank == 0 {
        println!("N={}, p={}, EPS={:.3e}, TAU={:.6e}", N, p, EPS, TAU);
        println!("iters={}, g(x_n)={:.6e}", iters_done, last_ratio);
        println!("time_sec={:.6}", elapsed);
        println!("Result x_n_full[0..3]: {:?}", &x_n_full[0..3]);
    }

    // выводим максимальную погрешность
    if rank == 0 {
        let mut max_err = 0.0_f64;
        for i in 0..N {
            let e = (x_n_full[i] - x_true[i]).abs();
            if e > max_err {
                max_err = e;
            }
        }
        println!("max_abs_error={:.6e}", max_err);
    }
    println!("Rank {} done.", rank);
}
