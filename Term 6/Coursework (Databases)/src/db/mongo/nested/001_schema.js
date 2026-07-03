const nestedDb = db.getSiblingDB(globalThis.nestedDatabase);

nestedDb.createCollection("areas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "area_code", "name", "area_type", "zones"],
      properties: {
        _id: { bsonType: "string" },
        area_code: { bsonType: "string" },
        name: { bsonType: "string" },
        area_type: { enum: ["office", "warehouse", "parking", "campus", "industrial_site"] },
        address: { bsonType: ["string", "null"] },
        description: { bsonType: ["string", "null"] },
        zones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["zone_code", "name", "zone_type", "importance_level"],
            properties: {
              zone_code: { bsonType: "string" },
              name: { bsonType: "string" },
              zone_type: { enum: ["entrance", "parking", "warehouse", "perimeter", "service_room"] },
              importance_level: { bsonType: "int" },
              description: { bsonType: ["string", "null"] }
            }
          }
        }
      }
    }
  }
});

nestedDb.createCollection("cameras", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "serial_number", "name", "model", "ip_address", "status", "area", "zone", "position", "settings"],
      properties: {
        _id: { bsonType: "string" },
        serial_number: { bsonType: "string" },
        name: { bsonType: "string" },
        model: { bsonType: "string" },
        ip_address: { bsonType: "string" },
        status: { enum: ["active", "offline", "maintenance", "signal_lost"] },
        area: {
          bsonType: "object",
          required: ["area_code", "name"],
          properties: {
            area_code: { bsonType: "string" },
            name: { bsonType: "string" }
          }
        },
        zone: {
          bsonType: "object",
          required: ["zone_code", "name", "zone_type"],
          properties: {
            zone_code: { bsonType: "string" },
            name: { bsonType: "string" },
            zone_type: { enum: ["entrance", "parking", "warehouse", "perimeter", "service_room"] }
          }
        },
        position: { bsonType: "object" },
        settings: { bsonType: "object" }
      }
    }
  }
});

nestedDb.createCollection("events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "event_number", "occurred_at", "event_type", "severity", "confidence", "area", "zone", "cameras", "payload"],
      properties: {
        _id: { bsonType: "string" },
        event_number: { bsonType: ["long", "int"] },
        occurred_at: { bsonType: "date" },
        event_type: { enum: ["motion_detected", "object_detected", "line_crossing", "signal_lost"] },
        severity: { enum: ["low", "medium", "high", "critical"] },
        confidence: { bsonType: ["double", "decimal", "int", "long"] },
        area: { bsonType: "object", required: ["area_code", "name"] },
        zone: { bsonType: "object", required: ["zone_code", "name", "zone_type", "importance_level"] },
        cameras: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["serial_number", "name"],
            properties: {
              serial_number: { bsonType: "string" },
              name: { bsonType: "string" }
            }
          }
        },
        payload: { bsonType: "object" }
      }
    }
  }
});

nestedDb.createCollection("camera_telemetry", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "recorded_at", "camera", "area", "zone", "status", "metrics"],
      properties: {
        _id: { bsonType: "string" },
        recorded_at: { bsonType: "date" },
        camera: { bsonType: "object", required: ["serial_number", "name"] },
        area: { bsonType: "object", required: ["area_code", "name"] },
        zone: { bsonType: "object", required: ["zone_code", "name"] },
        status: { enum: ["active", "offline", "maintenance", "signal_lost"] },
        metrics: { bsonType: "object" }
      }
    }
  }
});
