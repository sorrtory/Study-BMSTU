package httpapi

import (
	"context"
	"net/http"
	"strings"

	"github.com/google/uuid"
)

type requestIDContextKey struct{}

func (s *Server) loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		s.log.Debug().Msg("STARTED " + strings.Repeat(">", 50))
		s.log.Info().
			Str("method", r.Method).
			Str("path", r.URL.Path).
			Msg("Request")

		next.ServeHTTP(w, r)

		s.log.Debug().Msg("FINISHED " + strings.Repeat("<", 50))
	})
}

func (s *Server) recoveryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				s.log.Error().Interface("error", err).Msg("Panic recovered in HTTP handler")
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			}
		}()

		next.ServeHTTP(w, r)
	})
}

func (s *Server) requestIDMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := uuid.New().String()

		// Add the request ID to the request context for downstream handlers.
		r = r.WithContext(context.WithValue(r.Context(), requestIDContextKey{}, requestID))

		// Add the request ID to the response header for client reference
		w.Header().Set("X-Request-ID", requestID)

		next.ServeHTTP(w, r)
	})
}
