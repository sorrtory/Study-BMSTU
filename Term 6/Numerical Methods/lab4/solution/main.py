import math
from tabulate import tabulate

# Моя система
#
# cos(y-1)+x=0.5
# y-cos(x)=3

# В desmos мне выдало пересечение в точке (1.20691, 3.35591)
# Возьмем начальное приближение x0 = 1, y0 = 3

# Тогда матрица Якоби будет:
# J = [[1, -sin(y-1)],
#      [sin(x), 1]]

# Перепишем систему в виде:
# f1(x, y) = cos(y-1) + x - 0.5 = 0
# f2(x, y) = y - cos(x) - 3 = 0


def f1(x, y):
    return math.cos(y - 1) + x - 0.5


def f2(x, y):
    return y - math.cos(x) - 3


# Частные производные для матрицы Якоби
def df1_dx(x, y):
    return 1


def df1_dy(x, y):
    return -math.sin(y - 1)


def df2_dx(x, y):
    return math.sin(x)


def df2_dy(x, y):
    return 1


# Решение линейной системы 2x2 через крамера:
# a11*dx + a12*dy = b1
# a21*dx + a22*dy = b2
def solve_2x2(a11, a12, a21, a22, b1, b2):
    det = a11 * a22 - a12 * a21

    if abs(det) < 1e-12:
        raise ValueError("Определитель равен нулю, метод продолжить нельзя")

    dx = (b1 * a22 - a12 * b2) / det
    dy = (a11 * b2 - b1 * a21) / det
    return dx, dy


# Метод Ньютона
def newton_method(x0, y0, eps=0.01, max_iter=20):
    x = x0
    y = y0
    rows = []

    for k in range(max_iter):
        # Вычисляем значения функций в текущей точке
        F1 = f1(x, y)
        F2 = f2(x, y)

        # Вычисляем элементы матрицы Якоби
        a11 = df1_dx(x, y)
        a12 = df1_dy(x, y)
        a21 = df2_dx(x, y)
        a22 = df2_dy(x, y)

        # Решаем систему J * [dx, dy]^T = -F
        dx, dy = solve_2x2(a11, a12, a21, a22, -F1, -F2)

        # Находим следующее приближение
        x_new = x + dx
        y_new = y + dy

        # Норма для проверки точности
        norm = max(abs(dx), abs(dy))

        # Сохраняем данные для таблицы
        rows.append([
            k,
            x,
            y,
            dx,
            dy,
            norm
        ])

        # Переходим к следующей итерации
        x = x_new
        y = y_new

        # Проверка условия остановки
        if norm <= eps:
            break

    return x, y, rows


# Начальное приближение
x0 = 1
y0 = 3

# Точность
eps = 0.01

x, y, rows = newton_method(x0, y0, eps)

headers = ["k", "x_k", "y_k", "dx", "dy", "norm"]

print("Таблица итераций метода Ньютона:\n")
print(tabulate(rows, headers=headers, tablefmt="grid", floatfmt=".6f"))

print(f"\nИтоговое приближение: x = {x:.4f}, y = {y:.4f}")