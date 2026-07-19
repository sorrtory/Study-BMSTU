import math
from tabulate import tabulate

# Задаём функцию двух переменных
def f(x1, x2):
    return 2 * x1**2 + 3 * x2**2 - 2 * math.sin((x1 - x2) / 2) + x2


# Вычисляем градиент функции
def df_dx1(x1, x2):
    return 4 * x1 - math.cos((x1 - x2) / 2)


def df_dx2(x1, x2):
    return 6 * x2 + math.cos((x1 - x2) / 2) + 1


def grad(x1, x2):
    return df_dx1(x1, x2), df_dx2(x1, x2)


# Норма градиента для критерия остановки
def grad_norm(g1, g2):
    return max(abs(g1), abs(g2))


# Вторые производные для вычисления шага t*
def d2f_dx1dx1(x1, x2):
    return 4 + 0.5 * math.sin((x1 - x2) / 2)


def d2f_dx1dx2(x1, x2):
    return -0.5 * math.sin((x1 - x2) / 2)


def d2f_dx2dx2(x1, x2):
    return 6 + 0.5 * math.sin((x1 - x2) / 2)


# На каждом шаге находим параметр t*
def calc_t_star(x1, x2):
    fx = df_dx1(x1, x2)
    fy = df_dx2(x1, x2)

    fxx = d2f_dx1dx1(x1, x2)
    fxy = d2f_dx1dx2(x1, x2)
    fyy = d2f_dx2dx2(x1, x2)

    phi_1 = -(fx**2 + fy**2)
    phi_2 = fxx * fx**2 + 2 * fxy * fx * fy + fyy * fy**2

    if abs(phi_2) < 1e-12:
        raise ValueError("Невозможно вычислить шаг: phi''(0) = 0")

    return -phi_1 / phi_2


# Начальная точка X0 = (0, 0)
x1 = 0.0
x2 = 0.0

eps = 0.001
k = 0
rows = []

# Строим последовательные приближения до выполнения условия точности
while True:
    g1, g2 = grad(x1, x2)
    norm_g = grad_norm(g1, g2)
    fx_val = f(x1, x2)

    rows.append([k, x1, x2, fx_val, g1, g2, norm_g])

    if norm_g < eps:
        break

    t_star = calc_t_star(x1, x2)

    x1 = x1 - t_star * g1
    x2 = x2 - t_star * g2
    k += 1


# Сравниваем найденный минимум с аналитическим решением
# Приравниваем градиент к нулю:
# 4x1 - cos((x1 - x2)/2) = 0
# 6x2 + cos((x1 - x2)/2) + 1 = 0
#
# Отсюда:
# x1 = cos(u) / 4
# x2 = -(1 + cos(u)) / 6
# где u = (x1 - x2) / 2
#
# После подстановки получаем уравнение:
# u = (5*cos(u) + 2) / 24
#
# Его численное решение:
u = 0.283358712515895

# Подставляем найденное u в формулы для координат точки минимума
x1_anal = math.cos(u) / 4
x2_anal = -(1 + math.cos(u)) / 6

# Вычисляем значение функции в аналитически найденной точке
f_anal = f(x1_anal, x2_anal)

# Вывод таблицы итераций
headers = ["k", "x1", "x2", "f(x1,x2)", "df/dx1", "df/dx2", "||grad f||"]
print(tabulate(rows, headers=headers, tablefmt="grid", floatfmt=".6f"))

# Точка минимума через численный метод
print("\nЧисленное решение:")
print(f"x1 = {x1:.6f}")
print(f"x2 = {x2:.6f}")
print(f"f_min = {f(x1, x2):.6f}")

# Итог аналитического решения
print("\nАналитическое решение:")
print(f"x1* = {x1_anal:.6f}")
print(f"x2* = {x2_anal:.6f}")
print(f"f(x1*, x2*) = {f_anal:.6f}")

# Погрешности
print("\nСравнение:")
print(f"|x1 - x1*| = {abs(x1 - x1_anal):.6f}")
print(f"|x2 - x2*| = {abs(x2 - x2_anal):.6f}")
print(f"|f_num - f_anal| = {abs(f(x1, x2) - f_anal):.6f}")