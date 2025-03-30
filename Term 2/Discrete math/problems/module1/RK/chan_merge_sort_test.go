package main

import (
	"math"
	"testing"
)

var items = []float64{
	  915,
}

func TestMergeSort(t *testing.T) {
	indices := make(chan int)
	go MergeSort(len(items),
		func(i, j int) int {
			return int(math.Abs(items[i]) - math.Abs(items[j]))
		},
		indices)

	var index int
	var ok bool
	index, ok = <-indices
	if !ok {
		t.Error("Канал не должен быть пустым")
	}
	if index != 0 {
		t.Errorf("Неожиданный индекс %d, ожидался 0", index)
	}

	index, ok = <-indices
	if ok {
		t.Error("Канал должен быть пустым")
	}
}

func main() {
	TestMergeSort(&testing.T{});
}