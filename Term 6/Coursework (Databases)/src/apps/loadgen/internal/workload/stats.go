package workload

import (
	"math"
	"sync"
	"time"
)

type LatencyRecorder struct {
	mu      sync.Mutex
	samples map[string][]float64
	stats   map[string]OperationStats
}

func NewLatencyRecorder() *LatencyRecorder {
	return &LatencyRecorder{
		samples: make(map[string][]float64),
		stats:   make(map[string]OperationStats),
	}
}

func (r *LatencyRecorder) Observe(operation string, latency time.Duration, result OperationResult, err error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	stat := r.stats[operation]
	if err != nil {
		stat.Errors++
	} else {
		stat.Success++
		stat.Rows += int64(result.Rows)
		stat.Bytes += int64(result.Bytes)
	}
	r.samples[operation] = append(r.samples[operation], float64(latency.Microseconds())/1000)
	r.stats[operation] = stat
}

func (r *LatencyRecorder) Snapshot() map[string]OperationStats {
	r.mu.Lock()
	defer r.mu.Unlock()
	out := make(map[string]OperationStats, len(r.stats))
	for op, stat := range r.stats {
		values := append([]float64(nil), r.samples[op]...)
		sortFloat64(values)
		stat.MinMs = percentile(values, 0)
		stat.P50Ms = percentile(values, 50)
		stat.P95Ms = percentile(values, 95)
		stat.P99Ms = percentile(values, 99)
		stat.MaxMs = percentile(values, 100)
		out[op] = stat
	}
	return out
}

func AddStats(dst map[string]OperationStats, src map[string]OperationStats) {
	for op, stat := range src {
		cur := dst[op]
		cur.Success += stat.Success
		cur.Errors += stat.Errors
		cur.Rows += stat.Rows
		cur.Bytes += stat.Bytes
		cur.MinMs = minNonZero(cur.MinMs, stat.MinMs)
		cur.P50Ms = stat.P50Ms
		cur.P95Ms = stat.P95Ms
		cur.P99Ms = stat.P99Ms
		if stat.MaxMs > cur.MaxMs {
			cur.MaxMs = stat.MaxMs
		}
		dst[op] = cur
	}
}

func percentile(values []float64, p float64) float64 {
	if len(values) == 0 {
		return 0
	}
	if p <= 0 {
		return values[0]
	}
	if p >= 100 {
		return values[len(values)-1]
	}
	idx := int(math.Ceil((p/100)*float64(len(values)))) - 1
	if idx < 0 {
		idx = 0
	}
	if idx >= len(values) {
		idx = len(values) - 1
	}
	return values[idx]
}

func sortFloat64(values []float64) {
	for i := 1; i < len(values); i++ {
		key := values[i]
		j := i - 1
		for j >= 0 && values[j] > key {
			values[j+1] = values[j]
			j--
		}
		values[j+1] = key
	}
}

func minNonZero(a, b float64) float64 {
	if a == 0 {
		return b
	}
	if b == 0 {
		return a
	}
	if b < a {
		return b
	}
	return a
}
