# Commands that were run 


```bash
pnpm init
mkdir -p apps

# Agents / skills
npx skills add vuejs-ai/skills -a codex \
  --skill vue-best-practices

# Client
pnpm create vite apps/client
cd apps/client
pnpm add zod

# Server
mkdir -p apps/server
cd apps/server
pnpm init
pnpm add express cors
pnpm add -D typescript tsx @types/node @types/express @types/cors
pnpm add dotenv zod

# Runtime package manager version used in package.json and Dockerfiles
corepack prepare pnpm@11.2.2 --activate
# pnpm 11 requires explicitly approved dependency build scripts.
# apps/client and apps/server allow dependency build scripts in Docker through
# pnpm-workspace.yaml because the lockfiles are fixed for this coursework setup.

# Loadgen
mkdir -p apps/loadgen
cd apps/loadgen
go mod init loadgen
go get github.com/joho/godotenv
go get github.com/caarlos0/env/v11
go get -u github.com/rs/zerolog/log
go get github.com/jackc/pgx/v5
go get github.com/jackc/pgx/v5/pgxpool
go get github.com/google/uuid
go get go.mongodb.org/mongo-driver/v2/mongo
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promhttp
```

# Loadgen Docker

```bash
docker compose -f src/compose.yml build loadgen-postgres loadgen-mongo
docker compose -f src/compose.yml up -d loadgen-postgres loadgen-mongo prometheus
```

# Web Docker

```bash
docker compose -f src/compose.yml build client server
docker compose -f src/compose.yml up -d client server
```

# Grafana

```bash
# https://grafana.com/grafana/dashboards/21743-cadvisor-exporter-docker-containers-overview/?utm_source=chatgpt.com
# Grafana update "Datasource ${DS_PROMETHEUS} was not found" OR envsubst
sed -i 's/\${DS_PROMETHEUS}/Prometheus/g' grafana/dashboards/*.json
```

# Experiment metrics

```bash
# Compare p50/p95/p99 latency by model from Prometheus.
scripts/compare-latency.sh

# Show latency percentiles by model and operation.
scripts/compare-latency.sh --by-operation

# Common filters.
SCENARIO=balanced scripts/compare-latency.sh
RUN_ID='.*balanced.*' WINDOW=2h scripts/compare-latency.sh
```
