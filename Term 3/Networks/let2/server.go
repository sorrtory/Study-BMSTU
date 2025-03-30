package main

import (
    "fmt"
    "net"
    "bufio"
    "strings"
    "time"
)

func main() {
    // Listen for incoming connections on port 8080
    ln, err := net.Listen("tcp", ":8080")
    if err != nil {
        fmt.Println(err)
        return
    }
    defer ln.Close()


        c, err := ln.Accept()
        for {
                if err != nil {
                fmt.Println(err)
                continue
                }
                netData, err := bufio.NewReader(c).ReadString('\n')
                if err != nil {
                        fmt.Println(err)
                        return
                }
                if strings.TrimSpace(string(netData)) == "STOP" {
                        fmt.Println("Exiting TCP server!")
                        return
                }

                fmt.Print("-> ", string(netData))
                t := time.Now()
                myTime := t.Format(time.RFC3339) + "\n"
                c.Write([]byte(myTime))
        }
}
