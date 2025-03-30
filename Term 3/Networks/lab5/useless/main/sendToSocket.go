package main

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

// Global variables to hold connected clients and mutex to avoid race conditions
var clients = make(map[*websocket.Conn]bool)
var mu sync.Mutex

// Upgrader to upgrade HTTP connections to WebSocket connections
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all connections
	},
}

// Function to handle incoming WebSocket connections
func handleConnection(w http.ResponseWriter, r *http.Request) {
	// Upgrade the HTTP connection to a WebSocket connection
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Error upgrading connection:", err)
		return
	}
	defer conn.Close()

	// Add the new connection to the clients map
	mu.Lock()
	clients[conn] = true
	mu.Unlock()
	log.Println("New client connected")

	// Listen for messages from this client
	for {
		_, _, err := conn.NextReader() // Keep the connection open to listen for messages
		if err != nil {
			log.Println("Client disconnected:", err)
			break
		}
	}
}

func sendToClientInfo(conn *websocket.Conn, logMsg Info) error {
	if conn != nil {
		jsonData, err := json.Marshal(logMsg)
		if err != nil {
			log.Println("Error marshaling JSON:", err)
			return err
		}

		err = conn.WriteMessage(websocket.TextMessage, jsonData)
		if err != nil {
			log.Println("Error sending message:", err)
			return err
		}
		// fmt.Println("Sended data to socket")
		return nil
	}
	return http.ErrAbortHandler
}

func sendClear()  {
	mu.Lock()
	log.Println("Send to socket")
	defer mu.Unlock()
	// Loop through all connected clients and send the message
	for client := range clients {
		msg := "clear"
		err := client.WriteMessage(websocket.TextMessage, []byte(msg))
		if err != nil {
			log.Println("Error sending message:", err)
			
		}
	}
	
}
func sendToSocket(info Info) {
	mu.Lock()
	log.Println("Send to socket")
	defer mu.Unlock()
	// Loop through all connected clients and send the message
	for client := range clients {
		err := sendToClientInfo(client, info)
		if err != nil {
			log.Println("Error sending message:", err)
			client.Close()
			delete(clients, client) // Remove client if there's an error
		}
	}
}

func startSocket() {
	// Handle WebSocket connections
	http.HandleFunc("/ws", handleConnection)

	log.Println("Socket server started on", MyIP+MyPort)
	// Start the server
	err := http.ListenAndServe(MyIP+MyPort, nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
