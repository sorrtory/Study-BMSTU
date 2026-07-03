package metrics

import (
	"net/http"
	"strconv"

	"loadgen/internal/workload"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var durationBuckets = []float64{
	0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5,
	1, 2.5, 5, 10, 30, 60, 120,
}

var batchSizeBuckets = []float64{1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000}

type Metrics struct {
	registry *prometheus.Registry

	operationDuration *prometheus.HistogramVec
	operationTotal    *prometheus.CounterVec
	activeWorkers     *prometheus.GaugeVec
	batchSize         *prometheus.HistogramVec
	rowsTotal         *prometheus.CounterVec
	bytesTotal        *prometheus.CounterVec
}

type OperationLabels struct {
	RunID        string
	Model        string
	Scenario     string
	Operation    string
	StageClients string
}

func New() *Metrics {
	m := &Metrics{
		registry: prometheus.NewRegistry(),
		operationDuration: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Name:    "loadgen_operation_duration_seconds",
			Help:    "Duration of one loadgen operation.",
			Buckets: durationBuckets,
		}, []string{"run_id", "model", "scenario", "operation", "stage_clients"}),
		operationTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "loadgen_operation_total",
			Help: "Completed loadgen operations by status.",
		}, []string{"run_id", "model", "scenario", "operation", "stage_clients", "status"}),
		activeWorkers: prometheus.NewGaugeVec(prometheus.GaugeOpts{
			Name: "loadgen_active_workers",
			Help: "Current number of active loadgen workers.",
		}, []string{"run_id", "model", "scenario", "stage_clients"}),
		batchSize: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Name:    "loadgen_batch_size",
			Help:    "Batch size used by write operations.",
			Buckets: batchSizeBuckets,
		}, []string{"run_id", "model", "scenario", "operation", "stage_clients"}),
		rowsTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "loadgen_operation_rows_total",
			Help: "Rows or documents processed by loadgen operations.",
		}, []string{"run_id", "model", "scenario", "operation", "stage_clients"}),
		bytesTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Name: "loadgen_operation_bytes_total",
			Help: "Approximate bytes processed by loadgen operations.",
		}, []string{"run_id", "model", "scenario", "operation", "stage_clients", "direction"}),
	}
	m.registry.MustRegister(
		m.operationDuration,
		m.operationTotal,
		m.activeWorkers,
		m.batchSize,
		m.rowsTotal,
		m.bytesTotal,
	)
	return m
}

func (m *Metrics) Handler() http.Handler {
	return promhttp.HandlerFor(m.registry, promhttp.HandlerOpts{})
}

func (m *Metrics) ObserveOperation(labels OperationLabels, durationSeconds float64, batchSize int, result workload.OperationResult, err error) {
	values := labels.values()
	m.operationDuration.WithLabelValues(values...).Observe(durationSeconds)
	status := "success"
	if err != nil {
		status = "error"
	}
	m.operationTotal.WithLabelValues(append(values, status)...).Inc()

	if err == nil {
		m.rowsTotal.WithLabelValues(values...).Add(float64(result.Rows))
		m.observeBytes(labels, result)
	}

	if isWriteOperation(labels.Operation) {
		m.batchSize.WithLabelValues(values...).Observe(float64(batchSize))
	}
}

func (m *Metrics) SetActiveWorkers(runID, model, scenario string, stageClients int, active int) {
	m.activeWorkers.WithLabelValues(runID, model, scenario, strconv.Itoa(stageClients)).Set(float64(active))
}

func (m *Metrics) observeBytes(labels OperationLabels, result workload.OperationResult) {
	direction := "response"
	if isWriteOperation(labels.Operation) {
		direction = "request"
	}
	m.bytesTotal.WithLabelValues(append(labels.values(), direction)...).Add(float64(result.Bytes))
}

func (l OperationLabels) values() []string {
	return []string{l.RunID, l.Model, l.Scenario, l.Operation, l.StageClients}
}

func isWriteOperation(operation string) bool {
	return operation == workload.OpWriteComplexEvent || operation == workload.OpWriteTelemetry
}
