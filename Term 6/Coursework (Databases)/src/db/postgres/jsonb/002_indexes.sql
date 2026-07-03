CREATE INDEX idx_jsonb_zone_area_id ON jsonb.zone(area_id);

CREATE INDEX idx_jsonb_camera_zone_id ON jsonb.camera(zone_id);
CREATE INDEX idx_jsonb_camera_status ON jsonb.camera(status);
CREATE INDEX idx_jsonb_camera_settings_gin ON jsonb.camera USING GIN (settings);

CREATE INDEX idx_jsonb_event_zone_occurred_at ON jsonb.event(zone_id, occurred_at DESC);
CREATE INDEX idx_jsonb_event_type_severity_occurred_at ON jsonb.event(event_type, severity, occurred_at DESC);
CREATE INDEX idx_jsonb_event_payload_gin ON jsonb.event USING GIN (payload);

CREATE INDEX idx_jsonb_event_camera_camera_event ON jsonb.event_camera(camera_id, event_id);

CREATE INDEX idx_jsonb_camera_telemetry_recorded_at ON jsonb.camera_telemetry(recorded_at DESC);
CREATE INDEX idx_jsonb_camera_telemetry_status_recorded_at ON jsonb.camera_telemetry(status, recorded_at DESC);
CREATE INDEX idx_jsonb_camera_telemetry_metrics_gin ON jsonb.camera_telemetry USING GIN (metrics);
