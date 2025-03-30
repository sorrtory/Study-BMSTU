package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/creack/pty"
	"golang.org/x/crypto/ssh"
	"golang.org/x/term"
)

// SSHConfig holds the SSH connection configuration
type SSHConfig struct {
	User     string
	Host     string
	Port     int
	Password string
}

// NewSSHClient initializes an SSH client and connects to the server
func NewSSHClient(config SSHConfig) (*ssh.Client, error) {
	sshConfig := &ssh.ClientConfig{
		User: config.User,
		Auth: []ssh.AuthMethod{
			ssh.Password(config.Password),
		},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(), // For simplicity, ignore host key verification
	}

	address := fmt.Sprintf("%s:%d", config.Host, config.Port)
	client, err := ssh.Dial("tcp", address, sshConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to SSH server: %w", err)
	}

	return client, nil
}

// StartInteractiveShell starts an interactive shell session on the SSH server
func StartInteractiveShell(client *ssh.Client) error {
	session, err := client.NewSession()
	if err != nil {
		return fmt.Errorf("failed to create SSH session: %w", err)
	}
	defer session.Close()

	// Get the current terminal state for restoration after the session ends
	fd := int(os.Stdin.Fd())
	oldState, err := term.MakeRaw(fd)
	if err != nil {
		return fmt.Errorf("failed to set terminal raw mode: %w", err)
	}
	defer term.Restore(fd, oldState) // Restore terminal state on exit

	// Set up standard input, output, and error streams
	session.Stdout = os.Stdout
	session.Stderr = os.Stderr
	session.Stdin = os.Stdin

	// Request a pseudo-terminal
	rows, cols, err := pty.Getsize(os.Stdin)
	if err != nil {
		return fmt.Errorf("failed to get window size: %w", err)
	}
	if err := session.RequestPty("xterm-256color", rows, cols, ssh.TerminalModes{
		ssh.ECHO:          1,
		ssh.TTY_OP_ISPEED: 14400,
		ssh.TTY_OP_OSPEED: 14400,
	}); err != nil {
		return fmt.Errorf("failed to request pseudo-terminal: %w", err)
	}

	// Handle window size changes
	go func() {
		ch := make(chan os.Signal, 1)
		signal.Notify(ch, syscall.SIGWINCH)
		for range ch {
			rows, cols, _ := pty.Getsize(os.Stdin)
			session.WindowChange(rows, cols)
		}
	}()
	signal.Notify(make(chan os.Signal, 1), syscall.SIGWINCH) // Catch SIGWINCH

	// Start the interactive shell
	if err := session.Shell(); err != nil {
		return fmt.Errorf("failed to start shell: %w", err)
	}

	// Wait for the session to end
	if err := session.Wait(); err != nil && err != io.EOF {
		return fmt.Errorf("session error: %w", err)
	}

	return nil
}

func main() {
	// sshConfig := SSHConfig{
	// 	User:       "root",
	// 	Host:       "185.102.139.169",
	// 	Port:       22,
	// 	Password:   "w3Bt8hjge8oV",
	// }

	sshConfig := SSHConfig{
		User:     "user",
		Host:     "185.102.139.169",
		Port:     2288,
		Password: "123",
	}

	client, err := NewSSHClient(sshConfig)
	if err != nil {
		log.Fatalf("Error creating SSH client: %v", err)
	}
	defer client.Close()

	// Start the interactive shell
	if err := StartInteractiveShell(client); err != nil {
		log.Fatalf("Error starting interactive shell: %v", err)
	}
}
