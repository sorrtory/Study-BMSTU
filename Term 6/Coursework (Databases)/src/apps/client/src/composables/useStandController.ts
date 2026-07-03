import { computed, onMounted, onUnmounted, shallowRef } from 'vue'
import {
  clearLoadgenModel,
  getLoadgenOptions,
  getStandStatus,
  prepareLoadgenModel,
  runLoadgenExperiment,
  type LoadgenOptions,
  type RunRequest,
  type SeedRequest,
  type StandStatus,
} from '../api/loadgen'

export type StandAction = 'clear' | 'run'

export function useStandController() {
  const options = shallowRef<LoadgenOptions | null>(null)
  const stand = shallowRef<StandStatus | null>(null)
  const action = shallowRef<StandAction | null>(null)
  const errorMessage = shallowRef('')
  const updatedAt = shallowRef('')

  const isBusy = computed(() => Boolean(action.value) || Boolean(stand.value?.experiment.active))
  const experiment = computed(() => stand.value?.experiment ?? null)
  const services = computed(() => stand.value?.services ?? [])
  const grafana = computed(() => experiment.value?.grafana ?? stand.value?.grafana ?? null)

  let pollTimer: number | undefined

  async function refreshStand() {
    try {
      stand.value = await getStandStatus()
      updatedAt.value = new Date().toISOString()
      errorMessage.value = ''
    } catch (error) {
      errorMessage.value = error instanceof Error
        ? error.message
        : 'Не удалось обновить состояние стенда'
    }
  }

  async function loadOptions() {
    options.value = await getLoadgenOptions()
  }

  async function runAction<T>(name: StandAction, request: () => Promise<T>) {
    action.value = name
    errorMessage.value = ''

    try {
      const result = await request()
      await refreshStand()
      return result
    } catch (error) {
      errorMessage.value = error instanceof Error
        ? error.message
        : 'Действие завершилось с ошибкой'
      await refreshStand()
      return undefined
    } finally {
      action.value = null
    }
  }

  function clearModel(payload: SeedRequest) {
    return runAction('clear', () => clearLoadgenModel({ model: payload.model }))
  }

  function runExperiment(payload: RunRequest) {
    return runAction('run', async () => {
      await prepareLoadgenModel({
        model: payload.model,
        profile: payload.profile,
        seed: payload.seed,
      })

      return runLoadgenExperiment(payload)
    })
  }

  onMounted(() => {
    void loadOptions().catch((error) => {
      errorMessage.value = error instanceof Error
        ? error.message
        : 'Не удалось загрузить настройки стенда'
    })
    void refreshStand()
    pollTimer = window.setInterval(() => {
      void refreshStand()
    }, 2000)
  })

  onUnmounted(() => {
    if (pollTimer) {
      window.clearInterval(pollTimer)
    }
  })

  return {
    action,
    clearModel,
    errorMessage,
    experiment,
    grafana,
    isBusy,
    options,
    refreshStand,
    runExperiment,
    services,
    updatedAt,
  }
}
