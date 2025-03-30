package main

import (
	"log"
	"strconv"

	"github.com/SlyMarbo/rss"
)

func parseRSS() []Info {
	log.Println("Parse RSS")

	rssObject, err := rss.Fetch(RSS_Source)
	infos := make([]Info, 0)
	if err == nil {
		// s += fmt.Sprintf("<h3>Title:</h3><i>%s\n", rssObject.Title)
		// s += fmt.Sprintf("</i><b>Description:</b> </br><i>%s\n", rssObject.Description)
		// s += fmt.Sprintf("</br></i><b>Number of Items:</b> </br><i>%d\n", len(rssObject.Items))
		// s += "</br>"
		for _, v := range rssObject.Items {
			id, err := strconv.Atoi(v.ID)
			if err != nil {
				log.Println("Error with id")
			} else {
				infos = append(infos, Info{Header: v.Title, Text: v.Summary, Id: id})
			}
		}
	} else {
		log.Println("Error with rss")
	}

	return infos
}
