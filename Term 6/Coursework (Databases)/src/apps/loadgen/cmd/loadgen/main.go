package main

import (
	httpapi "loadgen/internal/api/http"
	"loadgen/internal/app"
	"loadgen/internal/config"
	"loadgen/internal/logger"
	"loadgen/internal/storage"
)

// Run from project root or from apps/loadgen.
var PossibleEnvLocations = []string{".env", "../../.env"}

func main() {
	// Read config
	cfg, err := config.NewConfig(PossibleEnvLocations)
	if err != nil {
		panic(err)
	}

	// Init logger
	log := logger.NewLogger(cfg.Environment)
	log.Logger = log.With().
		Str("target_db", cfg.TargetDB).
		Logger()
	log.Debug().Msg("Logger initialized")

	// Init storage engine
	storageEngine, err := storage.NewStorageEngine(log, *cfg)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to initialize storage engine")
	}
	log.Debug().Msg("Storage engine initialized")

	// Init storage
	storageService := storage.NewStorage(log, storageEngine)
	if err := storageService.Init(cfg.ConnectionPoolSize); err != nil {
		log.Fatal().Err(err).Msg("Failed to initialize storage")
	}
	defer func() {
		if err := storageService.Close(); err != nil {
			log.Error().Err(err).Msg("Failed to close storage")
		}
	}()
	log.Debug().Msg("Storage initialized")

	// Init app
	application := app.NewApp(log, storageService)

	// Start API server...
	httpServer := httpapi.NewServer(log, application, cfg.Port)
	if err := httpServer.Listen(); err != nil {
		log.Fatal().Err(err).Msg("HTTP server stopped")
	}
}
