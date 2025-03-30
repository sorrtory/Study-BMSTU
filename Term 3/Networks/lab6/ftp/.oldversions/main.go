package main

import ( /* w w    w . b   o  o   k2   s   . c  o m  */
	"fmt"

	"github.com/jlaffaye/ftp"
)

func main() {
	// FTP server details
	ftpHost := "students.yss.su"
	ftpPort := 21
	ftpUser := "ftpiu8"
	ftpPass := "3Ru7yOTA"

	// File to download
	//   filePath := "/path/to/remote/file.txt"
	//   localFilePath := "file.txt" // Local file path to save the downloaded file

	// Connect to the FTP server
	client, err := ftp.Dial(fmt.Sprintf("%s:%d", ftpHost, ftpPort))
	if err != nil {
		fmt.Println("Error connecting to FTP server:", err)
		return
	}
	defer client.Quit()

	// Login to the FTP server
	err = client.Login(ftpUser, ftpPass)
	if err != nil {
		fmt.Println("Error logging in to FTP server:", err)
		return
	}

	//   // Open the remote file for reading
	//   r, err := client.Retr(filePath)
	//   if err != nil {
	//     fmt.Println("Error opening remote file:", err)
	//     return
	//   }
	//   defer r.Close()

	//   // Create a new local file for writing
	//   localFile, err := os.Create(localFilePath)
	//   if err != nil {
	//     fmt.Println("Error creating local file:", err)
	//     return
	//   }
	//   defer localFile.Close()

	//   // Copy the contents of the remote file to the local file
	//   _, err = io.Copy(localFile, r)
	//   if err != nil {
	//     fmt.Println("Error downloading file:", err)
	//     return
	//   }

	fmt.Println("File downloaded successfully!")
}
