% Лабораторная работа № 3 «Обобщённые классы в Scala»
% 1 апреля 2026 г.
% Александр Федуков, ИУ9-62Б
# Цель работы

Целью данной работы является приобретение навыков разработки обобщённых классов на языке Scala с
использованием неявных преобразований типов.

# Индивидуальный вариант

Класс Matrix[T], представляющий квадратную матрицу размера n с элементами типа T и операцией удаления
указанных строки и столбца. Кроме того, если тип T — числовой, дополнительно должна быть реализована операция
вычисления определителя матрицы.

# Реализация

```scala
class Matrix[T](val items: Vector[Vector[T]])(implicit num: Numeric[T] = null) {
  val size: Int = items.length

  def remove(row: Int, col: Int): Matrix[T] = {

    val new_items =
      items.zipWithIndex
        .filter(_._2 != row)
        .map { case (line, _) =>
          line.zipWithIndex
            .filter(_._2 != col)
            .map(_._1)
        }

    new Matrix[T](new_items)
  }

  def determinant(implicit unused: Numeric[T]): T = {
    if (size == 1) {
      items(0)(0)
    } else if (size == 2) {
      num.minus(
        num.times(items(0)(0), items(1)(1)),
        num.times(items(0)(1), items(1)(0))
      )
    } else {
      var result = num.zero

      for (j <- 0 until size) {
        val minor = remove(0, j)
        val cofactor =
          if (j % 2 == 0)
            num.times(items(0)(j), minor.determinant)
          else
            num.negate(num.times(items(0)(j), minor.determinant))

        result = num.plus(result, cofactor)
      }

      result
    }
  }

  override def toString: String =
    items.map(_.mkString("[", ", ", "]")).mkString("\n")
}

object Main extends App {
  val m1 = new Matrix(
    Vector(
      Vector(1, 2),
      Vector(3, 4)
    )
  )

  println("Matrix m1:")
  println(m1)
  println(m1.remove(0, 1))
  println("det(m1) = " + m1.determinant)
  println()
}
```

# Тестирование

Результат запуска программы:

```
Matrix m1:
[1, 2]
[3, 4]
[3]
det(m1) = -2
```

# Вывод

В ходе лабораторной работы был разработан обобщенный класс `Matrix[T]`, позволяющий работать с матрицами
разных числовых типов. Для выполнения арифметических операций был использован неявный параметр `Numeric[T]`,
что позволило не привязывать реализацию к конкретному типу данных. Данные матрицы хранятся в неизменяемом
контейнере `Vector`, а методы `remove` и `determinant` реализованы с применением функциональных возможностей
Scala. Проведенное тестирование подтвердило корректность удаления строки и столбца, а также вычисления
определителя матрицы.
