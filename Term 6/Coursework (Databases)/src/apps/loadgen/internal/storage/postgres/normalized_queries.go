package postgres

const (
	clearNormalized = `
TRUNCATE TABLE
	normalized.person_object_attribute,
	normalized.vehicle_object_attribute,
	normalized.detected_object,
	normalized.signal_lost_event_detail,
	normalized.line_crossing_event_detail,
	normalized.object_detection_event_detail,
	normalized.motion_event_detail,
	normalized.event_camera,
	normalized.camera_telemetry,
	normalized.event,
	normalized.camera_crossing_line,
	normalized.camera_detection_zone_point,
	normalized.camera_detection_zone,
	normalized.camera_analytics_setting,
	normalized.camera_stream_setting,
	normalized.camera,
	normalized.zone,
	normalized.area
RESTART IDENTITY CASCADE`

	insertNormalizedArea = `
INSERT INTO normalized.area (area_type_id, area_code, name, address, description)
SELECT area_type_id, $2, $3, $4, $5
FROM normalized.area_type
WHERE code = $1
ON CONFLICT (area_code) DO UPDATE SET
	area_type_id = EXCLUDED.area_type_id,
	name = EXCLUDED.name,
	address = EXCLUDED.address,
	description = EXCLUDED.description`

	insertNormalizedZone = `
INSERT INTO normalized.zone (area_id, zone_type_id, zone_code, name, importance_level, description)
SELECT a.area_id, zt.zone_type_id, $3, $4, $5, $6
FROM normalized.area a
JOIN normalized.zone_type zt ON zt.code = $2
WHERE a.area_code = $1
ON CONFLICT (area_id, zone_code) DO UPDATE SET
	zone_type_id = EXCLUDED.zone_type_id,
	name = EXCLUDED.name,
	importance_level = EXCLUDED.importance_level,
	description = EXCLUDED.description`

	insertNormalizedCamera = `
INSERT INTO normalized.camera (
	zone_id, camera_status_id, serial_number, name, model, ip_address,
	position_x, position_y, position_z, yaw_angle, pitch_angle, roll_angle, view_angle
)
SELECT z.zone_id, cs.camera_status_id, $3, $4, $5, $6::inet, $7, $8, $9, $10, $11, $12, $13
FROM normalized.zone z
JOIN normalized.area a ON a.area_id = z.area_id
JOIN normalized.camera_status cs ON cs.code = $14
WHERE a.area_code = $1 AND z.zone_code = $2
ON CONFLICT (serial_number) DO UPDATE SET
	camera_status_id = EXCLUDED.camera_status_id,
	name = EXCLUDED.name,
	model = EXCLUDED.model,
	ip_address = EXCLUDED.ip_address,
	position_x = EXCLUDED.position_x,
	position_y = EXCLUDED.position_y,
	position_z = EXCLUDED.position_z,
	yaw_angle = EXCLUDED.yaw_angle,
	pitch_angle = EXCLUDED.pitch_angle,
	roll_angle = EXCLUDED.roll_angle,
	view_angle = EXCLUDED.view_angle`

	insertNormalizedStreamSetting = `
INSERT INTO normalized.camera_stream_setting (camera_id, video_codec_id, resolution_width, resolution_height, fps, bitrate_kbps, rtsp_enabled)
SELECT c.camera_id, vc.video_codec_id, $2, $3, $4, $5, $6
FROM normalized.camera c
JOIN normalized.video_codec vc ON vc.code = $7
WHERE c.serial_number = $1
ON CONFLICT (camera_id) DO UPDATE SET
	video_codec_id = EXCLUDED.video_codec_id,
	resolution_width = EXCLUDED.resolution_width,
	resolution_height = EXCLUDED.resolution_height,
	fps = EXCLUDED.fps,
	bitrate_kbps = EXCLUDED.bitrate_kbps,
	rtsp_enabled = EXCLUDED.rtsp_enabled`

	insertNormalizedAnalyticsSetting = `
INSERT INTO normalized.camera_analytics_setting (camera_id, motion_detection, line_crossing, object_detection, sensitivity, min_object_confidence)
SELECT camera_id, $2, $3, $4, $5, $6
FROM normalized.camera
WHERE serial_number = $1
ON CONFLICT (camera_id) DO UPDATE SET
	motion_detection = EXCLUDED.motion_detection,
	line_crossing = EXCLUDED.line_crossing,
	object_detection = EXCLUDED.object_detection,
	sensitivity = EXCLUDED.sensitivity,
	min_object_confidence = EXCLUDED.min_object_confidence`

	insertNormalizedDetectionZone = `
INSERT INTO normalized.camera_detection_zone (camera_id, detection_zone_code)
SELECT camera_id, $2
FROM normalized.camera
WHERE serial_number = $1
ON CONFLICT (camera_id, detection_zone_code) DO NOTHING`

	insertNormalizedDetectionPoint = `
INSERT INTO normalized.camera_detection_zone_point (camera_detection_zone_id, point_order, x, y)
SELECT cdz.camera_detection_zone_id, $3, $4, $5
FROM normalized.camera_detection_zone cdz
JOIN normalized.camera c ON c.camera_id = cdz.camera_id
WHERE c.serial_number = $1 AND cdz.detection_zone_code = $2
ON CONFLICT (camera_detection_zone_id, point_order) DO UPDATE SET
	x = EXCLUDED.x,
	y = EXCLUDED.y`

	insertNormalizedCrossingLine = `
INSERT INTO normalized.camera_crossing_line (camera_id, allowed_direction_id, line_code, name, start_x, start_y, end_x, end_y)
SELECT c.camera_id, d.direction_id, $3, $4, $5, $6, $7, $8
FROM normalized.camera c
JOIN normalized.direction d ON d.code = $2
WHERE c.serial_number = $1
ON CONFLICT (camera_id, line_code) DO UPDATE SET
	allowed_direction_id = EXCLUDED.allowed_direction_id,
	name = EXCLUDED.name,
	start_x = EXCLUDED.start_x,
	start_y = EXCLUDED.start_y,
	end_x = EXCLUDED.end_x,
	end_y = EXCLUDED.end_y`

	insertNormalizedEvent = `
INSERT INTO normalized.event (zone_id, event_type_id, event_severity_id, event_number, occurred_at, confidence)
SELECT z.zone_id, et.event_type_id, es.event_severity_id, $3, $4, $5
FROM normalized.zone z
JOIN normalized.area a ON a.area_id = z.area_id
JOIN normalized.event_type et ON et.code = $6
JOIN normalized.event_severity es ON es.code = $7
WHERE a.area_code = $1 AND z.zone_code = $2
ON CONFLICT (zone_id, event_number) DO UPDATE SET
	event_type_id = EXCLUDED.event_type_id,
	event_severity_id = EXCLUDED.event_severity_id,
	occurred_at = EXCLUDED.occurred_at,
	confidence = EXCLUDED.confidence
RETURNING event_id`

	insertNormalizedEventCamera = `
INSERT INTO normalized.event_camera (event_id, camera_id)
SELECT $1, camera_id
FROM normalized.camera
WHERE serial_number = $2
ON CONFLICT DO NOTHING`

	insertNormalizedMotionDetail = `
INSERT INTO normalized.motion_event_detail (event_id, camera_detection_zone_id, frame_time_ms, motion_area_percent, duration_ms)
SELECT $1, cdz.camera_detection_zone_id, $3, $4, $5
FROM normalized.camera_detection_zone cdz
JOIN normalized.camera c ON c.camera_id = cdz.camera_id
WHERE c.serial_number = $2 AND cdz.detection_zone_code = 'DZ-1'
LIMIT 1
ON CONFLICT (event_id) DO UPDATE SET
	frame_time_ms = EXCLUDED.frame_time_ms,
	motion_area_percent = EXCLUDED.motion_area_percent,
	duration_ms = EXCLUDED.duration_ms`

	insertNormalizedObjectDetail = `
INSERT INTO normalized.object_detection_event_detail (event_id, frame_time_ms)
VALUES ($1, $2)
ON CONFLICT (event_id) DO UPDATE SET frame_time_ms = EXCLUDED.frame_time_ms`

	insertNormalizedLineCrossingDetail = `
INSERT INTO normalized.line_crossing_event_detail (event_id, camera_crossing_line_id, direction_id, frame_time_ms)
SELECT $1, cl.camera_crossing_line_id, d.direction_id, $4
FROM normalized.camera_crossing_line cl
JOIN normalized.camera c ON c.camera_id = cl.camera_id
JOIN normalized.direction d ON d.code = $3
WHERE c.serial_number = $2 AND cl.line_code = 'CL-1'
LIMIT 1
ON CONFLICT (event_id) DO UPDATE SET
	camera_crossing_line_id = EXCLUDED.camera_crossing_line_id,
	direction_id = EXCLUDED.direction_id,
	frame_time_ms = EXCLUDED.frame_time_ms`

	insertNormalizedSignalLostDetail = `
INSERT INTO normalized.signal_lost_event_detail (event_id, signal_lost_reason_id, last_frame_at, downtime_seconds)
SELECT $1, signal_lost_reason_id, $3, $4
FROM normalized.signal_lost_reason
WHERE code = $2
ON CONFLICT (event_id) DO UPDATE SET
	signal_lost_reason_id = EXCLUDED.signal_lost_reason_id,
	last_frame_at = EXCLUDED.last_frame_at,
	downtime_seconds = EXCLUDED.downtime_seconds`

	insertNormalizedDetectedObject = `
INSERT INTO normalized.detected_object (
	event_id, object_type_id, object_number, confidence,
	bounding_box_x, bounding_box_y, bounding_box_width, bounding_box_height
)
SELECT $1, object_type_id, $3, $4, $5, $6, $7, $8
FROM normalized.object_type
WHERE code = $2
ON CONFLICT (event_id, object_number) DO UPDATE SET
	object_type_id = EXCLUDED.object_type_id,
	confidence = EXCLUDED.confidence,
	bounding_box_x = EXCLUDED.bounding_box_x,
	bounding_box_y = EXCLUDED.bounding_box_y,
	bounding_box_width = EXCLUDED.bounding_box_width,
	bounding_box_height = EXCLUDED.bounding_box_height
RETURNING detected_object_id`

	insertNormalizedPersonAttributes = `
INSERT INTO normalized.person_object_attribute (detected_object_id, direction_id, has_bag, clothing_color)
SELECT $1, direction_id, $3, $4 FROM normalized.direction WHERE code = $2
ON CONFLICT (detected_object_id) DO UPDATE SET
	direction_id = EXCLUDED.direction_id,
	has_bag = EXCLUDED.has_bag,
	clothing_color = EXCLUDED.clothing_color`

	insertNormalizedVehicleAttributes = `
INSERT INTO normalized.vehicle_object_attribute (detected_object_id, color, license_plate, license_plate_confidence)
VALUES ($1, $2, $3, $4)
ON CONFLICT (detected_object_id) DO UPDATE SET
	color = EXCLUDED.color,
	license_plate = EXCLUDED.license_plate,
	license_plate_confidence = EXCLUDED.license_plate_confidence`

	insertNormalizedTelemetry = `
INSERT INTO normalized.camera_telemetry (
	camera_id, recorded_at, camera_status_id, temperature_celsius, cpu_load,
	memory_usage, bitrate_kbps, packet_loss, latency_ms, uptime_seconds
)
SELECT c.camera_id, $2, cs.camera_status_id, $4, $5, $6, $7, $8, $9, $10
FROM normalized.camera c
JOIN normalized.camera_status cs ON cs.code = $3
WHERE c.serial_number = $1
ON CONFLICT (camera_id, recorded_at) DO UPDATE SET
	camera_status_id = EXCLUDED.camera_status_id,
	temperature_celsius = EXCLUDED.temperature_celsius,
	cpu_load = EXCLUDED.cpu_load,
	memory_usage = EXCLUDED.memory_usage,
	bitrate_kbps = EXCLUDED.bitrate_kbps,
	packet_loss = EXCLUDED.packet_loss,
	latency_ms = EXCLUDED.latency_ms,
	uptime_seconds = EXCLUDED.uptime_seconds`

	aggNormalizedObjectActivity = `
SELECT z.zone_code, ot.code, es.code, count(*), avg(o.confidence)
FROM normalized.detected_object o
JOIN normalized.event e ON e.event_id = o.event_id
JOIN normalized.zone z ON z.zone_id = e.zone_id
JOIN normalized.area a ON a.area_id = z.area_id
JOIN normalized.object_type ot ON ot.object_type_id = o.object_type_id
JOIN normalized.event_severity es ON es.event_severity_id = e.event_severity_id
WHERE a.area_code = $1 AND e.occurred_at BETWEEN $2 AND $3
GROUP BY z.zone_code, ot.code, es.code`

	aggNormalizedTelemetryHealth = `
SELECT c.serial_number, z.zone_code,
	avg(t.latency_ms),
	max(t.packet_loss),
	max(t.temperature_celsius),
	avg(CASE WHEN cs.code = 'signal_lost' THEN 1 ELSE 0 END)
FROM normalized.camera_telemetry t
JOIN normalized.camera c ON c.camera_id = t.camera_id
JOIN normalized.camera_status cs ON cs.camera_status_id = t.camera_status_id
JOIN normalized.zone z ON z.zone_id = c.zone_id
JOIN normalized.area a ON a.area_id = z.area_id
WHERE a.area_code = $1 AND t.recorded_at BETWEEN $2 AND $3
GROUP BY c.serial_number, z.zone_code
ORDER BY max(t.packet_loss) DESC NULLS LAST
LIMIT 100`

	readNormalizedIncidentTimeline = `
SELECT e.event_id, e.occurred_at, et.code, es.code, count(o.*), count(t.*)
FROM normalized.event e
JOIN normalized.zone z ON z.zone_id = e.zone_id
JOIN normalized.event_type et ON et.event_type_id = e.event_type_id
JOIN normalized.event_severity es ON es.event_severity_id = e.event_severity_id
LEFT JOIN normalized.detected_object o ON o.event_id = e.event_id
LEFT JOIN normalized.event_camera ec ON ec.event_id = e.event_id
LEFT JOIN normalized.camera_telemetry t ON t.camera_id = ec.camera_id
	AND t.recorded_at BETWEEN e.occurred_at - interval '5 minutes' AND e.occurred_at + interval '5 minutes'
WHERE z.zone_code = $1 AND es.code IN ('high', 'critical') AND e.occurred_at BETWEEN $2 AND $3
GROUP BY e.event_id, et.code, es.code
ORDER BY e.occurred_at DESC
LIMIT 100`
)
