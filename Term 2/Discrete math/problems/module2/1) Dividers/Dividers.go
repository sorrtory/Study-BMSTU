package main

import (
	"fmt"
	"math"
)

type graph map[int][]int

func getDividers(x int) []int {
	if x == 0 {
		return []int{0}
	}

	divs_before_sqrt := make([]int, 0)
	divs_after_sqrt := make([]int, 0)

	k := 1
	for k <= int(math.Sqrt(float64(x)))+1 {
		if x%k == 0 {
			if k > 1 && (k >= divs_after_sqrt[0] || x/k <= divs_before_sqrt[len(divs_before_sqrt)-1]) {
				break
			}
			divs_before_sqrt = append(divs_before_sqrt, k)
			if k != x/k {
				divs_after_sqrt = append([]int{x / k}, divs_after_sqrt...)
			}
		}
		k += 1
	}

	return append(divs_before_sqrt, divs_after_sqrt...)

}
func printGraph(g graph) {
	fmt.Println("graph {")
	for key := range g {
		fmt.Printf("    %d\n", key)
	}
	for key, links := range g {
		for _, v := range links {
			fmt.Printf("    %d -- %d\n", key, v)
		}
	}
	fmt.Println("}")
}
func buildGraph(sortedDividers []int) graph {
	g := make(graph, 0)
	for i := 0; i < len(sortedDividers); i++ {
		div := sortedDividers[i]
		g[div] = []int{}

		if i > 0 {
			// Going down finding dividables from sortedDividers
			for j := i - 1; j >= 0; j-- {
				should_add := true
				// Check the dividable dividables to not being dividables for div
				if div%sortedDividers[j] == 0 {
					for _, v := range g[sortedDividers[j]] {
						if div%v == 0 {
							should_add = false
							break
						}
					}
					if should_add {
						g[sortedDividers[j]] = append(g[sortedDividers[j]], div)
					}
				}
			}
		}

	}
	return g
}
func main() {
	var x int
	fmt.Scanf("%d", &x)
	printGraph(buildGraph(getDividers(x)))
}
