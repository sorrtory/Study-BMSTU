package main

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
	"strconv"
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
	N          int `json:"n"`
	StartIndex int `json:"startindex"`
	EndIndex   int `json:"endindex"`
}

type jsonSum struct {
	N          int `json:"n"`
	M          int `json:"m"`
	StartIndex int `json:"startindex"`
}

var MyPort = ":1572"
var MySocketPort = ":1494"
var MyHttpPort = ":1491"
var MySsePort = ":1497"
var MyIP = os.Getenv("MyIP")
var NetworkList = [...]string{"185.104.251.226", "185.102.139.161", "185.102.139.168", "185.102.139.169"}
var MyIndex int
var NeigborIndex int
var ConnectionMode = "Socket"
var MyValue = 1
var RequestedValue int
var SocketCommand string

type WebFormRequestParsed struct {
	command string
	data    interface{}
}

var WebFormRequest WebFormRequestParsed

func sendToWebForm(message string, mode string) {
	switch mode {
	case "Socket":
		dataSocketChannel <- message
	case "SSE":
		dataSseChannel <- message
	}
}

// Run commands from "c" and write response into "out"
func parseFromForm(out *string, c ...string)  {
	var data interface{}

	switch c[0] {
	case "setValue":
		i1, _ := strconv.Atoi(c[1])
		i2, _ := strconv.Atoi(c[2])
		data = &jsonInt{EndIndex: i1, N: i2, StartIndex: MyIndex}
		WebFormRequest.command = c[0]
		WebFormRequest.data = data
		interactWithWebForm(Connection, out)
	case "getSum":
		i1, _ := strconv.Atoi(c[1])
		i2, _ := strconv.Atoi(c[2])
		data = &jsonSum{N: i1, M: i2, StartIndex: MyIndex}
		WebFormRequest.command = c[0]
		WebFormRequest.data = data
		interactWithWebForm(Connection, out)
	case "showValue":
		fmt.Println(MyValue)
		*out = *out + strconv.Itoa(MyValue)
	default:
		fmt.Println("Unknown command from WebForm")
		SocketCommand = ""
		*out = *out + "Bad command!"

	}

}
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

	go startSocketServer()
	time.Sleep(1 * time.Second)
	go startHttpServer()
	time.Sleep(1 * time.Second)
	go startSseServer()
	time.Sleep(1 * time.Second)
	go startServer(MyIP + MyPort)
	time.Sleep(5 * time.Second)
	fmt.Println("Don't forget to reload a page!")
	go startClient(NetworkList[NeigborIndex] + MyPort)
	select {}

}
