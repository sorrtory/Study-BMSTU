package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/secsy/goftp"
)

var globalRemotePath = "/"

func main() {
	// FTP connection configuration
	config := goftp.Config{
		User:     "ftpiu8",   // FTP username
		Password: "3Ru7yOTA", // FTP password
	}
	client, err := goftp.DialConfig(config, "students.yss.su:21")
	if err != nil {
		log.Fatalf("Failed to connect to FTP server: %v", err)
	}
	defer client.Close()


	fmt.Println("\nEnter command:")
	fmt.Println("upload <local_path> <remote_path>")
	fmt.Println("download <remote_path> <local_path>")
	fmt.Println("mkdir <remote_path>")
	fmt.Println("rm <remote_path>")
	fmt.Println("ls <remote_path>")
	fmt.Println("cd <remote_path>")
	fmt.Println("rmdir <remote_path>")
	fmt.Println("rmdirall <remote_path>")
	fmt.Println("exit")

	// Main command loop
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")

		// Get user input
		if !scanner.Scan() {
			break
		}
		input := strings.Fields(scanner.Text())
		if len(input) == 0 {
			continue
		}
		command := input[0]

		// Handle each command
		switch command {

		case "help":
			fmt.Println("upload <local_path> <remote_path>")
			fmt.Println("download <remote_path> <local_path>")
			fmt.Println("mkdir <remote_path>")
			fmt.Println("rm <remote_path>")
			fmt.Println("ls <remote_path>")
			fmt.Println("cd <remote_path>")
			fmt.Println("rmdir <remote_path>")
			fmt.Println("rmdirall <remote_path>")
			fmt.Println("exit")

		case "upload":
			if len(input) != 2 || len(input) != 3 {
				fmt.Println("Usage: upload <local_path> <remote_path>")
				continue
			}
			localPath := input[1]

			remotePath := ""
			if len(input) == 3 {
				remotePath = input[2]

			}

			if len(input) == 2 {
				remotePath = globalRemotePath
			}

			err := uploadFile(client, localPath, remotePath)
			if err != nil {
				fmt.Println(localPath, remotePath)
				fmt.Printf("Failed to upload file: %v\n", err)
			} else {
				fmt.Println("File uploaded successfully.")
			}

		case "download":
			if len(input) != 2 || len(input) != 3 {
				fmt.Println("Usage: upload <local_path> <remote_path>")
				continue
			}
			localPath := input[1]

			remotePath := ""
			if len(input) == 3 {
				remotePath = input[2]

			}

			if len(input) == 2 {
				remotePath = globalRemotePath
			}
			err := downloadFile(client, remotePath, localPath)
			if err != nil {
				fmt.Printf("Failed to download file: %v\n", err)
			} else {
				fmt.Println("File downloaded successfully.")
			}

		case "mkdir":
			if len(input) != 1 || len(input) != 2 {
				fmt.Println("Usage: upload <local_path> <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 2 {
				remotePath = input[1]

			}

			if len(input) == 1 {
				remotePath = globalRemotePath
			}

			_, err := client.Mkdir(remotePath)
			if err != nil {
				fmt.Printf("Failed to create directory: %v\n", err)
			} else {
				fmt.Println("Directory created successfully.")
			}

		case "rm":
			if len(input) != 1 || len(input) != 2 {
				fmt.Println("Usage: upload <local_path> <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 2 {
				remotePath = input[1]

			}

			if len(input) == 1 {
				remotePath = globalRemotePath
			}
			err := client.Delete(remotePath)
			if err != nil {
				fmt.Printf("Failed to delete file: %v\n", err)
			} else {
				fmt.Println("File deleted successfully.")
			}

		case "ls":
			if len(input) != 1 ||  len(input) != 2{
				fmt.Println("Usage: upload <local_path> <remote_path>")
				continue
			}

			remotePath := ""
			if len(input) == 2 {
				remotePath = input[1]
				
			}
			
			if len(input) == 1 {
				remotePath = globalRemotePath
			}
			
			entries, err := client.ReadDir(remotePath)
			if err != nil {
				fmt.Printf("Failed to list directory: %v\n", err)
			} else {
				fmt.Println("Directory contents:")
				for _, entry := range entries {
					fmt.Printf(" - %s\n", entry.Name())
				}
			}

		case "cd":
			if len(input) != 2 {
				fmt.Println("Usage: cd <remote_path>")
				continue
			}
			// 'cd' command is generally a local shell feature, not standard for FTP.
			// So here we can just save the path for any future commands.
			fmt.Println("Changing directory not supported in FTP. Just use absolute paths in commands.")

		case "rmdir":
			if len(input) != 2 {
				fmt.Println("Usage: rmdir <remote_path>")
				continue
			}
			remotePath := input[1]

			err := client.Rmdir(remotePath)
			if err != nil {
				fmt.Printf("Failed to remove directory: %v\n", err)
			} else {
				fmt.Println("Directory removed successfully.")
			}

		case "rmdirall":
			if len(input) != 2 {
				fmt.Println("Usage: rmdirall <remote_path>")
				continue
			}
			remotePath := input[1]
			err := removeDirectoryRecursive(client, remotePath)
			if err != nil {
				fmt.Printf("Failed to recursively delete directory: %v\n", err)
			} else {
				fmt.Println("Directory recursively deleted successfully.")
			}

		case "exit":
			fmt.Println("Exiting...")
			return

		default:
			fmt.Println("Unknown command.")
		}
	}
}

// Helper functions for FTP operations

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
		fullPath := fmt.Sprintf("%s/%s", remotePath, entry.Name())
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
	globalRemotePath = newFullPath
	return nil
}

// Resolve path based on the current globalRemotePath
func resolvePath(path string) string {
	if filepath.IsAbs(path) {
		return path
	}
	return filepath.Join(globalRemotePath, path)
}