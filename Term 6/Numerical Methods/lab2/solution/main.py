import math
from tabulate import tabulate


def progonka(a, b, c, d):
    # a - нижняя диагональ (n-1 элементов)
    # b - главная диагональ (n элементов)
    # c - верхняя диагональ (n-1 элементов)
    # d - правая часть (n элементов)

    n = len(b)  # берем n как длину главной диагонали

    # Проверяем размеры входных данных
    if len(d) != n or len(a) != n - 1 or len(c) != n - 1:
        raise ValueError("Размеры: b,d длины n; a,c длины n-1")

    # Обрабатываем тривиальные случаи
    if n == 0:
        return []
    if n == 1:
        if b[0] == 0:
            raise ZeroDivisionError("b1 = 0")
        return [d[0] / b[0]]

    # Инициализируем массивы для коэффициентов прямого хода
    k = [0.0] * (n - 1)
    m = [0.0] * (n - 1)

    # Прямой ход. Cчитаем k_i, m_i из x_i = k_i * x_{i+1} + m_i
    # Сначала находим k_1, m_1 из первого уравнения
    denom = b[0]
    if denom == 0:
        raise ZeroDivisionError("b1 = 0")
    k[0] = -c[0] / denom
    m[0] = d[0] / denom

    # Считаем коэффициенты для уравнений 2..n-1
    for i in range(1, n - 1):
        denom = a[i - 1] * k[i - 1] + b[i]
        if denom == 0:
            raise ZeroDivisionError(f"Знаменатель = 0 в строке {i+1}")
        k[i] = -c[i] / denom
        m[i] = (d[i] - a[i - 1] * m[i - 1]) / denom

    # Находим x_n из последнего уравнения
    denom = a[n - 2] * k[n - 2] + b[n - 1]
    if denom == 0:
        raise ZeroDivisionError("Знаменатель = 0 в последней строке")
    x = [0.0] * n
    x[n - 1] = (d[n - 1] - a[n - 2] * m[n - 2]) / denom

    # Обратный ход: восстанавливаем x от n-1 до 1
    for i in range(n - 2, -1, -1):
        x[i] = k[i] * x[i + 1] + m[i]

    return x


# Дано:
# общий вид: y'' + p(x)y' + q(x)y = f(x)
# y(a) = A; y(b) = B

# Конкретная задача:
# Вариант 22
# p = -1, q = 0, f(x) = 3, y(0) = 6, y'(0) = 2

a = 0.0
b = 1.0

A = 6.0
B = 5.0 * math.e - 2.0

intervals_count = 10          # n = 10 промежутков
points_count = intervals_count + 1  # число узлов


def p(x):
    return -1.0


def q(x):
    return 0.0


def f(x):
    return 3.0


def y_exact(x):
    return 1.0 + 5.0 * math.exp(x) - 3.0 * x


def shooting_method(p, q, f, a, b, A, B, points_count, D0=None, D1=None):
    # x - массив узлов сетки
    x = [a + i * (b - a) / (points_count - 1) for i in range(points_count)]
    # h - шаг сетки
    h = x[1] - x[0]

    # D0, D1 - стартовые сеточные значения
    # y0[0] = A, y0[1] = D0
    # y1[0] = 0, y1[1] = D1
    if D0 is None:
        D0 = A
    if D1 is None:
        D1 = h

    y0 = [0.0] * points_count
    y1 = [0.0] * points_count

    # y0 - решение неоднородного уравнения
    y0[0] = A
    y0[1] = D0

    # y1 - решение однородного уравнения
    y1[0] = 0.0
    y1[1] = D1

    for i in range(1, points_count - 1):
        xi = x[i]
        pi = p(xi)
        qi = q(xi)
        fi = f(xi)

        denom = 1.0 + pi * h / 2.0

        y0[i + 1] = (
            fi * h * h + (2.0 - qi * h * h) * y0[i] - (1.0 - pi * h / 2.0) * y0[i - 1]
        ) / denom

        y1[i + 1] = (
            (2.0 - qi * h * h) * y1[i] - (1.0 - pi * h / 2.0) * y1[i - 1]
        ) / denom

    # Проверка деления на ноль
    if abs(y1[-1]) < 1e-14:
        raise ZeroDivisionError("y1(b) = 0, невозможно найти константу C")

    C = (B - y0[-1]) / y1[-1]
    y_approx = [y0[i] + C * y1[i] for i in range(points_count)]

    return x, y_approx, C, h


def progonka_method(p, q, f, a, b, A, B, points_count):
    # x - массив узлов сетки
    x = [a + i * (b - a) / (points_count - 1) for i in range(points_count)]
    # h - шаг сетки
    h = x[1] - x[0]

    lower = []
    main = []
    upper = []
    rhs = []

    for i in range(1, points_count - 1):
        xi = x[i]
        pi = p(xi)
        qi = q(xi)
        fi = f(xi)

        # Коэффициенты для уравнения i-го узла: ai*yi-1 + bi*yi + ci*yi+1 = di
        ai = 1.0 - pi * h / 2.0
        bi = h * h * qi - 2.0
        ci = 1.0 + pi * h / 2.0
        di = h * h * fi

        # Граничные условия
        if i == 1:
            di -= ai * A
        if i == points_count - 2:
            di -= ci * B

        # Заполняем массивы для прогонки
        if i > 1:
            lower.append(ai)
        main.append(bi)
        if i < points_count - 2:
            upper.append(ci)
        rhs.append(di)

    y_inner = progonka(lower, main, upper, rhs)
    y = [A] + y_inner + [B]

    return x, y, h


def main():
    x, y_shoot, C, h = shooting_method(p, q, f, a, b, A, B, points_count)
    _, y_prog, _ = progonka_method(p, q, f, a, b, A, B, points_count)

    print(f"Количество узлов: {points_count}")
    print(f"Количество промежутков: {intervals_count}")
    print(f"Шаг h = {h:.6f}")
    print(f"Константа C = {C:.10f}")
    print()

    table = []
    for i in range(points_count):
        exact = y_exact(x[i])
        prog = y_prog[i]
        shoot = y_shoot[i]

        err_prog = abs(exact - prog)
        err_shoot = abs(exact - shoot)

        table.append(
            [
                i,
                f"{x[i]:.6f}",
                f"{exact:.10f}",
                f"{prog:.10f}",
                f"{err_prog:.10e}",
                f"{shoot:.10f}",
                f"{err_shoot:.10e}",
            ]
        )

    print(
        tabulate(
            table,
            headers=[
                "i",
                "x",
                "Точное значение",
                "Прогонка",
                "Погрешность прогонки",
                "Стрельба",
                "Погрешность стрельбы",
            ],
            tablefmt="grid",
        )
    )


if __name__ == "__main__":
    main()