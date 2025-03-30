package main

import (
    "fmt"
    "net"
    "bufio"
    "os"
    "strings"
)

func main() {
    // Connect to the server
    conn, err := net.Dial("tcp", "localhost:8080")
    if err != nil {
        fmt.Println(err)
        return
    }


    // Close the connection
        defer conn.Close()

        for {
                reader := bufio.NewReader(os.Stdin)
                fmt.Print(">> ")
                text, _ := reader.ReadString('\n')
                fmt.Fprintf(conn, text+"\n")

                message, _ := bufio.NewReader(conn).ReadString('\n')
                fmt.Print("->: " + message)
                if strings.TrimSpace(string(text)) == "STOP" {
                        fmt.Println("TCP client exiting...")
                        return
                }
        }

}