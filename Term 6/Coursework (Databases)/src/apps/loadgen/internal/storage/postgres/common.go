package postgres

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"loadgen/internal/workload"

	"github.com/jackc/pgx/v5"
)

const eventTelemetryLookback = time.Minute

func (p *PostgresEngine) scanRows(ctx context.Context, query string, args ...any) (workload.OperationResult, error) {
	rows, err := p.ConnPool.Query(ctx, query, args...)
	if err != nil {
		return workload.OperationResult{}, err
	}
	defer rows.Close()

	count := 0
	bytes := 0
	for rows.Next() {
		values, err := rows.Values()
		if err != nil {
			return workload.OperationResult{}, err
		}
		count++
		for _, value := range values {
			bytes += len(fmt.Sprint(value))
		}
	}
	return workload.OperationResult{Rows: count, Bytes: bytes}, rows.Err()
}

func jsonBytes(v any) ([]byte, error) {
	return json.Marshal(v)
}

func rollback(ctx context.Context, tx pgx.Tx) {
	_ = tx.Rollback(ctx)
}

func nestedMap(src any, key string) map[string]any {
	var m map[string]any
	switch value := src.(type) {
	case map[string]any:
		m = value
	case workload.JSONMap:
		m = map[string]any(value)
	default:
		return map[string]any{}
	}
	if value, ok := m[key].(map[string]any); ok {
		return value
	}
	if value, ok := m[key].(workload.JSONMap); ok {
		return map[string]any(value)
	}
	return map[string]any{}
}

func intValue(v any) int {
	switch t := v.(type) {
	case int:
		return t
	case int64:
		return int(t)
	case float64:
		return int(t)
	default:
		return 0
	}
}

func floatValue(v any) float64 {
	switch t := v.(type) {
	case float64:
		return t
	case int:
		return float64(t)
	case int64:
		return float64(t)
	default:
		return 0
	}
}

func stringValue(v any, fallback string) string {
	if s, ok := v.(string); ok && s != "" {
		return s
	}
	return fallback
}

func boolValue(v any) bool {
	if b, ok := v.(bool); ok {
		return b
	}
	return false
}

func window(now time.Time) (time.Time, time.Time) {
	return now.Add(-24 * time.Hour), now.Add(time.Hour)
}
