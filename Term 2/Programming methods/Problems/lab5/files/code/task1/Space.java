package task1;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.lang.Math.*;

class Point implements Comparable<Point>{
    public double id, x, y, z;
    Point(double id, double x, double y, double z){
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }

    @Override
    public int compareTo(Point o) {
        return (int) (o.x - this.x + o.y - this.y + o.z - this.z + o.id - this.id);
    }

    @Override
    public String toString() {
        return "task1.Point{" +
                "id=" + id +
                ", x=" + x +
                ", y=" + y +
                ", z=" + z +
                '}';
    }
}
class Line implements Comparable<Line>{
    public Point start, end, crossOXY;
    public double length;
    Line(Point start, Point end){
        this.start = start;
        this.end = end;
        this.length = sqrt(pow(end.x - start.x, 2) + pow(end.y - start.y, 2) + pow(end.z - start.z, 2));
        this.crossOXY = getOXY();
    }
    private Point getOXY(){
        double t = (double) start.z /(start.z - end.z);
        double x = (end.x - start.x)*t + start.x;
        double y = (end.y - start.y)*t + start.y;
        return new Point(-1, x, y, 0);
    }
    public boolean getQuarter(int t){
        if (crossOXY.x >= 0 & crossOXY.y >= 0 & t == 1){
            return true;
        } else if (crossOXY.x < 0 & crossOXY.y >= 0 & t == 2) {
            return true;
        } else if (crossOXY.x < 0 & crossOXY.y < 0 & t == 3) {
            return true;
        }
        else if (crossOXY.x >= 0 & crossOXY.y < 0 & t == 4) {
            return true;
        }
        else return false;
    }

    @Override
    public int compareTo(Line o) {
        if (this.start == o.start & this.end == o.end){
            return 0;
        }
        if (this.start.x > o.start.x){
            return 1;
        }
        else {
            return -1;
        }
    }

    @Override
    public String toString() {
        return "task1.Line{" +
                "start=" + start +
                ", end=" + end +
                ", crossOXY=" + crossOXY +
                ", length=" + length +
                '}';
    }
}


public class Space {
    ArrayList<Point> Points;
    int count = 0;
    Space(){
        Points = new ArrayList<>();
    }
    public void add(int x, int y, int z){
        Points.add(new Point(count, x, y, z));
        count += 1;
    }
    public Point getPoint(int id){
        return Points.stream().filter(p -> p.id == id).findFirst().get();
    }

    public boolean isNeighbour(Line l, int neighbour_distance){
        return l.start.id < l.end.id & l.length <= neighbour_distance;
    }
    public boolean crossOXY(Line l){
        return l.start.z >= 0 & l.end.z <= 0 || l.end.z >= 0 & l.start.z <= 0;
    }


    public Stream<Line> linesStream(int neighbour_distance) {
        ArrayList<Line> result = new ArrayList<>();
        Points.stream()
                .forEach(p1 -> Points.stream()
                        .forEach(p2 -> result.add(new Line(p1, p2))));
        return result.stream().filter(this::crossOXY).filter(line -> isNeighbour(line, neighbour_distance));
    }
    public boolean isInside(Point p, int r){
        return abs(p.x) <= r & abs(p.y) <= r & abs(p.z) <= r;
    }
    public Optional<List<Point>> getPointsInside(int r) {
        Optional<List<Point>> result = Optional.of(Points.stream().filter(point -> isInside(point, r)).collect(Collectors.toList()));
        return result;
    }
    public Optional<List<Point>> getPointsOutside(int r) {
        Optional<List<Point>> result = Optional.of(Points.stream().filter(point -> !isInside(point, r)).collect(Collectors.toList()));
        return result;
    }

}
