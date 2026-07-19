class StrSet private (private val pred: String => Boolean) {
  def this(sub: String) = this(x => x.contains(sub))
  def in(x: String): Boolean = pred(x)
  def +(that: StrSet): StrSet = new StrSet(x => this.pred(x) || that.pred(x))
  def *(that: StrSet): StrSet = new StrSet(x => this.pred(x) && that.pred(x))
}

object Main {
  def main(args: Array[String]): Unit = {
    val a = new StrSet("cat")
    val b = new StrSet("dog")
    val u = a + b
    val i = a * b
    println(a.in("my cat"))
    println(b.in("hotdog"))
    println(i.in("hotdog"))
    println(i.in("catdog"))
  }
}