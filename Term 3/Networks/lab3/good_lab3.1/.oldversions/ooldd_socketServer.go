package main

import (
	"fmt"
	"net/http"
	"strconv"
	"github.com/gorilla/websocket"
)

var wsUpgrader = websocket.Upgrader{}
func handleSocket(w http.ResponseWriter, r *http.Request) {
	wsUpgrader.CheckOrigin = func(r *http.Request) bool { return true }

	conn, err := wsUpgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer conn.Close()
	cnt := 0
	// Read messages from the client.
	for {
		// Read a message from the client.
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			fmt.Println(err)
			return
		}
		// Print the message to the console.
		fmt.Println("Received:", string(message))
		// Send a message back to the client.
		// output := strings.Split(string(message), " ")
		err = conn.WriteMessage(messageType, []byte("Hello, client!" + strconv.Itoa(cnt)))
		if err != nil {
			fmt.Println(err)
			return
		}
		cnt += 1

	}
}


func startSocketServer() {

	// Listen for WebSocket connections on port 8080.
	go http.HandleFunc("/", handleSocket)

	// Start the server.
	go http.ListenAndServe(MyIP + MySocketPort, nil)

}