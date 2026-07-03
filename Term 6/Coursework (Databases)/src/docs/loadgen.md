# Loadgen

Universal app that connects to postgres/mongodb and runs queries with different load patterns.

## HTTP API

Loadgen запускается отдельным контейнером для PostgreSQL или MongoDB. Целевая
СУБД выбирается один раз при старте через `LOADGEN_TARGET_DB`, а модель
хранения передается в HTTP-запросах. Поэтому один PostgreSQL loadgen
обрабатывает модели `pg-jsonb` и `pg-normalized`, а один MongoDB loadgen -
`mongo-nested` и `mongo-normalized`.

В Docker Compose используется один Docker-образ и два сервиса:

| Service            | `LOADGEN_TARGET_DB` | Внутренний endpoint     | Host endpoint                        |
| ------------------ | ------------------- | ----------------------- | ------------------------------------ |
| `loadgen-postgres` | `postgres`          | `loadgen-postgres:1111` | `localhost:${LOADGEN_POSTGRES_PORT}` |
| `loadgen-mongo`    | `mongo`             | `loadgen-mongo:1111`    | `localhost:${LOADGEN_MONGO_PORT}`    |

Prometheus снимает метрики напрямую с обоих endpoint `/metrics`. Pushgateway
не используется, потому что loadgen является долгоживущим HTTP-сервисом.

Frontend не обращается к этим endpoint напрямую. Пользовательский интерфейс
вызывает Express API `/api/loadgen/*`, а Express выбирает нужный loadgen по
модели хранения и хранит текущее состояние эксперимента.

| Method | Endpoint   | Request body                                                                                                                                                                    | Response                                  | Назначение                                                                                                |
| ------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `GET`  | `/health`  | -                                                                                                                                                                               | `text/plain`                              | Проверяет доступность loadgen и подключение к выбранной БД.                                               |
| `GET`  | `/metrics` | -                                                                                                                                                                               | Prometheus text format                    | Отдает live-метрики операций: duration histogram, counters, active workers, batch size, rows и bytes.     |
| `POST` | `/clear`   | `{ "model": "pg-jsonb" }`                                                                                                                                                       | `{ "status": "ok", "model": "pg-jsonb" }` | Очищает данные выбранной модели без удаления схемы, коллекций, валидаторов и индексов.                    |
| `POST` | `/seed`    | `{ "model": "pg-jsonb", "seed": 42, "profile": "small" }`                                                                                                                       | `{ "status": "ok", ... }`                 | Заполняет базовый мир наблюдения: территории, зоны, камеры и настройки.                                   |
| `POST` | `/run`     | `{ "model": "pg-jsonb", "scenario": "balanced", "seed": 42, "profile": "small", "duration_seconds": 60, "stages": [1, 5, 10, 25], "event_batch_size": 25, "telemetry_batch_size": 50 }` | `RunSummary`                              | Запускает нагрузочный сценарий для выбранной модели и возвращает итоговые счетчики и latency percentiles. |

Поддерживаемые модели:

| `LOADGEN_TARGET_DB` | Models                             |
| ------------------- | ---------------------------------- |
| `postgres`          | `pg-jsonb`, `pg-normalized`        |
| `mongo`             | `mongo-nested`, `mongo-normalized` |

Поддерживаемые сценарии нагрузки:

| Scenario          | Описание                                                   |
| ----------------- | ---------------------------------------------------------- |
| `write-heavy`     | Основной вес на запись сложных событий и телеметрии.       |
| `analytics-heavy` | Основной вес на аналитические чтения и таймлайн инцидента. |
| `balanced`        | Смешанный профиль записи и чтения.                         |

Поддерживаемые профили размера seed:

| Profile  | Территории | Зоны на территорию | Камеры на зону |
| -------- | ---------: | -----------------: | -------------: |
| `small`  |          5 |                  5 |              5 |
| `medium` |         20 |                 10 |             10 |
| `large`  |         50 |                 20 |             20 |

Значения по умолчанию для запуска через Express API и loadgen:

| Параметр               | Значение           |
| ---------------------- | ------------------ |
| `scenario`             | `balanced`         |
| `profile`              | `small`            |
| `seed`                 | `42`               |
| `duration_seconds`     | `60`               |
| `stages`               | `[1, 5, 10, 25]`   |
| `event_batch_size`     | `25`               |
| `telemetry_batch_size` | `50`               |

`seed` должен быть положительным целым числом. Значение `0` считается
некорректным.

Перед прогоном обычно выполняется последовательность:

```bash
curl -X POST http://localhost:1111/clear \
  -H 'Content-Type: application/json' \
  -d '{"model":"pg-jsonb"}'

curl -X POST http://localhost:1111/seed \
  -H 'Content-Type: application/json' \
  -d '{"model":"pg-jsonb","seed":42,"profile":"small"}'

curl -X POST http://localhost:1111/run \
  -H 'Content-Type: application/json' \
  -d '{"model":"pg-jsonb","scenario":"balanced","seed":42,"profile":"small","duration_seconds":60,"stages":[1,5,10,25]}'
```

## Golangci-lint

```bash
# Install golangci-lint
curl -sSfL https://golangci-lint.run/install.sh | sh -s -- -b $(go env GOPATH)/bin v2.12.0

golangci-lint run
golangci-lint fmt
```
