#include <stdexcept>
#include <iostream>
#define DEBUGINFO 0

template <int L, int R, class T>
class PascalArray
{
public:
    T *data;

    PascalArray()
    {
        DEBUGINFO ? std::cout << "make " << L << " " << R << std::endl : std::cout;
        data = new T[R - L + 1];
    }

    PascalArray(PascalArray<L, R, T> &obj)
    {
        DEBUGINFO ? std::cout << "COPY " << L << " " << R << std::endl : std::cout;
        T *l = new T[R - L + 1];
        for (size_t i = 0; i < R - L + 1; i++)
        {
            l[i] = obj.data[i];
        }
        this->data = l;
    }
    ~PascalArray()
    {
        DEBUGINFO ? std::cout << "delete " << L << " " << R << std::endl : std::cout;
        delete[] data;
    }
    T &operator[](unsigned i) const
    {
        DEBUGINFO ? std::cout << "index " << i << " of " << L << " " << R << std::endl : std::cout;

        if (i > R || i < L || R == L - 1)
        {
            throw std::out_of_range("Index error of PascalArray!");
        }
        else
        {
            return data[i - L];
        }
    }
    template <int L2, int R2, class T2>
    PascalArray<L, R2, T> operator+(const PascalArray<L2, R2, T2> &l2)
    {
        if (R == L2 - 1)
        {
            PascalArray<L, R2, T> l;

            for (size_t i = 0; i < R - L + 1; i++)
            {
                l.data[i] = data[i];
            }
            for (size_t i = 0; i < R2 - L2 + 1; i++)
            {
                l.data[R - L + 1 + i] = l2.data[i];
            }

            // return PascalArray<L, R2, T>(l);
            return l;
        }
        else
        {
            throw std::out_of_range("Bad R1 and L2 for operation +");
        }
    }
};
