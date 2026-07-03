package httpapi

import (
	"context"
	"net/http"

	"loadgen/internal/logger"
	"loadgen/internal/workload"
)

type Service interface {
	HealthCheck() (string, error)
	Clear(ctx context.Context, req workload.ClearRequest) error
	Seed(ctx context.Context, req workload.SeedRequest) error
	Run(ctx context.Context, req workload.RunRequest) (workload.RunSummary, error)
	MetricsHandler() http.Handler
}

type Server struct {
	port    string
	log     *logger.Logger
	service Service
}

func NewServer(log *logger.Logger, service Service, port string) *Server {
	// We may also want to take `context` here for graceful shutdown in the future

	if log == nil {
		panic("logger cannot be nil")
	}
	if service == nil {
		panic("service cannot be nil")
	}
	if port == "" {
		panic("port cannot be empty")
	}
	return &Server{
		port:    port,
		log:     log,
		service: service,
	}
}

func (s *Server) Listen() error {
	mux := http.NewServeMux()

	// Connect handlers
	mux.HandleFunc("/", s.greet)
	mux.HandleFunc("/health", s.health)
	mux.HandleFunc("/clear", s.clear)
	mux.HandleFunc("/seed", s.seed)
	mux.HandleFunc("/run", s.run)
	mux.Handle("/metrics", s.service.MetricsHandler())

	// Attach middleware
	handler := s.loggingMiddleware(mux)
	handler = s.requestIDMiddleware(handler)
	handler = s.recoveryMiddleware(handler)

	// Start server
	addr := "0.0.0.0:" + s.port
	s.log.Info().
		Str("addr", addr).
		Msg("starting HTTP server")
	return http.ListenAndServe(addr, handler)
}
