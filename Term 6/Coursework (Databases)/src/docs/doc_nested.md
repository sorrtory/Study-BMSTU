# Вложенная документная модель MongoDB

Вложенная документная модель MongoDB строится на основе ER-модели и модели
PostgreSQL JSONB. В этой модели данные группируются в документы по
агрегатам, которые читаются и записываются вместе.

Модель не повторяет реляционную структуру таблица-в-коллекцию. Стабильные и
небольшие вложенные данные встраиваются в документы, а неограниченно растущие
потоки событий и телеметрии хранятся в отдельных коллекциях. Такой подход
соответствует типичному использованию MongoDB: минимизировать соединения при
чтении и хранить рядом данные, которые нужны одному сценарию запроса.

## Домены допустимых значений

Справочные значения хранятся строками внутри документов и валидируются на
уровне приложения или JSON Schema-валидации MongoDB.
Временные поля хранятся типом BSON Date; в примерах ниже они показаны в
ISO-формате для читаемости.

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

Коллекция `areas` хранит охраняемые территории. Зоны наблюдения встраиваются
в документ территории, так как зона не существует отдельно от территории, а
список зон имеет ограниченный размер по сравнению с потоком событий и
телеметрии.

```json
{
  "_id": "AREA-001",
  "area_code": "AREA-001",
  "name": "Main warehouse",
  "area_type": "warehouse",
  "address": "Moscow, Industrial street, 10",
  "description": "Main storage facility",
  "zones": [
    {
      "zone_code": "ENTRANCE",
      "name": "Main entrance",
      "zone_type": "entrance",
      "importance_level": 5,
      "description": "Entrance checkpoint"
    },
    {
      "zone_code": "STORAGE-A",
      "name": "Storage sector A",
      "zone_type": "warehouse",
      "importance_level": 3,
      "description": "Storage area"
    }
  ]
}
```

Поля документа:

- `_id` - идентификатор документа, совпадает с `area_code`;
- `area_code` - предметный идентификатор территории;
- `name` - название территории;
- `area_type` - тип территории;
- `address` - адрес или описание местоположения;
- `description` - дополнительное описание территории;
- `zones` - массив зон наблюдения внутри территории.

Поля элемента `zones`:

- `zone_code` - идентификатор зоны внутри территории;
- `name` - название зоны;
- `zone_type` - тип зоны;
- `importance_level` - уровень важности зоны;
- `description` - дополнительное описание зоны.

Рекомендуемые индексы:

```javascript
db.areas.createIndex({ area_code: 1 }, { unique: true })
db.areas.createIndex({ area_code: 1, "zones.zone_code": 1 })
```

### cameras

Коллекция `cameras` хранит камеры видеонаблюдения. Настройки камеры и ее
положение встраиваются в документ, так как они читаются вместе с камерой и
обновляются значительно реже, чем события и телеметрия.

```json
{
  "_id": "CAM-001",
  "serial_number": "CAM-001",
  "name": "Entrance camera 1",
  "model": "Hikvision DS-2CD",
  "ip_address": "192.168.10.21",
  "status": "active",
  "area": {
    "area_code": "AREA-001",
    "name": "Main warehouse"
  },
  "zone": {
    "zone_code": "ENTRANCE",
    "name": "Main entrance",
    "zone_type": "entrance"
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
- `area` - краткая встроенная информация о территории;
- `zone` - краткая встроенная информация о зоне установки;
- `position` - положение и ориентация камеры;
- `settings` - настройки видеопотока и видеоаналитики.

Рекомендуемые индексы:

```javascript
db.cameras.createIndex({ serial_number: 1 }, { unique: true })
db.cameras.createIndex({ ip_address: 1 }, { unique: true })
db.cameras.createIndex({ "area.area_code": 1, "zone.zone_code": 1 })
db.cameras.createIndex({ status: 1 })
```

### events

Коллекция `events` хранит аналитические события. Документ события содержит
встроенную информацию о зоне, территории, камерах-источниках и данные
события. Обнаруженные объекты хранятся в массиве `payload.objects`, так как
они не имеют самостоятельного жизненного цикла вне события.

```json
{
  "_id": "AREA-001:ENTRANCE:10025",
  "event_number": 10025,
  "occurred_at": "2026-05-24T12:31:20Z",
  "event_type": "line_crossing",
  "severity": "critical",
  "confidence": 0.94,
  "area": {
    "area_code": "AREA-001",
    "name": "Main warehouse"
  },
  "zone": {
    "zone_code": "ENTRANCE",
    "name": "Main entrance",
    "zone_type": "entrance",
    "importance_level": 5
  },
  "cameras": [
    {
      "serial_number": "CAM-001",
      "name": "Entrance camera 1"
    },
    {
      "serial_number": "CAM-002",
      "name": "Entrance camera 2"
    }
  ],
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
- `area` - краткая встроенная информация о территории;
- `zone` - краткая встроенная информация о зоне;
- `cameras` - массив камер, зафиксировавших событие;
- `payload` - типоспецифичные данные события.

Идентификатор `_id` формируется из `area.area_code`, `zone.zone_code` и
`event_number`, что соответствует предметному идентификатору события в
ER-модели.

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
db.events.createIndex({ occurred_at: -1 })
db.events.createIndex({ "area.area_code": 1, "zone.zone_code": 1, occurred_at: -1 })
db.events.createIndex({ "cameras.serial_number": 1, occurred_at: -1 })
db.events.createIndex({ event_type: 1, severity: 1, occurred_at: -1 })
db.events.createIndex({ "payload.objects.object_type": 1, occurred_at: -1 })
```

### camera_telemetry

Коллекция `camera_telemetry` хранит поток регулярных технических измерений.
Телеметрия не встраивается в документ камеры, потому что это неограниченно
растущий временной ряд.

```json
{
  "_id": "CAM-001:2026-05-24T12:31:00Z",
  "recorded_at": "2026-05-24T12:31:00Z",
  "camera": {
    "serial_number": "CAM-001",
    "name": "Entrance camera 1"
  },
  "area": {
    "area_code": "AREA-001",
    "name": "Main warehouse"
  },
  "zone": {
    "zone_code": "ENTRANCE",
    "name": "Main entrance"
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
- `camera` - краткая встроенная информация о камере;
- `area` - краткая встроенная информация о территории;
- `zone` - краткая встроенная информация о зоне;
- `status` - состояние камеры на момент фиксации;
- `metrics` - технические показатели камеры.

Идентификатор `_id` формируется из `camera.serial_number` и `recorded_at`.

Рекомендуемые индексы:

```javascript
db.camera_telemetry.createIndex({ "camera.serial_number": 1, recorded_at: -1 })
db.camera_telemetry.createIndex({ "area.area_code": 1, "zone.zone_code": 1, recorded_at: -1 })
db.camera_telemetry.createIndex({ status: 1, recorded_at: -1 })
```

## Обоснование вложенности

- Зоны вложены в `areas`, потому что они являются частью территории и не
  образуют неограниченно растущий поток данных.
- Настройки и положение камеры вложены в `cameras`, потому что обычно читаются
  вместе с камерой и редко изменяются.
- События вынесены в отдельную коллекцию, потому что это основной поток
  записей при нагрузочном эксперименте.
- Обнаруженные объекты вложены в `events.payload.objects`, потому что они
  существуют только как часть конкретного события.
- Телеметрия вынесена в отдельную коллекцию, потому что это регулярный
  временной ряд, который быстро растет и часто читается по диапазону времени.
- Территория, зона и камеры встраиваются в документы событий и телеметрии как
  денормализованные снимки, чтобы читать аналитические данные без соединений.

## Соответствие модели PostgreSQL JSONB

- Таблицы `area` и `zone` соответствуют коллекции `areas` со встроенным
  массивом `zones`.
- Таблица `camera` соответствует коллекции `cameras`; поля `position` и
  `settings` сохраняют структуру JSONB-модели.
- Таблицы `event` и `event_camera` соответствуют коллекции `events`, где
  камеры события встроены в массив `cameras`.
- Поле `event.payload` из JSONB-модели соответствует вложенному документу
  `payload` в коллекции `events`.
- Таблица `camera_telemetry` соответствует одноименной коллекции; поле
  `metrics` остается вложенным документом.
