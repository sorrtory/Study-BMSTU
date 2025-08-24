# Лабораторная работа №7 – оптимизация приложений OpenGL

## Цель работы

Изучение эффективных приемов организации приложений и оптимизации вызовов OpenGL.

## Задача

Оптимизировать приложение OpenGL, созданное в рамках предыдущей лабораторной работы, используя наиболее эффективные методики.

### Требования

- Обязательно использовать:
  - Дисплейные списки.
  - Массивы вершин.
- Применить еще как минимум 2 различные оптимизации (всего не менее 4 оптимизаций).
- Оценить применимость выбранных методов оптимизации на основании измерения производительности.

### Рекомендуемая литература

Баяковский Ю.М., Игнатенко А.В. *Начальный курс OpenGL*. — М.: «Планета Знаний», 2007. — 221 с. — Глава 9.

<!-- ### Results of Performance Measurements

The table below summarizes the performance improvements achieved through various optimization techniques applied to the OpenGL application:

| Optimization Technique       | FPS Range  | FPS Difference |
|------------------------------|------------|----------------|
| No Optimization              | 160-175    | 0              |
| Display Lists                | 180-195    | +20            |
| Vertex Arrays                | 200-215    | +40            |
| Frustum Culling              | 220-235    | +60            |
| Texture Compression          | 240-255    | +80            |
| **Total Improvement**        | **240-255**| **+80**        |

The FPS values represent the range of frames per second observed during testing. Each optimization technique was applied incrementally, and the FPS difference reflects the improvement over the baseline (no optimization). -->

## FPS optimization table

Otimizations are done for Torus. All numbers are average and taken several times.

Diferrence with default approach (everything's drawn on each frame)

| Optimization                  | FPS     | FPS Difference |
|:-----------------------------:|:-------:|:--------------:|
| None                          | 204.0   |       -        |
| Display Lists                 | 4883.9  |    +4680       |
| Vertex Arrays                 | 3992.8  |    +3788       |
| EBO                           | 197.1   |    +-20        |
| glColorMaterial               | 201.1   |    +-30        |


Coherent optimization

| Optimization                  | FPS     | FPS Difference |
|:-----------------------------:|:-------:|:--------------:|
| None                          | 188.4   |       -        |
| +Display Lists                | 4964.6  |    +4850       |
| +Vertex Arrays                | 5144.5  |    +180        |
| +glColorMaterial              | 5277.8  |    +200        |
| +EBO                          | 5183.7  |    -100        |





