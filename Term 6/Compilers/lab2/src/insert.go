package main

import (
	"fmt"
	"go/ast"
	"go/token"
)

func insertHello(file *ast.File) {
	// Вызываем обход дерева, начиная от корня
	ast.Inspect(file, func(node ast.Node) bool {
		// Для каждого узла дерева
		if ifStmt, ok := node.(*ast.IfStmt); ok {
			// Если этот узел имеет тип *ast.IfStmt,
			// добавляем в начало массива операторов
			// положительной ветки if'a новый оператор
			ifStmt.Body.List = append(
				[]ast.Stmt{
					// Новый оператор — выражение
					&ast.ExprStmt{
						// Выражение — вызов функции
						X: &ast.CallExpr{
							// Функция — "fmt.Printf"
							Fun: &ast.SelectorExpr{
								X:   ast.NewIdent("fmt"),
								Sel: ast.NewIdent("Printf"),
							},
							// Её параметр — строка "hello"
							Args: []ast.Expr{
								&ast.BasicLit{
									Kind:  token.STRING,
									Value: "\"hello\"",
								},
							},
						},
					},
				},
				ifStmt.Body.List...,
			)
		}
		// Возвращая true, мы разрешаем выполнять обход
		// дочерних узлов
		return true
	})
}

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
					Type:  ast.NewIdent("int"),
					Values: []ast.Expr{
						&ast.BasicLit{
							Kind:  token.INT,
							Value: fmt.Sprintf("%d", value),
						},
					},
				},
			},
		},
	)
	file.Decls = append(file.Decls, after...)
}
