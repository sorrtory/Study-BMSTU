package mongo

import (
	"context"

	"loadgen/internal/workload"
)

func (m *MongoEngine) seedNormalized(ctx context.Context, world workload.World) error {
	db := m.Client.Database(m.NormalizedDatabase)

	areas := make([]any, 0, len(world.Areas))
	for _, area := range world.Areas {
		areas = append(areas, normalizedAreaDocument(area))
	}
	if err := replaceAll(ctx, db.Collection("areas"), areas); err != nil {
		return err
	}

	zones := make([]any, 0, len(world.Zones))
	for _, zone := range world.Zones {
		zones = append(zones, normalizedZoneDocument(zone))
	}
	if err := replaceAll(ctx, db.Collection("zones"), zones); err != nil {
		return err
	}

	cameras := make([]any, 0, len(world.Cameras))
	for _, camera := range world.Cameras {
		cameras = append(cameras, normalizedCameraDocument(camera))
	}
	return replaceAll(ctx, db.Collection("cameras"), cameras)
}

func (m *MongoEngine) insertNormalizedEvents(ctx context.Context, events []workload.ComplexEvent) (workload.OperationResult, error) {
	eventDocs := make([]any, 0, len(events))
	linkDocs := make([]any, 0, len(events))
	bytes := 0
	for _, event := range events {
		doc := normalizedEventDocument(event)
		eventDocs = append(eventDocs, doc)
		bytes += approxBytes(doc)
		linkDocs = append(linkDocs, normalizedEventCameraDocuments(event)...)
	}

	db := m.Client.Database(m.NormalizedDatabase)
	if len(eventDocs) > 0 {
		if _, err := db.Collection("events").InsertMany(ctx, eventDocs); err != nil {
			return workload.OperationResult{}, err
		}
	}
	if len(linkDocs) > 0 {
		if _, err := db.Collection("event_cameras").InsertMany(ctx, linkDocs); err != nil {
			return workload.OperationResult{}, err
		}
	}
	return workload.OperationResult{Rows: len(eventDocs), Bytes: bytes}, nil
}

func (m *MongoEngine) insertNormalizedTelemetry(ctx context.Context, records []workload.Telemetry) (workload.OperationResult, error) {
	docs := make([]any, 0, len(records))
	bytes := 0
	for _, record := range records {
		doc := normalizedTelemetryDocument(record)
		bytes += approxBytes(doc)
		docs = append(docs, doc)
	}
	if len(docs) == 0 {
		return workload.OperationResult{}, nil
	}
	_, err := m.Client.Database(m.NormalizedDatabase).Collection("camera_telemetry").InsertMany(ctx, docs)
	return workload.OperationResult{Rows: len(docs), Bytes: bytes}, err
}

func (m *MongoEngine) aggNormalizedObjectActivityByArea(ctx context.Context, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	area := world.Areas[req.Rand.Intn(len(world.Areas))]
	from, to := mongoWindow(req.Now)
	return m.aggregate(ctx, m.Client.Database(m.NormalizedDatabase).Collection("events"), normalizedObjectActivityPipeline(area.Code, from, to))
}

func (m *MongoEngine) aggNormalizedTelemetryHealthWindow(ctx context.Context, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	area := world.Areas[req.Rand.Intn(len(world.Areas))]
	from, to := mongoWindow(req.Now)
	return m.aggregate(ctx, m.Client.Database(m.NormalizedDatabase).Collection("camera_telemetry"), normalizedTelemetryHealthPipeline(area.Code, from, to))
}

func (m *MongoEngine) readNormalizedIncidentTimeline(ctx context.Context, req workload.OperationRequest) (workload.OperationResult, error) {
	world := workload.GenerateWorld(req.Seed, req.Profile)
	zone := world.Zones[req.Rand.Intn(len(world.Zones))]
	from, to := mongoWindow(req.Now)
	return m.aggregate(ctx, m.Client.Database(m.NormalizedDatabase).Collection("events"), normalizedIncidentTimelinePipeline(zone.Code, from, to))
}

func normalizedAreaDocument(area workload.Area) map[string]any {
	return map[string]any{
		"_id": area.ID, "area_code": area.Code, "name": area.Name, "area_type": area.Type,
		"address": area.Address, "description": area.Description,
	}
}

func normalizedZoneDocument(zone workload.Zone) map[string]any {
	return map[string]any{
		"_id": zone.ID, "zone_code": zone.Code, "name": zone.Name,
		"zone_type": zone.Type, "importance_level": int32(zone.ImportanceLevel),
		"description": zone.Description, "area": ref("areas", zone.AreaID),
	}
}

func normalizedCameraDocument(camera workload.Camera) map[string]any {
	return map[string]any{
		"_id": camera.ID, "serial_number": camera.SerialNumber, "name": camera.Name,
		"model": camera.Model, "ip_address": camera.IPAddress, "status": camera.Status,
		"zone": ref("zones", camera.ZoneID), "position": camera.Position, "settings": camera.Settings,
	}
}

func normalizedEventDocument(event workload.ComplexEvent) map[string]any {
	return map[string]any{
		"_id": event.ID, "event_number": event.EventNumber, "occurred_at": event.OccurredAt,
		"event_type": event.EventType, "severity": event.Severity, "confidence": event.Confidence,
		"zone": ref("zones", event.ZoneID), "payload": event.Payload,
	}
}

func normalizedEventCameraDocuments(event workload.ComplexEvent) []any {
	docs := make([]any, 0, len(event.Cameras))
	for _, camera := range event.Cameras {
		docs = append(docs, map[string]any{
			"_id":    event.ID + "-" + camera.ID,
			"event":  ref("events", event.ID),
			"camera": ref("cameras", camera.ID),
		})
	}
	return docs
}

func normalizedTelemetryDocument(record workload.Telemetry) map[string]any {
	return map[string]any{
		"_id": record.ID, "recorded_at": record.RecordedAt,
		"camera": ref("cameras", record.Camera.ID),
		"status": record.Status, "metrics": record.Metrics,
	}
}
