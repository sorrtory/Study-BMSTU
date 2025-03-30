import java.util.HashSet;
import java.util.function.Consumer;
import java.util.function.Function;

public class Roots<T> {
    private HashSet<T> container;

    private Roots(HashSet<T> container) {
        this.container = container;
    }

    public static Roots<Double> of(double a, double b, double c, double eps) {
        HashSet<Double> roots = new HashSet<>();
        if (a == 0.0) {
            if (b != 0.0)
                roots.add(-c / b);
        } else {
            double d = b * b - 4 * a * c;
            if (d >= 0.0) {
                if (d < eps)
                    d = 0.0;
                roots.add((-b + Math.sqrt(d)) / (2 * a));
                roots.add((-b - Math.sqrt(d)) / (2 * a));
            }
        }
        return new Roots<>(roots);
    }

    public <R> Roots<R> map(Function<T, R> f) {
        HashSet<R> c = new HashSet<>();
        for (T t : container)
            c.add(f.apply(t));
        return new Roots<>(c);
    }

    public void forEach(Consumer<T> f) {
        for (T t : container)
            f.accept(t);
    }

    public <R> Roots<R> flatMap(Function<T, Roots<R>> f) {
        HashSet<R> c = new HashSet<>();
        map(f).forEach(rs -> c.addAll(rs.container));
        return new Roots<>(c);
    }

    public static void main(String[] args) {
        Roots.of(1, 2, 0, 1e-10)
                // .map(t -> t * 10)
                // .map(pt -> pt)
                .forEach(x -> System.out.println(x));

    }
}

// public class Rts {

// public static void main(String[] args) {
// System.out.println("ABOBA");
// }
// }