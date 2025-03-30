package main

var ftpCommandChan chan string
var wsMessageChan chan Message

var ftpCurrentDir = "/"
var ftpServer string   // students.yss.su:21
var ftpLogin string    // ftpiu8
var ftpPassword string // 3Ru7yOTA

var myIP = "localhost"
var wsPort = ":1429"

func main() {
	myIP = getip2()
	go startSocket()

	// ftpServer = "students.yss.su:21"
	// ftpLogin = "ftpiu8"
	// ftpPassword = "3Ru7yOTA"
	// client, err := connectFTP()
	// fmt.Println(err)
	// go runFTP(client)
	// ftpCommandChan <- "ls"
	select {}
}
