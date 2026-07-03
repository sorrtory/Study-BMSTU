nestedDb.areas.createIndex({ area_code: 1 }, { unique: true });
nestedDb.areas.createIndex({ area_code: 1, "zones.zone_code": 1 });

nestedDb.cameras.createIndex({ serial_number: 1 }, { unique: true });
nestedDb.cameras.createIndex({ ip_address: 1 }, { unique: true });
nestedDb.cameras.createIndex({ "area.area_code": 1, "zone.zone_code": 1 });
nestedDb.cameras.createIndex({ status: 1 });

nestedDb.events.createIndex({ occurred_at: -1 });
nestedDb.events.createIndex({ "area.area_code": 1, "zone.zone_code": 1, occurred_at: -1 });
nestedDb.events.createIndex({ "cameras.serial_number": 1, occurred_at: -1 });
nestedDb.events.createIndex({ event_type: 1, severity: 1, occurred_at: -1 });
nestedDb.events.createIndex({ "payload.objects.object_type": 1, occurred_at: -1 });

nestedDb.camera_telemetry.createIndex({ "camera.serial_number": 1, recorded_at: -1 });
nestedDb.camera_telemetry.createIndex({ "area.area_code": 1, "zone.zone_code": 1, recorded_at: -1 });
nestedDb.camera_telemetry.createIndex({ status: 1, recorded_at: -1 });
