package main

import (
	"fmt"
	"log"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	// Get full address of request
	scheme := "http"
	if r.TLS != nil {
		scheme = "https"
	}
	fullAddress := fmt.Sprintf("%s://%s%s", scheme, r.Host, r.RequestURI)
	log.Println("Handle link:", fullAddress)

	// Have to have url query parameter
	url := r.URL.Query().Get("url")
	if url == "" {
		http.Error(w, fmt.Sprintf("Wrong adress: %s. \nRewrite it like example: http://%s?url=%s", r.URL, SERVER, "http://gnuplot.info/"), http.StatusBadRequest)
	} else {
		w.Header().Set("Content-Type", "text/html")
		html := downloadURL(url)
		fmt.Fprint(w, html)
	}
	fmt.Println()
}

func startServer() {
	http.HandleFunc("/", handler)
	http.Handle("/site/", http.StripPrefix("/site/", http.FileServer(http.Dir("./site"))))
	log.Println("Server started: http://" + SERVER + "?url=")
	log.Fatal(http.ListenAndServe(SERVER, nil))
}
