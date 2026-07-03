import { computed, shallowRef } from 'vue'
import { runLoadgenExperiment, type LoadScenario, type RunRequest, type StorageModel } from '../api/loadgen'

export type ScenarioRunState = 'idle' | 'running' | 'success' | 'error'

export interface ScenarioRunRequest extends Omit<RunRequest, 'model' | 'scenario'> {
  model: StorageModel
  scenario: LoadScenario
}

export function useScenarioRunner() {
  const state = shallowRef<ScenarioRunState>('idle')
  const errorMessage = shallowRef('')
  const lastRunId = shallowRef('')
  const lastMessage = shallowRef('')
  const grafanaDashboardUrl = shallowRef('')

  const isRunning = computed(() => state.value === 'running')
  const statusText = computed(() => {
    if (state.value === 'running') {
      return 'Запуск сценария'
    }

    if (state.value === 'success') {
      return lastMessage.value || 'Сценарий запущен'
    }

    if (state.value === 'error') {
      return errorMessage.value
    }

    return 'Готов к запуску'
  })

  async function runScenario(payload: ScenarioRunRequest) {
    state.value = 'running'
    errorMessage.value = ''
    lastRunId.value = ''
    lastMessage.value = ''
    grafanaDashboardUrl.value = ''

    try {
      const data = await runLoadgenExperiment(payload)
      state.value = 'success'
      lastRunId.value = data.summary.run_id
      grafanaDashboardUrl.value = data.grafana.dashboard
      lastMessage.value = 'Эксперимент завершен'
    } catch (error) {
      state.value = 'error'
      errorMessage.value = error instanceof Error
        ? error.message
        : 'Не удалось запустить сценарий'
    }
  }

  return {
    errorMessage,
    grafanaDashboardUrl,
    isRunning,
    lastMessage,
    lastRunId,
    runScenario,
    state,
    statusText,
  }
}
