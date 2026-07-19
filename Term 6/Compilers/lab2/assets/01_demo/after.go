package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	//"go/printer"
	"go/token"
	"os"
)

const __strConst1 = "int"
const __strConst2 = "%d"
const __strConst3 = "fmt"
const __strConst4 = "Printf"
const __strConst5 = "\"hello\""
const __strConst6 = "xxx"
const __strConst7 = "Formatter error: %v\n"
const __strConst8 = "Errors in %s\n"

func insertIntVar(file *ast.File, name string, value int) {
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

	file.Decls = append(before,
		&ast.GenDecl{
			Tok: token.VAR,
			Specs: []ast.Spec{
				&ast.ValueSpec{
					Names: []*ast.Ident{ast.NewIdent(name)},
					Type:  ast.NewIdent(__strConst1),
					Values: []ast.Expr{
						&ast.BasicLit{
							Kind:  token.INT,
							Value: fmt.Sprintf(__strConst2, value),
						},
					},
				},
			},
		},
	)
	file.Decls = append(file.Decls, after...)
}

func insertHello(file *ast.File) {
	ast.Inspect(file, func(node ast.Node) bool {
		if ifStmt, ok := node.(*ast.IfStmt); ok {
			ifStmt.Body.List = append(
				[]ast.Stmt{
					&ast.ExprStmt{
						X: &ast.CallExpr{
							Fun: &ast.SelectorExpr{
								X:   ast.NewIdent(__strConst3),
								Sel: ast.NewIdent(__strConst4),
							},
							Args: []ast.Expr{
								&ast.BasicLit{
									Kind:  token.STRING,
									Value: __strConst5,
								},
							},
						},
					},
				},
				ifStmt.Body.List...,
			)
		}
		return true
	})
}

func main() {
	if len(os.Args) != 2 {
		return
	}

	fset := token.NewFileSet()
	if file, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments); err == nil {
		insertIntVar(file, __strConst6, 666)
		insertHello(file)

		if format.Node(os.Stdout, fset, file) != nil {
			fmt.Printf(__strConst7, err)
		}
		//ast.Fprint(os.Stdout, fset, file, nil)
	} else {
		fmt.Printf(__strConst8, os.Args[1])
	}
}
