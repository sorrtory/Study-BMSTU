package main

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

type Request struct {
	Command string `json:"command"`

	Data *json.RawMessage `json:"data"`
}

type Response struct {
	Status string `json:"status"`

	Data *json.RawMessage `json:"data"`
}

type jsonInt struct {
	N int `json:"n"`
	StartIndex int `json:"startindex"`
	EndIndex int `json:"endindex"`
}

type jsonSum struct {
	N int `json:"n"`
	M int `json:"m"`
	StartIndex int `json:"startindex"`
}

var MyPort = ":1572"
var MyIP = os.Getenv("MyIP")
var NetworkList = [...]string{"185.104.251.226", "185.102.139.161", "185.102.139.168", "185.102.139.169"}
var MyIndex int
var NeigborIndex int

var MyValue = 1
var RequestedValue int

func main() {
	// Set IP
	for i, v := range NetworkList {
		if MyIP == v {
			MyIndex = i
			NeigborIndex = (i + 1) % len(NetworkList)
			break
		}
	}

	fmt.Println("MyIP:", NetworkList[MyIndex])
	fmt.Println("NeigborIP:", NetworkList[NeigborIndex])
	fmt.Println("Port:", MyPort)

	// // Работа с командной строкой, в которой может указываться необязательный ключ -addr.
	// var addrStr string
	// flag.StringVar(&addrStr, "addr", MyIP+MyPort, "specify ip address and port")
	// flag.Parse()
	
	go startServer(MyIP+MyPort)
	time.Sleep(5 * time.Second) 
	go startClient(NetworkList[NeigborIndex]+MyPort)

	select {}

}
