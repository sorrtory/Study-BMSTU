const normalizedDb = db.getSiblingDB(globalThis.normalizedDatabase);

normalizedDb.createCollection("areas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "area_code", "name", "area_type"],
      properties: {
        _id: { bsonType: "string" },
        area_code: { bsonType: "string" },
        name: { bsonType: "string" },
        area_type: { enum: ["office", "warehouse", "parking", "campus", "industrial_site"] },
        address: { bsonType: ["string", "null"] },
        description: { bsonType: ["string", "null"] }
      }
    }
  }
});

normalizedDb.createCollection("zones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "zone_code", "name", "zone_type", "importance_level", "area"],
      properties: {
        _id: { bsonType: "string" },
        zone_code: { bsonType: "string" },
        name: { bsonType: "string" },
        zone_type: { enum: ["entrance", "parking", "warehouse", "perimeter", "service_room"] },
        importance_level: { bsonType: "int" },
        description: { bsonType: ["string", "null"] },
        area: {
          bsonType: "object",
          required: ["$ref", "$id"],
          properties: {
            $ref: { enum: ["areas"] },
            $id: { bsonType: "string" }
          }
        }
      }
    }
  }
});

normalizedDb.createCollection("cameras", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "serial_number", "name", "model", "ip_address", "status", "zone", "position", "settings"],
      properties: {
        _id: { bsonType: "string" },
        serial_number: { bsonType: "string" },
        name: { bsonType: "string" },
        model: { bsonType: "string" },
        ip_address: { bsonType: "string" },
        status: { enum: ["active", "offline", "maintenance", "signal_lost"] },
        zone: {
          bsonType: "object",
          required: ["$ref", "$id"],
          properties: {
            $ref: { enum: ["zones"] },
            $id: { bsonType: "string" }
          }
        },
        position: { bsonType: "object" },
        settings: { bsonType: "object" }
      }
    }
  }
});

normalizedDb.createCollection("events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "event_number", "occurred_at", "event_type", "severity", "confidence", "zone", "payload"],
      properties: {
        _id: { bsonType: "string" },
        event_number: { bsonType: ["long", "int"] },
        occurred_at: { bsonType: "date" },
        event_type: { enum: ["motion_detected", "object_detected", "line_crossing", "signal_lost"] },
        severity: { enum: ["low", "medium", "high", "critical"] },
        confidence: { bsonType: ["double", "decimal", "int", "long"] },
        zone: {
          bsonType: "object",
          required: ["$ref", "$id"],
          properties: {
            $ref: { enum: ["zones"] },
            $id: { bsonType: "string" }
          }
        },
        payload: { bsonType: "object" }
      }
    }
  }
});

normalizedDb.createCollection("event_cameras", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "event", "camera"],
      properties: {
        _id: { bsonType: "string" },
        event: {
          bsonType: "object",
          required: ["$ref", "$id"],
          properties: {
            $ref: { enum: ["events"] },
            $id: { bsonType: "string" }
          }
        },
        camera: {
          bsonType: "object",
          required: ["$ref", "$id"],
          properties: {
            $ref: { enum: ["cameras"] },
            $id: { bsonType: "string" }
          }
        }
      }
    }
  }
});

normalizedDb.createCollection("camera_telemetry", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "recorded_at", "camera", "status", "metrics"],
      properties: {
        _id: { bsonType: "string" },
        recorded_at: { bsonType: "date" },
        camera: {
          bsonType: "object",
          required: ["$ref", "$id"],
          properties: {
            $ref: { enum: ["cameras"] },
            $id: { bsonType: "string" }
          }
        },
        status: { enum: ["active", "offline", "maintenance", "signal_lost"] },
        metrics: { bsonType: "object" }
      }
    }
  }
});
