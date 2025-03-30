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

func (s *set) sort() {
	sort.Ints(s.values)
}

func (s *set) add(x int) {
	s.values = append(s.values, x)
	s.len += 1
	s.sort()
}

func joinSets(s1, s2 set) set {
	s := set{make([]int, 0), 0}
	s.values = append(s.values, s1.values...)
	s.values = append(s.values, s2.values...)
	s.len = s1.len + s2.len
	s.sort()
	return s
}

func (s *set) sum() int {
	sum := 0
	for _, v := range s.values {
		sum += v
	}
	return sum
}

func dfs_components(v, num int, component []int, g [][]int) {
	component[v] = num
	for _, u := range g[v] {
		if component[u] == 0 {
			dfs_components(u, num, component, g)
		}
	}
}

func dfs(v, col int, color []int, g [][]int) {
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

func remove(slice []set, s int) []set {
	return append(slice[:s], slice[s+1:]...)
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
func Abs(x int) int {
	if x >= 0 {
		return x
	} else {
		return -x
	}
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
func getMinLen(comp []set) int {
	// Component's min len
	if comp[0].len < comp[1].len {
		return comp[0].len
	} else {
		return comp[1].len
	}
}

func getMaxSum(comp []set) int {
	if comp[0].len < comp[1].len {
		return comp[1].sum()
	} else if comp[0].len > comp[1].len {
		return comp[0].sum()
	} else {
		if comp[1].sum() < comp[0].sum() {
			return comp[0].sum()
		} else {
			return comp[1].sum()
		}
	}
}

func getMinSum(comp []set) int {
	if comp[0].len < comp[1].len {
		return comp[0].sum()
	} else if comp[0].len > comp[1].len {
		return comp[1].sum()
	} else {
		if comp[1].sum() > comp[0].sum() {
			return comp[0].sum()
		} else {
			return comp[1].sum()
		}
	}
}

func groupDelta(group_len int, n int) int {
	x := n/2 - group_len
	if x > 0 {
		return x
	} else {
		return -x
	}
}

func countBestDeltaAndJoin(comp1 []set, comp2 []set) ([]set, int) {
	// var comp1Min set
	// var comp1Max set
	// if comp1[0].len > comp1[1].len {
	// 	comp1Min = comp1[1]
	// 	comp1Max = comp1[0]
	// } else if comp1[0].len > comp1[1].len {
	// 	comp1Min = comp1[0]
	// 	comp1Max = comp1[1]
	// } else {
	// 	if comp1[0].sum() < comp1[1].sum() {
	// 		comp1Min = comp1[0]
	// 		comp1Max = comp1[1]
	// 	} else {
	// 		comp1Min = comp1[1]
	// 		comp1Max = comp1[0]
	// 	}
	// }
	// var comp2Min set
	// var comp2Max set
	// if comp2[0].len > comp2[1].len {
	// 	comp2Min = comp2[1]
	// 	comp2Max = comp2[0]
	// } else if comp2[0].len > comp2[1].len {
	// 	comp2Min = comp2[0]
	// 	comp2Max = comp2[1]
	// } else {
	// 	if comp2[0].sum() < comp2[1].sum() {
	// 		comp2Min = comp2[0]
	// 		comp2Max = comp2[1]
	// 	} else {
	// 		comp2Min = comp2[1]
	// 		comp2Max = comp2[0]
	// 	}
	// }
	// comp := make([]set, 2)
	// comp[0], comp[1] = joinSets(comp1Min, comp2Max), joinSets(comp2Min, comp1Max)
	// d := getDelta(comp)
	// d1 := getDelta(comp1)
	// d2 := getDelta(comp2)
	
	// if d <=  || d <= getDelta(comp2) {
	// 	return comp, d
	// }
	// return make([]set, 0), -1
	compComb1 := make([]set, 2)
	ok1 := false
	compComb2 := make([]set, 2)
	ok2 := false
	A1 := comp1[0]
	B1 := comp1[1]
	A2 := comp2[0]
	B2 := comp2[1]

	compComb1[0], compComb1[1] = joinSets(A1, A2), joinSets(B1, B2)
	d1 := getDelta(compComb1)
	comp1d := getDelta(comp1)
	comp2d := getDelta(comp2)
	if d1 <= comp1d || d1 <= comp2d {
		ok1 = true
	}

	compComb2[0], compComb2[1] = joinSets(A1, B2), joinSets(B1, A2)
	d2 := getDelta(compComb2)
	comp1d = getDelta(comp1)
	comp2d = getDelta(comp2)

	if d2 <= comp1d || d2 <= comp2d {
		ok2 = true
	}

	if ok1 && ok2{
		if getMaxSum(compComb1) < getMaxSum(compComb2){
			return compComb2, d1
		} else {
			return compComb1, d2
		}
	} else if ok1{
		return compComb1, d1
	} else if ok2 {
		return compComb2, d2
	} else {
		return make([]set, 0), -1
	}

}

func combineComponents(C11 [][]set, n int) ([][]set, [][]set) {
	// Объединяем, если дельта между множествами уменьшится
	// Возможно алгоритм не идеален, так как в теории при одинаковой разнице между парами у нескольких компонентов могут возникнуть более сложные комбинации
	C12 := make([][]set, 0)
	C13 := make([][]set, 0)
	usedFromC11 := make([]bool, len(C11))

	for i := 0; i < len(C11); i++ {
		if !usedFromC11[i] {
			min_delta_combination := struct {
				comp  []set
				i, j  int
				delta int
				sum   int
			}{[]set{}, n, n, n, n}
			combined := false
			for j := i + 1; j < len(C11); j++ {
				// "Надейся на Господа всем сердцем твоим, и не полагайся на разум твой." (Притчи 3:5)
				if !usedFromC11[j] {
					comp, comp_delta := countBestDeltaAndJoin(C11[i], C11[j])
					fmt.Println("LOOK for", C11[i], C11[j])
					if comp_delta != -1 {
						combined = true
						s := getMaxSum(comp)
						fmt.Println("TRY COMBINE", C11[i], C11[j], min_delta_combination)
						if (comp_delta < min_delta_combination.delta) || (comp_delta == min_delta_combination.delta && s < min_delta_combination.sum) {
							fmt.Println("SET the combination", C11[i], C11[j])
							min_delta_combination.comp = comp
							min_delta_combination.i = i
							min_delta_combination.j = j
							min_delta_combination.delta = comp_delta
							min_delta_combination.sum = s
						}
					}
				}
			}
			if combined {
				fmt.Println("APPEND", min_delta_combination.comp)
				C12 = append(C12, min_delta_combination.comp)
				usedFromC11[min_delta_combination.i] = true
				usedFromC11[min_delta_combination.j] = true
				break
			}
		}
	}
	// Добавляем те, что не получилось объединить
	for index, v := range usedFromC11 {
		if !v {
			C13 = append(C13, C11[index])
		}
	}
	return C12, C13
}
func main() {
	var n int
	var c rune
	fmt.Scanf("%d", &n)

	g := make([][]int, n)

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
	// n := 8
	// g := [][]int{
	//     {2},
	//     {3},
	//     {0, 7},
	//     {1, 5},
	//     {},
	//     {3},
	//     {7},
	//     {2, 6},
	// }

	component := make([]int, n)
	num := 0

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

	C1 := make([][]set, 0)  // Список компонентов, разбитых по группам, по возможности объеденных так, чтобы суммы длин стремились к друг другу
	C11 := make([][]set, 0) // Список компонентов, разбитых по группам с разными длинами

	for _, comp := range C {
		if getDelta(comp) == 0 {
			C1 = append(C1, comp)
		} else {
			C11 = append(C11, comp)
		}
	}
	fmt.Println(C1, "C1 before")
	fmt.Println(C11, "C11 before")
	// sort.Slice(C11, func(i, j int) bool {
	// 	// return getDelta(C11[i]) > getDelta(C11[j])
	// 	d1 := getDelta(C11[i])
	// 	d2 := getDelta(C11[j])

	// 	if d1 == d2 {
	// 		// return getMaxSum(C11[i]) < getMaxSum(C11[j])
	// 		l1 := getMinLen(C11[i])
	// 		l2 := getMinLen(C11[j])
	// 		if l1 == l2 {
	// 			return getMaxSum(C11[i]) > getMaxSum(C11[j])
	// 		} else {
	// 			return l1 > l2
	// 		}

	// 	} else {
	// 		return d1 > d2
	// 	}
	// })
	// sort.Slice(C11, func(i, j int) bool {
	// 	l1 := getMinLen(C11[i])
	// 	l2 := getMinLen(C11[j])
	// 	if l1 == l2 {
	// 		s1 := getMinSum(C11[i])
	// 		s2 := getMinSum(C11[j])
	// 		if s1 == s2 {
	// 			return getDelta(C11[i]) > getDelta(C11[j])			
	// 		} else {
	// 			return s1 < s2
	// 		}
	// 	} else {
	// 		return l1 < l2
	// 	}
	// })
	// fmt.Println(C11, "sorted")

	// C12, C13 := combineComponents(C11, n)
	// fmt.Println(C12, "C12")
	// fmt.Println(C13, "C13")
	// attempt := 0
	// for len(C13) != 0 && attempt <= n {
	// 	C12, C13 = combineComponents(append(C12, C13...), n)
	// 	fmt.Println(C12, "C12 ar")
	// 	fmt.Println(C13, "C13 ar")
	// 	attempt += 1
	// 	fmt.Println(attempt, n)
	// }
	// C1 = append(C1, C12...)
	// C1 = append(C1, C13...)

	fmt.Println(C1, "C1 after")
	Group1 := make([]int, 0)
	Group2 := make([]int, 0)
	// last_v := C1[0]
	for _, v := range C1 {
		fmt.Println("C1 elem: ", v)
		if v[0].len > v[1].len {
			Group1 = append(Group1, v[1].values...)
			Group2 = append(Group2, v[0].values...)
		} else if v[0].len < v[1].len {
			Group1 = append(Group1, v[0].values...)
			Group2 = append(Group2, v[1].values...)
		} else {
			if v[0].sum() > v[1].sum() {
				Group1 = append(Group1, v[1].values...)
				Group2 = append(Group2, v[0].values...)
			} else {
				Group1 = append(Group1, v[0].values...)
				Group2 = append(Group2, v[1].values...)
			}		// if v[0].len < v[1].len || len(Group1) < len(Group2) {
		// 	Group1 = append(Group1, v[0].values...)
		// 	Group2 = append(Group2, v[1].values...)
		// } else if v[0].len > v[1].len || len(Group1) > len(Group2) {
		// 	Group1 = append(Group1, v[1].values...)
		// 	Group2 = append(Group2, v[0].values...)
		// } else {
		// 	fmt.Println("V:", v)
		// 	if v[0].equals(set{make([]int, 0), 0}) {
		// 		fmt.Println("BLANK v0")
		// 		Group1 = append(Group1, v[1].values...)

		// 	} else if v[1].equals(set{make([]int, 0), 0}) {
		// 		fmt.Println("BLANK v1")
		// 		Group1 = append(Group1, v[0].values...)

		// 	} else {
		// 		if setLexicographicallyLess(v[0], v[1]) {
		// 			Group1 = append(Group1, v[0].values...)
		// 			Group2 = append(Group2, v[1].values...)
		// 		} else {
		// 			Group1 = append(Group1, v[1].values...)
		// 			Group2 = append(Group2, v[0].values...)
		// 		}
		// 	}
		// }
		}
	}
	sort.Ints(Group1)
	for _, v := range Group1 {
		fmt.Printf("%d ", v+1)
	}
	fmt.Println("OUT")
	sort.Ints(Group2)
	for _, v := range Group2 {
		fmt.Printf("%d ", v+1)
	}
}
