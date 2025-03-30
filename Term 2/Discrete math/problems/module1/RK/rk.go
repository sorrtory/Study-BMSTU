package main

import "fmt"

func MergeSort(items int, compare func(i, j int) int, indices chan int) {
	defer close(indices)
	tempChan := make(chan int, items)
	go mergeSortHelper(0, items, compare, tempChan)
	for val := range tempChan {
		indices <- val
	}
}

func mergeSortHelper(start, end int, compare func(i, j int) int, output chan int) {
	if end-start <= 1 {
		if start < end {
			output <- start
		}
		close(output)
		return
	}

	mid := (start + end) / 2

	leftChan := make(chan int, mid-start)
	rightChan := make(chan int, end-mid)
	
	go mergeSortHelper(start, mid, compare, leftChan)
	go mergeSortHelper(mid, end, compare, rightChan)

	merge(leftChan, rightChan, compare, output)
}

func merge(left, right chan int, compare func(i, j int) int, output chan int) {
	defer close(output)
	
	leftVal, leftOpen := <-left
	rightVal, rightOpen := <-right

	for leftOpen || rightOpen {
		if !leftOpen {
			output <- rightVal
			rightVal, rightOpen = <-right
		} else if !rightOpen {
			output <- leftVal
			leftVal, leftOpen = <-left
		} else {
			if compare(leftVal, rightVal) <= 0 {
				output <- leftVal
				leftVal, leftOpen = <-left
			} else {
				output <- rightVal
				rightVal, rightOpen = <-right
			}
		}
	}
}

func main() {
	fmt.Print()
}
package main

import "fmt"

func MergeSort(items int, compare func(i, j int) int, indices chan int) {
	defer close(indices)
	tempChan := make(chan int, items)
	go mergeSortHelper(0, items, compare, tempChan)
	for val := range tempChan {
		indices <- val
	}
}

func mergeSortHelper(start, end int, compare func(i, j int) int, output chan int) {
	if end-start <= 1 {
		if start < end {
			output <- start
		}
		close(output)
		return
	}

	mid := (start + end) / 2

	leftChan := make(chan int, mid-start)
	rightChan := make(chan int, end-mid)
	
	go mergeSortHelper(start, mid, compare, leftChan)
	go mergeSortHelper(mid, end, compare, rightChan)

	merge(leftChan, rightChan, compare, output)
}

func merge(left, right chan int, compare func(i, j int) int, output chan int) {
	defer close(output)
	
	leftVal, leftOpen := <-left
	rightVal, rightOpen := <-right

	for leftOpen || rightOpen {
		if !leftOpen {
			output <- rightVal
			rightVal, rightOpen = <-right
		} else if !rightOpen {
			output <- leftVal
			leftVal, leftOpen = <-left
		} else {
			if compare(leftVal, rightVal) <= 0 {
				output <- leftVal
				leftVal, leftOpen = <-left
			} else {
				output <- rightVal
				rightVal, rightOpen = <-right
			}
		}
	}
}

func main() {
	fmt.Print()
}
