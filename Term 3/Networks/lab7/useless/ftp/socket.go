package main

import (
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"

	"github.com/gorilla/websocket"
)

type Message struct {
	Type string `json:"type"`
	Body string `json:"body"`
}

var (
	clients  = make(map[*websocket.Conn]bool) // Connected clients
	upgrader = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}
	mu sync.Mutex
)

// Initisalize connection
func handleConnections(w http.ResponseWriter, r *http.Request) {
	log.Println("New ws connection")
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Error upgrading connection: %v\n", err)
		return
	}
	defer ws.Close()

	mu.Lock()
	clients[ws] = true
	mu.Unlock()

	// Read from socket
	for {
		var msg Message
		err = ws.ReadJSON(&msg)
		log.Println("New ws message: ", msg)
		if err != nil {
			log.Printf("Error reading JSON: %v\n", err)
			mu.Lock()
			delete(clients, ws)
			mu.Unlock()
			break
		}

		if msg.Type == "ftpCommand" {
			go func() {
				ftpCommandChan <- msg.Body
			}()
		} else if msg.Type == "ftpLogin" {
			log.Println(msg.Body)
			logindata := strings.Split(msg.Body, " ")
			ftpServer = ""
			ftpLogin = ""
			ftpPassword = ""
			if len(logindata) == 3 {
				ftpServer = logindata[0]
				ftpLogin = logindata[1]
				ftpPassword = logindata[2]
			}

			if client, err := connectFTP(); err != nil {
				wsMessageChan <- Message{Type: "loginError", Body: "Error"}
				log.Printf("Failed to login: server|%s|, user|%s|, password|%s|", ftpServer, ftpLogin, ftpPassword)
			} else {
				wsMessageChan <- Message{Type: "loginSuccess", Body: "<3"}
				log.Println("FTP login")
				go runFTP(client)
			}
		} else {
			fmt.Printf("Unknown ws comman: %s", msg.Type)
		}

	}
}

func handleMessages() {
	// Send to socket
	for {
		msg := <-wsMessageChan

		mu.Lock()
		for client := range clients {
			err := client.WriteJSON(msg)
			if err != nil {
				log.Printf("Error writing JSON: %v\n", err)
				client.Close()
				delete(clients, client)
			}
		}
		mu.Unlock()
	}
}

func startSocket() {
	wsMessageChan = make(chan Message)
	clients = make(map[*websocket.Conn]bool)
	http.HandleFunc("/ws", handleConnections)

	go handleMessages()

	fmt.Println("WebSocket server started on " + myIP + wsPort)
	log.Fatal(http.ListenAndServe(myIP+wsPort, nil))
}
