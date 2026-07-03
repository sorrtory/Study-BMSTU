package storage

import (
	"context"
	"loadgen/internal/logger"
	"loadgen/internal/workload"
	"time"
)

type Storage struct {
	log    *logger.Logger
	engine StorageEngine
}

func NewStorage(log *logger.Logger, engine StorageEngine) *Storage {
	if log == nil {
		panic("logger cannot be nil")
	}
	if engine == nil {
		panic("storage engine cannot be nil")
	}
	return &Storage{
		log:    log,
		engine: engine,
	}
}

func (s *Storage) Init(connNumber int) error {
	s.log.Info().Msg("Initializing storage")
	if err := s.engine.Connect(connNumber); err != nil {
		return err
	}
	if err := s.engine.Ping(); err != nil {
		return err
	}
	s.log.Info().Msg("Storage initialized successfully")
	return nil
}

func (s *Storage) Close() error {
	s.log.Info().Msg("Closing storage")
	return s.engine.Close()
}

func (s *Storage) Status() (string, error) {
	s.log.Info().Msg("Checking storage status")
	output, err := s.engine.Status()
	if err != nil {
		s.log.Error().Err(err).Msg("Failed to get storage status")
		return "error", err
	}
	output = `Database: ` + s.engine.GetType() + "\n" +
		`Time: ` + time.Now().Format(time.DateTime) + "\n" +
		`Status: ` + output
	return output, nil
}

func (s *Storage) ChangePoolSize(newSize int) error {
	s.log.Info().Int("new_size", newSize).Msg("Changing connection pool size")
	return s.engine.ChangePoolSize(newSize)
}

func (s *Storage) TargetDB() string {
	return s.engine.GetType()
}

func (s *Storage) Clear(ctx context.Context, model string) error {
	s.log.Info().Str("model", model).Msg("Clearing model data")
	return s.engine.Clear(ctx, model)
}

func (s *Storage) Seed(ctx context.Context, model string, world workload.World) error {
	s.log.Info().
		Str("model", model).
		Str("profile", world.Profile.Name).
		Int64("seed", world.Seed).
		Msg("Seeding model data")
	return s.engine.Seed(ctx, model, world)
}

func (s *Storage) ExecuteOperation(ctx context.Context, operation string, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	switch operation {
	case workload.OpWriteComplexEvent:
		return s.engine.WriteComplexEventBatch(ctx, model, req)
	case workload.OpWriteTelemetry:
		return s.engine.WriteTelemetryStream(ctx, model, req)
	case workload.OpAggObjectActivity:
		return s.engine.AggObjectActivityByArea(ctx, model, req)
	case workload.OpAggTelemetryHealth:
		return s.engine.AggTelemetryHealthWindow(ctx, model, req)
	case workload.OpReadIncidentTimeline:
		return s.engine.ReadIncidentTimeline(ctx, model, req)
	default:
		return workload.OperationResult{}, nil
	}
}
