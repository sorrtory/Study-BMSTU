package main

import (
	"fmt"
	"net"
	"os"
)

// var WORKING_FOLDER = "/home/chinalap/Документы/ComputerNetworks/lab4.1/src/"
var WORKING_FOLDER string
var USER_LOGIN_FILE = "clients.json"
var SSH_PORT = ":2288"

func main() {
	WORKING_FOLDER, _ = os.Getwd()
	if WORKING_FOLDER[len(WORKING_FOLDER)-1] != '/' {
		WORKING_FOLDER += "/"
	}

	s := "127.0.0.1"
	s, _ = getLocalIP()
	fmt.Println("Server started")
	fmt.Printf("Command to connect:\nssh -p %s %s -o StrictHostKeyChecking=no\n", SSH_PORT[1:], s)
	startServer()
}

func getLocalIP() (string, error) {
	interfaces, err := net.Interfaces()
	if err != nil {
		return "", err
	}

	for _, iface := range interfaces {
		if iface.Flags&net.FlagUp == 0 || iface.Flags&net.FlagLoopback != 0 {
			continue // Ignore down interfaces and loopback interface
		}

		addrs, err := iface.Addrs()
		if err != nil {
			return "", err
		}

		for _, addr := range addrs {
			var ip net.IP

			switch v := addr.(type) {
			case *net.IPNet:
				ip = v.IP
			case *net.IPAddr:
				ip = v.IP
			}

			// Filter for IPv4 addresses only
			if ip != nil && ip.To4() != nil {
				return ip.String(), nil
			}
		}
	}
	return "", fmt.Errorf("no IP address found")
}
