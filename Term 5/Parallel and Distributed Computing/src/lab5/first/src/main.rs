use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use std::sync::{
    Arc, Barrier,
    atomic::{AtomicU8, Ordering},
};
use std::thread;
use std::time::Instant;

const ROWS: usize = 4096;
const COLS: usize = 4096;
const STEPS: usize = 1; // количество шагов эволюции
const THREADS: usize = 16;
const SEED: u64 = 1; // сид для генератора случайных чисел

#[inline(always)]
fn evolve(alive: u8, n: u32) -> u8 {
    if alive == 1 {
        if n < 2 {
            0
        } else if n == 2 || n == 3 {
            1
        } else {
            0
        }
    } else {
        if n == 3 { 1 } else { 0 }
    }
}

struct Inboxes {
    top: Vec<AtomicU8>,    // сосед сверху пишет сюда
    bottom: Vec<AtomicU8>, // сосед снизу пишет сюда
}

fn make_inboxes() -> Inboxes {
    // создаем буферы для верхней и нижней граничных строк потока
    Inboxes {
        top: (0..COLS).map(|_| AtomicU8::new(0)).collect(),
        bottom: (0..COLS).map(|_| AtomicU8::new(0)).collect(),
    }
}

fn main() {
    let threads_n = THREADS.min(ROWS).max(1); // проверяем что потоков не больше строк

    // Сколько строк на поток
    let base = ROWS / threads_n;
    // Сколько строк остаётся (прибавим к последнему потоку)
    let rem = ROWS % threads_n;

    let barrier = Arc::new(Barrier::new(threads_n));

    // Для каждого потока создаем буферы для обмена граничными (по вертикали) строками
    let inboxes: Vec<Arc<Inboxes>> = (0..threads_n).map(|_| Arc::new(make_inboxes())).collect();

    let start = Instant::now();

    let mut thread_handles = Vec::with_capacity(threads_n);

    for tid in 0..threads_n {
        // строки для текущего потока (для последнего потока + остаток)
        let my_rows = if tid == threads_n - 1 {
            base + rem
        } else {
            base
        };

        // номера потоков-соседей (замыкаем по кругу)
        let up = (tid + threads_n - 1) % threads_n;
        let down = (tid + 1) % threads_n;

        // создаем ссылки на
        let b = barrier.clone();
        let me = inboxes[tid].clone();
        let up_in = inboxes[up].clone();
        let down_in = inboxes[down].clone();

        thread_handles.push(thread::spawn(move || -> u64 {
            // Старые строки матрицы
            let mut local = vec![0u8; my_rows * COLS];
            // Новые строки матрицы
            let mut next = vec![0u8; my_rows * COLS];

            // скармливаем сид + tid для получения разных значений на каждом потоке
            let mut rng =
                StdRng::seed_from_u64(SEED ^ (tid as u64).wrapping_mul(0x9E3779B97F4A7C15));
            // заполняем полосу случайными 0 и 1
            for x in &mut local {
                *x = if rng.random_bool(0.5) { 1 } else { 0 };
            }

            for _ in 0..STEPS {
                // ------ 1: обновляем границы
                // отправляем верхнюю и нижнюю строки соседям
                let last_off = (my_rows - 1) * COLS;
                for j in 0..COLS {
                    // верхняя строка -> up.bottom
                    up_in.bottom[j].store(local[j], Ordering::Release);
                    // нижняя строка -> down.top
                    down_in.top[j].store(local[last_off + j], Ordering::Release);
                }
                // Ждем пока все потоки отправят свои граничные строки
                b.wait();

                // ------ 2: вычисляем следующее состояние для всех строк этого потока
                for i in 0..my_rows {
                    // смещение для текущей строки
                    let row_off = i * COLS;
                    // флаги. Является ли верхняя/нижняя строка граничной?
                    let up_is_inbox = i == 0;
                    let dn_is_inbox = i + 1 == my_rows;

                    // проходим по всем столбцам
                    for j in 0..COLS {
                        let jl = if j == 0 { COLS - 1 } else { j - 1 };
                        let jr = if j + 1 == COLS { 0 } else { j + 1 };

                        let mut n: u32 = 0;

                        // верзняя часть
                        if up_is_inbox {
                            // берем атомики из буфера
                            n += me.top[jl].load(Ordering::Acquire) as u32;
                            n += me.top[j].load(Ordering::Acquire) as u32;
                            n += me.top[jr].load(Ordering::Acquire) as u32;
                        } else {
                            let up_off = (i - 1) * COLS;
                            n += local[up_off + jl] as u32;
                            n += local[up_off + j] as u32;
                            n += local[up_off + jr] as u32;
                        }

                        // лево и право
                        n += local[row_off + jl] as u32;
                        n += local[row_off + jr] as u32;

                        // низ
                        if dn_is_inbox {
                            // берем атомики из буфера
                            n += me.bottom[jl].load(Ordering::Acquire) as u32;
                            n += me.bottom[j].load(Ordering::Acquire) as u32;
                            n += me.bottom[jr].load(Ordering::Acquire) as u32;
                        } else {
                            let dn_off = (i + 1) * COLS;
                            n += local[dn_off + jl] as u32;
                            n += local[dn_off + j] as u32;
                            n += local[dn_off + jr] as u32;
                        }

                        // Вызываем эволюцию и записываем в next
                        let alive = local[row_off + j];
                        next[row_off + j] = evolve(alive, n);
                    }
                }
                // Ждем пока все потоки подсчитают новое состояние
                b.wait();

                // ------ 3: меняем старое и новое состояние местами
                std::mem::swap(&mut local, &mut next);
                // Ждем пока все потоки закончат обновление состояния
                b.wait();
            }

            // Вычисляем контрольную сумму по локальному куску
            local.iter().map(|&x| x as u64).sum()
        }));
    }

    // Собираем контрольные суммы от всех потоков
    let mut checksum = 0u64;
    for h in thread_handles {
        checksum = checksum.wrapping_add(h.join().unwrap());
    }

    println!("{} ms (checksum={})", start.elapsed().as_millis(), checksum);
}
