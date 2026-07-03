CREATE INDEX idx_normalized_area_area_type_id ON normalized.area(area_type_id);

CREATE INDEX idx_normalized_zone_area_id ON normalized.zone(area_id);
CREATE INDEX idx_normalized_zone_zone_type_id ON normalized.zone(zone_type_id);

CREATE INDEX idx_normalized_camera_zone_id ON normalized.camera(zone_id);
CREATE INDEX idx_normalized_camera_status_id ON normalized.camera(camera_status_id);

CREATE INDEX idx_normalized_detection_zone_camera_id ON normalized.camera_detection_zone(camera_id);
CREATE INDEX idx_normalized_detection_zone_point_zone_id ON normalized.camera_detection_zone_point(camera_detection_zone_id);
CREATE INDEX idx_normalized_crossing_line_camera_id ON normalized.camera_crossing_line(camera_id);

CREATE INDEX idx_normalized_event_zone_occurred_at ON normalized.event(zone_id, occurred_at DESC);
CREATE INDEX idx_normalized_event_type_severity_occurred_at ON normalized.event(event_type_id, event_severity_id, occurred_at DESC);

CREATE INDEX idx_normalized_event_camera_camera_event ON normalized.event_camera(camera_id, event_id);

CREATE INDEX idx_normalized_motion_detection_zone_id ON normalized.motion_event_detail(camera_detection_zone_id);
CREATE INDEX idx_normalized_line_crossing_line_id ON normalized.line_crossing_event_detail(camera_crossing_line_id);
CREATE INDEX idx_normalized_detected_object_event_id ON normalized.detected_object(event_id);
CREATE INDEX idx_normalized_detected_object_object_type_id ON normalized.detected_object(object_type_id);

CREATE INDEX idx_normalized_camera_telemetry_recorded_at ON normalized.camera_telemetry(recorded_at DESC);
CREATE INDEX idx_normalized_camera_telemetry_status_recorded_at ON normalized.camera_telemetry(camera_status_id, recorded_at DESC);
