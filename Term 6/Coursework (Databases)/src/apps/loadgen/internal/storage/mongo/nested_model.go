package mongo

import (
	"context"

	"loadgen/internal/workload"
)

func (m *MongoEngine) seedNested(ctx context.Context, world workload.World) error {
	db := m.Client.Database(m.NestedDatabase)
	areas := make([]any, 0, len(world.Areas))
	for _, area := range world.Areas {
		areas = append(areas, nestedAreaDocument(area, world))
	}
	if err := replaceAll(ctx, db.Collection("areas"), areas); err != nil {
		return err
	}

	cameras := make([]any, 0, len(world.Cameras))
	for _, camera := range world.Cameras {
		cameras = append(cameras, nestedCameraDocument(camera))
	}
	return replaceAll(ctx, db.Collection("cameras"), cameras)
}

func (m *MongoEngine) insertNestedEvents(ctx context.Context, events []workload.ComplexEvent) (workload.OperationResult, error) {
	docs := make([]any, 0, len(events))
	bytes := 0
	for _, event := range events {
		doc := nestedEventDocument(event)
		bytes += approxBytes(doc)
		docs = append(docs, doc)
	}
	if len(docs) == 0 {
		return workload.OperationResult{}, nil
	}
	_, err := m.Client.Database(m.NestedDatabase).Collection("events").InsertMany(ctx, docs)
	return workload.OperationResult{Rows: len(docs), Bytes: bytes}, err
}

func (m *MongoEngine) insertNestedTelemetry(ctx context.Context, records []workload.Telemetry) (workload.OperationResult, error) {
	docs := make([]any, 0, len(records))
	bytes := 0
	for _, record := range records {
		doc := nestedTelemetryDocument(record)
		bytes += approxBytes(doc)
		docs = append(docs, doc)
	}
	if len(docs) == 0 {
		return workload.OperationResult{}, nil
	}
	_, err := m.Client.Database(m.NestedDatabase).Collection("camera_telemetry").InsertMany(ctx, docs)
	return workload.OperationResult{Rows: len(docs), Bytes: bytes}, err
}

func (m *MongoEngine) aggNestedObjectActivityByArea(ctx context.Context, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	area := world.Areas[req.Rand.Intn(len(world.Areas))]
	from, to := mongoWindow(req.Now)
	return m.aggregate(ctx, m.Client.Database(m.NestedDatabase).Collection("events"), nestedObjectActivityPipeline(area.Code, from, to))
}

func (m *MongoEngine) aggNestedTelemetryHealthWindow(ctx context.Context, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	area := world.Areas[req.Rand.Intn(len(world.Areas))]
	from, to := mongoWindow(req.Now)
	return m.aggregate(ctx, m.Client.Database(m.NestedDatabase).Collection("camera_telemetry"), nestedTelemetryHealthPipeline(area.Code, from, to))
}

func (m *MongoEngine) readNestedIncidentTimeline(ctx context.Context, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	zone := world.Zones[req.Rand.Intn(len(world.Zones))]
	from, to := mongoWindow(req.Now)
	return m.aggregate(ctx, m.Client.Database(m.NestedDatabase).Collection("events"), nestedIncidentTimelinePipeline(zone.Code, from, to))
}

func nestedAreaDocument(area workload.Area, world workload.World) map[string]any {
	zones := make([]map[string]any, 0, world.Profile.ZonesPerArea)
	for _, zone := range world.Zones {
		if zone.AreaCode == area.Code {
			zones = append(zones, map[string]any{
				"zone_code": zone.Code, "name": zone.Name, "zone_type": zone.Type,
				"importance_level": int32(zone.ImportanceLevel), "description": zone.Description,
			})
		}
	}

	return map[string]any{
		"_id": area.ID, "area_code": area.Code, "name": area.Name, "area_type": area.Type,
		"address": area.Address, "description": area.Description, "zones": zones,
	}
}

func nestedCameraDocument(camera workload.Camera) map[string]any {
	return map[string]any{
		"_id": camera.ID, "serial_number": camera.SerialNumber, "name": camera.Name, "model": camera.Model,
		"ip_address": camera.IPAddress, "status": camera.Status,
		"area":     map[string]any{"area_code": camera.AreaCode, "name": camera.AreaName},
		"zone":     map[string]any{"zone_code": camera.ZoneCode, "name": camera.ZoneName, "zone_type": camera.ZoneType},
		"position": camera.Position, "settings": camera.Settings,
	}
}

func nestedEventDocument(event workload.ComplexEvent) map[string]any {
	cameras := make([]map[string]any, 0, len(event.Cameras))
	for _, camera := range event.Cameras {
		cameras = append(cameras, map[string]any{"serial_number": camera.SerialNumber, "name": camera.Name})
	}

	return map[string]any{
		"_id": event.ID, "event_number": event.EventNumber, "occurred_at": event.OccurredAt,
		"event_type": event.EventType, "severity": event.Severity, "confidence": event.Confidence,
		"area":    map[string]any{"area_code": event.AreaCode, "name": event.AreaName},
		"zone":    map[string]any{"zone_code": event.ZoneCode, "name": event.ZoneName, "zone_type": event.ZoneType, "importance_level": int32(event.ZoneImportance)},
		"cameras": cameras, "payload": event.Payload,
	}
}

func nestedTelemetryDocument(record workload.Telemetry) map[string]any {
	return map[string]any{
		"_id": record.ID, "recorded_at": record.RecordedAt,
		"camera": map[string]any{"serial_number": record.Camera.SerialNumber, "name": record.Camera.Name},
		"area":   map[string]any{"area_code": record.Camera.AreaCode, "name": record.Camera.AreaName},
		"zone":   map[string]any{"zone_code": record.Camera.ZoneCode, "name": record.Camera.ZoneName},
		"status": record.Status, "metrics": record.Metrics,
	}
}
