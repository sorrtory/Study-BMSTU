package main

import (
	"fmt"
	"html/template"
	"net/http"
	"strconv"
	"strings"

	"github.com/gorilla/websocket"
)

var wsUpgrader = websocket.Upgrader{
	// ReadBufferSize:  1024,
	// WriteBufferSize: 1024,
}

func handleSocket(w http.ResponseWriter, r *http.Request) {

	conn, err := wsUpgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer conn.Close()

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
		output := strings.Split(string(message), " ")
		iout, _ := strconv.Atoi(output[0])
		MyTemplate.Data[iout] = output[1]
		err = conn.WriteMessage(messageType, []byte("Hello, client!"))
		if err != nil {
			fmt.Println(err)
			return
		}
	}
}

type temp struct {
	Ws   string
	Data [4]string
}

var MyTemplate temp

func home(w http.ResponseWriter, r *http.Request) {
	MyTemplate.Ws = "ws://" + r.Host + "/ws"
    fmt.Println(MyTemplate)
	homeTemplate.Execute(w, MyTemplate)
}

func main() {
    for i, _ := range MyTemplate.Data {
        MyTemplate.Data[i] = "DATA"
    }
	// Listen for WebSocket connections on port 8080.
	http.HandleFunc("/ws", handleSocket)
	http.HandleFunc("/", home)

	// Start the server.
	http.ListenAndServe("localhost:8080", nil)

}

var homeTemplate = template.Must(template.New("").Parse(`
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script>
var ws;
socket = new WebSocket("{{ .Ws }}");
socket.onopen = function(e) {
  //alert("[open] Соединение установлено");
  //alert("Отправляем данные на сервер");
  socket.send("Тестовая строка в сторону сервера! Прием!");
  console.log("123")
};
socket.onmessage = function(event) {
    console.log("fdkjfdkfk")
  document.getElementById("id0").innerHTML = event.data; 
};
</script>

<div id="id0">ds</div>
<div id="id1">{{index .Data 1}}</div>
<div id="id2">{{index .Data 2}}</div>
<div id="id3">{{index .Data 3}}</div>

</body>
</html>
`))
