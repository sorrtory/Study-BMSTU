package postgres

const (
	clearJSONB = `
TRUNCATE TABLE
	jsonb.event_camera,
	jsonb.camera_telemetry,
	jsonb.event,
	jsonb.camera,
	jsonb.zone,
	jsonb.area
RESTART IDENTITY CASCADE`

	insertJSONBArea = `
INSERT INTO jsonb.area (area_code, name, area_type, address, description)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (area_code) DO UPDATE SET
	name = EXCLUDED.name,
	area_type = EXCLUDED.area_type,
	address = EXCLUDED.address,
	description = EXCLUDED.description`

	insertJSONBZone = `
INSERT INTO jsonb.zone (area_id, zone_code, name, zone_type, importance_level, description)
SELECT area_id, $2, $3, $4, $5, $6
FROM jsonb.area
WHERE area_code = $1
ON CONFLICT (area_id, zone_code) DO UPDATE SET
	name = EXCLUDED.name,
	zone_type = EXCLUDED.zone_type,
	importance_level = EXCLUDED.importance_level,
	description = EXCLUDED.description`

	insertJSONBCamera = `
INSERT INTO jsonb.camera (zone_id, serial_number, name, model, ip_address, status, position, settings)
SELECT z.zone_id, $3, $4, $5, $6::inet, $7, $8::jsonb, $9::jsonb
FROM jsonb.zone z
JOIN jsonb.area a ON a.area_id = z.area_id
WHERE a.area_code = $1 AND z.zone_code = $2
ON CONFLICT (serial_number) DO UPDATE SET
	name = EXCLUDED.name,
	model = EXCLUDED.model,
	ip_address = EXCLUDED.ip_address,
	status = EXCLUDED.status,
	position = EXCLUDED.position,
	settings = EXCLUDED.settings`

	insertJSONBEvent = `
WITH inserted AS (
	INSERT INTO jsonb.event (zone_id, event_number, occurred_at, event_type, severity, confidence, payload)
	SELECT z.zone_id, $3, $4, $5, $6, $7, $8::jsonb
	FROM jsonb.zone z
	JOIN jsonb.area a ON a.area_id = z.area_id
	WHERE a.area_code = $1 AND z.zone_code = $2
	ON CONFLICT (zone_id, event_number) DO UPDATE SET
		occurred_at = EXCLUDED.occurred_at,
		event_type = EXCLUDED.event_type,
		severity = EXCLUDED.severity,
		confidence = EXCLUDED.confidence,
		payload = EXCLUDED.payload
	RETURNING event_id
)
INSERT INTO jsonb.event_camera (event_id, camera_id)
SELECT inserted.event_id, c.camera_id
FROM inserted
JOIN jsonb.camera c ON c.serial_number = $9
ON CONFLICT DO NOTHING`

	insertJSONBTelemetry = `
INSERT INTO jsonb.camera_telemetry (camera_id, recorded_at, status, metrics)
SELECT camera_id, $2, $3, $4::jsonb
FROM jsonb.camera
WHERE serial_number = $1
ON CONFLICT (camera_id, recorded_at) DO UPDATE SET
	status = EXCLUDED.status,
	metrics = EXCLUDED.metrics`

	aggJSONBObjectActivity = `
SELECT z.zone_code, obj->>'object_type', e.severity, count(*), avg((obj->>'confidence')::numeric)
FROM jsonb.event e
JOIN jsonb.zone z ON z.zone_id = e.zone_id
JOIN jsonb.area a ON a.area_id = z.area_id
CROSS JOIN LATERAL jsonb_array_elements(COALESCE(e.payload->'objects', '[]'::jsonb)) obj
WHERE a.area_code = $1 AND e.occurred_at BETWEEN $2 AND $3
GROUP BY z.zone_code, obj->>'object_type', e.severity`

	aggJSONBTelemetryHealth = `
SELECT c.serial_number, z.zone_code,
	avg((t.metrics->>'latency_ms')::numeric),
	max((t.metrics->>'packet_loss')::numeric),
	max((t.metrics->>'temperature_celsius')::numeric),
	avg(CASE WHEN t.status = 'signal_lost' THEN 1 ELSE 0 END)
FROM jsonb.camera_telemetry t
JOIN jsonb.camera c ON c.camera_id = t.camera_id
JOIN jsonb.zone z ON z.zone_id = c.zone_id
JOIN jsonb.area a ON a.area_id = z.area_id
WHERE a.area_code = $1 AND t.recorded_at BETWEEN $2 AND $3
GROUP BY c.serial_number, z.zone_code
ORDER BY max((t.metrics->>'packet_loss')::numeric) DESC NULLS LAST
LIMIT 100`

	readJSONBIncidentTimeline = `
SELECT e.event_id, e.occurred_at, e.event_type, e.severity, e.payload, count(t.*)
FROM jsonb.event e
JOIN jsonb.zone z ON z.zone_id = e.zone_id
LEFT JOIN jsonb.event_camera ec ON ec.event_id = e.event_id
LEFT JOIN jsonb.camera_telemetry t ON t.camera_id = ec.camera_id
	AND t.recorded_at BETWEEN e.occurred_at - interval '5 minutes' AND e.occurred_at + interval '5 minutes'
WHERE z.zone_code = $1 AND e.severity IN ('high', 'critical') AND e.occurred_at BETWEEN $2 AND $3
GROUP BY e.event_id
ORDER BY e.occurred_at DESC
LIMIT 100`
)
