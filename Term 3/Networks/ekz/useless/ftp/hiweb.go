package main

import (
	"fmt"
	"net/http"
	"text/template"
)

type ViewData struct{
 OUT string
}

func greet(w http.ResponseWriter, r *http.Request) {
	// homeTemplate.Execute(w, "ws://"+r.Host+"/echo")
	// go func() {
	// 	time.Sleep(time.Second * 1)
	// 	fmt.Fprintf(w, "Hello World! %s\nResult: %v", time.Now(), A+B)
		
	// }()
	data := fmt.Sprint(C)
	tmpl, _ := template.New("data").Parse(`
		<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="2">
<body>
{{.}}
</body>
</html>
	`)
	tmpl.Execute(w, data)
	fmt.Println(C)
}

// var homeTemplate = template.Must(template.New("").Parse(`
// <!DOCTYPE html>
// <html>
// <head>
// <meta charset="utf-8">
// <body>
// {{.}}
// </body>
// </html>
// `))
