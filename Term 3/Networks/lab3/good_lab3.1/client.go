package main

import (
	"encoding/json"
	"fmt"
	"net"
	"strconv"
	"time"

	log "github.com/mgutz/logxi/v1"
	"github.com/skorobogatov/input"
)

var Connection *net.TCPConn

func interactWithWebForm(conn *net.TCPConn, webFormResponse *string) {
	encoder, decoder := json.NewEncoder(conn), json.NewDecoder(conn)

	switch WebFormRequest.command {
	case "quit":
		send_request(encoder, "quit", nil)
		return
	case "help":
		*webFormResponse = *webFormResponse + "You should use client after connection to server!"
		*webFormResponse = *webFormResponse + "showValue - prints current index value"
		*webFormResponse = *webFormResponse + "setValue - define a value of given index"
		*webFormResponse = *webFormResponse + "getSum - count sum from n to m indexes"
	case "showValue":
		fmt.Println(MyValue)
		*webFormResponse = *webFormResponse + strconv.Itoa(MyValue)
	case "setValue":
		// by id
		fmt.Println("Updating value by webForm")
		send_request(encoder, "setValue", WebFormRequest.data)
		*webFormResponse = *webFormResponse + "Sended setValue request"

	case "getSum":
		// from n to m
		csum := 0
		cstart := WebFormRequest.data.(*jsonSum).N
		if WebFormRequest.data.(*jsonSum).N == MyIndex {
			csum += MyValue
			cstart = WebFormRequest.data.(*jsonSum).N + 1
		}
		fmt.Println("Requests for sum...")

		for i := cstart; i <= WebFormRequest.data.(*jsonSum).M; i++ {
			// Запрос значения
			send_request(encoder, "getValue", &jsonSum{N: i, StartIndex: MyIndex})
			// Получение ответа.
			var resp Response
			if err := decoder.Decode(&resp); err != nil {
				fmt.Printf("error: %v\n", err)
				break
			} else {
				if resp.Status != "ok" {
					fmt.Printf("error: data field is absent in response\n")
				} else {
					fmt.Printf("Recieved %d from index %d\n", RequestedValue, i)
					csum += RequestedValue
				}
			}
		}
		fmt.Printf("Sum is %d\n", csum)
		*webFormResponse = *webFormResponse + fmt.Sprintf("Sum is %d\n", csum)

	default:
		fmt.Printf("error: unknown command\n")
		*webFormResponse = *webFormResponse + "error: unknown command"
	}
	WebFormRequest = WebFormRequestParsed{}
}

// interact - функция, содержащая цикл взаимодействия с сервером.
func interact(conn *net.TCPConn) {
	defer conn.Close()
	encoder, decoder := json.NewEncoder(conn), json.NewDecoder(conn)
	for {
		// Чтение команды из стандартного потока ввода
		fmt.Printf("\ncommand = ")
		command := input.Gets()

		fmt.Println("Send command to WebForm: ", command)
		go sendToWebForm("Client command: " + command, "SSE")

		// Отправка запроса.
		switch command {
		case "quit":
			send_request(encoder, "quit", nil)
			return
		case "help":
			fmt.Println("You should use client after connection to server!")
			fmt.Println("showValue - prints current index value")
			fmt.Println("setValue - define a value of given index")
			fmt.Println("getSum - count sum from n to m indexes")
			continue
		case "showValue":
			fmt.Println(MyValue)
			continue
		case "setValue":
			// by id
			fmt.Printf("Index = ")
			if valInd, err := strconv.Atoi(input.Gets()); err != nil {
				fmt.Println("\nMust be number!")
				continue
			} else {
				fmt.Printf("Value = ")
				if valN, err := strconv.Atoi(input.Gets()); err != nil {
					fmt.Println("\nMust be number!")
					continue
				} else {
					send_request(encoder, "setValue", &jsonInt{N: valN, StartIndex: MyIndex, EndIndex: valInd})
				}
			}

		case "getSum":
			// from n to m
			fmt.Printf("From index = ")
			if valN, err := strconv.Atoi(input.Gets()); err != nil {
				fmt.Println("\nMust be number!")
				continue
			} else {
				fmt.Printf("To index = ")
				if valM, err := strconv.Atoi(input.Gets()); err != nil {
					fmt.Println("\nMust be number!")
					continue
				} else {
					csum := 0
					cstart := valN
					if valN == MyIndex {
						csum += MyValue
						cstart = valN + 1
					}
					fmt.Println("Requests for sum...")
					for i := cstart; i <= valM; i++ {
						// Запрос значения
						send_request(encoder, "getValue", &jsonSum{N: i, StartIndex: MyIndex})
						// Получение ответа.
						var resp Response
						if err := decoder.Decode(&resp); err != nil {
							fmt.Printf("error: %v\n", err)
							break
						} else {
							if resp.Status != "ok" {
								fmt.Printf("error: data field is absent in response\n")
							} else {
								fmt.Printf("Recieved %d from index %d\n", RequestedValue, i)
								csum += RequestedValue
							}
						}
					}
					fmt.Printf("Sum is %d\n", csum)
					continue
				}
			}

		default:
			fmt.Printf("error: unknown command\n")
			// Quit for Socket interaction
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

func startClient(addrStr string) {
	// Установка соединения с сервером и
	// запуск цикла взаимодействия с сервером.
	if addr, err := net.ResolveTCPAddr("tcp", addrStr); err != nil {
		log.Error("cannot resolve addres to connect", "adress", addrStr, "reason", err)
	} else if conn, err := net.DialTCP("tcp", nil, addr); err != nil {
		log.Error("cannot establish connection to")
		log.Info("waiting 5 seconds and trying again")
		time.Sleep(5 * time.Second)
		go startClient(addrStr)
	} else {
		log.Info("establish connection to", "address", conn.RemoteAddr().String())
		Connection = conn
		go interact(conn)
	}
}
