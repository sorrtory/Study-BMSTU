package postgres

import (
	"context"

	"loadgen/internal/workload"

	"github.com/jackc/pgx/v5"
)

func (p *PostgresEngine) seedNormalized(ctx context.Context, world workload.World) error {
	tx, err := p.ConnPool.Begin(ctx)
	if err != nil {
		return err
	}
	defer rollback(ctx, tx)

	for _, area := range world.Areas {
		if _, err := tx.Exec(ctx, insertNormalizedArea, area.Type, area.Code, area.Name, area.Address, area.Description); err != nil {
			return err
		}
	}
	for _, zone := range world.Zones {
		if _, err := tx.Exec(ctx, insertNormalizedZone, zone.AreaCode, zone.Type, zone.Code, zone.Name, zone.ImportanceLevel, zone.Description); err != nil {
			return err
		}
	}
	for _, camera := range world.Cameras {
		if err := p.seedNormalizedCamera(ctx, tx, camera); err != nil {
			return err
		}
	}
	return tx.Commit(ctx)
}

func (p *PostgresEngine) seedNormalizedCamera(ctx context.Context, tx pgx.Tx, camera workload.Camera) error {
	position := camera.Position
	if _, err := tx.Exec(ctx, insertNormalizedCamera,
		camera.AreaCode, camera.ZoneCode, camera.SerialNumber, camera.Name, camera.Model, camera.IPAddress,
		position["x"], position["y"], position["z"], position["yaw_angle"], position["pitch_angle"], position["roll_angle"], position["view_angle"], camera.Status,
	); err != nil {
		return err
	}

	stream := nestedMap(camera.Settings, "stream")
	if _, err := tx.Exec(ctx, insertNormalizedStreamSetting,
		camera.SerialNumber, stream["resolution_width"], stream["resolution_height"], stream["fps"], stream["bitrate_kbps"], stream["rtsp_enabled"], stream["video_codec"],
	); err != nil {
		return err
	}

	analytics := nestedMap(camera.Settings, "analytics")
	if _, err := tx.Exec(ctx, insertNormalizedAnalyticsSetting,
		camera.SerialNumber, analytics["motion_detection"], analytics["line_crossing"], analytics["object_detection"], analytics["sensitivity"], analytics["min_object_confidence"],
	); err != nil {
		return err
	}

	return p.seedNormalizedCameraGeometry(ctx, tx, camera.SerialNumber)
}

func (p *PostgresEngine) seedNormalizedCameraGeometry(ctx context.Context, tx pgx.Tx, serialNumber string) error {
	if _, err := tx.Exec(ctx, insertNormalizedDetectionZone, serialNumber, "DZ-1"); err != nil {
		return err
	}

	// The deterministic generator creates one rectangular detection zone and one crossing line.
	// Keeping these constants here makes event detail inserts independent of the JSON settings shape.
	for i, point := range []struct{ x, y float64 }{{0, 0}, {1, 0}, {1, 1}, {0, 1}} {
		if _, err := tx.Exec(ctx, insertNormalizedDetectionPoint, serialNumber, "DZ-1", i+1, point.x, point.y); err != nil {
			return err
		}
	}
	_, err := tx.Exec(ctx, insertNormalizedCrossingLine, serialNumber, "unknown", "CL-1", "Main line", 0.1, 0.5, 0.9, 0.5)
	return err
}

func (p *PostgresEngine) insertNormalizedEvents(ctx context.Context, events []workload.ComplexEvent) (workload.OperationResult, error) {
	tx, err := p.ConnPool.Begin(ctx)
	if err != nil {
		return workload.OperationResult{}, err
	}
	defer rollback(ctx, tx)

	rows := 0
	bytes := 0
	for _, event := range events {
		eventID, err := p.insertNormalizedEventBase(ctx, tx, event)
		if err != nil {
			return workload.OperationResult{}, err
		}
		if err := p.insertNormalizedEventCameras(ctx, tx, eventID, event.Cameras); err != nil {
			return workload.OperationResult{}, err
		}
		if err := p.insertNormalizedEventDetail(ctx, tx, eventID, event); err != nil {
			return workload.OperationResult{}, err
		}
		payload, _ := jsonBytes(event.Payload)
		bytes += len(payload)
		rows++
	}
	return workload.OperationResult{Rows: rows, Bytes: bytes}, tx.Commit(ctx)
}

func (p *PostgresEngine) insertNormalizedEventBase(ctx context.Context, tx pgx.Tx, event workload.ComplexEvent) (int64, error) {
	var eventID int64
	err := tx.QueryRow(
		ctx,
		insertNormalizedEvent,
		event.AreaCode,
		event.ZoneCode,
		event.EventNumber,
		event.OccurredAt,
		event.Confidence,
		event.EventType,
		event.Severity,
	).Scan(&eventID)
	return eventID, err
}

func (p *PostgresEngine) insertNormalizedEventCameras(ctx context.Context, tx pgx.Tx, eventID int64, cameras []workload.Camera) error {
	for _, camera := range cameras {
		if _, err := tx.Exec(ctx, insertNormalizedEventCamera, eventID, camera.SerialNumber); err != nil {
			return err
		}
	}
	return nil
}

func (p *PostgresEngine) insertNormalizedEventDetail(ctx context.Context, tx pgx.Tx, eventID int64, event workload.ComplexEvent) error {
	// Each event type owns a different detail table in the normalized schema.
	// Keep the dispatcher small and let dedicated helpers handle table-specific fields.
	switch event.EventType {
	case "motion_detected":
		return p.insertNormalizedMotionDetail(ctx, tx, eventID, event)
	case "line_crossing":
		return p.insertNormalizedLineCrossingDetail(ctx, tx, eventID, event)
	case "signal_lost":
		return p.insertNormalizedSignalLostDetail(ctx, tx, eventID, event)
	default:
		return p.insertNormalizedObjectDetectionDetail(ctx, tx, eventID, event)
	}
}

func (p *PostgresEngine) insertNormalizedMotionDetail(ctx context.Context, tx pgx.Tx, eventID int64, event workload.ComplexEvent) error {
	payload := event.Payload
	_, err := tx.Exec(
		ctx,
		insertNormalizedMotionDetail,
		eventID,
		event.Cameras[0].SerialNumber,
		intValue(payload["frame_time_ms"]),
		floatValue(payload["motion_area_percent"]),
		intValue(payload["duration_ms"]),
	)
	if err != nil {
		return err
	}
	return p.insertDetectedObjects(ctx, tx, eventID, payload)
}

func (p *PostgresEngine) insertNormalizedObjectDetectionDetail(ctx context.Context, tx pgx.Tx, eventID int64, event workload.ComplexEvent) error {
	payload := event.Payload
	if _, err := tx.Exec(ctx, insertNormalizedObjectDetail, eventID, intValue(payload["frame_time_ms"])); err != nil {
		return err
	}
	return p.insertDetectedObjects(ctx, tx, eventID, payload)
}

func (p *PostgresEngine) insertNormalizedLineCrossingDetail(ctx context.Context, tx pgx.Tx, eventID int64, event workload.ComplexEvent) error {
	payload := event.Payload
	_, err := tx.Exec(
		ctx,
		insertNormalizedLineCrossingDetail,
		eventID,
		event.Cameras[0].SerialNumber,
		stringValue(payload["direction"], "unknown"),
		intValue(payload["frame_time_ms"]),
	)
	if err != nil {
		return err
	}
	return p.insertDetectedObjects(ctx, tx, eventID, payload)
}

func (p *PostgresEngine) insertNormalizedSignalLostDetail(ctx context.Context, tx pgx.Tx, eventID int64, event workload.ComplexEvent) error {
	payload := event.Payload
	_, err := tx.Exec(
		ctx,
		insertNormalizedSignalLostDetail,
		eventID,
		stringValue(payload["reason"], "network_timeout"),
		event.OccurredAt.Add(-eventTelemetryLookback),
		intValue(payload["downtime_seconds"]),
	)
	return err
}

func (p *PostgresEngine) insertDetectedObjects(ctx context.Context, tx pgx.Tx, eventID int64, payload workload.EventPayload) error {
	objects, ok := payload["objects"].([]workload.JSONMap)
	if !ok {
		return nil
	}
	// Object rows are common for motion/object/line events; optional attributes
	// are split only when the object type has its own attribute table.
	for _, object := range objects {
		objectID, err := p.insertDetectedObject(ctx, tx, eventID, object)
		if err != nil {
			return err
		}
		if err := p.insertDetectedObjectAttributes(ctx, tx, objectID, object); err != nil {
			return err
		}
	}
	return nil
}

func (p *PostgresEngine) insertDetectedObject(ctx context.Context, tx pgx.Tx, eventID int64, object workload.JSONMap) (int64, error) {
	box := nestedMap(object, "bounding_box")
	var objectID int64
	err := tx.QueryRow(
		ctx,
		insertNormalizedDetectedObject,
		eventID,
		stringValue(object["object_type"], "unknown"),
		intValue(object["object_number"]),
		floatValue(object["confidence"]),
		intValue(box["x"]),
		intValue(box["y"]),
		intValue(box["width"]),
		intValue(box["height"]),
	).Scan(&objectID)
	return objectID, err
}

func (p *PostgresEngine) insertDetectedObjectAttributes(ctx context.Context, tx pgx.Tx, objectID int64, object workload.JSONMap) error {
	attrs := nestedMap(object, "attributes")
	switch stringValue(object["object_type"], "unknown") {
	case "person":
		_, err := tx.Exec(ctx, insertNormalizedPersonAttributes, objectID, stringValue(attrs["direction"], "unknown"), boolValue(attrs["has_bag"]), stringValue(attrs["clothing_color"], ""))
		return err
	case "vehicle":
		_, err := tx.Exec(ctx, insertNormalizedVehicleAttributes, objectID, stringValue(attrs["color"], ""), stringValue(attrs["license_plate"], ""), floatValue(attrs["license_plate_confidence"]))
		return err
	default:
		return nil
	}
}

func (p *PostgresEngine) insertNormalizedTelemetry(ctx context.Context, records []workload.Telemetry) (workload.OperationResult, error) {
	tx, err := p.ConnPool.Begin(ctx)
	if err != nil {
		return workload.OperationResult{}, err
	}
	defer rollback(ctx, tx)

	bytes := 0
	for _, record := range records {
		metrics := record.Metrics
		raw, _ := jsonBytes(metrics)
		bytes += len(raw)
		if _, err := tx.Exec(ctx, insertNormalizedTelemetry,
			record.Camera.SerialNumber,
			record.RecordedAt,
			record.Status,
			metrics["temperature_celsius"],
			metrics["cpu_load"],
			metrics["memory_usage"],
			metrics["bitrate_kbps"],
			metrics["packet_loss"],
			metrics["latency_ms"],
			metrics["uptime_seconds"],
		); err != nil {
			return workload.OperationResult{}, err
		}
	}
	return workload.OperationResult{Rows: len(records), Bytes: bytes}, tx.Commit(ctx)
}
