package workload

import "math/rand"

func ChooseOperation(scenario string, r *rand.Rand) string {
	roll := r.Intn(100)
	switch scenario {
	case ScenarioWriteHeavy:
		return chooseWriteHeavyOperation(roll)
	case ScenarioAnalytics:
		return chooseAnalyticsOperation(roll)
	default:
		return chooseBalancedOperation(roll)
	}
}

func chooseWriteHeavyOperation(roll int) string {
	switch {
	case roll < 60:
		return OpWriteComplexEvent
	case roll < 95:
		return OpWriteTelemetry
	case roll < 97:
		return OpAggObjectActivity
	case roll < 99:
		return OpAggTelemetryHealth
	default:
		return OpReadIncidentTimeline
	}
}

func chooseAnalyticsOperation(roll int) string {
	switch {
	case roll < 15:
		return OpWriteComplexEvent
	case roll < 30:
		return OpWriteTelemetry
	case roll < 60:
		return OpAggObjectActivity
	case roll < 90:
		return OpAggTelemetryHealth
	default:
		return OpReadIncidentTimeline
	}
}

func chooseBalancedOperation(roll int) string {
	switch {
	case roll < 35:
		return OpWriteComplexEvent
	case roll < 70:
		return OpWriteTelemetry
	case roll < 80:
		return OpAggObjectActivity
	case roll < 90:
		return OpAggTelemetryHealth
	default:
		return OpReadIncidentTimeline
	}
}
