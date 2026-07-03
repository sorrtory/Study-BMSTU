package app

import (
	"context"
	"fmt"
	"math/rand"
	"net/http"
	"strconv"
	"sync"
	"time"

	"loadgen/internal/logger"
	loadmetrics "loadgen/internal/metrics"
	"loadgen/internal/storage"
	"loadgen/internal/workload"
)

type App struct {
	storage *storage.Storage
	log     *logger.Logger
	metrics *loadmetrics.Metrics
}

func NewApp(log *logger.Logger, storage *storage.Storage) *App {
	if log == nil {
		panic("logger cannot be nil")
	}
	if storage == nil {
		panic("storage cannot be nil")
	}
	return &App{
		log:     log,
		storage: storage,
		metrics: loadmetrics.New(),
	}
}

func (a *App) HealthCheck() (string, error) {
	a.log.Info().Msg("Health check passed")
	status, err := a.storage.Status()
	if err != nil {
		return "error", err
	}

	return status, nil
}

func (a *App) Clear(ctx context.Context, req workload.ClearRequest) error {
	if err := workload.ValidateModelForTarget(req.Model, a.storage.TargetDB()); err != nil {
		return err
	}
	return a.storage.Clear(ctx, req.Model)
}

func (a *App) Seed(ctx context.Context, req workload.SeedRequest) error {
	if err := workload.ValidateModelForTarget(req.Model, a.storage.TargetDB()); err != nil {
		return err
	}
	if err := workload.ValidateSeed(req.Seed); err != nil {
		return err
	}
	profile, err := workload.ProfileByName(req.Profile)
	if err != nil {
		return err
	}
	world := workload.GenerateWorld(req.Seed, profile)
	return a.storage.Seed(ctx, req.Model, world)
}

func (a *App) Run(ctx context.Context, req workload.RunRequest) (workload.RunSummary, error) {
	if err := workload.ValidateModelForTarget(req.Model, a.storage.TargetDB()); err != nil {
		return workload.RunSummary{}, err
	}
	req, profile, err := workload.DefaultRunRequest(req)
	if err != nil {
		return workload.RunSummary{}, err
	}

	summary := workload.RunSummary{
		RunID: req.RunID, Model: req.Model, Scenario: req.Scenario,
		StartedAt: time.Now(), Totals: map[string]workload.OperationStats{},
	}
	for _, clients := range req.Stages {
		if clients <= 0 {
			return workload.RunSummary{}, fmt.Errorf("stage client count must be positive")
		}
		stageStats, err := a.runStage(ctx, req, profile, clients)
		if err != nil {
			return workload.RunSummary{}, err
		}
		summary.Stages = append(summary.Stages, workload.StageSummary{Clients: clients, Stats: stageStats})
		workload.AddStats(summary.Totals, stageStats)
	}
	summary.FinishedAt = time.Now()
	return summary, nil
}

func (a *App) MetricsHandler() http.Handler {
	return a.metrics.Handler()
}

func (a *App) runStage(ctx context.Context, req workload.RunRequest, profile workload.SizeProfile, clients int) (map[string]workload.OperationStats, error) {
	deadline := time.Now().Add(time.Duration(req.DurationSeconds) * time.Second)

	recorder := workload.NewLatencyRecorder()
	var wg sync.WaitGroup
	a.metrics.SetActiveWorkers(req.RunID, req.Model, req.Scenario, clients, clients)
	defer a.metrics.SetActiveWorkers(req.RunID, req.Model, req.Scenario, clients, 0)
	for worker := 0; worker < clients; worker++ {
		workerID := worker
		wg.Add(1)
		go func() {
			defer wg.Done()
			r := rand.New(rand.NewSource(req.Seed + int64(clients*1000) + int64(workerID)))
			for {
				if time.Now().After(deadline) {
					return
				}
				select {
				case <-ctx.Done():
					return
				default:
				}
				operation := workload.ChooseOperation(req.Scenario, r)
				batchSize := req.EventBatchSize
				if operation == workload.OpWriteTelemetry {
					batchSize = req.TelemetryBatchSize
				}
				opReq := workload.OperationRequest{
					Model: req.Model, Seed: req.Seed, Profile: profile,
					Rand: r, BatchSize: batchSize, Now: time.Now(),
				}
				start := time.Now()
				result, err := a.storage.ExecuteOperation(ctx, operation, req.Model, opReq)
				duration := time.Since(start)
				recorder.Observe(operation, duration, result, err)
				a.metrics.ObserveOperation(loadmetrics.OperationLabels{
					RunID:        req.RunID,
					Model:        req.Model,
					Scenario:     req.Scenario,
					Operation:    operation,
					StageClients: strconv.Itoa(clients),
				}, duration.Seconds(), batchSize, result, err)
				if err != nil {
					a.log.Error().Err(err).Str("operation", operation).Str("model", req.Model).Msg("load operation failed")
				}
			}
		}()
	}
	wg.Wait()
	return recorder.Snapshot(), nil
}
