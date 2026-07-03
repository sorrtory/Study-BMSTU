package workload

import (
	"fmt"
	"hash/fnv"
	"math"
	"math/rand"
	"time"
)

func GenerateWorld(seed int64, profile SizeProfile) World {
	r := rand.New(rand.NewSource(seed))
	areaTypes := []string{"office", "warehouse", "parking", "campus", "industrial_site"}
	zoneTypes := []string{"entrance", "parking", "warehouse", "perimeter", "service_room"}
	statuses := []string{"active", "offline", "maintenance", "signal_lost"}
	codecs := []string{"H.264", "H.265", "MJPEG"}

	world := World{Seed: seed, Profile: profile}
	for a := 0; a < profile.Areas; a++ {
		area := Area{
			ID:          fmt.Sprintf("area-%03d", a+1),
			Code:        fmt.Sprintf("AREA-%03d", a+1),
			Name:        fmt.Sprintf("Area %03d", a+1),
			Type:        areaTypes[a%len(areaTypes)],
			Address:     fmt.Sprintf("Building %d", a+1),
			Description: fmt.Sprintf("Observation area %03d", a+1),
		}
		world.Areas = append(world.Areas, area)
		for z := 0; z < profile.ZonesPerArea; z++ {
			zone := Zone{
				ID:              fmt.Sprintf("zone-%03d-%03d", a+1, z+1),
				AreaID:          area.ID,
				AreaCode:        area.Code,
				Code:            fmt.Sprintf("ZONE-%03d-%03d", a+1, z+1),
				Name:            fmt.Sprintf("Zone %03d-%03d", a+1, z+1),
				Type:            zoneTypes[(a+z)%len(zoneTypes)],
				ImportanceLevel: 1 + ((a + z) % 5),
				Description:     fmt.Sprintf("Observation zone %03d-%03d", a+1, z+1),
			}
			world.Zones = append(world.Zones, zone)
			for c := 0; c < profile.CamerasPerZone; c++ {
				cameraNo := a*profile.ZonesPerArea*profile.CamerasPerZone + z*profile.CamerasPerZone + c + 1
				camera := Camera{
					ID:           fmt.Sprintf("camera-%06d", cameraNo),
					AreaID:       area.ID,
					AreaCode:     area.Code,
					AreaName:     area.Name,
					ZoneID:       zone.ID,
					ZoneCode:     zone.Code,
					ZoneName:     zone.Name,
					ZoneType:     zone.Type,
					SerialNumber: fmt.Sprintf("CAM-%06d", cameraNo),
					Name:         fmt.Sprintf("Camera %06d", cameraNo),
					Model:        fmt.Sprintf("VC-%d", 100+(cameraNo%5)),
					IPAddress:    fmt.Sprintf("10.%d.%d.%d", 10+(a%200), z%250, 1+c%240),
					Status:       statuses[r.Intn(len(statuses))],
					Position:     cameraPosition(r),
					Settings:     cameraSettings(r, cameraNo, codecs),
				}
				world.Cameras = append(world.Cameras, camera)
			}
		}
	}
	return world
}

func GenerateEvents(req OperationRequest) []ComplexEvent {
	batchSize := req.BatchSize
	if batchSize <= 0 {
		batchSize = 25
	}
	world := GenerateWorld(req.Seed, req.Profile)
	r := operationRand(req)
	eventTypes := []string{"motion_detected", "object_detected", "line_crossing", "signal_lost"}
	severities := []string{"low", "medium", "high", "critical"}
	events := make([]ComplexEvent, 0, batchSize)
	for i := 0; i < batchSize; i++ {
		zone := world.Zones[r.Intn(len(world.Zones))]
		cameras := camerasForZone(world, zone.Code)
		camera := cameras[r.Intn(len(cameras))]
		eventType := eventTypes[r.Intn(len(eventTypes))]
		eventTime := req.Now.Add(-time.Duration(r.Intn(3600)) * time.Second)
		eventNumber := int64(eventHash(req.Seed, zone.Code, eventTime, i))
		events = append(events, ComplexEvent{
			ID:             fmt.Sprintf("event-%s-%d-%d", zone.Code, eventTime.UnixNano(), i),
			EventNumber:    eventNumber,
			OccurredAt:     eventTime,
			EventType:      eventType,
			Severity:       severities[r.Intn(len(severities))],
			Confidence:     round(0.5+r.Float64()*0.5, 4),
			AreaCode:       zone.AreaCode,
			AreaName:       areaName(world, zone.AreaCode),
			ZoneID:         zone.ID,
			ZoneCode:       zone.Code,
			ZoneName:       zone.Name,
			ZoneType:       zone.Type,
			ZoneImportance: zone.ImportanceLevel,
			Cameras:        []Camera{camera},
			Payload:        eventPayload(eventType, r, eventTime),
		})
	}
	return events
}

func GenerateTelemetry(req OperationRequest) []Telemetry {
	batchSize := req.BatchSize
	if batchSize <= 0 {
		batchSize = 50
	}
	world := GenerateWorld(req.Seed, req.Profile)
	r := operationRand(req)
	statuses := []string{"active", "offline", "maintenance", "signal_lost"}
	records := make([]Telemetry, 0, batchSize)
	for i := 0; i < batchSize; i++ {
		camera := world.Cameras[r.Intn(len(world.Cameras))]
		recordedAt := req.Now.Add(-time.Duration(r.Intn(3600)) * time.Second)
		records = append(records, Telemetry{
			ID:         fmt.Sprintf("telemetry-%s-%d-%d", camera.SerialNumber, recordedAt.UnixNano(), i),
			RecordedAt: recordedAt,
			Camera:     camera,
			Status:     statuses[r.Intn(len(statuses))],
			Metrics: JSONMap{
				"temperature_celsius": round(30+r.Float64()*55, 2),
				"cpu_load":            round(r.Float64(), 4),
				"memory_usage":        round(0.2+r.Float64()*0.75, 4),
				"bitrate_kbps":        1200 + r.Intn(5000),
				"packet_loss":         round(r.Float64()*0.2, 4),
				"latency_ms":          10 + r.Intn(450),
				"uptime_seconds":      3600 + r.Intn(86400*30),
			},
		})
	}
	return records
}

func cameraPosition(r *rand.Rand) JSONMap {
	return JSONMap{
		"x":           round(r.Float64()*100, 2),
		"y":           round(r.Float64()*100, 2),
		"z":           round(2+r.Float64()*8, 2),
		"yaw_angle":   round(r.Float64()*360, 2),
		"pitch_angle": round(-30+r.Float64()*60, 2),
		"roll_angle":  round(-5+r.Float64()*10, 2),
		"view_angle":  round(60+r.Float64()*60, 2),
	}
}

func cameraSettings(r *rand.Rand, cameraNo int, codecs []string) JSONMap {
	return JSONMap{
		"stream": JSONMap{
			"video_codec":       codecs[cameraNo%len(codecs)],
			"resolution_width":  1920,
			"resolution_height": 1080,
			"fps":               25,
			"bitrate_kbps":      2500 + cameraNo%1500,
			"rtsp_enabled":      true,
		},
		"analytics": JSONMap{
			"motion_detection":      true,
			"line_crossing":         cameraNo%2 == 0,
			"object_detection":      true,
			"sensitivity":           round(0.5+r.Float64()*0.45, 2),
			"min_object_confidence": 0.55,
		},
		"detection_zones": []JSONMap{{
			"code":   "DZ-1",
			"points": []JSONMap{{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 0, "y": 1}},
		}},
		"crossing_lines": []JSONMap{{
			"code":              "CL-1",
			"name":              "Main line",
			"allowed_direction": "unknown",
			"start":             JSONMap{"x": 0.1, "y": 0.5},
			"end":               JSONMap{"x": 0.9, "y": 0.5},
		}},
	}
}

func eventPayload(eventType string, r *rand.Rand, at time.Time) EventPayload {
	objects := generateObjects(r, 1+r.Intn(4))
	switch eventType {
	case "motion_detected":
		return EventPayload{
			"detection_zone_code": "DZ-1",
			"frame_time_ms":       r.Intn(1000),
			"motion_area_percent": round(1+r.Float64()*40, 2),
			"duration_ms":         300 + r.Intn(5000),
			"objects":             objects,
		}
	case "line_crossing":
		return EventPayload{
			"line_code":     "CL-1",
			"direction":     []string{"inside", "outside", "left_to_right", "right_to_left"}[r.Intn(4)],
			"frame_time_ms": r.Intn(1000),
			"objects":       objects,
		}
	case "signal_lost":
		return EventPayload{
			"reason":           []string{"network_timeout", "power_off", "stream_error"}[r.Intn(3)],
			"last_frame_at":    at.Add(-time.Duration(1+r.Intn(60)) * time.Second).Format(time.RFC3339Nano),
			"downtime_seconds": 5 + r.Intn(900),
			"objects":          []JSONMap{},
		}
	default:
		return EventPayload{
			"frame_time_ms": r.Intn(1000),
			"objects":       objects,
		}
	}
}

func generateObjects(r *rand.Rand, n int) []JSONMap {
	objectTypes := []string{"person", "vehicle", "unknown"}
	colors := []string{"black", "white", "blue", "red", "gray"}
	objects := make([]JSONMap, 0, n)
	for i := 0; i < n; i++ {
		objectType := objectTypes[r.Intn(len(objectTypes))]
		obj := JSONMap{
			"object_number": i + 1,
			"object_type":   objectType,
			"confidence":    round(0.5+r.Float64()*0.5, 4),
			"bounding_box": JSONMap{
				"x":      r.Intn(1600),
				"y":      r.Intn(900),
				"width":  50 + r.Intn(250),
				"height": 50 + r.Intn(250),
			},
		}
		if objectType == "person" {
			obj["attributes"] = JSONMap{"direction": "unknown", "has_bag": r.Intn(2) == 0, "clothing_color": colors[r.Intn(len(colors))]}
		}
		if objectType == "vehicle" {
			obj["attributes"] = JSONMap{"color": colors[r.Intn(len(colors))], "license_plate": fmt.Sprintf("A%03dAA", r.Intn(1000)), "license_plate_confidence": round(0.6+r.Float64()*0.35, 3)}
		}
		objects = append(objects, obj)
	}
	return objects
}

func operationRand(req OperationRequest) *rand.Rand {
	if req.Rand != nil {
		return req.Rand
	}
	return rand.New(rand.NewSource(req.Seed))
}

func camerasForZone(world World, zoneCode string) []Camera {
	out := make([]Camera, 0, world.Profile.CamerasPerZone)
	for _, camera := range world.Cameras {
		if camera.ZoneCode == zoneCode {
			out = append(out, camera)
		}
	}
	return out
}

func areaName(world World, areaCode string) string {
	for _, area := range world.Areas {
		if area.Code == areaCode {
			return area.Name
		}
	}
	return areaCode
}

func eventHash(seed int64, zoneCode string, t time.Time, i int) uint64 {
	h := fnv.New64a()
	_, _ = fmt.Fprintf(h, "%d:%s:%d:%d", seed, zoneCode, t.UnixNano(), i)
	return h.Sum64()
}

func round(v float64, places int) float64 {
	p := math.Pow10(places)
	return math.Round(v*p) / p
}
