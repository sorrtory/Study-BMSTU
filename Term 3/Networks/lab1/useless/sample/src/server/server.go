package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/mgutz/logxi/v1"
	"math/big"
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


// Client - состояние клиента.
type Client struct {
	logger log.Logger    // Объект для печати логов
	conn   *net.TCPConn  // Объект TCP-соединения
	enc    *json.Encoder // Объект для кодирования и отправки сообщений
	sum    *big.Rat      // Текущая сумма полученных от клиента дробей
	count  int64         // Количество полученных от клиента дробей
}

// NewClient - конструктор клиента, принимает в качестве параметра
// объект TCP-соединения.
func NewClient(conn *net.TCPConn) *Client {
	return &Client{
		logger: log.New(fmt.Sprintf("client %s", conn.RemoteAddr().String())),
		conn:   conn,
		enc:    json.NewEncoder(conn),
		sum:    big.NewRat(0, 1),
		count:  0,
	}
}

// serve - метод, в котором реализован цикл взаимодействия с клиентом.
// Подразумевается, что метод serve будет вызаваться в отдельной go-программе.
func (client *Client) serve() {
	defer client.conn.Close()
	decoder := json.NewDecoder(client.conn)
	for {
		var req Request
		if err := decoder.Decode(&req); err != nil {
			client.logger.Error("cannot decode message", "reason", err)
			break
		} else {
			client.logger.Info("received command", "command", req.Command)
			if client.handleRequest(&req) {
				client.logger.Info("shutting down connection")
				break
			}
		}
	}
}
var globalN int

func calcScalar(vec1 []string, vec2 []string) string {
	sum := 0
	for i := 0; i < globalN; i++ {
		v1, _ := strconv.Atoi(vec1[i])
		v2, _ := strconv.Atoi(vec2[i])
		sum += v1*v2
	}
	return strconv.Itoa(sum)
}
type vecs struct {
	Vec1 []string `json: "vec1"`
	Vec2 []string `json: "vec2"`
}
var vectors vecs
type oneint struct{
	N string `json:n`
}


// handleRequest - метод обработки запроса от клиента. Он возвращает true,
// если клиент передал команду "quit" и хочет завершить общение.
func (client *Client) handleRequest(req *Request) bool {
	switch req.Command {
	case "quit":
		client.respond("ok", nil)
		return true
	case "setN":
		errorMsg := ""
		if req.Data == nil {
			errorMsg = "data field is absent"
		} else {
			var s oneint
            if err := json.Unmarshal(*req.Data, &s); err != nil {
                errorMsg = "malformed data field"
            } else {
                globalN, _ = strconv.Atoi(s.N)
                fmt.Printf("N is set to %d\n", globalN)
            }
        }

		if errorMsg == "" {
			client.respond("ok", nil)
		} else {
			client.logger.Error("addition failed", "reason", errorMsg)
			client.respond("failed", errorMsg)
		}
	case "setVectors":
		errorMsg := ""
		if req.Data == nil {
			errorMsg = "data field is absent"
		} else {
			if err := json.Unmarshal(*req.Data, &vectors); err != nil {
				errorMsg = "malformed data field"
			} else {
				// fmt.Printf("N is set to %d\n", globalN)
				fmt.Println("Vec1 is set to", vectors.Vec1)
				fmt.Println("Vec2 is set to", vectors.Vec2)
			}
		}
		if errorMsg == "" {
			client.respond("ok", nil)
		} else {
			client.logger.Error("addition failed", "reason", errorMsg)
			client.respond("failed", errorMsg)
		}
	case "calc":
		var result oneint
		result.N = calcScalar(vectors.Vec1, vectors.Vec2)
        fmt.Printf("Result: %s\n", result.N)
		client.respond("result", &result)
	default:
		client.logger.Error("unknown command")
		client.respond("failed", "unknown command")
	}
	return false
}

// respond - вспомогательный метод для передачи ответа с указанным статусом
// и данными. Данные могут быть пустыми (data == nil).
func (client *Client) respond(status string, data interface{}) {
	var raw json.RawMessage
	raw, _ = json.Marshal(data)
	client.enc.Encode(&Response{status, &raw})
}

func main() {
    // Работа с командной строкой, в которой может указываться необязательный ключ -addr.
	var addrStr string
	flag.StringVar(&addrStr, "addr", "185.102.139.169:1572", "specify ip address and port")
	flag.Parse()

    // Разбор адреса, строковое представление которого находится в переменной addrStr.
	if addr, err := net.ResolveTCPAddr("tcp", addrStr); err != nil {
		log.Error("address resolution failed", "address", addrStr)
	} else {
		log.Info("resolved TCP address", "address", addr.String())

        // Инициация слушания сети на заданном адресе.
		if listener, err := net.ListenTCP("tcp", addr); err != nil {
			log.Error("listening failed", "reason", err)
		} else {
            // Цикл приёма входящих соединений.
			for {
				if conn, err := listener.AcceptTCP(); err != nil {
					log.Error("cannot accept connection", "reason", err)
				} else {
					log.Info("accepted connection", "address", conn.RemoteAddr().String())

                    // Запуск go-программы для обслуживания клиентов.
					go NewClient(conn).serve()
				}
			}
		}
	}
}
