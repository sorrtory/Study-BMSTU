from tabulate import tabulate

# Вариант
k = 22
alpha = 0.1 * k
beta = 0.1 * k

# Исходная система Ax = b
A = [
    [10.0 + alpha, -1.0, 0.2, 2.0],
    [1.0, 12.0 - alpha, -2.0, 0.1],
    [0.3, -4.0, 12.0 - alpha, 1.0],
    [0.2, -0.3, -0.5, 8.0 - alpha]
]

b = [
    1.0 + beta,
    2.0 - beta,
    3.0,
    1.0
]

n = 4

print("k =", k)
print("alpha =", alpha)
print("beta =", beta)

print("\nМатрица A:")
print(tabulate(A, tablefmt="grid", floatfmt=".6f"))

print("\nВектор b:")
print([round(x, 6) for x in b])

# Диагональное преобладание:
# 12.2 > 1 + 0.2 + 2 = 3.2
# 9.8  > 1 + 2 + 0.1 = 3.1
# 9.8  > 0.3 + 4 + 1 = 5.3
# 5.8  > 0.2 + 0.3 + 0.5 = 1.0
# Cистема уже имеет диагональное преобладание

# Приведение к виду x = Fx + c
F = []
c = []

for i in range(n):
    row = []

    for j in range(n):
        if i == j:
            row.append(0.0)
        else:
            row.append(-A[i][j] / A[i][i])

    F.append(row)
    c.append(b[i] / A[i][i])

print("\nМатрица F:")
print(tabulate(F, tablefmt="grid", floatfmt=".6f"))

print("\nВектор c:")
print([round(x, 6) for x in c])

# Норма матрицы F
norm_F = max(sum(abs(F[i][j]) for j in range(n)) for i in range(n))

print("\n||F|| =", round(norm_F, 6))

# Метод простой итерации
x_old = c.copy()
eps = 0.01
max_iter = 1000

simple_table = []

for k_iter in range(1, max_iter + 1):
    x_new = []

    for i in range(n):
        s = 0

        for j in range(n):
            s += F[i][j] * x_old[j]

        x_new.append(s + c[i])

    diff = max(abs(x_new[i] - x_old[i]) for i in range(n))

    Delta = norm_F / (1 - norm_F) * diff
    delta = Delta / max(abs(x_new[i]) for i in range(n))

    simple_table.append([
        k_iter,
        Delta,
        delta
    ])

    if delta < eps:
        break

    x_old = x_new.copy()

print("\nМетод простой итерации:")
print(tabulate(
    simple_table,
    headers=["k", "Delta", "delta"],
    tablefmt="grid",
    floatfmt=".6f"
))

print("\nОтвет методом простой итерации:")
print([round(x, 6) for x in x_new])
print("Число итераций:", k_iter)

# Метод Зейделя
x_old = c.copy()
eps_seidel = 10 ** (-4)

seidel_table = []

for k_iter_seidel in range(1, max_iter + 1):
    x_new = x_old.copy()

    for i in range(n):
        s = c[i]

        for j in range(n):
            if j < i:
                s += F[i][j] * x_new[j]
            else:
                s += F[i][j] * x_old[j]

        x_new[i] = s

    diff = max(abs(x_new[i] - x_old[i]) for i in range(n))

    Delta = norm_F / (1 - norm_F) * diff
    delta = Delta / max(abs(x_new[i]) for i in range(n))

    seidel_table.append([
        k_iter_seidel,
        diff,
        Delta,
        delta
    ])

    if diff <= eps_seidel:
        break

    x_old = x_new.copy()

print("\nМетод Зейделя:")
print(tabulate(
    seidel_table,
    headers=["k", "diff", "Delta", "delta"],
    tablefmt="grid",
    floatfmt=".6f"
))

print("\nОтвет методом Зейделя:")
print([round(x, 6) for x in x_new])
print("Число итераций:", k_iter_seidel)