package storage

import (
	"context"
	"fmt"
	"loadgen/internal/config"
	"loadgen/internal/logger"
	"loadgen/internal/storage/mongo"
	"loadgen/internal/storage/postgres"
	"loadgen/internal/workload"
)

type StorageEngine interface {
	Connect(numberOfConnections int) error
	Ping() error
	Status() (string, error)
	Close() error
	ChangePoolSize(newSize int) error
	GetType() string
	Clear(ctx context.Context, model string) error
	Seed(ctx context.Context, model string, world workload.World) error
	WriteComplexEventBatch(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error)
	WriteTelemetryStream(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error)
	AggObjectActivityByArea(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error)
	AggTelemetryHealthWindow(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error)
	ReadIncidentTimeline(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error)
}

func NewStorageEngine(log *logger.Logger, cfg config.Config) (StorageEngine, error) {
	switch cfg.TargetDB {
	case "postgres":
		return postgres.NewPostgresEngine(
			log,
			cfg.PostgresHost,
			cfg.PostgresPort,
			cfg.PostgresUser,
			cfg.PostgresPass,
			cfg.PostgresDB,
		), nil

	case "mongo":
		return mongo.NewMongoEngine(
			log,
			cfg.MongoHost,
			cfg.MongoPort,
			cfg.MongoUser,
			cfg.MongoPass,
			cfg.MongoDB,
			cfg.MongoNestedDB,
			cfg.MongoNormalizedDB,
		), nil
	default:
		return nil, fmt.Errorf("unsupported target database: %s", cfg.TargetDB)
	}
}
