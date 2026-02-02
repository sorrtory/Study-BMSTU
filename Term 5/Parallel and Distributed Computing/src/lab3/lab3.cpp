#include <cmath>
#include <iostream>
#include <vector>
#include <limits>
#include <omp.h>
#include <random>

constexpr int N = 10000;             // размерность матрицы
constexpr double EPS = 1e-4;         // критерий остановки
constexpr double TAU = 0.1 / N;      // шаг итерации
constexpr int MAX_ITERS = 2'000'000; // максимум итераций

// 0 = не печатать, >0 = печатать каждые PRINT_EVERY итераций
constexpr int PRINT_EVERY = 0;
// ===================================================================

// разбиение строк [0..N) на p кусков, кусок tid: [row_start, row_end)
static inline void get_rows_range(int N, int p, int tid, int &row_start, int &row_end)
{
    int base = N / p;
    int extra = N % p;

    if (tid < extra)
    {
        row_start = tid * (base + 1);
        row_end = row_start + (base + 1);
    }
    else
    {
        row_start = extra * (base + 1) + (tid - extra) * base;
        row_end = row_start + base;
    }
}

int main()
{
    std::cout << "OpenMP threads = " << omp_get_max_threads() << "\n";

    // x_true = 1 (решение системы)
    std::vector<double> x_true(N, 1.0);

    // Матрица A (NxN) в 1D (row-major): A[i*N + j]
    std::vector<double> A;
    try
    {
        // Пытаемся выделить память под A
        A.assign(static_cast<size_t>(N) * static_cast<size_t>(N), 0.0);
    }
    catch (const std::bad_alloc &)
    {
        std::cerr << "Not enough RAM to allocate A (" << N << "x" << N << ").\n";
        return 1;
    }

// Заполняем A параллельно
// по диагонали 2, вне диагонали 1
#pragma omp parallel
    {
        int tid = omp_get_thread_num();   // номер текущего потока
        int nthr = omp_get_num_threads(); // всего потоков
        int rs = 0, re = 0;
        get_rows_range(N, nthr, tid, rs, re); // получаем диапазон строк для этого потока

        // Заполняем строки с rs до re
        for (int i = rs; i < re; ++i)
        {
            size_t row_off = static_cast<size_t>(i) * static_cast<size_t>(N);
            for (int j = 0; j < N; ++j)
            {
                A[row_off + j] = (i == j ? 2.0 : 1.0);
            }
        }
    }

    // b = A * x_true
    std::vector<double> b(N, 0.0);

// Заполняем вектор b так, чтобы решение системы было x_true (все единицы)
#pragma omp parallel
    {
        int tid = omp_get_thread_num();
        int nthr = omp_get_num_threads();
        int rs = 0, re = 0;
        get_rows_range(N, nthr, tid, rs, re);

        for (int i = rs; i < re; ++i)
        {
            const size_t row_off = static_cast<size_t>(i) * static_cast<size_t>(N);
            double sum = 0.0;
            for (int j = 0; j < N; ++j)
            {
                sum += A[row_off + j] * x_true[j];
            }
            b[i] = sum;
        }
    }

    // norm_b = ||b||2
    double norm_b2 = 0.0;

// сворачивание суммы квадратов элементов b в norm_b2
// в кажом потоке своя локальная копия norm_b2, в конце они суммируются
// schedule(static) итерации делятся заранее и равномерно между потоками
#pragma omp parallel for reduction(+ : norm_b2) schedule(static)
    for (int i = 0; i < N; ++i)
        norm_b2 += b[i] * b[i];
    const double norm_b = std::sqrt(norm_b2);

    // Начальное приближение x_0 = random в [-1, 1]
    std::vector<double> x_n(N, 0.0);
    std::vector<double> x_np1(N, 0.0);

// Рандом в диапазоне [-1, 1]
#pragma omp parallel
    {
        int tid = omp_get_thread_num();
        // фиксированный сид
        std::mt19937 rng(12345u + static_cast<unsigned>(tid));
        std::uniform_real_distribution<double> dist(-1.0, 1.0);

#pragma omp for schedule(static)
        for (int i = 0; i < N; ++i)
        {
            x_n[i] = dist(rng);
        }
    }

    const double t0 = omp_get_wtime();

    int iters_done = 0;
    double last_ratio = std::numeric_limits<double>::infinity();

    for (int iter = 0; iter < MAX_ITERS; ++iter)
    {
        double global_r2 = 0.0;

// Параллельно по строкам: считаем Ax, r_i, и x_{n+1}[i]
#pragma omp parallel reduction(+ : global_r2)
        {
            int tid = omp_get_thread_num();
            int nthr = omp_get_num_threads();
            int rs = 0, re = 0;
            get_rows_range(N, nthr, tid, rs, re);

            double local_r2 = 0.0;

            for (int i = rs; i < re; ++i)
            {
                const size_t row_off = static_cast<size_t>(i) * static_cast<size_t>(N);

                // Вычисляем (Ax)_i
                double ax = 0.0;
                for (int j = 0; j < N; ++j)
                {
                    ax += A[row_off + j] * x_n[j];
                }

                // Вычисляем r_i = (Ax)_i - b_i
                const double r_i = ax - b[i];
                // Вычисляем локальное ||r||^2
                local_r2 += r_i * r_i;

                // Обновляем x_{n+1}
                x_np1[i] = x_n[i] - TAU * r_i;
            }
            // Суммируем локальные ||r||^2 в глобальный
            global_r2 += local_r2;
        }
        // конец параллельной области

        // Вычисляем g(x_n) = ||r||2 / ||b||2
        last_ratio = std::sqrt(global_r2) / norm_b;
        iters_done = iter + 1;

        // Переходим к следующей итерации
        x_n.swap(x_np1);

        // печатаем прогресс
        if constexpr (PRINT_EVERY > 0)
        {
            if (iters_done % PRINT_EVERY == 0)
            {
                std::cout << "iter " << iters_done << ", g(x_n)=" << last_ratio << "\n";
            }
        }

        if (last_ratio < EPS)
            break;
    }

    // получаем время окончания вычислений
    const double t1 = omp_get_wtime();

    // max_abs_error относительно x_true=1
    double max_err = 0.0;
// кадому потоку своя копия max_err, мы ее вычисляем параллельно,
// а после по ним считается общий max
#pragma omp parallel for reduction(max : max_err) schedule(static)
    for (int i = 0; i < N; ++i)
    {
        // считаем погрешность для i-го элемента
        const double e = std::abs(x_n[i] - 1.0);
        if (e > max_err)
            max_err = e;
    }

    std::cout << "N=" << N << " EPS=" << EPS << " TAU=" << TAU << " MAX_ITERS=" << MAX_ITERS << "\n";
    // !
    std::cout << "iters=" << iters_done << " g(x_n)=" << last_ratio << " time_sec=" << (t1 - t0) << "\n";
    std::cout << "x[0..3]=[" << x_n[0] << ", " << x_n[1] << ", " << x_n[2] << "]\n";
    std::cout << "max_abs_error=" << max_err << "\n";
    // выводить количество итераций за которое сошелся алгоритм
    // взять другое значение x_start

    return 0;
}
