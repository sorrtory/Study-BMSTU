package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/skorobogatov/input"
	"net"
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

type vecs struct {
	Vec1 []string `json: "vec1"`
	Vec2 []string `json: "vec2"`
}
var vectors vecs
type oneint struct{
	N string `json:n`
}
var result oneint
var globalN int
var vec1 []string
var vec2 []string
// interact - функция, содержащая цикл взаимодействия с сервером.
func interact(conn *net.TCPConn) {
	defer conn.Close()
	encoder, decoder := json.NewEncoder(conn), json.NewDecoder(conn)
	for {
        // Чтение команды из стандартного потока ввода
		fmt.Printf("command = ")
		command := input.Gets()

        // Отправка запроса.
		switch command {
		case "quit":
			send_request(encoder, "quit", nil)
			return
		case "setN":
			fmt.Printf("Set n = ")
			n := input.Gets()
			globalN , _= strconv.Atoi(n)
			var q oneint
			q.N = n
			send_request(encoder, "setN", q)
		case "setVecs":
			fmt.Printf("Vector 1 \n")
			vec1 = make([]string, globalN)
			for i := 0; i < globalN; i++ {
				fmt.Printf("Set x%d/x%d = ", i, globalN-1)
				vec1[i] = input.Gets()
			}
			fmt.Printf("Vector 2 \n")
			vec2 = make([]string, globalN)
			for i := 0; i < globalN; i++ {
				fmt.Printf("Set x%d/x%d = ", i, globalN-1)
				vec2[i] = input.Gets()
			}
			var v vecs
			v.Vec1 = vec1
			v.Vec2 = vec2
			send_request(encoder, "setVectors", &v)
		case "calc":
			send_request(encoder, "calc", nil)

        default:
            fmt.Printf("error: unknown command\n")
            continue
		}

		// Получение ответа.
		var resp Response
		if err := decoder.Decode(&resp); err != nil {
			fmt.Printf("error: %v\n", err)
			break
		}

		// Вывод ответа в стандартный поток вывода.
		switch resp.Status {
		case "ok":
			fmt.Printf("ok\n")
		case "failed":
			if resp.Data == nil {
				fmt.Printf("error: data field is absent in response\n")
			} else {
				var errorMsg string
				if err := json.Unmarshal(*resp.Data, &errorMsg); err != nil {
					fmt.Printf("error: malformed data field in response\n")
				} else {
					fmt.Printf("failed: %s\n", errorMsg)
				}
			}
		case "result":
			if resp.Data == nil {
				fmt.Printf("error: data field is absent in response\n")
			} else {
				var out oneint
				if err := json.Unmarshal(*resp.Data, &out); err != nil {
					fmt.Printf("error: malformed data field in response\n")
				} else {
					fmt.Printf("result: %s\n", out.N)
				}
			}
		default:
			fmt.Printf("error: server reports unknown status %q\n", resp.Status)
		}
	}
}

// send_request - вспомогательная функция для передачи запроса с указанной командой
// и данными. Данные могут быть пустыми (data == nil).
func send_request(encoder *json.Encoder, command string, data interface{}) {
	var raw json.RawMessage
	raw, _ = json.Marshal(data)
	encoder.Encode(&Request{command, &raw})
}

func main() {
	// Работа с командной строкой, в которой может указываться необязательный ключ -addr.
	var addrStr string
	flag.StringVar(&addrStr, "addr", "185.102.139.169:1572", "specify ip address and port")
	flag.Parse()

	// Разбор адреса, установка соединения с сервером и
	// запуск цикла взаимодействия с сервером.
	if addr, err := net.ResolveTCPAddr("tcp", addrStr); err != nil {
		fmt.Printf("error: %v\n", err)
	} else if conn, err := net.DialTCP("tcp", nil, addr); err != nil {
		fmt.Printf("error: %v\n", err)
	} else {
		interact(conn)
	}
}
