package main

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"text/tabwriter"

	"github.com/secsy/goftp"
)

func sendMsg(msg string) {
	fmt.Print(msg)
	wsMessageChan <- Message{Type: "display", Body: msg}
}

func sendMsgln(msg string) {
	msg += "\n"
	sendMsg(msg)
}

func updatePrompt() {
	prompt := fmt.Sprintf("%s@%s:[%s]", ftpLogin, ftpServer, ftpCurrentDir)
	wsMessageChan <- Message{Type: "setPrompt", Body: prompt}
}

func connectFTP() (*goftp.Client, error) {
	ftpCommandChan = make(chan string)

	// FTP connection configuration
	config := goftp.Config{
		User:     ftpLogin,    // FTP username
		Password: ftpPassword, // FTP password
	}

	client, err := goftp.DialConfig(config, ftpServer)
	return client, err
}

func runFTP(client *goftp.Client) {
	defer client.Close()
	updatePrompt()
	for commandLine := range ftpCommandChan {
		if commandLine == "Exit" {
			break
		}

		input := strings.Fields(commandLine)
		if len(input) == 0 {
			continue
		}
		command := input[0]

		// Handle each command
		switch command {
		case "help":
			sendMsgln("upload <local_path> <remote_path>\n" +
				"download <remote_path> <local_path>\n" +
				"mkdir <remote_path>\n" +
				"rm <remote_path>\n" +
				"ls <remote_path>\n" +
				"cd <remote_path>\n" +
				"rmdir <remote_path>\n" +
				"rmdirall <remote_path>\n" +
				"exit")
		case "upload":
			if len(input) != 3 && len(input) != 2 {
				sendMsgln("Usage: upload <local_path> <remote_path>")
				continue
			}
			localPath := input[1]
			remotePath := ""
			if len(input) == 2 {
				remotePath = ftpCurrentDir + filepath.Base(input[1])
			} else {
				remotePath = resolvePath(input[2])
			}

			err := uploadFile(client, localPath, remotePath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to upload file: %v\n", err))
			} else {
				sendMsgln("File uploaded successfully." + "\n")
			}

		case "download":
			if len(input) != 3 && len(input) != 2 {
				sendMsgln("Usage: download <remote_path> <local_path>")
				continue
			}
			remotePath := input[1]
			localPath := ""
			if len(input) == 2 {
				localPath = filepath.Base(input[1])
			} else {
				localPath = resolvePath(input[2])
			}

			err := downloadFile(client, remotePath, localPath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to download file: %v\n", err))
			} else {
				sendMsgln("File downloaded successfully.")
			}

		case "mkdir":
			if len(input) != 2 {
				sendMsgln("Usage: mkdir <remote_path>")
				continue
			}
			remotePath := resolvePath(input[1])
			_, err := client.Mkdir(remotePath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to create directory: %v\n", err))
			} else {
				sendMsgln("Directory created successfully.")
			}

		case "rm":
			if len(input) != 2 && len(input) != 1 {
				sendMsgln("Usage: rm <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 1 {
				remotePath = resolvePath("")
			} else {
				remotePath = resolvePath(input[1])
			}

			err := client.Delete(remotePath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to delete file: %v\n", err))
			} else {
				sendMsgln("File deleted successfully.")
			}

		case "ls":
			if len(input) != 2 && len(input) != 1 {
				sendMsgln("Usage: ls <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 1 {
				remotePath = resolvePath("")
			} else {
				remotePath = resolvePath(input[1])
			}

			entries, err := client.ReadDir(remotePath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to list directory: %v\n", err))
			} else {
				out := "Directory contents:\n"
				tab := [][]string{}

				tab = append(tab, []string{"[Count]", "[Type]", "[Name]", "[Size]"})
				for i, entry := range entries {
					row := []string{}
					row = append(row, fmt.Sprint(i)+")")
					etype := ""
					if entry.IsDir() {
						etype = "d"
					} else {
						etype = "-"
					}
					row = append(row, etype)
					row = append(row, entry.Name())
					row = append(row, fmt.Sprint(entry.Size()))
					tab = append(tab, row)
				}
				out += formatTable(tab)
				sendMsg(out)
			}

		case "cd":
			if len(input) != 2 {
				sendMsgln("Usage: cd <remote_path>")
				continue
			}
			newPath := input[1]
			if err := changeDirectory(client, newPath); err != nil {
				sendMsg(fmt.Sprintf("Failed to change directory: %v\n", err))
			} else {
				sendMsg(fmt.Sprintf("Changed directory to: %s\n", ftpCurrentDir))
			}

		case "rmdir":
			if len(input) != 2 && len(input) != 1 {
				sendMsgln("Usage: rmdir <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 1 {
				remotePath = resolvePath("")
			} else {
				remotePath = resolvePath(input[1])
			}

			err := client.Rmdir(remotePath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to remove directory: %v\n", err))
			} else {
				sendMsgln("Directory removed successfully.")
			}

		case "rmdirall":
			if len(input) != 2 && len(input) != 1 {
				sendMsgln("Usage: rmdirall <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 1 {
				remotePath = resolvePath("")
			} else {
				remotePath = resolvePath(input[1])
			}

			err := removeDirectoryRecursive(client, remotePath)
			if err != nil {
				sendMsg(fmt.Sprintf("Failed to recursively delete directory: %v\n", err))
			} else {
				sendMsgln("Directory recursively deleted successfully.")
			}

		case "exit":
			sendMsgln("Exiting...")
			wsMessageChan <- Message{Type: "loginError", Body: "Error"}
			return

		default:
			sendMsgln("Unknown command.")
		}
		updatePrompt()

	}
}

func formatTable(data [][]string) string {
	if len(data) == 0 {
		return ""
	}

	// Calculate the maximum width for each column
	colWidths := calculateColumnWidths(data)

	// Use a bytes.Buffer to build the formatted string
	var buf bytes.Buffer
	writer := tabwriter.NewWriter(&buf, 0, 0, 1, '_', 0)

	// Build each row
	for _, row := range data {
		for i, col := range row {
			// Pad each column to its calculated width
			formattedCol := fmt.Sprintf("%-*s", colWidths[i], col)
			// Replace spaces with underscores
			writer.Write([]byte(strings.ReplaceAll(formattedCol, " ", "_")))
			// Add a tab to separate columns
			writer.Write([]byte("\t"))
		}
		writer.Write([]byte("\n")) // End the row
	}

	writer.Flush()
	return buf.String()
}

// calculateColumnWidths determines the maximum width for each column in the table
func calculateColumnWidths(data [][]string) []int {
	// Find the number of columns
	colCount := len(data[0])
	colWidths := make([]int, colCount)

	// Iterate over the data to calculate the max width for each column
	for _, row := range data {
		for i, col := range row {
			if len(col) > colWidths[i] {
				colWidths[i] = len(col)
			}
		}
	}

	return colWidths
}

// Change directory function that updates globalRemotePath
func changeDirectory(client *goftp.Client, newPath string) error {
	// Resolve the path relative to current directory
	newFullPath := resolvePath(newPath)

	// Check if the directory exists on the server by attempting to read it
	_, err := client.ReadDir(newFullPath)
	if err != nil {
		return fmt.Errorf("directory does not exist or cannot be accessed")
	}

	// Update the global path
	ftpCurrentDir = newFullPath

	if ftpCurrentDir[len(ftpCurrentDir)-1] != '/' {
		ftpCurrentDir += "/"
	}

	return nil
}

// Resolve path based on the current globalRemotePath
func resolvePath(path string) string {

	if path == "" {
		return ftpCurrentDir
	}

	if filepath.IsAbs(path) {
		return path
	}
	return filepath.Join(ftpCurrentDir, path)
}

// Other helper functions for FTP operations
func uploadFile(client *goftp.Client, localPath, remotePath string) error {
	file, err := os.Open(localPath)
	if err != nil {
		return err
	}
	defer file.Close()
	return client.Store(remotePath, file)
}

func downloadFile(client *goftp.Client, remotePath, localPath string) error {
	file, err := os.Create(localPath)
	if err != nil {
		return err
	}
	defer file.Close()
	return client.Retrieve(remotePath, file)
}

func removeDirectoryRecursive(client *goftp.Client, remotePath string) error {
	entries, err := client.ReadDir(remotePath)
	if err != nil {
		return err
	}
	for _, entry := range entries {
		fullPath := filepath.Join(remotePath, entry.Name())
		if entry.IsDir() {
			err := removeDirectoryRecursive(client, fullPath)
			if err != nil {
				return err
			}

		} else {
			err := client.Delete(fullPath)
			if err != nil {
				return err
			}
		}
	}
	return client.Rmdir(remotePath)
}
