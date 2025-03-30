package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "log"
)

type MyHttpResponse struct {
    Message string `json:"message"`
}

type MyHttpPayload struct {
    Command string `json:"command"`
    I1 string `json:"i1"`
    I2  string `json:"i2"`
}

var dataHttpGetResponse string
var dataHttpPostResponse string

func enableCors(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*") // Allow all origins
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func getHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    // Parse query parameters
    comm := r.URL.Query().Get("command")
    i1 := r.URL.Query().Get("i1")
    i2 := r.URL.Query().Get("i2")

	fmt.Println("Get request command:", comm)

    dataHttpGetResponse = "Get: "
    parseFromForm(&dataHttpGetResponse, comm, i1, i2)

    // if i1 == "" || i2 == "" {
    //     http.Error(w, "Missing query parameters", http.StatusBadRequest)
    //     return
    // }

    response := MyHttpResponse{Message: dataHttpGetResponse}
    json.NewEncoder(w).Encode(response)

}

func postHandler(w http.ResponseWriter, r *http.Request) {
    var requestData MyHttpPayload

    // Parse JSON body
    err := json.NewDecoder(r.Body).Decode(&requestData)
    if err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    fmt.Println("Post request command:", requestData.Command)

    dataHttpPostResponse = "Post: "
    parseFromForm(&dataHttpPostResponse, requestData.Command, requestData.I1, requestData.I2)

    response := MyHttpResponse{Message: dataHttpPostResponse}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func startHttpServer() {
    http.Handle("/get", enableCors(http.HandlerFunc(getHandler)))
    http.Handle("/post", enableCors(http.HandlerFunc(postHandler)))


    fmt.Println("HTTP Server started at", MyHttpPort)
    log.Fatal(http.ListenAndServe(MyIP + MyHttpPort, nil))
}
