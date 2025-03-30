package main

import (
	"fmt"
	"os"
	"sort"
)

type set struct {
	values []int
	len    int
}

func (s *set) add(x int) {
	s.values = append(s.values, x)
	s.len += 1
	sort.Ints(s.values)
}
func (s set) equals(s1 set) bool {
	if s.len != s1.len {
		return false
	} else {
		for i := 0; i < s.len; i++ {
			if s.values[i] != s1.values[i] {
				return false
			}
		}
	}
	return true
}

func dfs_components(v, num int, component []int, g [][]int) {
	// Идем в глубину, разбиваем по островкам
	component[v] = num
	for _, u := range g[v] {
		if component[u] == 0 {
			dfs_components(u, num, component, g)
		}
	}
}

func dfs(v, col int, color []int, g [][]int) {
	// Идем в глубину, разбиваем на две несвязные группы
	color[v] = col
	for _, u := range g[v] {
		if color[u] == 0 {
			dfs(u, -col, color, g)
		} else if color[u] != -col {
			fmt.Println("No solution")
			os.Exit(0)
		}
	}
}

func getMax(arr []int) int {
	// Max int from int array
	m := arr[0]
	for _, v := range arr {
		if v > m {
			m = v
		}
	}
	return m
}

func getDelta(s1 []set) int {
	// Component's delta between two sets
	x := s1[0].len - s1[1].len
	if x >= 0 {
		return x
	} else {
		return -x
	}

}
func abs(x int) int {
	if x > 0 {
		return x
	}
	return -x
}

func groupsLexicographicallyLess(g1, g2 []int) bool {
	// g1 < g2
	if len(g1) < len(g2) {
		return true
	} else if len(g1) > len(g2) {
		return false
	} else {
		for i, v := range g1 {
			if g2[i] < v {
				return false
			} else if g2[i] > v {
				return true
			}
		}
	}
	return true
}

func getBestGroups(C [][]set, Group1, Group2 []int) ([]int, []int) {
	sort.Ints(Group1)
	sort.Ints(Group2)
	if len(C) == 0 {
		return Group1, Group2
	} else {

		g11, g12 := append(append(make([]int, 0), Group1...), C[0][0].values...), append(append(make([]int, 0), Group2...), C[0][1].values...)
		g21, g22 := append(append(make([]int, 0), Group1...), C[0][1].values...), append(append(make([]int, 0), Group2...), C[0][0].values...)

		g11_, g12_ := getBestGroups(C[1:], g11, g12)
		g21_, g22_ := getBestGroups(C[1:], g21, g22)
		if abs(len(g11_)-len(g12_)) < abs(len(g21_)-len(g22_)) {
			return g11_, g12_
		} else if abs(len(g11_)-len(g12_)) == abs(len(g21_)-len(g22_)) {
			if groupsLexicographicallyLess(g11_, g21_) {
				return g11_, g12_
			}
			return g21_, g22_
		}
		return g21_, g22_

	}
}

func main() {
	var n int
	var c rune
	fmt.Scanf("%d", &n)

	g := make([][]int, n) // Список смежности

	for i := 0; i < n; i++ {
		g[i] = make([]int, 0)
		for j := 0; j < n; j++ {
			fmt.Scanf("%c", &c)
			if c == '+' {
				g[i] = append(g[i], j)
			}
			fmt.Scanf("%c", &c)

		}
	}

	component := make([]int, n)
	num := 0
	// Разбиваем на независимые компоненты связности
	for v := 0; v < n; v++ {
		if component[v] == 0 {
			num += 1
			dfs_components(v, num, component, g)
		}
	}

	compNum := getMax(component)
	C0 := make([][]int, compNum) // Список компонентов связности
	for i, v := range component {
		C0[v-1] = append(C0[v-1], i)
	}

	// Разбиваем каждый копонент на две группы, между которыми нет соседних ребер
	color := make([]int, n)
	for v := 0; v < n; v++ {
		if color[v] == 0 {
			dfs(v, 1, color, g)
		}
	}

	C := make([][]set, compNum) // Список компонентов, разбитых по группам
	for compIndex := range C0 {
		C[compIndex] = make([]set, 2)
		C[compIndex][0] = set{make([]int, 0), 0}
	}

	for compIndex, compElements := range C0 {
		for _, vertex := range compElements {
			if color[vertex] == 1 {
				C[compIndex][0].add(vertex)
			} else if color[vertex] == -1 {
				C[compIndex][1].add(vertex)
			} else {
				fmt.Println("No solution")
				os.Exit(0)
			}
		}
	}
	C1 := make([][]set, 0)  // Компоненты, у которых равные доли
	C11 := make([][]set, 0) // Компоненты, у которых НЕравные доли
	for _, comp := range C {
		if getDelta(comp) == 0 {
			C1 = append(C1, comp)
		} else {
			C11 = append(C11, comp)
		}
	}
	Group1 := make([]int, 0)
	Group2 := make([]int, 0)
	for _, pair := range C1 {
		if groupsLexicographicallyLess(pair[0].values, pair[1].values) {
			Group1 = append(Group1, pair[0].values...)
			Group2 = append(Group2, pair[1].values...)
		} else {
			Group1 = append(Group1, pair[1].values...)
			Group2 = append(Group2, pair[2].values...)
		}
	}

	Group1Add, Group2Add := getBestGroups(C11, make([]int, 0), make([]int, 0))

	Group1 = append(Group1, Group1Add...)
	Group2 = append(Group2, Group2Add...)

	sort.Ints(Group1)
	sort.Ints(Group2)

	for _, v := range Group1 {
		fmt.Printf("%d ", v+1)
	}

}
