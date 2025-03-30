package main

import (
	"fmt"
	"net/http"
	"github.com/SlyMarbo/rss"
)

func GetRSS() string {
	rssObject, err := rss.Fetch("https://ldpr.ru/rss")
	s := ""
	s += `
	<html lang="en">
  <head>
    <title>My Website</title>
  </head>
  <body>
    <main>
        `
	if err == nil {
		s += fmt.Sprintf("<h3>Title:</h3><i>%s\n", rssObject.Title)
		s += fmt.Sprintf("</i><b>Description:</b> </br><i>%s\n", rssObject.Description)
		s += fmt.Sprintf("</br></i><b>Number of Items:</b> </br><i>%d\n", len(rssObject.Items))
		s += "</br>"

		for v := range rssObject.Items {
			item := rssObject.Items[v]
			s += fmt.Sprintf("</br></i><b>Item Number:</b> <i>%d\n", v)
			s += fmt.Sprintf("</br></i><b>Title:</b> </br><i>%s\n", item.Title)
			s += fmt.Sprintf("</br></i><b>Link:</b></br> <i>%s\n", item.Link)
			s += fmt.Sprintf("</br></i><b>Summary:</b> </br><i>%s\n", item.Summary)
			s += "</br>"

		}
	} else {
		s = "RSS ERROR"
	}
	s += `</i>
    </main>
	<script src="index.js"></script>
  </body>
</html>`
	return s

}
func hello(w http.ResponseWriter, req *http.Request) {

	fmt.Fprintf(w, GetRSS())

}

func main() {
	http.HandleFunc("/news", hello)

	http.ListenAndServe(":1221", nil)

}
