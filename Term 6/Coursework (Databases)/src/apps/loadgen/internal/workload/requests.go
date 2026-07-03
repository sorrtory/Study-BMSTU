package workload

import "encoding/json"

func (r *SeedRequest) UnmarshalJSON(data []byte) error {
	var raw struct {
		Model   string `json:"model"`
		Seed    *int64 `json:"seed"`
		Profile string `json:"profile"`
	}
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	*r = SeedRequest{
		Model:   raw.Model,
		Seed:    42,
		Profile: raw.Profile,
	}
	if raw.Seed != nil {
		if err := ValidateSeed(*raw.Seed); err != nil {
			return err
		}
		r.Seed = *raw.Seed
	}
	return nil
}

func (r *RunRequest) UnmarshalJSON(data []byte) error {
	var raw struct {
		Model              string `json:"model"`
		Scenario           string `json:"scenario"`
		Seed               *int64 `json:"seed"`
		Profile            string `json:"profile"`
		RunID              string `json:"run_id"`
		DurationSeconds    int    `json:"duration_seconds"`
		Stages             []int  `json:"stages"`
		EventBatchSize     int    `json:"event_batch_size"`
		TelemetryBatchSize int    `json:"telemetry_batch_size"`
	}
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	*r = RunRequest{
		Model:              raw.Model,
		Scenario:           raw.Scenario,
		Seed:               42,
		Profile:            raw.Profile,
		RunID:              raw.RunID,
		DurationSeconds:    raw.DurationSeconds,
		Stages:             raw.Stages,
		EventBatchSize:     raw.EventBatchSize,
		TelemetryBatchSize: raw.TelemetryBatchSize,
	}
	if raw.Seed != nil {
		if err := ValidateSeed(*raw.Seed); err != nil {
			return err
		}
		r.Seed = *raw.Seed
	}
	return nil
}
