% Лабораторная работа № 2.1. Синтаксические деревья
% 2 марта 2026 г.
% Александр Федуков, ИУ9-62Б

# Цель работы

Целью данной работы является изучение представления синтаксических деревьев в памяти компилятора и
приобретение навыков преобразования синтаксических деревьев.

# Индивидуальный вариант

Каждое вхождение строкового литерала в текст программы должно быть заменено идентификатором константы,
добавленной в начало программы и имеющей соответствующее значение (при этом значения добавляемых констант не
должны дублироваться).

# Реализация

Демонстрационная программа:

```go
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
```

Программа, осуществляющая преобразование синтаксического дерева:

```go
package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"io"
	"os"
	"path/filepath"
)

const (
	// Solution to my task
	SOLUTION_FILE_BEFORE = "../assets/00_solution/before.go"
	SOLUTION_FILE_AFTER  = "../assets/01_solution/after.go"

	// Demo
	DEMO_FILE_BEFORE = "../assets/00_demo/before.go"
	DEMO_FILE_AFTER  = "../assets/01_demo/after.go"

	// For printing AST
	FILE_PRINT = "../assets/ast.txt"
)

func process(file_from, file_to string, function func(io.Writer, *token.FileSet, *ast.File)) {
	file_from, err := filepath.Abs(file_from)
	if err != nil {
		fmt.Printf("cannot find file: %v", err)
		return
	}
	file_to, err = filepath.Abs(file_to)
	if err != nil {
		fmt.Printf("cannot find file: %v", err)
		return
	}

	// Создаём хранилище данных об исходных файлах
	fset := token.NewFileSet()

	// Вызываем парсер
	if file, err := parser.ParseFile(
		fset,                 // данные об исходниках
		file_from,            // имя файла с исходником программы
		nil,                  // пусть парсер сам загрузит исходник
		parser.ParseComments, // приказываем сохранять комментарии
	); err == nil {
		// Если парсер отработал без ошибок, вызываем переданную функцию
		to, err := os.Create(file_to)
		if err != nil {
			fmt.Printf("cannot create file: %v", err)
			return
		}
		defer to.Close()
		function(to, fset, file)
	} else {
		// в противном случае, выводим сообщение об ошибке
		fmt.Printf("Error: %v", err)
	}
}

func insertStrConst(file *ast.File) {
	strs := make(map[string]string) // original string -> const name

	// Collect all string literals in the file
	ast.Inspect(file, func(node ast.Node) bool {
		// skip import declarations
		if genDcl, ok := node.(*ast.GenDecl); ok {
			if genDcl.Tok == token.IMPORT {
				return false
			}
		}

		// For each node in the AST, check if it's a basic literal
		if basicLit, ok := node.(*ast.BasicLit); ok {
			if basicLit.Kind == token.STRING {
				if _, exists := strs[basicLit.Value]; !exists {
					strs[basicLit.Value] = fmt.Sprintf("__strConst%d", len(strs)+1)
				}
			}
		}
		return true
	})

	// Replace string literals with const identifiers
	ast.Inspect(file, func(node ast.Node) bool {
		// skip import declarations
		if genDcl, ok := node.(*ast.GenDecl); ok {
			if genDcl.Tok == token.IMPORT {
				return false
			}
		}

		if basicLit, ok := node.(*ast.BasicLit); ok {
			if basicLit.Kind == token.STRING {
				if constName, exists := strs[basicLit.Value]; exists {
					*basicLit = ast.BasicLit{
						Kind:  token.IDENT,
						Value: constName,
					}
				}
			}
		}
		return true
	})

	// Declare new consts for each unique string literal
	var before, after []ast.Decl

	if len(file.Decls) > 0 {
		hasImport := false
		if genDecl, ok := file.Decls[0].(*ast.GenDecl); ok {
			hasImport = genDecl.Tok == token.IMPORT
		}

		if hasImport {
			before, after = []ast.Decl{file.Decls[0]}, file.Decls[1:]
		} else {
			after = file.Decls
		}
	}

	file.Decls = before
	for str, constName := range strs {
		file.Decls = append(file.Decls,
			&ast.GenDecl{
				Tok: token.CONST,
				Specs: []ast.Spec{
					&ast.ValueSpec{
						Names: []*ast.Ident{ast.NewIdent(constName)},
						Values: []ast.Expr{
							&ast.BasicLit{
								Kind:  token.STRING,
								Value: str,
							},
						},
					},
				},
			},
		)
	}
	file.Decls = append(file.Decls, after...)

	fmt.Println("Replaces:")
	for str, constName := range strs {
		fmt.Printf("%s -> %s\n", str, constName)
	}
}

func main() {
	// Run demo
	process(
		DEMO_FILE_BEFORE,
		DEMO_FILE_AFTER,
		func(w io.Writer, fset *token.FileSet, file *ast.File) {
			// insertHello(file)
			// insertIntVar(file, "xxx", 666)
			insertStrConst(file)
			err := format.Node(w, fset, file)
			if err != nil {
				fmt.Printf("Error formatting file: %v", err)
			}
		})

	fmt.Println()
	// Run solution
	process(
		SOLUTION_FILE_BEFORE,
		SOLUTION_FILE_AFTER,
		func(w io.Writer, fset *token.FileSet, file *ast.File) {
			// insertHello(file)
			// insertIntVar(file, "xxx", 666)
			insertStrConst(file)
			err := format.Node(w, fset, file)
			if err != nil {
				fmt.Printf("Error formatting file: %v", err)
			}
		})

	// Print AST of the solution file
	process(
		SOLUTION_FILE_BEFORE,
		FILE_PRINT,
		func(w io.Writer, fset *token.FileSet, file *ast.File) {
			err := ast.Fprint(w, fset, file, nil)
			if err != nil {
				fmt.Printf("Error printing AST: %v", err)
			}
		})

}
```

# Тестирование

Результат трансформации демонстрационной программы:

```go
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
```

# Вывод

Я реализовал программу, которая преобразует синтаксическое дерево программы на языке Go, заменяя все строковые
литералы на константы. Я использовал пакет `go/ast` и `go/parser` для обхода синтаксического дерева и парсинга
исходного кода и `go/format` и `go/token` для создание результирующего кода. Я протестировал код на
демонстрационной программе, которая содержит несколько строковых литералов, и убедился, что все литералы были
заменены на константы, при этом одинаковые литералы были заменены на одну и ту же константу.
