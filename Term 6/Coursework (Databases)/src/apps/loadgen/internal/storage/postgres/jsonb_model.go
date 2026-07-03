package postgres

import (
	"context"

	"loadgen/internal/workload"
)

func (p *PostgresEngine) seedJSONB(ctx context.Context, world workload.World) error {
	tx, err := p.ConnPool.Begin(ctx)
	if err != nil {
		return err
	}
	defer rollback(ctx, tx)

	for _, area := range world.Areas {
		if _, err := tx.Exec(ctx, insertJSONBArea, area.Code, area.Name, area.Type, area.Address, area.Description); err != nil {
			return err
		}
	}
	for _, zone := range world.Zones {
		if _, err := tx.Exec(ctx, insertJSONBZone, zone.AreaCode, zone.Code, zone.Name, zone.Type, zone.ImportanceLevel, zone.Description); err != nil {
			return err
		}
	}
	for _, camera := range world.Cameras {
		position, err := jsonBytes(camera.Position)
		if err != nil {
			return err
		}
		settings, err := jsonBytes(camera.Settings)
		if err != nil {
			return err
		}
		if _, err := tx.Exec(ctx, insertJSONBCamera, camera.AreaCode, camera.ZoneCode, camera.SerialNumber, camera.Name, camera.Model, camera.IPAddress, camera.Status, position, settings); err != nil {
			return err
		}
	}
	return tx.Commit(ctx)
}

func (p *PostgresEngine) insertJSONBEvents(ctx context.Context, events []workload.ComplexEvent) (workload.OperationResult, error) {
	tx, err := p.ConnPool.Begin(ctx)
	if err != nil {
		return workload.OperationResult{}, err
	}
	defer rollback(ctx, tx)

	bytes := 0
	for _, event := range events {
		// JSONB keeps type-specific event data in one payload; only camera links stay relational.
		payload, err := jsonBytes(event.Payload)
		if err != nil {
			return workload.OperationResult{}, err
		}
		bytes += len(payload)
		for _, camera := range event.Cameras {
			if _, err := tx.Exec(ctx, insertJSONBEvent, event.AreaCode, event.ZoneCode, event.EventNumber, event.OccurredAt, event.EventType, event.Severity, event.Confidence, payload, camera.SerialNumber); err != nil {
				return workload.OperationResult{}, err
			}
		}
	}
	return workload.OperationResult{Rows: len(events), Bytes: bytes}, tx.Commit(ctx)
}

func (p *PostgresEngine) insertJSONBTelemetry(ctx context.Context, records []workload.Telemetry) (workload.OperationResult, error) {
	tx, err := p.ConnPool.Begin(ctx)
	if err != nil {
		return workload.OperationResult{}, err
	}
	defer rollback(ctx, tx)

	bytes := 0
	for _, record := range records {
		metrics, err := jsonBytes(record.Metrics)
		if err != nil {
			return workload.OperationResult{}, err
		}
		bytes += len(metrics)
		if _, err := tx.Exec(ctx, insertJSONBTelemetry, record.Camera.SerialNumber, record.RecordedAt, record.Status, metrics); err != nil {
			return workload.OperationResult{}, err
		}
	}
	return workload.OperationResult{Rows: len(records), Bytes: bytes}, tx.Commit(ctx)
}
