package main

import (
	"fmt"
)

const __strConst1 = "Hello, World!"
const __strConst2 = "Hello, World"

const (
	str1 = __strConst1
	str2 = __strConst2
)

func main() {
	const str1 = __strConst1
	const str2 = __strConst1
	fmt.Println(str1)        // one str
	fmt.Println(__strConst1) // same str
	fmt.Println(__strConst2) // different str

	if true {
	} else {
	}
}
