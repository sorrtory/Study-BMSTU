package workload

import (
	"math/rand"
	"time"
)

const (
	ModelPGJSONB         = "pg-jsonb"
	ModelPGNormalized    = "pg-normalized"
	ModelMongoNested     = "mongo-nested"
	ModelMongoNormalized = "mongo-normalized"
)

const (
	ScenarioWriteHeavy = "write-heavy"
	ScenarioAnalytics  = "analytics-heavy"
	ScenarioBalanced   = "balanced"
)

const (
	OpWriteComplexEvent    = "WRITE_COMPLEX_EVENT_BATCH"
	OpWriteTelemetry       = "WRITE_TELEMETRY_STREAM"
	OpAggObjectActivity    = "AGG_OBJECT_ACTIVITY_BY_AREA"
	OpAggTelemetryHealth   = "AGG_TELEMETRY_HEALTH_WINDOW"
	OpReadIncidentTimeline = "READ_INCIDENT_TIMELINE"
)

type SizeProfile struct {
	Name           string `json:"name"`
	Areas          int    `json:"areas"`
	ZonesPerArea   int    `json:"zones_per_area"`
	CamerasPerZone int    `json:"cameras_per_zone"`
}

type SeedRequest struct {
	Model   string `json:"model"`
	Seed    int64  `json:"seed"`
	Profile string `json:"profile"`
}

type ClearRequest struct {
	Model string `json:"model"`
}

type RunRequest struct {
	Model              string `json:"model"`
	Scenario           string `json:"scenario"`
	Seed               int64  `json:"seed"`
	Profile            string `json:"profile"`
	RunID              string `json:"run_id"`
	DurationSeconds    int    `json:"duration_seconds"`
	Stages             []int  `json:"stages"`
	EventBatchSize     int    `json:"event_batch_size"`
	TelemetryBatchSize int    `json:"telemetry_batch_size"`
}

type OperationRequest struct {
	Model     string
	Seed      int64
	Profile   SizeProfile
	Rand      *rand.Rand
	BatchSize int
	Now       time.Time
}

type OperationResult struct {
	Rows  int
	Bytes int
}

type RunSummary struct {
	RunID      string                    `json:"run_id"`
	Model      string                    `json:"model"`
	Scenario   string                    `json:"scenario"`
	StartedAt  time.Time                 `json:"started_at"`
	FinishedAt time.Time                 `json:"finished_at"`
	Stages     []StageSummary            `json:"stages"`
	Totals     map[string]OperationStats `json:"totals"`
}

type StageSummary struct {
	Clients int                       `json:"clients"`
	Stats   map[string]OperationStats `json:"stats"`
}

type OperationStats struct {
	Success int64   `json:"success"`
	Errors  int64   `json:"errors"`
	Rows    int64   `json:"rows"`
	Bytes   int64   `json:"bytes"`
	MinMs   float64 `json:"min_ms"`
	P50Ms   float64 `json:"p50_ms"`
	P95Ms   float64 `json:"p95_ms"`
	P99Ms   float64 `json:"p99_ms"`
	MaxMs   float64 `json:"max_ms"`
}

type EventPayload map[string]any
type JSONMap map[string]any

type Area struct {
	ID          string
	Code        string
	Name        string
	Type        string
	Address     string
	Description string
}

type Zone struct {
	ID              string
	AreaID          string
	AreaCode        string
	Code            string
	Name            string
	Type            string
	ImportanceLevel int
	Description     string
}

type Camera struct {
	ID           string
	AreaID       string
	AreaCode     string
	AreaName     string
	ZoneID       string
	ZoneCode     string
	ZoneName     string
	ZoneType     string
	SerialNumber string
	Name         string
	Model        string
	IPAddress    string
	Status       string
	Position     JSONMap
	Settings     JSONMap
}

type ComplexEvent struct {
	ID             string
	EventNumber    int64
	OccurredAt     time.Time
	EventType      string
	Severity       string
	Confidence     float64
	AreaCode       string
	AreaName       string
	ZoneID         string
	ZoneCode       string
	ZoneName       string
	ZoneType       string
	ZoneImportance int
	Cameras        []Camera
	Payload        EventPayload
}

type Telemetry struct {
	ID         string
	RecordedAt time.Time
	Camera     Camera
	Status     string
	Metrics    JSONMap
}

type World struct {
	Profile SizeProfile
	Seed    int64
	Areas   []Area
	Zones   []Zone
	Cameras []Camera
}
