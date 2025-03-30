package main

import (
	"fmt"
	"log"
	"net/http"
)
var dataSseChannel = make(chan string)

// SSE handler function
func sseHandler(w http.ResponseWriter, r *http.Request) {
    // Set CORS headers to allow cross-origin requests
    w.Header().Set("Access-Control-Allow-Origin", "*") // Allow all origins
    w.Header().Set("Access-Control-Allow-Methods", "GET") // Allow GET requests
    w.Header().Set("Access-Control-Allow-Headers", "Content-Type") // Allow content-type headers

    // Set headers for SSE
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    
    // Create a channel for client disconnection
    clientGone := r.Context().Done()

    for {
        select {
            case message := <-dataSseChannel:
                _, err := fmt.Fprintf(w, "data: %s \n\n", MyIP + "$" + message)
                if err != nil {
                    fmt.Println("Not sended")
                    return
                }

                if f, ok := w.(http.Flusher); ok {
                    f.Flush()
                } else {
                    fmt.Println("Bad flush")
                }
            case <-clientGone:
                fmt.Println("SSE client disconnected")
                return
        }

    }

}

func startSseServer() {
    http.HandleFunc("/events", sseHandler)

    fmt.Println("SSE server started at ", MySsePort)
    log.Fatal(http.ListenAndServe(MyIP + MySsePort, nil))
}
