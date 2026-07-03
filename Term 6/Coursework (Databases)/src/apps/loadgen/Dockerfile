FROM golang:1.25 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /loadgen ./cmd/loadgen

FROM alpine:3.22

RUN addgroup -S loadgen && adduser -S loadgen -G loadgen
COPY --from=builder /loadgen /loadgen
USER loadgen

EXPOSE 1111

ENTRYPOINT ["/loadgen"]
