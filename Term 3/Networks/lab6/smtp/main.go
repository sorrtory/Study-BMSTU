package main

import (
	"fmt"
	"log"
	"net/smtp"
	"os"
	"strings"
)

// Global variables for email credentials
var (
	smtpServer = "smtp.yandex.ru"
	port       = "587"
	login      = "trysmpt@yandex.com"
	password   = "mcjcmsxckrifuxsb"
)

func main() {
	// List of recipients
	recipients := []string{
		// "posevin@mail.ru",
		// "danila@posevin.com",
		// "posevin@bmstu.ru",
		"orlando20056@yandex.ru",
	}
	// Email details
	subject := "Федуков ИУ9-32Б"
	readbody, err := os.ReadFile("message.txt")
    if err != nil {
        log.Fatalf("unable to read file: %v", err)
    }
	body := string(readbody)

	err = sendEmails(recipients, subject, body)
	if err != nil {
		log.Fatalf("Failed to send emails: %v", err)
	} else {
		fmt.Println("Emails sent successfully!")
	}
}

// Function to send emails
func sendEmails(recipients []string, subject, body string) error {
	auth := smtp.PlainAuth("", login, password, smtpServer)

	// Format the email headers and body
	for _, recipient := range recipients {
		msg := strings.Builder{}
		msg.WriteString(fmt.Sprintf("From: %s\r\n", login))
		msg.WriteString(fmt.Sprintf("To: %s\r\n", recipient))
		msg.WriteString(fmt.Sprintf("Subject: %s\r\n", subject))
		msg.WriteString("\r\n") // Blank line between headers and body
		msg.WriteString(body)

		// Send the email
		err := smtp.SendMail(
			smtpServer+":"+port,
			auth,
			login,
			[]string{recipient},
			[]byte(msg.String()),
		)
		if err != nil {
			log.Printf("Failed to send email to %s: %v", recipient, err)
			continue
		}
		log.Printf("Email sent to %s successfully", recipient)
	}
	return nil
}
