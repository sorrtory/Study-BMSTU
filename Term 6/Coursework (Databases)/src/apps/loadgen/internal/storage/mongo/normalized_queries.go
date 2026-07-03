package mongo

import (
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
)

var normalizedCollections = []string{"camera_telemetry", "event_cameras", "events", "cameras", "zones", "areas"}

func ref(collection, id string) map[string]any {
	return map[string]any{"$ref": collection, "$id": id}
}

func normalizedObjectActivityPipeline(areaCode string, from, to time.Time) mongo.Pipeline {
	// The normalized document model intentionally pays lookup cost on analytics
	// because events store zone references instead of embedded area/zone snapshots.
	return mongo.Pipeline{
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "zones"}, {Key: "localField", Value: "zone.$id"}, {Key: "foreignField", Value: "_id"}, {Key: "as", Value: "zone_doc"}}}},
		{{Key: "$unwind", Value: "$zone_doc"}},
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "areas"}, {Key: "localField", Value: "zone_doc.area.$id"}, {Key: "foreignField", Value: "_id"}, {Key: "as", Value: "area_doc"}}}},
		{{Key: "$unwind", Value: "$area_doc"}},
		{{Key: "$match", Value: bson.D{{Key: "area_doc.area_code", Value: areaCode}, {Key: "occurred_at", Value: bson.D{{Key: "$gte", Value: from}, {Key: "$lte", Value: to}}}}}},
		{{Key: "$unwind", Value: "$payload.objects"}},
		{{Key: "$group", Value: bson.D{
			{Key: "_id", Value: bson.D{{Key: "zone", Value: "$zone_doc.zone_code"}, {Key: "object_type", Value: "$payload.objects.object_type"}, {Key: "severity", Value: "$severity"}}},
			{Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
			{Key: "avg_confidence", Value: bson.D{{Key: "$avg", Value: "$payload.objects.confidence"}}},
		}}},
	}
}

func normalizedTelemetryHealthPipeline(areaCode string, from, to time.Time) mongo.Pipeline {
	// Telemetry references cameras only, so area filtering goes through camera -> zone -> area.
	return mongo.Pipeline{
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "cameras"}, {Key: "localField", Value: "camera.$id"}, {Key: "foreignField", Value: "_id"}, {Key: "as", Value: "camera_doc"}}}},
		{{Key: "$unwind", Value: "$camera_doc"}},
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "zones"}, {Key: "localField", Value: "camera_doc.zone.$id"}, {Key: "foreignField", Value: "_id"}, {Key: "as", Value: "zone_doc"}}}},
		{{Key: "$unwind", Value: "$zone_doc"}},
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "areas"}, {Key: "localField", Value: "zone_doc.area.$id"}, {Key: "foreignField", Value: "_id"}, {Key: "as", Value: "area_doc"}}}},
		{{Key: "$unwind", Value: "$area_doc"}},
		{{Key: "$match", Value: bson.D{{Key: "area_doc.area_code", Value: areaCode}, {Key: "recorded_at", Value: bson.D{{Key: "$gte", Value: from}, {Key: "$lte", Value: to}}}}}},
		{{Key: "$group", Value: bson.D{
			{Key: "_id", Value: bson.D{{Key: "camera", Value: "$camera_doc.serial_number"}, {Key: "zone", Value: "$zone_doc.zone_code"}}},
			{Key: "avg_latency", Value: bson.D{{Key: "$avg", Value: "$metrics.latency_ms"}}},
			{Key: "max_packet_loss", Value: bson.D{{Key: "$max", Value: "$metrics.packet_loss"}}},
			{Key: "max_temperature", Value: bson.D{{Key: "$max", Value: "$metrics.temperature_celsius"}}},
			{Key: "signal_lost_share", Value: bson.D{{Key: "$avg", Value: bson.D{{Key: "$cond", Value: bson.A{bson.D{{Key: "$eq", Value: bson.A{"$status", "signal_lost"}}}, 1, 0}}}}}},
		}}},
		{{Key: "$limit", Value: 100}},
	}
}

func normalizedIncidentTimelinePipeline(zoneCode string, from, to time.Time) mongo.Pipeline {
	return mongo.Pipeline{
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "zones"}, {Key: "localField", Value: "zone.$id"}, {Key: "foreignField", Value: "_id"}, {Key: "as", Value: "zone_doc"}}}},
		{{Key: "$unwind", Value: "$zone_doc"}},
		{{Key: "$match", Value: bson.D{
			{Key: "zone_doc.zone_code", Value: zoneCode},
			{Key: "severity", Value: bson.D{{Key: "$in", Value: bson.A{"high", "critical"}}}},
			{Key: "occurred_at", Value: bson.D{{Key: "$gte", Value: from}, {Key: "$lte", Value: to}}},
		}}},
		{{Key: "$lookup", Value: bson.D{{Key: "from", Value: "event_cameras"}, {Key: "localField", Value: "_id"}, {Key: "foreignField", Value: "event.$id"}, {Key: "as", Value: "camera_links"}}}},
		{{Key: "$sort", Value: bson.D{{Key: "occurred_at", Value: -1}}}},
		{{Key: "$limit", Value: 100}},
	}
}
