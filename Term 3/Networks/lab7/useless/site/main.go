package main

import (
	"log"
	"net/http"
)

func main() {
	// Serve static files (CSS, JS, images)
	fs := http.FileServer(http.Dir("./static"))
	http.Handle("/static/", http.StripPrefix("/static/", fs))

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Requested URL: %s", r.URL.Path)
		
		http.ServeFile(w, r, "./static/index.html")
	})
	
	// http.HandleFunc("/work", func(w http.ResponseWriter, r *http.Request) {
	// 	log.Printf("Requested URL: %s", r.URL.Path)
	// 	http.ServeFile(w, r, "./static/console.html")
	// })
	log.Println("JS client started on localhost:1932")
	log.Fatal(http.ListenAndServe(":1932", nil))
}
