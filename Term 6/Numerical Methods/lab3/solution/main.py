import math
from tabulate import tabulate

# верная и точная цифра посмотреть

# Параметры
a, b = 0.5, 2 * math.e
eps = 1e-3
print("eps =", eps)

def f(x):
    return math.log(2 * x)

print("Функция: f(x) = ln(2x)")

# Аналитическое значение интеграла
exact_integral = 2 * math.e * math.log(4) + 0.5
print(f"Точное значение интеграла: {exact_integral:.10f}")

def rectangle(a, b, n):
    h = (b - a) / n
    s = 0.0
    for i in range(n):
        s += f(a + (i + 0.5) * h)
    return h * s

def trapec(a, b, n):
    h = (b - a) / n
    s = (f(a) + f(b)) / 2.0
    for i in range(1, n):
        s += f(a + i * h)
    return h * s

def simpson(a, b, n):
    if n % 2 == 1:
        raise ValueError("n должно быть чётным")
    h = (b - a) / n
    s = f(a) + f(b)
    # Сумма для нечётных i
    for i in range(1, n, 2):
        s += 4.0 * f(a + i * h)
    # Для чётных i
    for i in range(2, n, 2):
        s += 2.0 * f(a + i * h)
    return (h / 3.0) * s

def richardson(method, k, a, b, eps, max_iter=100):
    n = 2
    prev_I = None
    for iteration in range(max_iter):
        I_n = method(a, b, n)
        I_2n = method(a, b, 2 * n)

        # Уточнение по Ричардсону
        R = (I_2n - I_n) / (2**k - 1)
        I_rich = I_2n + R

        # Проверка точности: сравниваем с предыдущей итерацией
        if prev_I is not None and abs(I_rich - prev_I) < eps:
            return n * 2, I_2n, R, I_rich

        prev_I = I_rich
        n *= 2

    raise RuntimeError(f"Не удалось достичь точности {eps} за {max_iter} итераций")

# Собираем результаты
results = []
try:
    results.append(["Прямоугольники", *richardson(rectangle, 2, a, b, eps)])
    results.append(["Трапеции", *richardson(trapec, 2, a, b, eps)])
    results.append(["Симпсон", *richardson(simpson, 4, a, b, eps)])
except Exception as e:
    print(f"Ошибка при вычислении: {e}")

# Добавляем точное значение в каждую строку результатов
for row in results:
    I_rich = row[4]  # I* + R
    error = abs(I_rich - exact_integral)
    row.extend([exact_integral, error])

# Выводим таблицу
if results:
    print("\nРезультаты численного интегрирования:")
    print(
        tabulate(
            results,
            headers=["Метод", "n", "I*", "R", "I* + R", "Точное", "Погрешность"],
            tablefmt="github",
            floatfmt=("", ".0f", ".10f", ".10f", ".10f", ".10f", ".10f"),
        )
    )
