package main

// #include <stdlib.h>
// #include "input.h"
//
// #cgo CFLAGS: -O3 -Wno-error=format-security -Wno-format-nonliteral -Wno-format-extra-args -Wno-format-security
//
import "C"

import "unsafe"

func Scanf(format string, a ...interface{}) (n int) {
	var buf []byte
	i, arg := 0, 0
	for {
		for ; i < len(format) && format[i] != '%'; i++ {
			buf = append(buf, format[i])
		}

		if i == len(format) {
			if len(buf) > 0 {
				fmt := C.CString(string(buf))
				n += int(C.scanverbatim(fmt))
				C.free(unsafe.Pointer(fmt))
			}
			break
		}

		buf = append(buf, '%')
		if i++; i == len(format) {
			panic("input.Scanf: format string ends with '%'")
		} else if format[i] == '%' {
			buf = append(buf, '%')
		} else {
			spec := format[i]
			if arg == len(a) {
				panic("input.Scanf: the number of format specifiers exeeds the number of arguments")
			}

			if a[arg] == nil {
				panic("input.Scanf: nil pointer passed as argument")
			}

			if spec == 'd' {
				switch p := a[arg].(type) {
				case *uint: {
					buf = append(buf, ([]byte)("llu")...)
					fmt := C.CString(string(buf))
					var res C.ulonglong
					n += int(C.scanuint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = uint(res)
				}
				case *uint8: {
					buf = append(buf, 'l', 'l' ,'u')
					fmt := C.CString(string(buf))
					var res C.ulonglong
					n += int(C.scanuint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = uint8(res)
				}
				case *uint16: {
					buf = append(buf, 'l', 'l' ,'u')
					fmt := C.CString(string(buf))
					var res C.ulonglong
					n += int(C.scanuint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = uint16(res)
				}
				case *uint32: {
					buf = append(buf, 'l', 'l' ,'u')
					fmt := C.CString(string(buf))
					var res C.ulonglong
					n += int(C.scanuint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = uint32(res)
				}
				case *uint64: {
					buf = append(buf, 'l', 'l' ,'u')
					fmt := C.CString(string(buf))
					var res C.ulonglong
					n += int(C.scanuint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = uint64(res)
				}
				case *int: {
					buf = append(buf, 'l', 'l' ,'d')
					fmt := C.CString(string(buf))
					var res C.longlong
					n += int(C.scanint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = int(res)
				}
				case *int8: {
					buf = append(buf, 'l', 'l' ,'d')
					fmt := C.CString(string(buf))
					var res C.longlong
					n += int(C.scanint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = int8(res)
				}
				case *int16: {
					buf = append(buf, 'l', 'l' ,'d')
					fmt := C.CString(string(buf))
					var res C.longlong
					n += int(C.scanint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = int16(res)
				}
				case *int32: {
					buf = append(buf, 'l', 'l' ,'d')
					fmt := C.CString(string(buf))
					var res C.longlong
					n += int(C.scanint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = int32(res)
				}
				case *int64: {
					buf = append(buf, 'l', 'l' ,'d')
					fmt := C.CString(string(buf))
					var res C.longlong
					n += int(C.scanint(fmt, &res))
					C.free(unsafe.Pointer(fmt))
					*p = int64(res)
				}
				default:
					panic("input.Scanf: argument must be pointer to some integer variable")
				}

				buf = buf[:0]
			} else if spec == 'c' {
				buf = append(buf, 'l', 'c')
				fmt := C.CString(string(buf))
				var res C.wchar_t
				n += int(C.scanchar(fmt, &res))
				C.free(unsafe.Pointer(fmt))

				switch p := a[arg].(type) {
				case *uint: *p = uint(res)
				case *uint8: *p = uint8(res)
				case *uint16: *p = uint16(res)
				case *uint32: *p = uint32(res)
				case *uint64: *p = uint64(res)
				case *int: *p = int(res)
				case *int8: *p = int8(res)
				case *int16: *p = int16(res)
				case *int32: *p = int32(res)
				case *int64: *p = int64(res)
				default:
					panic("input.Scanf: argument must be pointer to some integer variable")
				}

				buf = buf[:0]
			} else if spec == 'f' {
				buf = append(buf, 'l', 'f')
				fmt := C.CString(string(buf))
				var res C.double
				n += int(C.scandouble(fmt, &res))
				C.free(unsafe.Pointer(fmt))
				
				switch p := a[arg].(type) {
				case *float32: *p = float32(res)
				case *float64: *p = float64(res)
				default:
					panic("input.Scanf: argument must be pointer to some floating-point variable")
				}

				buf = buf[:0]
			} else if spec == 's' {
				buf = append(buf, 'm', 's')
				fmt := C.CString(string(buf))
				buf = buf[:0]
				var res *C.char
				count := int(C.scanstring(fmt, &res))
				C.free(unsafe.Pointer(fmt))

				if count == 1 {
					n++
					if p, ok := a[arg].(*string); ok {
						*p = C.GoString(res)
						C.free(unsafe.Pointer(res))
					} else {
						panic("input.Scanf: argument must be pointer to string variable")
					}
				}
			} else {
				panic("input.Scanf: only '%d', '%c' and 's' format specifiers allowed")
			}

			arg++
		}
		i++
	}

	return
}

func Gets() (s string) {
	cs := C.getstring()
	if cs == nil {
		panic("input.Gets: I/O error or out of memory")
	}

	s = C.GoString(cs)
	C.free(unsafe.Pointer(cs))
	return
}

func main() {
	var m int
	input.Scanf("%d ", &m)
	X := make([]string, m)
	s := input.Gets()
	words := strings.Fields(s)
	for i := 0; i < m; i++ {
		X[i] = words[i]
	}

	var k int
	input.Scanf("%d ", &k)
	Y := make([]string, k)
	s = input.Gets()
	words = strings.Fields(s)
	for i := 0; i < k; i++ {
		Y[i] = words[i]
	}

	var n int
	input.Scanf("%d ", &n)

	delta := make([][]int, n)
	for i := 0; i < n; i++ {
		delta[i] = make([]int, m)
		for j := 0; j < m; j++ {
			input.Scanf("%d ", &delta[i][j])
		}
	}

	phi := make([][]string, n)
	for i := 0; i < n; i++ {
		phi[i] = make([]string, m)
		s := input.Gets()
		words := strings.Fields(s)
		for j := 0; j < m; j++ {
			phi[i][j] = words[j]
		}
	}

	count := 0
	r := make([]*R, 0)
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			targetK := delta[i][j]
			targetY := phi[i][j]
			k, c := find(r, targetK, targetY)
			if !c {
				k = &R{y : targetY, c : count, i : targetK}
				r = append(r, k)
				count++
			}
		}
	}
	n2 := len(r)

	psi := make([]string, n2)
	delta2 := make([][]*R, n2)
	for i := 0; i < n2; i++ {
		psi[i] = r[i].y
		delta2[i] = make([]*R, m)
	}

	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			number := delta[i][j]
			name := phi[i][j]
			target, _ := find(r, number, name)
			parents := findbyi(r, i)
			for _, p := range parents {
				delta2[p.c][j] = target
			}
		}
	}

	fmt.Printf("digraph {\nrankdir = LR\n")
	for i := 0; i < n2; i++ {
		fmt.Printf("%d [label = \"(%d,%s)\"]\n", i, r[i].i, r[i].y)
		for j := 0; j < m; j++ {
			fmt.Printf("%d -> %d [label = \"%s\"]\n", r[i].c, delta2[i][j].c, X[j])
		}
	}
	fmt.Printf("}\n")
}

func findbyi(r []*R, k int) []*R {
	result := make([]*R, 0)
	for i := 0; i < len(r); i++ {
		if r[i].i == k {
			result = append(result, r[i])
		}
	}
	return result
}

func find(r []*R, k int, y string) (*R, bool) {
	for i := 0; i < len(r); i++ {
		if r[i].y == y && r[i].i == k {
			return r[i], true
		}
	}
	return nil, false
}

type Mealy struct {
	X []int
	Y []string
	Q []*Q
	delta [][]int
	phi [][]string
}

type Moore struct {
	X []int
	Y []string
	R []*R
	delta [][]int
	psi [][]int
}

type Q struct {
	i int
}

type R struct {
	y string
	i, c int
}