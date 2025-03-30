package main

import (
	"fmt"
	"io"
	"log"
	"strings"

	"github.com/gliderlabs/ssh"
	terminal "golang.org/x/term"
)

// ssh -p 2222 127.0.0.1 -o StrictHostKeyChecking=no

var is_Authenticated = false
var userName = ""
var userLogin = ""

func updatePromt(term *terminal.Terminal) {
	term.SetPrompt(fmt.Sprintf("%s@%s:%s > ", userLogin, userName, WORKING_FOLDER))
}

func sessionHandler(s ssh.Session) {
	defer s.Close()
	if s.RawCommand() != "" {
		io.WriteString(s, "raw commands are not supported")
		return
	}

	// создаем терминал
	term := terminal.NewTerminal(s, fmt.Sprintf("/%s/ > ", s.User()))

	// добавляем обработку pty-request
	pty, winCh, isPty := s.Pty()
	if isPty {
		_ = pty
		go func() {
			// реагируем на изменение размеров терминала
			for chInfo := range winCh {
				_ = term.SetSize(chInfo.Width, chInfo.Height)
			}
		}()
	}

	for {
		if !is_Authenticated {
			term.SetPrompt("")

			io.WriteString(term, "Enter Login: ")
			lgn, err := term.ReadLine()
			if err == io.EOF {
				_, _ = io.WriteString(s, "EOF.\n")
				break
			}
			userLogin = lgn
			userName = s.User()

			psswd, err := term.ReadPassword("Enter Password: ")
			if err == io.EOF {
				_, _ = io.WriteString(s, "EOF.\n")
				break
			}

			if checkUserPasswd(lgn, psswd) {
				is_Authenticated = true
				updatePromt(term)
				io.WriteString(term, "Authenticated\n")

			} else {
				io.WriteString(term, "Wrong login or password\n")
			}
		} else {
			line, err := term.ReadLine()
			if err == io.EOF {
				_, _ = io.WriteString(s, "EOF.\n")
				break
			}
			fmt.Println("Recieved line:", line)
			cmd := strings.Split(line, " ")
			handleCommand(term, cmd[0], cmd[1:]...)

		}

	}
}

func startServer() {
	ssh.Handle(sessionHandler)

	log.Fatal(ssh.ListenAndServe(SSH_PORT, nil))
}
