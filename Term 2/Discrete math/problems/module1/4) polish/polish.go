package main

import (
	"bufio"
	"fmt"
	"os"
)

type Stack []rune

// IsEmpty: check if stack is empty
func (s *Stack) IsEmpty() bool {
	return len(*s) == 0
}

// Push a new value onto the stack
func (s *Stack) Push(str rune) {
	*s = append(*s, str) // Simply append the new value to the end of the stack
}

// Remove and return top element of stack. Return false if stack is empty.
func (s *Stack) Pop() rune {
	if s.IsEmpty() {
		return '0'
	} else {
		index := len(*s) - 1   // Get the index of the top most element.
		element := (*s)[index] // Index into the slice and obtain the element.
		*s = (*s)[:index]      // Remove it from the stack by slicing it off.
		return element
	}
}

func operate(operator rune, operand1, operand2 rune) rune {
	intOperand1 := int(operand1) - '0'
	intOperand2 := int(operand2) - '0'
	var result int
	switch operator {
	case '+':
		result = intOperand1 + intOperand2
	case '-':
		result = intOperand1 - intOperand2
	case '*':
		result = intOperand1 * intOperand2
	}
	return rune(result + '0')
}

func calcPrefixExpr(s string) int {
	var stack Stack

	for _, char := range s {
		switch char {
		case ')':
			operand2 := stack.Pop()
			operand1 := stack.Pop()
			operator := stack.Pop()
			stack.Push(operate(operator, operand1, operand2))
		case '(', ' ', '\n':

		default:
			stack.Push(char)
		}
	}

	return int(stack.Pop()) - '0'
}

func main() {
	var s string
	// s = "(* 5 (+ 3 4))"

	in := bufio.NewReader(os.Stdin)
	s, _ = in.ReadString('\n')

	fmt.Println(calcPrefixExpr(s))

}
