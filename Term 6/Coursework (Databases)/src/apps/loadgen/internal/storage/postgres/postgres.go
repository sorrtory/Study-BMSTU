package postgres

import (
	"context"
	"fmt"
	"loadgen/internal/logger"
	"loadgen/internal/workload"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresEngine struct {
	log      *logger.Logger
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	ConnPool *pgxpool.Pool
}

func NewPostgresEngine(log *logger.Logger, host string, port int, user, password, dbName string) *PostgresEngine {
	if log == nil {
		panic("logger cannot be nil")
	}
	if host == "" {
		panic("host cannot be empty")
	}
	if port <= 0 {
		panic("port must be a positive integer")
	}
	if user == "" {
		panic("user cannot be empty")
	}
	if password == "" {
		panic("password cannot be empty")
	}
	if dbName == "" {
		panic("dbName cannot be empty")
	}
	return &PostgresEngine{
		log:      log,
		Host:     host,
		Port:     port,
		User:     user,
		Password: password,
		DBName:   dbName,
	}
}

func (p *PostgresEngine) Connect(numberOfConnections int) error {
	connectionString := fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=disable",
		p.User, p.Password, p.Host, p.Port, p.DBName)

	// Configure connection pool
	dbConfig, err := pgxpool.ParseConfig(connectionString)
	if err != nil {
		return fmt.Errorf("failed to parse Postgres connection string: %w", err)
	}
	dbConfig.MaxConns = int32(numberOfConnections)
	dbConfig.MinConns = int32(numberOfConnections)
	dbConfig.MaxConnLifetime = time.Hour
	dbConfig.MaxConnIdleTime = 30 * time.Minute
	dbConfig.HealthCheckPeriod = time.Minute

	// Create connection pool
	conn, err := pgxpool.NewWithConfig(context.Background(), dbConfig)
	if err != nil {
		return fmt.Errorf("failed to connect to Postgres: %w", err)
	}
	p.ConnPool = conn
	return nil
}

func (p *PostgresEngine) Ping() error {
	if p.ConnPool == nil {
		return fmt.Errorf("connection pool is not initialized")
	}
	return p.ConnPool.Ping(context.Background())
}

func (p *PostgresEngine) Close() error {
	if p.ConnPool != nil {
		p.ConnPool.Close()
	}
	return nil
}

func (p *PostgresEngine) Status() (string, error) {
	if p.ConnPool == nil {
		return "disconnected", nil
	}

	stat := p.ConnPool.Stat()
	status := fmt.Sprintf(
		"acquired: %d, idle: %d, total: %d, empty acquire count: %d, acquire duration: %s",
		stat.AcquiredConns(),
		stat.IdleConns(),
		stat.TotalConns(),
		stat.EmptyAcquireCount(),
		stat.AcquireDuration(),
	)

	return status, nil
}

func (p *PostgresEngine) ChangePoolSize(newSize int) error {
	if p.ConnPool == nil {
		return fmt.Errorf("connection pool is not initialized")
	}
	if newSize <= 0 {
		return fmt.Errorf("new pool size must be a positive integer")
	}

	config := p.ConnPool.Config()
	config.MaxConns = int32(newSize)
	config.MinConns = int32(newSize)

	newPool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		return fmt.Errorf("failed to resize Postgres connection pool: %w", err)
	}

	oldPool := p.ConnPool
	p.ConnPool = newPool
	go oldPool.Close()

	return nil
}

func (p *PostgresEngine) GetType() string {
	return "postgres"
}

func (p *PostgresEngine) Clear(ctx context.Context, model string) error {
	switch model {
	case workload.ModelPGJSONB:
		_, err := p.ConnPool.Exec(ctx, clearJSONB)
		return err
	case workload.ModelPGNormalized:
		_, err := p.ConnPool.Exec(ctx, clearNormalized)
		return err
	default:
		return fmt.Errorf("unsupported Postgres model: %s", model)
	}
}

func (p *PostgresEngine) Seed(ctx context.Context, model string, world workload.World) error {
	switch model {
	case workload.ModelPGJSONB:
		return p.seedJSONB(ctx, world)
	case workload.ModelPGNormalized:
		return p.seedNormalized(ctx, world)
	default:
		return fmt.Errorf("unsupported Postgres model: %s", model)
	}
}

func (p *PostgresEngine) WriteComplexEventBatch(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	events := workload.GenerateEvents(req)
	switch model {
	case workload.ModelPGJSONB:
		return p.insertJSONBEvents(ctx, events)
	case workload.ModelPGNormalized:
		return p.insertNormalizedEvents(ctx, events)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported Postgres model: %s", model)
	}
}

func (p *PostgresEngine) WriteTelemetryStream(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	records := workload.GenerateTelemetry(req)
	switch model {
	case workload.ModelPGJSONB:
		return p.insertJSONBTelemetry(ctx, records)
	case workload.ModelPGNormalized:
		return p.insertNormalizedTelemetry(ctx, records)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported Postgres model: %s", model)
	}
}

func (p *PostgresEngine) AggObjectActivityByArea(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	area := world.Areas[req.Rand.Intn(len(world.Areas))]
	from, to := window(req.Now)
	query := aggJSONBObjectActivity
	if model == workload.ModelPGNormalized {
		query = aggNormalizedObjectActivity
	}
	return p.scanRows(ctx, query, area.Code, from, to)
}

func (p *PostgresEngine) AggTelemetryHealthWindow(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	area := world.Areas[req.Rand.Intn(len(world.Areas))]
	from, to := window(req.Now)
	query := aggJSONBTelemetryHealth
	if model == workload.ModelPGNormalized {
		query = aggNormalizedTelemetryHealth
	}
	return p.scanRows(ctx, query, area.Code, from, to)
}

func (p *PostgresEngine) ReadIncidentTimeline(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	zone := world.Zones[req.Rand.Intn(len(world.Zones))]
	from, to := window(req.Now)
	query := readJSONBIncidentTimeline
	if model == workload.ModelPGNormalized {
		query = readNormalizedIncidentTimeline
	}
	return p.scanRows(ctx, query, zone.Code, from, to)
}
