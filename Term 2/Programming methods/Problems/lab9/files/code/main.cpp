// Согласно выбранному из таблиц 1–26 описанию требуется составить шаблон класса, перегрузив указанные операции.

/*
// Task 15
Shape<T> – множество точек в пространстве T × T, задающих некоторую геометрическую фигуру. Операции, перегружаемые для Shape<T>:

    1.  «+» и «−» – объединение и разность двух множеств;
    2. «( )» – проверка принадлежности точки множеству.

У класса Shape<T> должно быть два конструктора:
    1. первый конструктор принимает координаты нижней левой и верхней правой вершин прямоугольника, каждая сторона которого параллельна одной из осей координат, и порождает множество точек, принадлежащих этому прямоугольнику;
    2. аналогично, второй конструктор порождает множество точек круга по координатам центра и радиусу.


*/

#include <iostream>
#include <vector>
#include <cmath>
#include <stdexcept>

#define ERROR throw std::invalid_argument("Outside of the area!")
#define CHECK_POINT(x, y, T) (x > T || y > T || x < 0 || y < 0) ? 1 : 0

template <int T>
class Shape_
{
private:
    int type; // 1 - rectangle  ; 2 - circle
    int x1, y1, x2, y2;
    int x, y, r;

public:
    Shape_(int x1, int y1, int x2, int y2); // rect
    Shape_(int x, int y, int r);            // circle
    bool Inhere(int x, int y);
};

template <int T>
Shape_<T>::Shape_(int x1, int y1, int x2, int y2)
{
    if (CHECK_POINT(x1, y1, T) || CHECK_POINT(x2, y2, T))
        ERROR;

    this->x1 = x1;
    this->y1 = y1;
    this->x2 = x2;
    this->y2 = y2;
    this->type = 1;
}

template <int T>
Shape_<T>::Shape_(int x, int y, int r)
{
    if (CHECK_POINT(x, y, T) || r > T || r < 0)
        ERROR;

    this->x = x;
    this->y = y;
    this->r = r;
    this->type = 2;
}

template <int T>
bool Shape_<T>::Inhere(int x, int y)
{

    if (type == 1)
    {
        return x >= x1 && y >= y1 && x <= x2 && y <= y2;
    }
    else if (type == 2)
    {
        return pow((x - this->x), 2) + pow((y - this->y), 2) <= pow(r, 2);
    }
    return false;
}

template <int T>
class Shape
{
private:
    std::vector<Shape_<T>> shapesPlus;
    std::vector<Shape_<T>> shapesMinus;

public:
    Shape(int x1, int y1, int x2, int y2); // rect
    Shape(int x, int y, int r);            // circle
    Shape<T> operator+(const Shape<T> &shape);
    Shape<T> operator-(const Shape<T> &shape);
    bool operator()(int x, int y);
};

template <int T>
Shape<T>::Shape(int x1, int y1, int x2, int y2)
{
    shapesPlus.push_back(Shape_<T>(x1, y1, x2, y2));
}

template <int T>
Shape<T>::Shape(int x, int y, int r)
{
    shapesPlus.push_back(Shape_<T>(x, y, r));
}

template <int T>
Shape<T> Shape<T>::operator+(const Shape<T> &shape)
{
    for (auto &&i : shape.shapesPlus)
        this->shapesPlus.push_back(i);

    for (auto &&i : shape.shapesMinus)
        this->shapesMinus.push_back(i);

    return *this;
}

template <int T>
Shape<T> Shape<T>::operator-(const Shape<T> &shape)
{
    for (auto &&i : shape.shapesPlus)
        this->shapesMinus.push_back(i);

    for (auto &&i : shape.shapesMinus)
        this->shapesPlus.push_back(i);

    return *this;
}

template <int T>
bool Shape<T>::operator()(int x, int y)
{
    if (CHECK_POINT(x, y, T))
        ERROR;

    int inside = 0;

    for (auto &&i : shapesPlus)
        if (i.Inhere(x, y))
            inside++;

    for (auto &&i : shapesMinus)
        if (i.Inhere(x, y))
            inside--;

    return inside > 0;
}

int main()
{
    Shape<100> cc{10, 10, 5};
    // Возможен ли мудрый принт объектов, как перегрузка toString в Java?
    std::cout << "Check (7, 8) of {10, 10, 5}: " << cc(7, 8) << std::endl;
    std::cout << "Check (7, 8) minus area: " << (cc - Shape<100>(0, 0, 100, 100))(7, 8) << std::endl;
    std::cout << "Check (7, 8) plus area: " << (cc + Shape<100>(9, 9, 10))(7, 8) << std::endl;
    return 0;
}