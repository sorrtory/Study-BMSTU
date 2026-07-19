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
