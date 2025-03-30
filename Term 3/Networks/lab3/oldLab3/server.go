package main

import (
	"encoding/json"
	"fmt"
	"math/big"
	"net"
	log "github.com/mgutz/logxi/v1"
)

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

func goPeer(addrStr string, command string, data interface{}, args ...int){
	if addrStr == "next" {
		addrStr = NetworkList[NeigborIndex]+MyPort
	} else if addrStr == "back" {
		addrStr = NetworkList[args[0]]+MyPort
	}

	if addr, err := net.ResolveTCPAddr("tcp", addrStr); err != nil {
		log.Error("cannot resolve addres to connect", "adress", addrStr, "reason", err)
	}else if conn, err := net.DialTCP("tcp", nil, addr); err != nil {
		log.Error("cannot establish connection to")
	} else {
		log.Info("establish connection to", "address", conn.RemoteAddr().String())
		encoder, decoder := json.NewEncoder(conn), json.NewDecoder(conn)
		send_request(encoder, command, data)

		// Получение ответа.
		var resp Response
		if err := decoder.Decode(&resp); err != nil {
			fmt.Printf("error: %v\n", err)
		} 
		// Вывод ответа в стандартный поток вывода.
		switch resp.Status {
		case "ok":
			fmt.Printf("Data sended\n")
		case "failed":
			if resp.Data == nil {
				fmt.Printf("error: while next peer data field is absent in response\n")
			} else {
				var errorMsg string
				if err := json.Unmarshal(*resp.Data, &errorMsg); err != nil {
					fmt.Printf("error: malformed data field in response\n")
				} else {
					fmt.Printf("failed: %s\n", errorMsg)
				}
			}
		default:
			fmt.Printf("error: server reports unknown status %q\n", resp.Status)
		}
	}
}
// handleRequest - метод обработки запроса от клиента. Он возвращает true,
// если клиент передал команду "quit" и хочет завершить общение.
func (client *Client) handleRequest(req *Request) bool {
	switch req.Command {
	case "quit":
		client.respond("ok", nil)
		return true
	case "getValue":
		// by id
		errorMsg := ""
		if req.Data == nil {
			errorMsg = "data field is absent"
		} else {
			var s jsonSum
            if err := json.Unmarshal(*req.Data, &s); err != nil {
                errorMsg = "malformed data field"
            } else {
				if s.M >= MyIndex && MyIndex >= s.N {
					fmt.Printf("\nReturned MyValue to index %d\n", s.StartIndex)
					goPeer("back", "giveRequestedValue", &jsonInt{N: MyValue, StartIndex: MyIndex, EndIndex: s.StartIndex}, s.StartIndex)
				} else {
					fmt.Println("Going to next peer")
					goPeer("next", "getValue", req.Data)
				}
            }
        }

		if errorMsg == "" {
			client.respond("ok", nil)
		} else {
			client.logger.Error("addition failed", "reason", errorMsg)
			client.respond("failed", errorMsg)
		}

	case "setValue":
		// by id
		errorMsg := ""
		if req.Data == nil {
			errorMsg = "data field is absent"
		} else {
			var s jsonInt
	        if err := json.Unmarshal(*req.Data, &s); err != nil {
	            errorMsg = "malformed data field"
	        } else {
				if s.EndIndex == MyIndex {
					MyValue = s.N
					fmt.Printf("\nMyValue is updated to %d by index %d\n", MyValue, s.StartIndex)
				} else {
					goPeer("next", "setValue", req.Data)
				}
	        }
	    }

		if errorMsg == "" {
			client.respond("ok", nil)
		} else {
			client.logger.Error("addition failed", "reason", errorMsg)
			client.respond("failed", errorMsg)
		}

	case "getSum":
		// increase id and count sum
	
	case "giveRequestedValue":
		// by id
		errorMsg := ""
		if req.Data == nil {
			errorMsg = "data field is absent"
		} else {
			var s jsonInt
	        if err := json.Unmarshal(*req.Data, &s); err != nil {
	            errorMsg = "malformed data field"
	        } else {
				RequestedValue = s.N
				fmt.Printf("\nGot value %d from index %d\n", RequestedValue, s.StartIndex)
	        }
	    }

		if errorMsg == "" {
			client.respond("ok", nil)
		} else {
			client.logger.Error("addition failed", "reason", errorMsg)
			client.respond("failed", errorMsg)
		}

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

// func (client *Client) sendInt(){}
func startServer(addrStr string){
	if addr, err := net.ResolveTCPAddr("tcp", addrStr); err != nil {
		log.Error("address resolution failed", "address", addrStr)
	} else {
		log.Info("resolved TCP address", "address", addr.String())

		// Инициация слушания сети на заданном адресе.
		if listener, err := net.ListenTCP("tcp", addr); err != nil {
			log.Error("listening failed", "reason", err)
		} else {
			// Цикл приёма входящих соединений и обработки запросов.
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
