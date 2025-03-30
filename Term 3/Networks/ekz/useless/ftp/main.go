package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
)

var ftpCommandChan chan string
var wsMessageChan chan Message

var ftpCurrentDir = "/"
var ftpServer string   // students.yss.su:21
var ftpLogin string    // ftpiu8
var ftpPassword string // 3Ru7yOTA

var myIP = "localhost"
var wsPort = ":1429"

type Msg struct {
	A string `json:"a"`
	B string `json:"b"`
}

func test(rw http.ResponseWriter, req *http.Request) {
	rw.Header().Set("Access-Control-Allow-Origin", "*")
	rw.Header().Set("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
	rw.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	// rw.Header().Set("Content-Type", "application/json")
	rw.Header().Set("Content-Type", "application/json")
	// rw.Header().Set("Access-Control-Allow-Origin", "*")
	// rw.Header().Set("Access-Control-Allow-Origin", "*") // Allow all origins
	// rw.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
	// rw.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	fmt.Println(123, req.Body)
	decoder := json.NewDecoder(req.Body)
	var t Msg
	decoder.Decode(&t)
	// _ := decoder.Decode(&t)
	// if err != nil {
	// panic(err)
	// }
	A, _ = strconv.Atoi(t.A)
	B, _ = strconv.Atoi(t.B)
	C = A+B

}
var C int
func main() {
	// myIP = getip2()
	// go startSocket()
	http.HandleFunc("/post", test)

	http.HandleFunc("/result", greet)
	// homeTemplate.Execute(w, "ws://"+r.Host+"/echo")

	http.ListenAndServe("localhost:8081", nil)
	// ftpServer = "students.yss.su:21"
	// ftpLogin = "ftpiu8"
	// ftpPassword = "3Ru7yOTA"
	// client, err := connectFTP()
	// fmt.Println(err)
	// go runFTP(client)
	// ftpCommandChan <- "ls"
	select {}
}
