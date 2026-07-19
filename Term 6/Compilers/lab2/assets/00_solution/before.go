package main

import (
	"fmt"
)

const (
	str1 = "Hello, World!"
	str2 = "Hello, World"
)

func main() {
	const str1 = "Hello, World!"
	const str2 = "Hello, World!"
	fmt.Println(str1) 			 // one str
	fmt.Println("Hello, World!") // same str
	fmt.Println("Hello, World")  // different str

	if true {
	} else {
	}
}
