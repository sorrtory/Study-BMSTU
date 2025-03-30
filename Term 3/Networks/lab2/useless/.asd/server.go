package main

import (
	"fmt"
	"html/template"
	"net/http"
	"github.com/mgutz/logxi/v1"
)

const INDEX_HTML = `
    <!doctype html>
    <html lang="ru">
        <head>
            <meta charset="utf-8">
            <title>Последние новости с foxnews</title>
        </head>
        <body>
            {{range .}}
				<div class="article">
					<h3 class="title">
						<a href={{ .Link.Ref }}> {{ .Link.Text }} </a>
					</h3>

					
					<div class="pic">
						{{ if eq .Pic.Src "https://static.foxnews.com/static/orion/img/clear-16x9.gif"}}
							<p>
								<i>Картинка не может быть загружена </i> <br>
								{{.Pic.Alt}}
							</p>
						{{ else }}
						 	{{if eq .Pic.Alt "VIDEO"}}
								<video playsinline="" autoplay="" muted="" loop="">
									<source src={{.Pic.Src}} type={{.Pic.W}}>
								</video>
							{{else if eq .Pic.Alt "IFRAME"}}
								<iframe aria-label="MVPD Picker" src={{ .Pic.Src }} border="0" frameborder="0" allow="autoplay" scrolling="no" style="width: 100%; height: 1px; min-height: 100%;" referrerpolicy="no-referrer-when-downgrade" mozallowfullscreen="" webkitallowfullscreen="" allowfullscreen=""></iframe>
							{{else}}
								<img src={{ .Pic.Src }} width={{ .Pic.W }} height={{ .Pic.H }}  alt={{ .Pic.Alt }}>
							{{end}}
						{{ end }}
					</div>
				</div>
				<hr>
			{{end}}
        </body>
    </html>
    `
var indexHtml = template.Must(template.New("index").Parse(INDEX_HTML))

func serveClient(response http.ResponseWriter, request *http.Request) {
	path := request.URL.Path
	log.Info("got request", "Method", request.Method, "Path", path)
	if path != "/" && path != "/index.html" {
		log.Error("invalid path", "Path", path)
		response.WriteHeader(http.StatusNotFound)
	} else if err := indexHtml.Execute(response, downloadNews()); err != nil {
		log.Error("HTML creation failed", "error", err)
	} else {
		log.Info("response sent to client successfully")
	}
}

func main() {
	fmt.Println("export LOGXI=*")
	fmt.Println("export LOGXI_FORMAT=pretty,happy")
	http.HandleFunc("/", serveClient)
	log.Info("starting listener")
	log.Error("listener failed", "error", http.ListenAndServe("127.0.0.1:6060", nil))

}
