package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os/exec"
	"strings"
	"bufio"
)

func sendGet(subject string, fio string, pass string) {
	baseURL := "http://pstgu.yss.su/iu9/networks/let1_2024/send_from_go.php"

	params := url.Values{}

	params.Add("subject", subject)
	params.Add("fio", fio)
	params.Add("pass", pass)

	// Construct the final URL with encoded query parameters
	finalURL := baseURL + "?" + params.Encode()

	response, err := http.Get(finalURL)
	if err != nil {
		log.Fatalf("Failed to send GET request: %v", err)
	}
	defer response.Body.Close()

	if response.StatusCode != http.StatusOK {
		log.Fatalf("Error: received status code %d", response.StatusCode)
	}

	body, err := io.ReadAll(response.Body)
	if err != nil {
		log.Fatalf("Failed to read response body: %v", err)
	}

	fmt.Println("Response: ")
	fmt.Println(string(body))
}

func getHash() string {
		cmd := exec.Command("tcpdump", "-A")
		out := ""

		stdout, err := cmd.StdoutPipe()
		if err != nil {
			log.Fatalf("Failed to get stdout pipe: %v", err)
		}
	
	
		if err := cmd.Start(); err != nil {
			log.Fatalf("Failed to start tcpdump: %v", err)
		}
	
		go func() {
			scanner := bufio.NewScanner(stdout)
			for scanner.Scan() {
				line := scanner.Text()
				// fmt.Println("line:", line)
				if (strings.Contains(line, "key")){
					fmt.Println("Found key:", line) // Print each stdout line
					if strings.Contains(line, "Fedukov") {
						out = strings.Split(line, " ")[1]
						fmt.Println("My key", out)
						cmd.Process.Kill()
						return
					}
					
				}
			}
		}()

	if err := cmd.Wait(); err != nil {
		fmt.Println("Killed+Found")
	}

	fmt.Println("tcpdump finished.")
	
	
	return out
}

func main() {
	subj := "let1_2024_ИУ9-32Б_Федуков_А_А"
	fio := "Федуков_Александр"
	hash := getHash()
	// hash := "e235accbff857f26dc79b090abb47849"
	fmt.Println(hash)
	url := "http://pstgu.yss.su/iu9/networks/let1_2024/getkey.php?hash=" + hash
	pass := OnPage(url)
	fmt.Println("Recieved pass: ", pass)
	pass = pass[6:]

	sendGet(subj, fio, pass)
}

func OnPage(link string) string {
	res, err := http.Get(link)
	if err != nil {
		log.Fatal(err)
	}
	content, err := io.ReadAll(res.Body)
	res.Body.Close()
	if err != nil {
		log.Fatal(err)
	}

	return string(content)
}
