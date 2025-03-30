package main

import (
	"fmt"
	"math"
)

type num struct {
	n          int
	d          int
	isNegative bool
	isZero     bool
}

func (x num) simplify() num {
	if x.isZero {
		x.n = 0
		x.d = 1
		return x
	}

	var d_dividers []int
	k := 2
	n := x.n
	d := x.d

	proper := n > d

	if !proper {
		n, d = d, n
	}

	start_d := d
	for k <= int(math.Sqrt(float64(start_d))+1) {
		if d%k == 0 {
			d_dividers = append(d_dividers, k)
			d /= k
		} else {
			k += 1
		}
	}
	d_dividers = append(d_dividers, d)

	for i, v := range d_dividers {
		if n%v == 0 {
			n /= v
			d_dividers[i] = 1
		}
	}

	d = 1
	for _, v := range d_dividers {
		d *= v
	}

	if proper {
		return num{n, d, x.isNegative, x.isZero}
	} else {
		return num{d, n, x.isNegative, x.isZero}
	}
}
func divide(a, b num) num {
	n := a.n * b.d
	d := a.d * b.n

	if b.isZero {
		panic("Can't divide by zero")
	}

	return num{n, d, a.isNegative != b.isNegative, a.isZero || b.isZero}.simplify()
}
func multiply(a, b num) num {
	n := a.n * b.n
	d := a.d * b.d
	return num{n, d, a.isNegative != b.isNegative, a.isZero || b.isZero}.simplify()
}
func subtract(a, b num) num {
	x := a.n * b.d
	y := a.d * b.n
	d := a.d * b.d

	var sum int
	if a.isNegative {
		sum += -x
	} else {
		sum += x
	}
	if b.isNegative {
		sum -= -y
	} else {
		sum -= y
	}

	switch {
	case sum == 0:
		return num{sum, d, false, true}
	case sum > 0:
		return num{sum, d, false, false}.simplify()
	case sum < 0:
		return num{-sum, d, true, false}.simplify()
	default:
		return num{}
	}
}

func stepForm(matrix [][]num, n int) bool {
	// Ступеним, return true если ошибка
	for step := 0; step < n; step++ {
	    try_again_after_lines_swapped:
		// Make zeros under step num
		for i := step; i < n; i++ {
			div := matrix[i][step] // Set the value the line gonna be divided

			if div.isZero == false {
				// Divide the line
				for j := step; j < n+1; j++ {
					matrix[i][j] = divide(matrix[i][j], div)
				}

				// Subtract from the upper line
				if i > step {
					for j := step; j < n+1; j++ {
						matrix[i][j] = subtract(matrix[i][j], matrix[step][j])
					}
				}
			} else {
				// Try to swap the zero div line with the downer num that is not zero div
				for j := i+1; j < n; j++ {
					if !matrix[j][step].isZero {
						for k := 0; k < n+1; k++ {
							matrix[i][k], matrix[j][k] = matrix[j][k], matrix[i][k]
						}
						goto try_again_after_lines_swapped
					}
				}

			}

		}
	}
	// Check the matrix to be unsolvable
	for i := 0; i < n; i++ {
		count0 := 0
		for j := 0; j < n; j++ {
			if matrix[i][j].isZero {
				count0 += 1
			}
		}
		if count0 == n && !matrix[i][n].isZero {
			return true
		}
	}
	return false
}

func rvrsMoveNPrint(matrix [][]num, n int) bool {
	x := make([]num, n) // solutions

	for i := n - 1; i >= 0; i-- {

		right := matrix[i][n] // right part of equation
		if right.isZero {
			for j := i; j < n; j++ {
				x[j] = num{0, 1, false, true} // = 0 solutions could be anything or 0
			}
			continue
		}
		for j := i + 1; j < n; j++ {
			// Substitude the known solutions and move it to the right
			right = subtract(right, multiply(matrix[i][j], x[j]))
		}

		if matrix[i][i].isZero {
			return true
		}
		x[i] = divide(right, matrix[i][i])
	}

	for _, v := range x {
		printNum(v, "")
		fmt.Println()
	}
	return false
}

func printNum(q num, delimiter string) {
	if q.isZero {
		fmt.Printf(delimiter + "0" + delimiter + delimiter + delimiter)
	} else if q.isNegative {
		fmt.Printf("-%d/%d"+delimiter, q.n, q.d)
	} else {
		fmt.Printf(delimiter+"%d/%d"+delimiter+delimiter, q.n, q.d)
	}
}
func printMatrix(matrix [][]num) {
	for _, v := range matrix {
		for _, q := range v {
			printNum(q, " ")
		}
		fmt.Println()
	}
}
func main() {
	var n int
	fmt.Scan(&n)

	eqs := make([][]int, n)
	for i := 0; i < n; i++ {
		eqs[i] = make([]int, n+1)
		for j := 0; j < n+1; j++ {
			fmt.Scan(&eqs[i][j])
		}
	}
	// const n = 3
	// eqs := [n][n + 1]int{{-4, -1, 8, 2}, {7, -7, 7, 3}, {5, -1, -4, 7}}

	matrix := make([][]num, n)
	for i := 0; i < n; i++ {
		matrix[i] = make([]num, n+1)
		for j := 0; j < n+1; j++ {
			matrix[i][j] = num{int(math.Abs(float64(eqs[i][j]))), 1, eqs[i][j] < 0, eqs[i][j] == 0}
		}
	}

	if stepForm(matrix, n) || rvrsMoveNPrint(matrix, n) {
		fmt.Println("No solution")
	}
	
}
