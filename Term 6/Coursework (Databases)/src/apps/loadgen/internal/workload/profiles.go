package workload

import (
	"fmt"
	"time"
)

func ProfileByName(name string) (SizeProfile, error) {
	switch name {
	case "", "small":
		return SizeProfile{Name: "small", Areas: 5, ZonesPerArea: 5, CamerasPerZone: 5}, nil
	case "medium":
		return SizeProfile{Name: "medium", Areas: 20, ZonesPerArea: 10, CamerasPerZone: 10}, nil
	case "large":
		return SizeProfile{Name: "large", Areas: 50, ZonesPerArea: 20, CamerasPerZone: 20}, nil
	default:
		return SizeProfile{}, fmt.Errorf("unsupported size profile: %s", name)
	}
}

func ValidateModelForTarget(model, target string) error {
	switch target {
	case "postgres":
		if model == ModelPGJSONB || model == ModelPGNormalized {
			return nil
		}
	case "mongo":
		if model == ModelMongoNested || model == ModelMongoNormalized {
			return nil
		}
	}
	return fmt.Errorf("model %q is not supported by target database %q", model, target)
}

func ValidateScenario(scenario string) error {
	switch scenario {
	case ScenarioWriteHeavy, ScenarioAnalytics, ScenarioBalanced:
		return nil
	default:
		return fmt.Errorf("unsupported scenario: %s", scenario)
	}
}

func ValidateSeed(seed int64) error {
	if seed <= 0 {
		return fmt.Errorf("seed must be a positive integer")
	}
	return nil
}

func NewRunID(model, scenario string, seed int64) string {
	return fmt.Sprintf("%s_%s_%s_seed-%d", time.Now().Format("2006-01-02_15-04-05"), model, scenario, seed)
}

func DefaultRunRequest(req RunRequest) (RunRequest, SizeProfile, error) {
	if err := ValidateScenario(req.Scenario); err != nil {
		return req, SizeProfile{}, err
	}
	profile, err := ProfileByName(req.Profile)
	if err != nil {
		return req, SizeProfile{}, err
	}
	if err := ValidateSeed(req.Seed); err != nil {
		return req, SizeProfile{}, err
	}
	if req.RunID == "" {
		req.RunID = NewRunID(req.Model, req.Scenario, req.Seed)
	}
	if req.DurationSeconds <= 0 {
		req.DurationSeconds = 60
	}
	if len(req.Stages) == 0 {
		req.Stages = []int{1, 5, 10, 25}
	}
	if req.EventBatchSize <= 0 {
		req.EventBatchSize = 25
	}
	if req.TelemetryBatchSize <= 0 {
		req.TelemetryBatchSize = 50
	}
	return req, profile, nil
}
