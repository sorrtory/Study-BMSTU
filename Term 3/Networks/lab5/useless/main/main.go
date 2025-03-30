package main

import (
	"os"
	"time"
)

var MyIP = "127.0.0.1"
var MyPort = ":4411"
var RSS_Source = "https://news.rambler.ru/rss/Magadan/"

type Info struct {
	Id     int    `json:"id"`
	Header string `json:"header"`
	Text   string `json:"text"`
}

func main() {
	MyIP = os.Getenv("MyIP")

	go startSocket()

	for {
		infos := parseRSS()
		
		sendClear()
		time.Sleep(10 * time.Second)
		getFromEstonia(&infos)
		for _, v := range infos {
			sendToSocket(v)
		}
		
		infos = parseRSS()
		// loadToEstonia(&infos)
		loadToEstonia(&infos)

		time.Sleep(10 * time.Second)
	}
}
