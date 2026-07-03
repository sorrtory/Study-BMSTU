normalizedDb.areas.createIndex({ area_code: 1 }, { unique: true });

normalizedDb.zones.createIndex({ "area.$id": 1, zone_code: 1 }, { unique: true });
normalizedDb.zones.createIndex({ zone_type: 1 });

normalizedDb.cameras.createIndex({ serial_number: 1 }, { unique: true });
normalizedDb.cameras.createIndex({ ip_address: 1 }, { unique: true });
normalizedDb.cameras.createIndex({ "zone.$id": 1 });
normalizedDb.cameras.createIndex({ status: 1 });

normalizedDb.events.createIndex({ "zone.$id": 1, event_number: 1 }, { unique: true });
normalizedDb.events.createIndex({ occurred_at: -1 });
normalizedDb.events.createIndex({ "zone.$id": 1, occurred_at: -1 });
normalizedDb.events.createIndex({ event_type: 1, severity: 1, occurred_at: -1 });
normalizedDb.events.createIndex({ "payload.objects.object_type": 1, occurred_at: -1 });

normalizedDb.event_cameras.createIndex({ "event.$id": 1, "camera.$id": 1 }, { unique: true });
normalizedDb.event_cameras.createIndex({ "camera.$id": 1, "event.$id": 1 });

normalizedDb.camera_telemetry.createIndex({ "camera.$id": 1, recorded_at: -1 });
normalizedDb.camera_telemetry.createIndex({ status: 1, recorded_at: -1 });
