package mongo

import (
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
)

var nestedCollections = []string{"camera_telemetry", "events", "cameras", "areas"}

func nestedObjectActivityPipeline(areaCode string, from, to time.Time) mongo.Pipeline {
	return mongo.Pipeline{
		{{Key: "$match", Value: bson.D{{Key: "area.area_code", Value: areaCode}, {Key: "occurred_at", Value: bson.D{{Key: "$gte", Value: from}, {Key: "$lte", Value: to}}}}}},
		{{Key: "$unwind", Value: "$payload.objects"}},
		{{Key: "$group", Value: bson.D{
			{Key: "_id", Value: bson.D{{Key: "zone", Value: "$zone.zone_code"}, {Key: "object_type", Value: "$payload.objects.object_type"}, {Key: "severity", Value: "$severity"}}},
			{Key: "count", Value: bson.D{{Key: "$sum", Value: 1}}},
			{Key: "avg_confidence", Value: bson.D{{Key: "$avg", Value: "$payload.objects.confidence"}}},
		}}},
	}
}

func nestedTelemetryHealthPipeline(areaCode string, from, to time.Time) mongo.Pipeline {
	return mongo.Pipeline{
		{{Key: "$match", Value: bson.D{{Key: "area.area_code", Value: areaCode}, {Key: "recorded_at", Value: bson.D{{Key: "$gte", Value: from}, {Key: "$lte", Value: to}}}}}},
		{{Key: "$group", Value: bson.D{
			{Key: "_id", Value: bson.D{{Key: "camera", Value: "$camera.serial_number"}, {Key: "zone", Value: "$zone.zone_code"}}},
			{Key: "avg_latency", Value: bson.D{{Key: "$avg", Value: "$metrics.latency_ms"}}},
			{Key: "max_packet_loss", Value: bson.D{{Key: "$max", Value: "$metrics.packet_loss"}}},
			{Key: "max_temperature", Value: bson.D{{Key: "$max", Value: "$metrics.temperature_celsius"}}},
			{Key: "signal_lost_share", Value: bson.D{{Key: "$avg", Value: bson.D{{Key: "$cond", Value: bson.A{bson.D{{Key: "$eq", Value: bson.A{"$status", "signal_lost"}}}, 1, 0}}}}}},
		}}},
		{{Key: "$limit", Value: 100}},
	}
}

func nestedIncidentTimelinePipeline(zoneCode string, from, to time.Time) mongo.Pipeline {
	return mongo.Pipeline{
		{{Key: "$match", Value: bson.D{
			{Key: "zone.zone_code", Value: zoneCode},
			{Key: "severity", Value: bson.D{{Key: "$in", Value: bson.A{"high", "critical"}}}},
			{Key: "occurred_at", Value: bson.D{{Key: "$gte", Value: from}, {Key: "$lte", Value: to}}},
		}}},
		{{Key: "$sort", Value: bson.D{{Key: "occurred_at", Value: -1}}}},
		{{Key: "$limit", Value: 100}},
	}
}
