package main

import (
	"fmt"
	"log"

	"github.com/knadh/go-pop3"
)

func read() string {
	var out string
	// Initialize the client.
	p := pop3.New(pop3.Opt{
		Host:       "pop.yandex.ru",
		Port:       995,
		TLSEnabled: true,
	})

	// Create a new connection. POP3 connections are stateful and should end
	// with a Quit() once the opreations are done.
	c, err := p.NewConn()
	if err != nil {
		log.Fatal(err)
	}
	defer c.Quit()

	// Authenticate.
	if err := c.Auth("trysmpt@yandex.com", "mcjcmsxckrifuxsb"); err != nil {
		log.Fatal(err)
	}

	// Print the total number of messages and their size.
	count, size, _ := c.Stat()
	out += fmt.Sprintln("total messages=", count, "size=", size)

	// Pull the list of all message IDs and their sizes.
	msgs, _ := c.List(0)
	for _, m := range msgs {
		out += fmt.Sprintln("id=", m.ID, "size=", m.Size)
	}

	// Pull all messages on the server. Message IDs go from 1 to N.
	for id := 1; id <= count; id++ {
		m, _ := c.Retr(id)

		out += fmt.Sprintln(id, "=", m.Header.Get("subject"))

		// To read the multi-part e-mail bodies, see:
		// https://github.com/emersion/go-message/blob/master/example_test.go#L12
	}

	// Delete all the messages. Server only executes deletions after a successful Quit()
	// for id := 1; id <= count; id++ {
	// 	c.Dele(id)
	// }
	c.Quit()

	return out
}

func deletePop() string{
	// Initialize the client.
	p := pop3.New(pop3.Opt{
		Host:       "pop.yandex.ru",
		Port:       995,
		TLSEnabled: true,
	})

	// Create a new connection. POP3 connections are stateful and should end
	// with a Quit() once the opreations are done.
	c, err := p.NewConn()
	if err != nil {
		log.Fatal(err)
	}
	defer c.Quit()

	// Authenticate.
	if err := c.Auth("trysmpt@yandex.com", "mcjcmsxckrifuxsb"); err != nil {
		log.Fatal(err)
	}

	// Print the total number of messages and their size.
	count, _, _ := c.Stat()

	// Delete all the messages. Server only executes deletions after a successful Quit()
	for id := 1; id <= count; id++ {
		c.Dele(id)
	}
	c.Quit()

	return "Deleted"
}
