package main

import (
	"fmt"
)

func max(v1, v2 int) int {
	if v1 > v2 {
		return v1
	}
	return v2
}
func add(a, b []int32, p int) []int32 {
	sum := make([]int32, max(len(a), len(b))+1)

	for i, v := range sum[:len(sum)-1] {
		if i < len(a) && i < len(b) {
			sum[i] = (v + a[i] + b[i]) % int32(p)
			sum[i+1] = (v + a[i] + b[i]) / int32(p)

		} else if i >= len(a) && i < len(b) {
			sum[i] = (v + b[i]) % int32(p)
			sum[i+1] = (v + b[i]) / int32(p)

		} else if i < len(a) && i >= len(b) {
			sum[i] = (v + a[i]) % int32(p)
			sum[i+1] = (v + a[i]) / int32(p)
		}
	}
	for i := len(sum); i > 0; i-- {
		if sum[i-1] != 0 {
			return sum[:i]
		}
	}
	return sum
}

func main() {
	fmt.Print(add([]int32{3, 0, 3}, []int32{2, 3, 1}, 4))
}
