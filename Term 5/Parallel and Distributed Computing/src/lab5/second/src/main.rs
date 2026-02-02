use parking_lot::RwLock;
use rand::{rngs::ThreadRng, Rng};
use std::collections::{HashSet, LinkedList};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

const THREADS: usize = 16;
const COUNT: usize = 1_000_000;

fn contains(list: &LinkedList<i32>, v: i32) -> bool {
    list.iter().any(|&x| x == v)
}

fn worker(num_values: usize, list: Arc<RwLock<LinkedList<i32>>>) {
    let mut rng: ThreadRng = rand::thread_rng();

    for _ in 0..num_values {
        let v: i32 = rng.gen_range(0..=1000);

        // 1) Проверка под read-lock
        {
            let guard = list.read();
            if contains(&guard, v) {
                continue;
            }
        }

        // 2) Запись под write-lock + повторная проверка
        {
            let mut guard = list.write();
            if !contains(&guard, v) {
                guard.push_back(v);
            }
        }
    }
}

fn main() {
    let start_time = Instant::now();
    let list = Arc::new(RwLock::new(LinkedList::<i32>::new()));

    let mut thread_handles = Vec::with_capacity(THREADS);
    for _ in 0..THREADS {
        let l = Arc::clone(&list);
        thread_handles.push(thread::spawn(move || worker(COUNT, l)));
    }

    // Ждем пока все потоки завершатся
    for h in thread_handles {
        h.join().unwrap();
    }

    // Вывод результата
    let values: Vec<i32> = {
        let guard = list.read();
        guard.iter().copied().collect()
    };

    // print!("Result list: ");
    // for v in &values {
        // print!("{v} ");
    // }
    // println!();
    let elapsed = start_time.elapsed().as_millis();
    println!("Elapsed time: {} ms", elapsed);

    // Проверка на дубли
    let mut seen = HashSet::new();
    for &v in &values {
        if !seen.insert(v) {
            panic!("Duplicate value found: {v}");
        }
    }
    println!("No duplicates found. Total unique values: {}", seen.len());
}
