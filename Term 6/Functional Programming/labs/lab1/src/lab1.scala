redmibook :: ~ % cs launch scala:2.13.18                                       
Welcome to Scala 2.13.18 (OpenJDK 64-Bit Server VM, Java 21.0.10).
Type in expressions for evaluation. Or try :help.

scala> val n1 = 1 :: 0 :: 2 :: Nil
val n1: List[Int] = List(1, 0, 2)

scala> val n2 = 3 :: 1 :: Nil
val n2: List[Int] = List(3, 1)

scala> val mul: (List[Int], List[Int]) => List[Int] = {
     | case (Nil, Nil) => Nil
     | case (x :: xs, Nil) => x :: mul(xs, Nil)
     | case (Nil, x :: xs) => x :: mul(Nil, xs)
     | case (x :: xs, y :: ys) => x + y :: mul(xs, ys)
     | }
val mul: (List[Int], List[Int]) => List[Int] = $Lambda/0x000077739c586a50@6d4c18b8

scala> mul(n1, n2)
val res0: List[Int] = List(4, 1, 2)


scala> 