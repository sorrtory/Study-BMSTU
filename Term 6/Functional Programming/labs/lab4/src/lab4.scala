object Main {

  // Абстрактный синтаксис
  sealed abstract class Expr
  case class Var(name: String) extends Expr
  case class Add(left: Expr, right: Expr) extends Expr
  case class Mul(left: Expr, right: Expr) extends Expr
  case class Let(name: String, value: Expr, body: Expr) extends Expr

  // Подсчет числа вхождений переменной в выражение
  def countVar(x: String, expr: Expr): Int = expr match {
    case Var(name) =>
      if (name == x) 1 else 0

    case Add(left, right) =>
      countVar(x, left) + countVar(x, right)

    case Mul(left, right) =>
      countVar(x, left) + countVar(x, right)

    case Let(name, value, body) =>
      countVar(x, value) + (if (name == x) 0 else countVar(x, body))
  }

  // Подстановка replacement вместо переменной x
  def substitute(x: String, replacement: Expr, expr: Expr): Expr = expr match {
    case Var(name) =>
      if (name == x) replacement else expr

    case Add(left, right) =>
      Add(
        substitute(x, replacement, left),
        substitute(x, replacement, right)
      )

    case Mul(left, right) =>
      Mul(
        substitute(x, replacement, left),
        substitute(x, replacement, right)
      )

    case Let(name, value, body) =>
      val newValue = substitute(x, replacement, value)
      if (name == x) {
        Let(name, newValue, body)
      } else {
        Let(name, newValue, substitute(x, replacement, body))
      }
  }

  // Разбираем выражение
  def subexpressions(expr: Expr): List[Expr] = expr match {
    case v @ Var(_) =>
      List(v)

    case a @ Add(left, right) =>
      a :: (subexpressions(left) ::: subexpressions(right))

    case m @ Mul(left, right) =>
      m :: (subexpressions(left) ::: subexpressions(right))

    case l @ Let(_, value, body) =>
      l :: (subexpressions(value) ::: subexpressions(body))
  }

  // Сколько раз подвыражение e встречается в expr
  def countExpr(e: Expr, expr: Expr): Int =
    subexpressions(expr).count(_ == e)

  // Замена каждого вхождения target на Var(name)
  def replaceExpr(target: Expr, name: String, expr: Expr): Expr = expr match {
    case _ if expr == target =>
      Var(name)

    case Var(_) =>
      expr

    case Add(left, right) =>
      Add(
        replaceExpr(target, name, left),
        replaceExpr(target, name, right)
      )

    case Mul(left, right) =>
      Mul(
        replaceExpr(target, name, left),
        replaceExpr(target, name, right)
      )

    case Let(letName, value, body) =>
      Let(
        letName,
        replaceExpr(target, name, value),
        replaceExpr(target, name, body)
      )
  }

  // разбираем НЕ Var
  def extractable(expr: Expr): Boolean = expr match {
    case Var(_) => false
    case _      => true
  }

  // Поиск первого повторяющегося подвыражения
  def firstRepeated(expr: Expr): Option[Expr] = {
    val all = subexpressions(expr)

    // ищем первое подвыражение, которое можно извлечь в let
    //  и которое встречается более одного раза
    all.find(e => extractable(e) && countExpr(e, expr) > 1)
  }

  // Основная оптимизация с генерацией имён v0, v1
  def optimize(expr: Expr, nextId: Int): (Expr, Int) = {
    val recursivelyOptimized: (Expr, Int) = expr match {
      case v @ Var(_) =>
        (v, nextId)

      case Add(left, right) =>
        val (leftOpt, id1) = optimize(left, nextId)
        val (rightOpt, id2) = optimize(right, id1)
        (Add(leftOpt, rightOpt), id2)

      case Mul(left, right) =>
        val (leftOpt, id1) = optimize(left, nextId)
        val (rightOpt, id2) = optimize(right, id1)
        (Mul(leftOpt, rightOpt), id2)

      case Let(name, value, body) =>
        val (valueOpt, id1) = optimize(value, nextId)
        val (bodyOpt, id2) = optimize(body, id1)

        val letExpr = Let(name, valueOpt, bodyOpt)
        val uses = countVar(name, bodyOpt)

        if (uses == 1) {
          optimize(substitute(name, valueOpt, bodyOpt), id2)
        } else {
          (letExpr, id2)
        }
    }

    // Проверяем уже оптимизированное выражение
    recursivelyOptimized match {
      case (optimizedExpr, idAfterRec) =>
        firstRepeated(optimizedExpr) match {
          case Some(commonExpr) =>
            val freshName = "v" + idAfterRec.toString
            val replaced = replaceExpr(commonExpr, freshName, optimizedExpr)
            val withLet = Let(freshName, commonExpr, replaced)
            optimize(withLet, idAfterRec + 1)

          case None =>
            (optimizedExpr, idAfterRec)
        }
    }
  }

  def letsOptimize(expr: Expr): Expr =
    optimize(expr, 0)._1

  def main(args: Array[String]): Unit = {
    val expr =
      Mul(
        Add(Var("x"), Var("y")),
        Add(Var("x"), Var("y"))
      )

    println("Исходное выражение:")
    println(expr)
    println("После оптимизации:")
    println(letsOptimize(expr))
    println()

  }
}
