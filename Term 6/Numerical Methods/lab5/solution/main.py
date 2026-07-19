from math import sqrt, log, exp
from tabulate import tabulate


# Исходные данные

x = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
y = [1.24, 1.74, 1.61, 2.16, 3.06, 2.88, 4.53, 5.40, 7.07]


# Линейная интерполяция


def linear_interpolate(xs, ys, x_star):
    if x_star <= xs[0]:
        return ys[0]
    if x_star >= xs[-1]:
        return ys[-1]

    for i in range(len(xs) - 1):
        if xs[i] <= x_star <= xs[i + 1]:
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[i], ys[i + 1]
            return y0 + (y1 - y0) * (x_star - x0) / (x1 - x0)

    raise ValueError("Точка не попала в интервал интерполяции.")


# Специальные средние

x_a = (x[0] + x[-1]) / 2
x_g = sqrt(x[0] * x[-1])
x_h = 2 / (1 / x[0] + 1 / x[-1])

y_a = (y[0] + y[-1]) / 2
y_g = sqrt(y[0] * y[-1])
y_h = 2 / (1 / y[0] + 1 / y[-1])

z_xa = linear_interpolate(x, y, x_a)
z_xg = linear_interpolate(x, y, x_g)
z_xh = linear_interpolate(x, y, x_h)


# Дельты

deltas = [
    abs(z_xa - y_a),
    abs(z_xg - y_g),
    abs(z_xa - y_g),
    abs(z_xg - y_a),
    abs(z_xh - y_a),
    abs(z_xa - y_h),
    abs(z_xh - y_h),
    abs(z_xh - y_g),
    abs(z_xg - y_h),
]

best_delta_index = deltas.index(min(deltas)) + 1
# Выбрана модель z3(x) = alpha * exp(beta * x)

# Линеаризация:
# ln(y) = beta * x + ln(alpha)

# Обозначим:
# X = x
# Y = ln(y)

# Тогда Y = A*X + B
# где A = beta, B = ln(alpha)

X = x[:]
Y = [log(yi) for yi in y]

n = len(X)
Sx = sum(X)
Sy = sum(Y)
Sxx = sum(xi * xi for xi in X)
Sxy = sum(xi * yi for xi, yi in zip(X, Y))

A = (n * Sxy - Sx * Sy) / (n * Sxx - Sx * Sx)
B = (Sy - A * Sx) / n

# Делинеаризация
beta = A
alpha = exp(B)


# Аппроксимирующая функция

def model_z3(x_value, alpha_value, beta_value):
    return alpha_value * exp(beta_value * x_value)


# Таблица результатов

table_rows = []
sum_sq = 0.0

for i, (xi, yi) in enumerate(zip(x, y), start=1):
    fi = model_z3(xi, alpha, beta)
    err = fi - yi
    abs_err = abs(err)
    # rel_err = abs_err / abs(yi) * 100
    sq_err = err**2
    sum_sq += sq_err

    # table_rows.append([i, xi, yi, fi, err, abs_err, rel_err, sq_err])
    table_rows.append([i, xi, yi, fi, err, abs_err, sq_err])

Delta = sqrt(sum_sq / n)


# Вывод

print("Средние:")
print(f"x_a = {x_a:.6f}")
print(f"x_g = {x_g:.6f}")
print(f"x_h = {x_h:.6f}")
print(f"y_a = {y_a:.6f}")
print(f"y_g = {y_g:.6f}")
print(f"y_h = {y_h:.6f}")
print()

print("Значения по графику (линейная интерполяция):")
print(f"z(x_a) = {z_xa:.6f}")
print(f"z(x_g) = {z_xg:.6f}")
print(f"z(x_h) = {z_xh:.6f}")
print()

print("Дельты:")
for i, d in enumerate(deltas, start=1):
    print(f"delta_{i} = {d:.6f}")
print()

print(f"Минимальная дельта: delta_{best_delta_index} = {min(deltas):.6f}")
print("Выбранная модель: z_3(x) = alpha * exp(beta * x)")
print()

print("Коэффициенты после линеаризации:")
print(f"A = {A:.6f}")
print(f"B = {B:.6f}")
print()

print("Коэффициенты после делинеаризации:")
print(f"alpha = e^B = {alpha:.6f}")
print(f"beta  = A   = {beta:.6f}")
print()

print("Аппроксимирующая функция:")
print(f"z(x) = {alpha:.6f} * exp({beta:.6f} * x)")
print()

headers = [
    "i",
    "x_i",
    "y_i",
    "z(x_i)",
    "z(x_i)-y_i",
    "|ошибка|",
    # "ошибка, %",
    "(ошибка)^2",
]

print(tabulate(table_rows, headers=headers, tablefmt="grid", floatfmt=".6f"))
print()
print(f"Сумма квадратов отклонений |z(x_i) - y_i|^2 = {sum_sq:.6f}")
print(f"Среднее квадратичное отклонение = sqrt(sum_sq / {n}) = {Delta:.6f}")
