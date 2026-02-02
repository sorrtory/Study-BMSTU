use rand::Rng;
use std::{
    fmt,
    sync::{
        Arc, Condvar, Mutex,
        atomic::{AtomicBool, Ordering},
        mpsc,
    },
    thread,
    time::{Duration, Instant},
};

const N: usize = 5; // Число философов
const SECONDS: u64 = 1; // Время симуляции

#[derive(Clone, Copy, Debug)]
enum State {
    Thinking,
    TakingLeft,
    TakingRight,
    Eating,
    PuttingDown,
}

impl fmt::Display for State {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            State::Thinking => "THINK",
            State::TakingLeft => "TAKE_L",
            State::TakingRight => "TAKE_R",
            State::Eating => "EAT",
            State::PuttingDown => "PUT",
        };
        write!(f, "{s}")
    }
}

struct Waiter {
    permits: Mutex<usize>,
    cv: Condvar,
}

impl Waiter {
    fn new(initial: usize) -> Self {
        Self {
            permits: Mutex::new(initial),
            cv: Condvar::new(),
        }
    }

    /// Возвращает false, если надо завершаться.
    fn acquire(&self, running: &AtomicBool) -> bool {
        // Блокируем мьютекс
        let mut p = self.permits.lock().unwrap();
        while *p == 0 {
            // Проверяем общий флаг завершения
            if !running.load(Ordering::Relaxed) {
                return false;
            }
            // Ждем свободной вилки (с таймаутом)
            let (pp, _) = self.cv.wait_timeout(p, Duration::from_millis(50)).unwrap();
            p = pp;
        }
        // Выдаем одну вилку
        *p -= 1;
        true
    }

    fn release(&self) {
        let mut p = self.permits.lock().unwrap();
        // Освобождаем вилку
        *p += 1;
        // Уведомляем что вилка освобождена
        self.cv.notify_one();
    }
}

// Событие для логгера
#[derive(Debug)]
struct Event {
    t_ms: u128,
    id: usize,
    state: State,
}

fn main() {
    assert!(N >= 2, "N должно быть >= 2");

    // Запоминаем стартовое время
    let start_time = Instant::now();

    // Общий флаг работы
    let running = Arc::new(AtomicBool::new(true));

    // Создаем вилки
    let forks: Arc<Vec<Mutex<()>>> = Arc::new((0..N).map(|_| Mutex::new(())).collect());

    // ОСоздаем официанта, разрешаем максимум N - 1 философов одновременно
    let waiter = Arc::new(Waiter::new(N));

    // Создаем канал для логов
    let (tx, rx) = mpsc::channel::<Event>();

    // Создаем логгер как отдельный поток
    let logger_n = N;
    let logger = thread::spawn(move || {
        let mut states = vec![State::Thinking; logger_n];

        print!("t(ms) | ");
        for i in 0..logger_n {
            print!("P{i:02} ");
        }
        println!();
        println!("{}", "-".repeat(7 + 1 + logger_n * 7)); // под ширину "TAKE_L "

        while let Ok(ev) = rx.recv() {
            states[ev.id] = ev.state;
            print!("{:>5} | ", ev.t_ms);
            for i in 0..logger_n {
                print!("{:>6} ", states[i]);
            }
            println!();
        }
    });

    // Запускаем философов
    let mut thread_handles = Vec::with_capacity(N);
    for id in 0..N {
        // Клонируем ссылки для потоков
        let forks = Arc::clone(&forks);
        let waiter = Arc::clone(&waiter);
        let running = Arc::clone(&running);
        let tx = tx.clone();
        let start = start_time;

        let thread_handle = thread::spawn(move || {
            let mut rng = rand::thread_rng();
            let left = id;
            let right = (id + 1) % N;

            // Последний философ берёт сначала правую, потом левую.
            let reverse = id == N - 1;

            // Функция отправки состояния в логгер
            let send_state = |state: State, tx: &mpsc::Sender<Event>| {
                let _ = tx.send(Event {
                    t_ms: start.elapsed().as_millis(),
                    id,
                    state,
                });
            };

            while running.load(Ordering::Relaxed) {
                // THINK
                send_state(State::Thinking, &tx);
                thread::sleep(Duration::from_millis(rng.gen_range(80..250)));

                // Завершаемся, если официант не дал разрешение
                if !waiter.acquire(&running) {
                    break;
                }

                // Определяем взятия вилок (для последнего философа в обратном порядке)
                let (first_idx, second_idx, first_state, second_state) = if !reverse {
                    (left, right, State::TakingLeft, State::TakingRight)
                } else {
                    (right, left, State::TakingRight, State::TakingLeft)
                };

                // Берем первую вилку
                // Запускаем цикл с попытками взять вилку
                send_state(first_state, &tx);
                let first_guard = loop {
                    // Если общее завершение, то отпускаем официанта и выходим
                    if !running.load(Ordering::Relaxed) {
                        waiter.release();
                        return;
                    }
                    // Пытаемся взять вилку
                    if let Ok(g) = forks[first_idx].try_lock() {
                        break g;
                    }
                    // Пауза перед повторной попыткой
                    thread::sleep(Duration::from_millis(5));
                };
                // Делаем паузу между действиями
                thread::sleep(Duration::from_millis(rng.gen_range(10..40)));

                // Берем вторую вилку
                send_state(second_state, &tx);
                let second_guard = loop {
                    if !running.load(Ordering::Relaxed) {
                        // Освобождаем первую вилку и завершаемся
                        drop(first_guard);
                        waiter.release();
                        return;
                    }
                    if let Ok(g) = forks[second_idx].try_lock() {
                        break g;
                    }
                    thread::sleep(Duration::from_millis(5));
                };
                thread::sleep(Duration::from_millis(rng.gen_range(10..40)));

                // EAT
                send_state(State::Eating, &tx);
                thread::sleep(Duration::from_millis(rng.gen_range(80..220)));

                // PUT
                send_state(State::PuttingDown, &tx);
                drop(second_guard);
                drop(first_guard);
                waiter.release();

                thread::sleep(Duration::from_millis(rng.gen_range(10..40)));
            }
        });

        thread_handles.push(thread_handle);
    }

    // Считаем время
    thread::sleep(Duration::from_secs(SECONDS));

    // Завершаем работу философов
    running.store(false, Ordering::Relaxed);

    // Закрываем канал логгера
    drop(tx);

    // Ждем завершения всех потоков
    for h in thread_handles {
        let _ = h.join();
    }

    // Ждем завершения логгера
    let _ = logger.join();

    println!("Simulation finished cleanly");
}
