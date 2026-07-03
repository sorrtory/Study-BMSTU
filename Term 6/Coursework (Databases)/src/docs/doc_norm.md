# Нормализованная документная модель MongoDB

Нормализованная документная модель MongoDB строится на основе ER-модели и
модели PostgreSQL JSONB. В отличие от вложенной документной модели, основные
сущности предметной области хранятся в отдельных коллекциях, а связи между
ними представлены ссылками.

Составные и вариативные поля, которые в PostgreSQL JSONB представлены типом
`JSONB`, сохраняются как вложенные документы MongoDB. Поэтому эта модель
нормализует связи между сущностями, но не раскладывает `position`,
`settings`, `payload` и `metrics` на отдельные коллекции.

## Домены допустимых значений

Справочные значения хранятся строками внутри документов и валидируются на
уровне приложения или JSON Schema-валидации MongoDB. Временные поля хранятся
типом BSON Date; в примерах ниже они показаны в ISO-формате для читаемости.

- `area_type`: `office`, `warehouse`, `parking`, `campus`,
  `industrial_site`;
- `zone_type`: `entrance`, `parking`, `warehouse`, `perimeter`,
  `service_room`;
- `camera_status`: `active`, `offline`, `maintenance`, `signal_lost`;
- `event_type`: `motion_detected`, `object_detected`, `line_crossing`,
  `signal_lost`;
- `severity`: `low`, `medium`, `high`, `critical`;
- `object_type`: `person`, `vehicle`, `unknown`;
- `direction`: `inside`, `outside`, `left_to_right`, `right_to_left`,
  `unknown`.

## Коллекции

### areas

Коллекция `areas` хранит охраняемые территории.

```json
{
  "_id": "AREA-001",
  "area_code": "AREA-001",
  "name": "Main warehouse",
  "area_type": "warehouse",
  "address": "Moscow, Industrial street, 10",
  "description": "Main storage facility"
}
```

Поля документа:

- `_id` - идентификатор документа, совпадает с `area_code`;
- `area_code` - предметный идентификатор территории;
- `name` - название территории;
- `area_type` - тип территории;
- `address` - адрес или описание местоположения;
- `description` - дополнительное описание территории.

Рекомендуемые индексы:

```javascript
db.areas.createIndex({ area_code: 1 }, { unique: true })
```

### zones

Коллекция `zones` хранит зоны наблюдения. Каждая зона содержит ссылку на
территорию.
Одна территория может иметь множество документов зон в коллекции `zones`.

```json
{
  "_id": "AREA-001:ENTRANCE",
  "zone_code": "ENTRANCE",
  "name": "Main entrance",
  "zone_type": "entrance",
  "importance_level": 5,
  "description": "Entrance checkpoint",
  "area": {
    "$ref": "areas",
    "$id": "AREA-001"
  }
}
```

Поля документа:

- `_id` - идентификатор документа зоны;
- `zone_code` - идентификатор зоны внутри территории;
- `name` - название зоны;
- `zone_type` - тип зоны;
- `importance_level` - уровень важности зоны;
- `description` - дополнительное описание зоны;
- `area` - ссылка на документ территории.

Идентификатор `_id` формируется из `area.$id` и `zone_code`, так как код зоны
уникален внутри территории.

Рекомендуемые индексы:

```javascript
db.zones.createIndex({ "area.$id": 1, zone_code: 1 }, { unique: true })
db.zones.createIndex({ zone_type: 1 })
```

### cameras

Коллекция `cameras` хранит камеры видеонаблюдения. Документ камеры содержит
ссылку на зону, а `position` и `settings` сохраняются как вложенные документы
по аналогии с полями `camera.position` и `camera.settings` в PostgreSQL JSONB.
Одна камера относится к одной зоне, при этом разные камеры могут ссылаться на
разные зоны или на одну и ту же зону.

```json
{
  "_id": "CAM-001",
  "serial_number": "CAM-001",
  "name": "Entrance camera 1",
  "model": "Hikvision DS-2CD",
  "ip_address": "192.168.10.21",
  "status": "active",
  "zone": {
    "$ref": "zones",
    "$id": "AREA-001:ENTRANCE"
  },
  "position": {
    "x": 12.5,
    "y": 8.0,
    "z": 3.2,
    "yaw_angle": 90.0,
    "pitch_angle": -12.0,
    "roll_angle": 0.0,
    "view_angle": 110.0
  },
  "settings": {
    "stream": {
      "codec": "H.264",
      "resolution_width": 1920,
      "resolution_height": 1080,
      "fps": 25,
      "bitrate_kbps": 4096,
      "rtsp_enabled": true
    },
    "analytics": {
      "motion_detection": true,
      "line_crossing": true,
      "object_detection": true,
      "sensitivity": 0.75,
      "min_object_confidence": 0.6
    },
    "detection_zones": [
      {
        "code": "entrance_area",
        "points": [
          { "x": 10, "y": 20 },
          { "x": 300, "y": 20 },
          { "x": 300, "y": 200 },
          { "x": 10, "y": 200 }
        ]
      }
    ],
    "crossing_lines": [
      {
        "code": "L-01",
        "name": "Entrance line",
        "start": { "x": 120, "y": 40 },
        "end": { "x": 120, "y": 220 },
        "allowed_direction": "outside"
      }
    ]
  }
}
```

Поля документа:

- `_id` - идентификатор документа, совпадает с `serial_number`;
- `serial_number` - серийный номер камеры;
- `name` - название камеры;
- `model` - модель камеры;
- `ip_address` - сетевой адрес камеры;
- `status` - текущее состояние камеры;
- `zone` - ссылка на документ зоны;
- `position` - положение и ориентация камеры;
- `settings` - настройки видеопотока и видеоаналитики.

Если в дальнейшем потребуется описывать камеру, которая одновременно
относится к нескольким зонам наблюдения, связь `Zone` - `Camera` нужно будет
изменить с 1:N на M:N и добавить отдельную коллекцию связей. В текущей
предметной области камера устанавливается в одной зоне, а ее внутренние зоны
детекции описываются в `settings.detection_zones`.

Рекомендуемые индексы:

```javascript
db.cameras.createIndex({ serial_number: 1 }, { unique: true })
db.cameras.createIndex({ ip_address: 1 }, { unique: true })
db.cameras.createIndex({ "zone.$id": 1 })
db.cameras.createIndex({ status: 1 })
```

### events

Коллекция `events` хранит аналитические события. Документ события содержит
ссылку на зону, а типоспецифичные данные события хранятся во вложенном
документе `payload`, соответствующем `event.payload` в PostgreSQL JSONB.

```json
{
  "_id": "AREA-001:ENTRANCE:10025",
  "event_number": 10025,
  "occurred_at": "2026-05-24T12:31:20Z",
  "event_type": "line_crossing",
  "severity": "critical",
  "confidence": 0.94,
  "zone": {
    "$ref": "zones",
    "$id": "AREA-001:ENTRANCE"
  },
  "payload": {
    "frame_time_ms": 1540,
    "line_code": "L-01",
    "direction": "inside",
    "objects": [
      {
        "object_number": 1,
        "object_type": "person",
        "confidence": 0.93,
        "bounding_box": {
          "x": 130,
          "y": 70,
          "width": 58,
          "height": 175
        },
        "attributes": {
          "has_bag": false
        }
      }
    ]
  }
}
```

Поля документа:

- `_id` - идентификатор документа события;
- `event_number` - номер события внутри зоны;
- `occurred_at` - время возникновения события;
- `event_type` - тип события;
- `severity` - уровень значимости события;
- `confidence` - уверенность аналитического алгоритма;
- `zone` - ссылка на документ зоны;
- `payload` - типоспецифичные данные события.

Идентификатор `_id` формируется из идентификатора зоны и `event_number`.
Обнаруженные объекты хранятся в `payload.objects`, так как они являются
частью события и не имеют самостоятельного жизненного цикла.

#### `payload` для `motion_detected`

```json
{
  "frame_time_ms": 920,
  "motion_area_percent": 18.5,
  "detection_zone_code": "entrance_area",
  "duration_ms": 2400,
  "objects": []
}
```

#### `payload` для `object_detected`

```json
{
  "frame_time_ms": 1100,
  "objects": [
    {
      "object_number": 1,
      "object_type": "vehicle",
      "confidence": 0.87,
      "bounding_box": {
        "x": 420,
        "y": 210,
        "width": 220,
        "height": 120
      },
      "attributes": {
        "color": "white",
        "license_plate": "A123BC",
        "license_plate_confidence": 0.74
      }
    }
  ]
}
```

#### `payload` для `line_crossing`

```json
{
  "frame_time_ms": 1540,
  "line_code": "L-01",
  "direction": "inside",
  "objects": [
    {
      "object_number": 1,
      "object_type": "person",
      "confidence": 0.93,
      "bounding_box": {
        "x": 130,
        "y": 70,
        "width": 58,
        "height": 175
      },
      "attributes": {
        "has_bag": false
      }
    }
  ]
}
```

#### `payload` для `signal_lost`

```json
{
  "reason": "network_timeout",
  "last_frame_at": "2026-05-24T12:30:05Z",
  "downtime_seconds": 45
}
```

Рекомендуемые индексы:

```javascript
db.events.createIndex({ "zone.$id": 1, event_number: 1 }, { unique: true })
db.events.createIndex({ occurred_at: -1 })
db.events.createIndex({ "zone.$id": 1, occurred_at: -1 })
db.events.createIndex({ event_type: 1, severity: 1, occurred_at: -1 })
db.events.createIndex({ "payload.objects.object_type": 1, occurred_at: -1 })
```

### event_cameras

Коллекция `event_cameras` реализует связь многие-ко-многим между событиями и
камерами. Она соответствует таблице `event_camera` в PostgreSQL JSONB.

```json
{
  "_id": "AREA-001:ENTRANCE:10025:CAM-001",
  "event": {
    "$ref": "events",
    "$id": "AREA-001:ENTRANCE:10025"
  },
  "camera": {
    "$ref": "cameras",
    "$id": "CAM-001"
  }
}
```

Поля документа:

- `_id` - идентификатор связи события и камеры;
- `event` - ссылка на событие;
- `camera` - ссылка на камеру.

На уровне предметной области событие должно быть связано хотя бы с одной
камерой. В MongoDB это требование обеспечивается логикой записи данных.

Рекомендуемые индексы:

```javascript
db.event_cameras.createIndex({ "event.$id": 1, "camera.$id": 1 }, { unique: true })
db.event_cameras.createIndex({ "camera.$id": 1, "event.$id": 1 })
```

### camera_telemetry

Коллекция `camera_telemetry` хранит регулярные записи технического состояния
камер. Документ содержит ссылку на камеру, а технические показатели хранятся
во вложенном документе `metrics`, соответствующем `camera_telemetry.metrics`
в PostgreSQL JSONB.

```json
{
  "_id": "CAM-001:2026-05-24T12:31:00Z",
  "recorded_at": "2026-05-24T12:31:00Z",
  "camera": {
    "$ref": "cameras",
    "$id": "CAM-001"
  },
  "status": "active",
  "metrics": {
    "temperature_celsius": 42.5,
    "cpu_load": 0.61,
    "memory_usage": 0.74,
    "bitrate_kbps": 4096,
    "packet_loss": 0.01,
    "latency_ms": 35,
    "uptime_seconds": 86400
  }
}
```

Поля документа:

- `_id` - идентификатор записи телеметрии;
- `recorded_at` - время фиксации телеметрии;
- `camera` - ссылка на документ камеры;
- `status` - состояние камеры на момент фиксации;
- `metrics` - технические показатели камеры.

Идентификатор `_id` формируется из `camera.$id` и `recorded_at`.

Рекомендуемые индексы:

```javascript
db.camera_telemetry.createIndex({ "camera.$id": 1, recorded_at: -1 })
db.camera_telemetry.createIndex({ status: 1, recorded_at: -1 })
```

## Соответствие модели PostgreSQL JSONB

- Таблица `area` соответствует коллекции `areas`.
- Таблица `zone` соответствует коллекции `zones`; связь с территорией
  представлена ссылкой `area`.
- Таблица `camera` соответствует коллекции `cameras`; связь с зоной
  представлена ссылкой `zone`.
- Поля `camera.position` и `camera.settings` сохраняют структуру JSONB-модели
  как вложенные документы.
- Таблица `event` соответствует коллекции `events`; связь с зоной
  представлена ссылкой `zone`.
- Таблица `event_camera` соответствует коллекции `event_cameras`.
- Поле `event.payload` сохраняет структуру JSONB-модели как вложенный
  документ.
- Таблица `camera_telemetry` соответствует одноименной коллекции; связь с
  камерой представлена ссылкой `camera`, а поле `metrics` сохраняет структуру
  JSONB-модели как вложенный документ.

## Отличие от вложенной документной модели

- Вложенная модель встраивает зоны в `areas`, а нормализованная хранит зоны в
  отдельной коллекции `zones`.
- Вложенная модель встраивает краткие данные территории и зоны в `cameras`,
  `events` и `camera_telemetry`, а нормализованная использует ссылки.
- Вложенная модель хранит камеры события массивом внутри `events`, а
  нормализованная использует коллекцию `event_cameras`.
- Обе документные модели сохраняют `position`, `settings`, `payload` и
  `metrics` вложенными документами, чтобы соответствовать PostgreSQL JSONB.
