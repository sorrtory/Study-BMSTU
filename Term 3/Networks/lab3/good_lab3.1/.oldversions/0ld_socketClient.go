package main

import (
	"fmt"
	"net/url"
	"strconv"
	"time"

	"github.com/gorilla/websocket"
)

var counter int

func main() {
	sendToWebForm(strconv.Itoa(counter))
	counter += 1
	time.Sleep(3 * time.Second)
	main()
}

func sendToWebForm(data string) {
	// Create a new WebSocket connection.
	u := url.URL{
		Scheme: "ws",
		Host:   "185.102.139.169:1593",
		Path:   "/ws",
	}
	dialer := websocket.Dialer{}
	conn, _, err := dialer.Dial(u.String(), nil)
	if err != nil {
		fmt.Println(err)
		return
	}

	MyIndex := 3
	// Send a message to the server.
	wrStr := strconv.Itoa(MyIndex) + " " + data
	// wrStr := "ABOBA"
	fmt.Println("Sended:", wrStr)
	err = conn.WriteMessage(websocket.TextMessage, []byte(wrStr))
	if err != nil {
		fmt.Println(err)
		return
	}

	// Read a message from the server.
	_, message, err := conn.ReadMessage()
	if err != nil {
		fmt.Println(err)
		return
	}

	// Print the message from the server.
	fmt.Println("Received:", string(message))
}
