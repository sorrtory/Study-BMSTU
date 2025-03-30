package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	terminal "golang.org/x/term"
)

func handleCommand(term *terminal.Terminal, command string, args ...string) {
	path := WORKING_FOLDER
	if len(args) != 0 {
		path = args[0]
	}

	switch command {
	case "pwd":
		term.Write([]byte(WORKING_FOLDER + "\n"))
	case "exit":
		is_Authenticated = false
	case "cd":
		fmt.Println(args)
		if args[0] == ".." {
			WORKING_FOLDER = filepath.Dir(WORKING_FOLDER[:len(WORKING_FOLDER)-1]) + "/"
		} else {
			dest := args[0]
			if filepath.IsLocal(dest) {
				dest = WORKING_FOLDER + dest
			}

			if dest[len(dest)-1] != '/' {
				dest += "/"
			}

			WORKING_FOLDER = dest
		}
		updatePromt(term)

	case "ls":
		term.Write([]byte(WORKING_FOLDER + "\n"))
		intend := "  --> "
		files, err := os.ReadDir(path)
		if err != nil {
			term.Write([]byte("Error reading directory: " + err.Error()))
		} else {
			for _, file := range files {
				term.Write([]byte(intend + file.Name() + "\n"))
			}
		}

	case "mkdir":
		if err := os.Mkdir(path, 0755); err != nil {
			term.Write([]byte("Error creating directory: " + err.Error()))
		} else {
			term.Write([]byte("Directory created\n"))
		}

	case "rmdir":
		if err := os.Remove(path); err != nil {
			term.Write([]byte("Error deleting directory: " + err.Error()))
		} else {
			term.Write([]byte("Directory deleted\n"))
		}

	case "mv":
		fmt.Println(args[0], args[1])
		if err := os.Rename(args[0], args[1]); err != nil {
			term.Write([]byte("Error moving file: " + err.Error()))
		} else {
			term.Write([]byte("File moved\n"))
		}

	case "rm":
		if err := os.Remove(path); err != nil {
			term.Write([]byte("Error deleting file: " + err.Error()))
		} else {
			term.Write([]byte("File deleted\n"))
		}

	case "exec":
		cmd := exec.Command(args[0], args[1:]...)
		output, err := cmd.CombinedOutput()
		if err != nil {
			term.Write([]byte("Error running command: " + err.Error()))
		}
		term.Write(output)

	default:
		term.Write([]byte("Unknown command: " + command + "\n"))

	}
}
