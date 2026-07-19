import math


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


def spline(a_left=0.0, b_right=1.0, n=10, f=math.exp):
    # табулирование: x_i = a + i*h, y_i = f(x_i)
    h = (b_right - a_left) / n
    x = [a_left + i * h for i in range(n + 1)]
    y = [f(xi) for xi in x]

    # СЛАУ для C1..C_{n-1}:
    # Ci-1 + 4Ci + Ci+1 = rhs_i, i=1..n-1
    # rhs_i = 3*(y[i-1] - 2*y[i] + y[i+1]) / h^2
    lower = [1.0] * (n - 2)
    main = [4.0] * (n - 1)
    upper = [1.0] * (n - 2)
    rhs = [3.0 * (y[i - 1] - 2.0 * y[i] + y[i + 1]) / (h * h) for i in range(1, n)]

    C_inner = progonka(lower, main, upper, rhs)  # C1..C_{n-1}
    C = [0.0] + C_inner + [0.0]  # C0=0, Cn=0

    # коэффициенты на отрезках [x[i-1], x[i]], i=1..n
    # S_i(x) = a_i + b_i t + c_i t^2 + d_i t^3, t = x - x_{i-1}
    # a_i=y[i-1]
    # b_i=(y[i]-y[i-1])/h - (h/3)*(2*C[i-1] + C[i])
    # c_i=C[i-1]
    # d_i=(C[i]-C[i-1])/(3h)
    a_i = [0.0] * n
    b_i = [0.0] * n
    c_i = [0.0] * n
    d_i = [0.0] * n
    for i in range(1, n + 1):
        a_i[i - 1] = y[i - 1]
        b_i[i - 1] = (y[i] - y[i - 1]) / h - (h / 3.0) * (2.0 * C[i - 1] + C[i])
        c_i[i - 1] = C[i - 1]
        d_i[i - 1] = (C[i] - C[i - 1]) / (3.0 * h)

    return x, y, h, a_i, b_i, c_i, d_i


def S(a_i, b_i, c_i, d_i, x_left, x_val):
    # t = x - x_{i-1}
    # S_i(x) = a_i + b_i*t + c_i*t^2 + d_i*t^3
    t = x_val - x_left
    return a_i + b_i * t + c_i * t * t + d_i * t * t * t


if __name__ == "__main__":
    # y=exp(x), x in [0,1], n=10
    x, y, h, a_i, b_i, c_i, d_i = spline(0.0, 1.0, 10, math.exp)

    # Ззначения y на концах
    # print("y0 =", y[0])  # 1
    # print("yN =", y[-1])  # 2.718...

    print("Дельта в узлах:")
    # delta в узлах: delta_i = |S_i(x_i) - y_i|
    delta_nodes = []

    for i in range(len(x)):  # pylint: disable=consider-using-enumerate
        if i == 0:
            s_val = S(a_i[0], b_i[0], c_i[0], d_i[0], x[0], x[0])
        else:
            s_val = S(a_i[i - 1], b_i[i - 1], c_i[i - 1], d_i[i - 1], x[i - 1], x[i])
        delta_nodes.append(abs(s_val - y[i]))

        delta = abs(s_val - y[i])
        print(
            f"x[{i}]={x[i]:.3f}, "
            f"y[{i}]={y[i]:.6f}, "
            f"S[{i}]={s_val:.6f}, "
            f"delta={delta:.6f}"
        )

    # delta между узлами: x_{i-0.5} = x_{i-1} + h/2
    # delta_{i-0.5} = |S_i(x_{i-0.5}) - y_{i-0.5}|
    # проверка 5%: delta_{i-0.5} <= 0.05 * |y_{i-0.5}|
    print("\nДельта в серединах отрезков:")

    delta_mids = []
    ok_5_percent = True
    for i in range(1, len(x)):  # i=1..n
        x_mid = x[i - 1] + h / 2.0
        y_mid = math.exp(x_mid)
        s_mid = S(a_i[i - 1], b_i[i - 1], c_i[i - 1], d_i[i - 1], x[i - 1], x_mid)

        delta = abs(s_mid - y_mid)
        delta_mids.append(delta)

        if delta > 0.05 * abs(y_mid):
            ok_5_percent = False

        print(
            f"x_mid={x_mid:.3f}, "
            f"y_mid={y_mid:.6f}, "
            f"S_mid={s_mid:.6f}, "
            f"delta={delta:.6f}"
        )

    print("\nМаксимальные дельта:")
    print("максимальная дельта в узлах =", max(delta_nodes))
    print("максимальная дельта в серединах =", max(delta_mids))
    print("дельта в серединах не превышает 5% =", ok_5_percent)
