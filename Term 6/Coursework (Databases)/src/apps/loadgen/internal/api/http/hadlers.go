package httpapi

import (
	"encoding/json"
	"loadgen/internal/workload"
	"net/http"
	"time"
)

func (s *Server) greet(w http.ResponseWriter, r *http.Request) {
	_, _ = w.Write([]byte("Hello World! " + time.Now().Format(time.RFC3339)))
}

func (s *Server) health(w http.ResponseWriter, r *http.Request) {
	status, err := s.service.HealthCheck()
	if err != nil {
		s.log.Error().Err(err).Msg("health check failed")
		http.Error(w, "service unavailable", http.StatusServiceUnavailable)
		return
	}

	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte(status))
}

func (s *Server) clear(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var req workload.ClearRequest
	if err := decodeJSON(r, &req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	if err := s.service.Clear(r.Context(), req); err != nil {
		s.log.Error().Err(err).Msg("clear failed")
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"status": "ok", "model": req.Model})
}

func (s *Server) seed(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var req workload.SeedRequest
	if err := decodeJSON(r, &req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	if err := s.service.Seed(r.Context(), req); err != nil {
		s.log.Error().Err(err).Msg("seed failed")
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"status": "ok", "model": req.Model, "profile": req.Profile, "seed": req.Seed})
}

func (s *Server) run(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	var req workload.RunRequest
	if err := decodeJSON(r, &req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	summary, err := s.service.Run(r.Context(), req)
	if err != nil {
		s.log.Error().Err(err).Msg("run failed")
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	writeJSON(w, http.StatusOK, summary)
}

func decodeJSON(r *http.Request, dst any) error {
	defer func() {
		_ = r.Body.Close()
	}()
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	return dec.Decode(dst)
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}
