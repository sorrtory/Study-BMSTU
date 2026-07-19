import numpy as np
import matplotlib.pyplot as plt
import os

# точки соединять нельзя!

# Исходные данные
x = np.array([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], dtype=float)
y = np.array([1.24, 1.74, 1.61, 2.16, 3.06, 2.88, 4.53, 5.40, 7.07], dtype=float)

# Специальные средние для x
x_a = (x[0] + x[-1]) / 2
x_g = np.sqrt(x[0] * x[-1])
x_h = 2 / (1 / x[0] + 1 / x[-1])

# Значения z(x_a), z(x_g), z(x_h) по графику
# np.interp выполняет линейную интерполяцию между соседними узлами
z_xa = np.interp(x_a, x, y)
z_xg = np.interp(x_g, x, y)
z_xh = np.interp(x_h, x, y)

# Построение графика
plt.figure(figsize=(11, 7))

# Табличная функция
plt.plot(x, y, marker='o', linewidth=2, markersize=7, label='Табличная функция')

# Специальные точки
special_x = [x_a, x_g, x_h]
special_z = [z_xa, z_xg, z_xh]
special_labels = [
    rf"$x_a={x_a:.4f},\ z(x_a)={z_xa:.4f}$",
    rf"$x_g={x_g:.4f},\ z(x_g)={z_xg:.4f}$",
    rf"$x_h={x_h:.4f},\ z(x_h)={z_xh:.4f}$"
]

# Нанесение специальных точек и направляющих линий
for xs, zs, lab in zip(special_x, special_z, special_labels):
    plt.plot([xs, xs], [0, zs], linestyle='--')     # вертикальная линия
    plt.plot([0.9, xs], [zs, zs], linestyle='--')   # горизонтальная линия
    plt.plot(xs, zs, marker='o', markersize=9, label=lab)

# Оформление
plt.xlim(0.9, 5.2)
plt.ylim(0, 7.6)
plt.grid(True, alpha=0.5)
plt.xlabel('x')
plt.ylabel('z(x)')
plt.title('Графическое определение значений $z(x_a)$, $z(x_g)$, $z(x_h)$')
plt.legend(fontsize=11)
plt.tight_layout()

# Save figure to file (works in headless environments where plt.show() is not available)
out_path = os.path.join(os.path.dirname(__file__), 'plot.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close()

print(f"Saved plot to {out_path}")

# Вывод численных значений
print(f"x_a = {x_a:.4f}, z(x_a) = {z_xa:.4f}")
print(f"x_g = {x_g:.4f}, z(x_g) = {z_xg:.4f}")
print(f"x_h = {x_h:.4f}, z(x_h) = {z_xh:.4f}")