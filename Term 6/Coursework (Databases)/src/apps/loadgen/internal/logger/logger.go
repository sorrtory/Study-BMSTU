package logger

import (
	"io"
	"os"
	"strings"
	"time"

	"github.com/rs/zerolog"
)

type Logger struct {
	zerolog.Logger
}

func NewLogger(environment string) *Logger {
	env := strings.ToLower(environment)

	level := zerolog.InfoLevel
	var output io.Writer = os.Stdout

	if env != "production" && env != "prod" {
		level = zerolog.DebugLevel
		output = zerolog.ConsoleWriter{
			Out:        os.Stdout,
			TimeFormat: time.DateTime,
		}
	}

	l := zerolog.New(output).
		Level(level).
		With().
		Timestamp().
		Caller().
		Logger()

	return &Logger{Logger: l}
}
