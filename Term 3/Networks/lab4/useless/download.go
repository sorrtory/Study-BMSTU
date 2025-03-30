package main

import (
	"log"
	"net/http"
	"os"
)


func downloadURL(url string) string{

	// Make the GET request
	resp, err := http.Get(url)

	log.Println("Downloading HTML")
	if err != nil{
		msg := "Cannot download html of " + url
		log.Println(msg)
		log.Println("ERROR: \n	", err)
		return msg
	}
	defer resp.Body.Close()

	os.RemoveAll("site")
	os.Mkdir("site", 0755)

	return parsedHTML(resp.Body, url)
}