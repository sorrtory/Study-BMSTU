package main

import (
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}
var dataSocketChannel = make(chan string)

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	// Upgrade HTTP to WebSocket
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade error:", err)
		return
	}
	defer conn.Close()

	// Waiting for socket reques
	go func() {
		for {
			// Read a message from the client.
			_, message, err := conn.ReadMessage()
			if err != nil {
				fmt.Println(err)
				return
			}
			// Print the message to the console.
			fmt.Println("Received command:", string(message))
			SocketCommand = string(message)
			c := strings.Split(SocketCommand, " ")

			out := "Socket: "
			parseFromForm(&out, c...)
			conn.WriteMessage(websocket.TextMessage, []byte(out))
		}
	}()
	
	
	// Waiting for dataSocketChannel to send to WebForm
	for message := range dataSocketChannel {
		// Send message to client
		err := conn.WriteMessage(websocket.TextMessage, []byte(message))
		if err != nil {
			log.Println("Write error:", err)
			return
		}
	}

}

func startSocketServer() {
	http.HandleFunc("/", handleWebSocket)
	fmt.Println("Socket server listening on", MySocketPort)
	err := http.ListenAndServe(MyIP+MySocketPort, nil)
	if err != nil {
		log.Fatal("ListenAndServe:", err)
	}
}


